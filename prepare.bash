#!/bin/bash

REG_ADDR=192.168.2.1:5000

docker build -t hadoop-base:local_latest ./base

while [ $# -gt 0 ]; do
    case $1 in 
        -d) docker run --rm -it base:latest /bin/bash
        shift
        ;;
        -p) docker tag hadoop-base:local_latest ${REG_ADDR}/hadoop-base:local_latest
        docker image push ${REG_ADDR}/hadoop-base:local_latest
        shift
        ;;
    esac
done