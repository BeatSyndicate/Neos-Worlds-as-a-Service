from sanic import Sanic
from sanic.response import json
from sanic.log import logger
import httpx

app = Sanic("NaaS")


@app.route("/neos/instance/<instance_id>", methods=['GET'])
async def instance_endpoint(request, instance_id):
    # logger.info("route='/neos/instance/%s", instance_id)
    return json({"status": "healthy", "instance_id": instance_id, "log_websocket": ""})


@app.route("/neos/instance/<instance_id>/create", methods=['POST'])
async def instance_endpoint(request, instance_id):
    async with httpx.AsyncClient() as client:
        r = await client.post("https://api.digitalocean.com/v2/droplets", headers={"Content-Type": "application/json",
                                                                                   "Authorization": "Bearer b7d03a6947b217efb6f3ec3bd3504582"},
                              data={"name": "instance_name",
                                    "region": "nyc3",
                                    "size": "s-1vcpu-1gb",
                                    "image": "ubuntu-16-04-x64",
                                    "ssh_keys": [107149],
                                    "backups": False,
                                    "ipv6": True,
                                    "user_data": None,
                                    "private_networking": None,
                                    "volumes": None,
                                    "tags": ["web"]})
    return json({"status": "created", "instance_id": instance_id})


@app.route("/neos/instance/<instance_id>/delete", methods=['POST'])
async def instance_endpoint(request, instance_id):
    return json({"status": "deleted", "instance_id": instance_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True, access_log=True)
