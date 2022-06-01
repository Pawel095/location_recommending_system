#!/bin/bash

stack_name=data_collector

while [ $# -gt 0 ]; do
    case $1 in
        up)
        docker stack deploy -c ./docker-compose.yaml $stack_name
        shift
        ;;
        down)
        docker stack rm $stack_name
        shift
        ;;
        *)
        echo unknown argument $1
        shift
        ;;
    esac
done