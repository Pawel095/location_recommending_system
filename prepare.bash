#!/bin/bash

build_image(){
    docker build -t hadoop-base:local_latest ./base
    docker-compose build
}

REG_ADDR=192.168.2.1:5000

while [ $# -gt 0 ]; do
    case $1 in 
        -d) 
        docker build -t hadoop-base:debug ./base
        docker run --rm -it hadoop-base:debug /bin/bash
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
        docker-compose pull --no-parallel
        shift
        ;;
        *)
        echo unknown argument $1
        shift
        ;;
    esac
done