#!/bin/bash
# test1
stack_name=lrs

while [ $# -gt 0 ]; do
    case $1 in
        up)
        docker stack deploy -c ./docker-compose.yml $stack_name
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