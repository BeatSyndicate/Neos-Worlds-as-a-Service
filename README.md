# Neos-as-a-Service
A webservice which integrates with Neos and spins up new machines to provide new headless Neos instances. 

## Building the Base Image
The base image which NaaS instantiates every droplet can be rebuilt with packer using the following command:
```
export STEAM_PASS="the steam password"
export NEOS_BETA_PASS="the neos headless server password"
export NEOS_PASS="the neos password"
export DIGITALOCEAN_API_TOKEN="a digital ocean api token"
cd base_image
./build_base_image.sh
```

