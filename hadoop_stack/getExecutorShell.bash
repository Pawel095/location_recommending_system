#!/bin/bash
containerId=`docker container ps -aqf "name=executor" -f "status=running"`

echo xhost +local:`docker inspect --format='{{ .Config.Hostname }}' $containerId`
xhost +local:`docker inspect --format='{{ .Config.Hostname }}' $containerId`

docker exec -it $containerId /bin/bash

echo xhost -local:`docker inspect --format='{{ .Config.Hostname }}' $containerId`
xhost -local:`docker inspect --format='{{ .Config.Hostname }}' $containerId`