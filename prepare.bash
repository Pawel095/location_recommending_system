#!/bin/bash

docker build -t base:latest ./base

while [ $# -gt 0 ]; do
    case $1 in 
        -d) docker run --rm -it base:latest
        shift
        ;;
    esac
done