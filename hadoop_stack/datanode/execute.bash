#!/bin/bash

echo `env`
$HADOOP_HOME/bin/hdfs --config $HADOOP_CONF_DIR datanode
