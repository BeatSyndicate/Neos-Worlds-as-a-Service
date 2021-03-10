#!/usr/bin/env sh

export DEBIAN_FRONTEND=noninteractive

set -xe

# sleep timer for packer
sleep 30

# Install base utils
sudo apt-get update && sudo apt-get upgrade -y -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confnew
sudo apt-get install -y systemd mosh htop tmux
sudo systemctl restart systemd-journald # otherwise journald isn't recording

# Install mono
sudo apt-get install -y dirmngr gnupg apt-transport-https ca-certificates software-properties-common
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
sudo apt-add-repository 'deb https://download.mono-project.com/repo/ubuntu stable-focal main'
sudo apt-get update
sudo apt-get install -y mono-runtime mono-complete

# Install steamcmd
sudo apt-get install -y software-properties-common
sudo add-apt-repository multiverse
sudo dpkg --add-architecture i386
sudo apt-get update
sudo apt-get install -y unzip binutils jq netcat lib32stdc++6 libsdl2-2.0-0:i386
echo steam steam/question select "I AGREE" | sudo debconf-set-selections
echo steam steam/license note '' | sudo debconf-set-selections
sudo apt-get -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confnew install -y lib32gcc1 steamcmd

# Setup steam user
sudo adduser --disabled-password --shell /bin/bash --gecos 'steam' steam
