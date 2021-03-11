import os

DIGITALOCEAN_COMMON_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {token}".format(token=os.environ['DO_API_TOKEN'])
}
