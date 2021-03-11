# Neos-as-a-Service
A webservice which integrates with Neos and spins up new machines to provide new headless Neos instances. 

## Building the Base Image
The base image which NaaS instantiates every droplet can be rebuilt with packer using the following command:
1. Fill in secrets.env
2. `cd base_image`
3. `DIGITALOCEAN_API_TOKEN=<My DO API token> ./build_base_image.sh`
