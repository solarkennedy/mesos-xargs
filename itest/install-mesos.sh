#!/bin/bash
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv E56151BF
DISTRO=$(lsb_release -is | tr '[:upper:]' '[:lower:]')
CODENAME=$(lsb_release -cs)

# Add the repository
echo "deb http://repos.mesosphere.com/${DISTRO} ${CODENAME} main" | 
  sudo tee /etc/apt/sources.list.d/mesosphere.list
sudo apt-get -y update

# Install packages
sudo apt-get -y --force-yes install mesos 
sudo start mesos-master
sudo start mesos-slave
