from functools import partial

from digitalocean_auth import DIGITALOCEAN_COMMON_HEADERS
import threading
from typing import List, Optional, Callable
import httpx
from sanic.log import logger
import time
from dateutil.parser import isoparse
from datetime import timezone


def _vm_cleanup():
    with httpx.Client() as client:
        r = client.get(
            "https://api.digitalocean.com/v2/droplets",
            headers=DIGITALOCEAN_COMMON_HEADERS,
        )
        if r.is_error:
            logger.error("request={}".format(r.request.__dict__))
        j = r.json()
    droplets = j['droplets']
    if len(droplets) > 0:
        logger.info(f"droplets count={len(droplets)}")
        for droplet in droplets:
            tags = droplet['tags']
            lifetime = _parse_lifetime_tag(tags)
            instance_id = _parse_instance_id_tag(tags)
            launch_time = isoparse(droplet['created_at']).replace(tzinfo=timezone.utc).timestamp()
            current_time = time.time()
            if lifetime is None:
                logger.info(f"Lifetime of instance_id={instance_id} not specified, deleting...")
                _delete_droplet(instance_id)
            elif lifetime + launch_time > current_time:
                logger.info(f"Lifetime of instance_id={instance_id} runtime={current_time - launch_time} exceeds "
                            f"specified lifetime={lifetime}, deleting...")
                _delete_droplet(instance_id)


def _parse_lifetime_tag(tags: List[str]) -> Optional[int]:
    list_lifetime_tag = [tag for tag in tags if tag.lower().startswith('lifetime')]
    if len(list_lifetime_tag) == 0:
        return None
    lifetime_tag = list_lifetime_tag[0]
    return int(lifetime_tag.split(":")[1])


def _parse_instance_id_tag(tags: List[str]) -> Optional[str]:
    list_instance_id_tag = [tag for tag in tags if tag.lower().startswith('instance_id')]
    if len(list_instance_id_tag) == 0:
        return None
    instance_id_tag = list_instance_id_tag[0]
    return instance_id_tag.split(":")[1]


def _delete_droplet(instance_id: str):
    with httpx.Client() as client:
        r = client.delete(
            f"https://api.digitalocean.com/v2/droplets?tag_name=instance_id:{instance_id}",
            headers=DIGITALOCEAN_COMMON_HEADERS
        )
        if r.is_error:
            logger.info("request={}".format(r.request.__dict__))
            logger.error("response={}".format(r.json()))
        else:
            logger.info(f"instance_id={instance_id} status=deleted")


def schedule_vm_cleanup(loop):
    _vm_cleanup()
    loop.call_later(600, partial(schedule_vm_cleanup, loop))
