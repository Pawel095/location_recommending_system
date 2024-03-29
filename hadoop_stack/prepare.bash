#!/bin/bash


update_base_packages(){
    # build executor package and copy to here
    (cd executor/package ; poetry build) && cp executor/package/dist/executor-0.1.0-py3-none-any.whl base/executor-0.1.0-py3-none-any.whl
    # export all packages (with versions) from executor to base image
    (cd executor/package ; poetry export --without-hashes) > base/temp.txt
    echo "" > base/requirements.txt 
    # remove all file-installs from poetry export
    sed -i '/@/d' base/temp.txt
    # template, replace <<PACKAGE NAME HERE>> with package name:
    # sed -n '/<<PACKAGE NAME HERE>>/p' base/temp.txt >> base/requirements.txt
    # Keep only necesery packages
    sed -n '/geographiclib/p' base/temp.txt >> base/requirements.txt
    rm -v base/temp.txt
    echo /packages/geomesa_pyspark-3.4.0.tar.gz >> base/requirements.txt
    echo /packages/executor-0.1.0-py3-none-any.whl >> base/requirements.txt
}


build_image(){
    docker build -t hadoop-base:local_latest ./base
    docker-compose build
}

build_image_no_cache(){
    docker build --no-cache -t hadoop-base:local_latest ./base
    docker-compose build --no-cache
}

REG_ADDR=192.168.2.1:5000
# pip install poetry docker-compose

while [ $# -gt 0 ]; do
    case $1 in 
        # Build all images without cache
        --no-cache)
        update_base_packages
        build_image_no_cache
        shift
        ;;
        # launch bash shell in base image
        -d)
        update_base_packages
        docker build -t hadoop-base:debug ./base
        # docker run --rm -it hadoop-base:debug /bin/bash
        shift
        ;;
        # build images using cache
        -b)
        update_base_packages
        build_image
        shift
        ;;
        # push images into the registry
        -p)
        docker tag hadoop-base:local_latest ${REG_ADDR}/hadoop-base:local_latest
        docker image push ${REG_ADDR}/hadoop-base:local_latest
        docker-compose push
        shift
        ;;
        # pull (get) images from the registry
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