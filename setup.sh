#!/bin/bash

# Container set up

sudo apt update
sudo apt upgrade
sudo apt-get install \
  build-essential \
  pkg-config \
  libc6-dev \
  libssl-dev \
  libexpat1-dev \
  libavcodec-dev \
  libgl1-mesa-dev \
  qtbase5-dev \
  zlib1g-dev

wget https://www.makemkv.com/download/makemkv-bin-1.18.2.tar.gz
wget https://www.makemkv.com/download/makemkv-oss-1.18.2.tar.gz

mkdir makemkv-dist
cd  makemkv-dist
tar -xvzf ../makemkv-bin-*.tar.gz
tar -xvzf ../makemkv-oss-*.tar.gz