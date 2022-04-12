#!/bin/bash

while [ $# -gt 0 ]; do
    case $1 in 
        up) 
        docker stack deploy -c ./docker-compose.yml test1
        shift
        ;;
        down)
        docker stack rm test1
        shift
        ;;
    esac
done