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
async def instance_endpoint(request, instance_id):
    # logger.info("route='/neos/instance/%s", instance_id)
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://api.digitalocean.com/v2/droplets?tag_name={instance_id}".format(instance_id=instance_id),
            headers=DIGITALOCEAN_COMMON_HEADERS,
        )
    # TODO: parse and return vm info
    return json({"status": "healthy", "instance_id": instance_id, "log_websocket": ""})


# Unfortunately Neos lacks a DELETE HTTP request logix node so we have to put the verb in the method.
@app.route("/neos/instance/<instance_id>/create", methods=['POST'])
async def instance_endpoint(request, instance_id):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://api.digitalocean.com/v2/droplets",
            headers=DIGITALOCEAN_COMMON_HEADERS,
            data={
                "name": "neos-server-{}".format(instance_id),
                "region": "sfo3",
                "size": "s-1vcpu-1gb",
                "image": "ubuntu-16-04-x64",
                "ssh_keys": [107149],
                "backups": False,
                "ipv6": True,
                "user_data": None,
                "private_networking": None,
                "volumes": None,
                "tags": ["neos", instance_id]
            }
        )
    # TODO: actually check status code
    return json({"status": "created", "instance_id": instance_id})


# Unfortunately Neos lacks a DELETE HTTP request logix node so we have to put the verb in the method.
@app.route("/neos/instance/<instance_id>/delete", methods=['POST'])
async def instance_endpoint(request, instance_id):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://api.digitalocean.com/v2/droplets?tag_name={instance_id}".format(instance_id=instance_id),
            headers=DIGITALOCEAN_COMMON_HEADERS
        )
    # TODO: actually check status code
    return json({"status": "deleted", "instance_id": instance_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True, access_log=True, workers=os.cpu_count())
