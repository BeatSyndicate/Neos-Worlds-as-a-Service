# Neos-as-a-Service
A webservice which integrates with Neos and spins up new machines to provide new headless Neos instances. 

## Building the Base Image
The base image which NaaS instantiates every droplet can be rebuilt with packer using the following command:
```
cd base_image
DIGITALOCEAN_API_TOKEN=<My DO API token> packer build base_image.json
```
