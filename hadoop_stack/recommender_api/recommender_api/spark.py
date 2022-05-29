from typing import Union
from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext
from decouple import config
from pprint import pp
from pyspark import SparkContext
from pyspark.mllib.recommendation import MatrixFactorizationModel

HDFS_BASE_ADDRESS = "hdfs:///data_checkpoints/"


s: Union[None, SparkSession, SparkSession]
recmodel: Union[None, MatrixFactorizationModel]


def start_spark():
    global s
    global recmodel
    conf = SparkConf().setAppName("api-spark").setMaster("yarn")
    s = SparkContext.getOrCreate(conf=conf)
    recmodel = MatrixFactorizationModel.load(s, config("MODEL_PATH", cast=str))
    pp(s.getConf().getAll())
    print("Spark init done")


def stop_spark():
    s.stop()
    print("Spark stopped")


def model():
    return recmodel
