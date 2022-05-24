#!/bin/bash

HDFS_JARS_PATH="/spark/"
JAR_ARCHIVE="jars.tar"

HDFS_MAP_PATH="/data"
MAP_FOLDER="map/"

get_test_data

echo Making folders
hdfs dfs -mkdir -p $HDFS_MAP_PATH


echo Uploading map files:
for file in `ls -A $MAP_FOLDER`; do
    pv $MAP_FOLDER$file | hdfs dfs -put - $HDFS_MAP_PATH/$file
done

preprocess_data