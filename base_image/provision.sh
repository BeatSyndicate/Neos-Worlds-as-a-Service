#!/usr/bin/env sh

export DEBIAN_FRONTEND=noninteractive

set -xe

# sleep timer for packer
sleep 30

# Install base utils
apt-get update
apt-get upgrade -y -o Dpkg::Options::=--force-confnew
apt-get install -y systemd mosh htop tmux
systemctl restart systemd-journald # otherwise journald isn't recording

# Configure firewall
ufw allow 22
ufw enable

# Install mono
apt-get install -y dirmngr gnupg apt-transport-https ca-certificates software-properties-common
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
apt-add-repository 'deb https://download.mono-project.com/repo/ubuntu stable-focal main'
apt-get update
apt-get install -y mono-runtime mono-complete

# Install steamcmd
apt-get install -y software-properties-common
add-apt-repository multiverse
dpkg --add-architecture i386
apt-get update
apt-get install -y unzip binutils jq netcat lib32stdc++6 libsdl2-2.0-0:i386
echo steam steam/question select "I AGREE" | sudo debconf-set-selections
echo steam steam/license note '' | sudo debconf-set-selections
apt-get -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confnew install -y lib32gcc1 steamcmd

# Setup steam user
adduser --disabled-password --shell /bin/bash --gecos 'steam' steam
cp -r /root/.ssh /home/steam/
chown -R steam:steam /home/steam/.ssh
