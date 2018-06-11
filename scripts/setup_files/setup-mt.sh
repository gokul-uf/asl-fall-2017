#!/bin/bash
sudo apt-get update
sudo apt-get install -y git unzip
wget https://github.com/RedisLabs/memtier_benchmark/archive/master.zip
unzip master.zip
cd memtier_benchmark-master
sudo apt-get install -y build-essential autoconf automake libpcre3-dev libevent-dev pkg-config zlib1g-dev
autoreconf -ivf
./configure
make