from glob import glob
import geomesa_pyspark
from pyspark.find_spark_home import _find_spark_home as fsh
from typing import Union
from pyspark.sql import SparkSession, DataFrame
from pyspark import SparkConf, SparkContext
from decouple import config
from pprint import pp
from pyspark import SparkContext
from pyspark.mllib.recommendation import MatrixFactorizationModel, Rating
import asyncio

HDFS_BASE_ADDRESS = "hdfs:///data_checkpoints/"


s: Union[None, SparkSession, SparkSession]
recmodel: Union[None, MatrixFactorizationModel]
nodes: Union[None, DataFrame]
recmap: Union[None, DataFrame]
conf: Union[None, SparkConf]

SPARK_STARTED = False


def start_spark():
    global SPARK_STARTED
    SPARK_STARTED = False
    global s
    global conf
    global recmodel
    global nodes
    global recmap
    print("Geomesa Init")

    conf = (
        geomesa_pyspark.configure(
            spark_home=fsh(),
            jars=[
                "/opt/geomesa-fs_2.12-3.4.0/dist/spark/geomesa-fs-spark-runtime_2.12-3.4.0.jar",
            ],
        )
        .setAppName("Recommendation_api_worker")
        .set("spark.executor.memory", "2G")
        .set("spark.executor.cores", "4")
    )

    # conf = SparkConf().setAppName("api-spark").setMaster("yarn")
    s = SparkSession.builder.config(conf=conf).getOrCreate()
    geomesa_pyspark.init_sql(s)
    pp(s.sparkContext.getConf().getAll())
    SPARK_STARTED = True
    print("Spark init done")
    recmodel = MatrixFactorizationModel.load(s, config("MODEL_PATH", cast=str))
    nodes = s.read.parquet(HDFS_BASE_ADDRESS + "/n_filtered")
    recmap = s.read.parquet("/recomender_name_id_map")
    print("Data reading done")


def stop_spark():
    if not SPARK_STARTED:
        raise AttributeError
    s.stop()
    print("Spark stopped")


def get_spark():
    global s
    if not SPARK_STARTED:
        raise AttributeError
    return s


def get_recmap():
    global recmap
    if not SPARK_STARTED:
        raise AttributeError
    return recmap


def get_nodes():
    global nodes
    if not SPARK_STARTED:
        raise AttributeError
    return nodes


def model():
    global recmodel
    if not SPARK_STARTED:
        raise AttributeError
    return recmodel
