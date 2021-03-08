#!/usr/bin/env sh

export DEBIAN_FRONTEND=noninteractive

# sleep timer for packer
sleep 30

# Install base utils
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y systemd mosh htop tmux

# Install mono
sudo apt-get install dirmngr gnupg apt-transport-https ca-certificates software-properties-common
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
sudo apt-add-repository 'deb https://download.mono-project.com/repo/ubuntu stable-focal main'
sudo apt-get install -y mono-complete

# Install steamcmd
sudo apt-get install -y software-properties-common
sudo add-apt-repository multiverse
sudo dpkg --add-architecture i386
sudo apt-get update
echo steam steam/question select "I AGREE" | sudo debconf-set-selections
echo steam steam/license note '' | sudo debconf-set-selections
sudo apt-get install -y lib32gcc1 steamcmd

# Setup steam user
sudo adduser --disabled-password --shell /bin/bash --gecos 'steam' steam
