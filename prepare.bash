#!/bin/bash

build_image(){
    docker-compose build
    docker build -t hadoop-base:local_latest ./base
}

REG_ADDR=192.168.2.1:5000

while [ $# -gt 0 ]; do
    case $1 in 
        -d) 
        build_image
        docker run --rm -it base:latest /bin/bash
        shift
        ;;
        -p)
        build_image
        docker tag hadoop-base:local_latest ${REG_ADDR}/hadoop-base:local_latest
        docker image push ${REG_ADDR}/hadoop-base:local_latest
        docker-compose push
        shift
        ;;
        -g)
        docker image pull ${REG_ADDR}/hadoop-base:local_latest
        docker-compose pull
        shift
        ;;
    esac
done