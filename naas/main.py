import base64
from functools import partial

import httpx
from sanic import Sanic, response
from sanic.log import logger
from sanic_openapi import swagger_blueprint
import json
import os

import vm_cleanup
from digitalocean_auth import DIGITALOCEAN_COMMON_HEADERS

app = Sanic("NaaS")
app.blueprint(swagger_blueprint)


def generate_cloud_init() -> str:
    config_template_path = "server_config_templates"
    with open(f"{config_template_path}/headless_config.json") as f:
        headless_config = json.load(f)
        headless_config['loginCredential'] = os.environ['NEOS_USER']
        headless_config['loginPassword'] = os.environ['NEOS_PASS']
        base64_headless_config = base64.b64encode(json.dumps(headless_config).encode('utf-8')).decode('utf-8')

    with open(f"{config_template_path}/cloud_init.yaml") as f:
        cloud_init_template = f.read()

    return cloud_init_template.format(base64_headless_config=base64_headless_config)


@app.route("/", methods=['GET'])
async def root_path(request):
    return response.redirect('/swagger')


@app.route("/neos/instance/<instance_id>", methods=['GET'])
async def instance_get_endpoint(request, instance_id):
    # logger.info("route='/neos/instance/%s", instance_id)
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.digitalocean.com/v2/droplets?tag_name=instance_id:{instance_id}".format(instance_id=instance_id),
            headers=DIGITALOCEAN_COMMON_HEADERS,
        )
    if r.is_error:
        logger.info("request={}".format(r.request.__dict__))
        logger.error("response={}".format(r.json()))
        return response.json({"status": "error", "message": r.reason_phrase}, status=500)
    droplets = r.json()['droplets']
    if len(droplets) == 0:
        return response.json(
            {"status": "error", "message": "Not droplets match that id. id={}".format(instance_id)}, status=400)
    if len(droplets) > 1:
        return response.json(
            {"status": "error", "message": "More than one droplet matches that id. id={}".format(instance_id)}, status=400)
    if droplets[0]["status"] == "new":
        return response.json({"status": "instantiating", "instance_id": instance_id}, status=200)
    if droplets[0]["status"] != "active":
        return response.json({"status": "error",
                              "message": "The server's status does not equal 'active'. status={}"
                             .format(droplets[0]["status"])}, status=500)
    logger.info("response={}".format(r.json()))
    return response.json({"status": "healthy", "instance_id": instance_id})


async def get_ssh_key_ids():
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.digitalocean.com/v2/account/keys",
            headers=DIGITALOCEAN_COMMON_HEADERS,
        )
    if r.is_error:
        logger.info("request={}".format(r.request.__dict__))
        logger.error("response={}".format(r.json()))
        # TODO handle this error correctly
        return response.json({"status": "error", "message": r.reason_phrase}, status=500)
    return [k['id'] for k in r.json()['ssh_keys']]


async def get_base_images():
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.digitalocean.com/v2/images?private=true",
            headers=DIGITALOCEAN_COMMON_HEADERS,
        )
    if r.is_error:
        logger.info("request={}".format(r.request.__dict__))
        logger.error("response={}".format(r.json()))
        # TODO handle this error correctly
        return response.json({"status": "error", "message": r.reason_phrase}, status=500)
    base_images = [i for i in r.json()['images'] if i['name'].startswith('baseimage')]
    latest_base = sorted(base_images, key=lambda x: x['created_at'], reverse=True)[0]
    return latest_base


# Unfortunately Neos lacks a DELETE HTTP request logix node so we have to put the verb in the method.
@app.route("/neos/instance/<instance_id>/create", methods=['POST'])
async def instance_create_endpoint(request, instance_id):
    data = request.json
    if data is None:
        return response.HTTPResponse("Missing json payload.", status=400)
    if 'user' not in data.keys():
        return response.HTTPResponse("Missing 'user' json payload parameter.", status=400)
    if 'lifetime' not in data.keys():
        return response.HTTPResponse("Missing 'lifetime' json payload parameter.", status=400)
    ssh_keys = await get_ssh_key_ids()
    base_image = await get_base_images()
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://api.digitalocean.com/v2/droplets",
            headers=DIGITALOCEAN_COMMON_HEADERS,
            json={
                "name": "neos-server-{}".format(instance_id),
                "region": "sfo3",
                "size": "s-1vcpu-1gb",
                "image": base_image['id'],
                "ipv6": True,
                "monitoring": True,
                "tags": ["neos", f"instance_id:{instance_id}", f"lifetime:{data['lifetime']}", f"user:{data['user']}"],
                "ssh_keys": ssh_keys,
                "user_data": generate_cloud_init()
            }
        )
        if r.is_error:
            logger.info("request={}".format(r.request.__dict__))
            logger.error("response={}".format(r.json()))
            return response.json({"status": "error", "message": r.reason_phrase}, status=500)
        else:
            return response.json({"status": "created", "instance_id": instance_id}, status=201)


# Unfortunately Neos lacks a DELETE HTTP request logix node so we have to put the verb in the method.
@app.route("/neos/instance/<instance_id>/delete", methods=['POST'])
async def instance_delete_endpoint(request, instance_id):
    async with httpx.AsyncClient() as client:
        r = await client.delete(
            "https://api.digitalocean.com/v2/droplets?tag_name={instance_id}".format(instance_id=instance_id),
            headers=DIGITALOCEAN_COMMON_HEADERS
        )
    if r.is_error:
        logger.info("request={}".format(r.request.__dict__))
        logger.error("response={}".format(r.json()))
        return response.json({"status": "error", "message": r.reason_phrase}, status=500)
    else:
        return response.json({"status": "deleted", "instance_id": instance_id})


@app.listener('after_server_start')
async def schedule_jobs(app, loop):
    loop.call_later(600, partial(vm_cleanup.schedule_vm_cleanup, loop))


if __name__ == "__main__":
    # Warning: Don't use workers or scheduled jobs will be executed more than one at a time.
    app.run(host="0.0.0.0", port=8000, debug=True, access_log=True)
