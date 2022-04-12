#!/bin/bash

HDFS_JARS_PATH="/spark/"
JAR_ARCHIVE="jars.tar.gz"

HDFS_MAP_PATH="/data"
MAP_FOLDER="map/"

collect_jars

echo Making folders
hdfs dfs -mkdir -p $HDFS_JARS_PATH
hdfs dfs -mkdir -p $HDFS_MAP_PATH

hdfs dfs -rm /spark/jars.tar.gz
echo Uploading jar archive
pv $JAR_ARCHIVE | hdfs dfs -put - $HDFS_JARS_PATH$JAR_ARCHIVE

echo Uploading map files:
for file in `ls -A $MAP_FOLDER`; do
    pv $MAP_FOLDER$file | hdfs dfs -put - $HDFS_MAP_PATH/$file
done

rm -rfv ./ivyJarsCache
rm -rfv ./jars
rm -rfv $JAR_ARCHIVE
