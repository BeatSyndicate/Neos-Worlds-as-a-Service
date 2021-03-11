#!/usr/bin/env bash

full_path="$(realpath "$0")"
dir_path="$(dirname "$full_path")"
source "${dir_path}/secrets.env"

/usr/games/steamcmd +@sSteamCmdForcePlatformType linux +login beatsyndicatevr "${STEAM_PASS}" +app_update 740250 -beta headless-client -betapassword "${NEOS_BETA_PASS}" validate +app_license_request 740250 +quit
cd /home/steam/.steam/steamapps/common/NeosVR || exit 1
./Neos.exe --user beatsyndicatevr --password "${NEOS_PASS}" --config /home/steam/headless_config.json
