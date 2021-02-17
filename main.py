from sanic import Sanic
from sanic.response import json
from sanic.log import logger

app = Sanic("NaaS")


@app.route("/neos/instance/<instance_id>", methods=['GET'])
async def instance_endpoint(request, instance_id):
    # logger.info("route='/neos/instance/%s", instance_id)
    return json({"status": "healthy", "instance_id": instance_id, "log_websocket": ""})


@app.route("/neos/instance/<instance_id>/create", methods=['POST'])
async def instance_endpoint(request, instance_id):
    return json({"status": "created", "instance_id": instance_id})


@app.route("/neos/instance/<instance_id>/delete", methods=['POST'])
async def instance_endpoint(request, instance_id):
    return json({"status": "deleted", "instance_id": instance_id})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True, access_log=True)
