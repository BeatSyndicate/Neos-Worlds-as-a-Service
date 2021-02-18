from sanic import Sanic
from sanic.response import json
from sanic.log import logger
import httpx
import os

app = Sanic("NaaS")

DIGITALOCEAN_COMMON_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {token}".format(token=os.environ['DO_API_TOKEN'])
}


@app.route("/neos/instance/<instance_id>", methods=['GET'])
async def instance_get_endpoint(request, instance_id):
    # logger.info("route='/neos/instance/%s", instance_id)
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.digitalocean.com/v2/droplets?tag_name={instance_id}".format(instance_id=instance_id),
            headers=DIGITALOCEAN_COMMON_HEADERS,
        )
    if r.is_error:
        logger.info("request={}".format(r.request.__dict__))
        logger.error("response={}".format(r.json()))
        return json({"status": "error", "message": r.reason_phrase})
    droplets = r.json()['droplets']
    if len(droplets) > 1:
        return json({"status": "error", "message": "More than one droplet matches that id. id={}".format(instance_id)})
    if droplets[0]["status"] == "new":
        return json({"status": "instantiating", "instance_id": instance_id})
    if droplets[0]["status"] != "active":
        return json({"status": "error",
                     "message": "The server's status does not equal 'active'. status={}"
                    .format(droplets[0]["status"])})
    logger.info("response={}".format(r.json()))
    return json({"status": "healthy", "instance_id": instance_id})


# Unfortunately Neos lacks a DELETE HTTP request logix node so we have to put the verb in the method.
@app.route("/neos/instance/<instance_id>/create", methods=['POST'])
async def instance_create_endpoint(request, instance_id):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://api.digitalocean.com/v2/droplets",
            headers=DIGITALOCEAN_COMMON_HEADERS,
            json={
                "name": "neos-server-{}".format(instance_id),
                "region": "sfo3",
                "size": "s-1vcpu-1gb",
                "image": "ubuntu-16-04-x64",
                "ipv6": True,
                "monitoring": True,
                "tags": ["neos", instance_id]
            }
        )
        if r.is_error:
            logger.info("request={}".format(r.request.__dict__))
            logger.error("response={}".format(r.json()))
            return json({"status": "error", "message": r.reason_phrase})
        else:
            return json({"status": "created", "instance_id": instance_id})


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
        return json({"status": "error", "message": r.reason_phrase})
    else:
        return json({"status": "deleted", "instance_id": instance_id})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True, access_log=True, workers=os.cpu_count())
