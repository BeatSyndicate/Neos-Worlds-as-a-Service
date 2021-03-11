#!/usr/bin/env bash
set -e
source ./secrets.env
[ -z "$DIGITALOCEAN_API_TOKEN" ] && echo 'ERROR: the env var DIGITALOCEAN_API_TOKEN is required' && exit 1
[ -z "$STEAM_PASS" ] && echo 'ERROR: specify STEAM_PASS in secrets.env' && exit 1
[ -z "$NEOS_BETA_PASS" ] && echo 'ERROR: specify NEOS_BETA_PASS in secrets.env' && exit 1
[ -z "$NEOS_PASS" ] && echo 'ERROR: specify NEOS_PASS in secrets.env' && exit 1
PACKER_LOG=1 exec packer build -color base_image.json
