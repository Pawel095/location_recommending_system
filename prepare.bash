#!/bin/bash

docker build -t hadoop-base:local_latest ./base

while [ $# -gt 0 ]; do
    case $1 in 
        -d) docker run --rm -it base:latest /bin/bash
        shift
        ;;
    esac
done