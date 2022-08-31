import geomesa_pyspark as g
from pyspark.find_spark_home import _find_spark_home as fsh

from pprint import pp

from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession, Row, types as t, DataFrame, functions as f


def repl():
    from ptpython.repl import embed

    embed(globals(), locals())


if __name__ == "__main__":
    conf = (
    g.configure(
        spark_home=fsh(),
        jars=[
            "/opt/geomesa-fs_2.12-3.4.0/dist/spark/geomesa-fs-spark-runtime_2.12-3.4.0.jar",
        ],
    )
    .setAppName("getClosest")
    .set("spark.executor.memory", "15G")
    .set("spark.executor.cores", "16")
    )
    
    s = SparkSession.builder.config(conf=conf).getOrCreate()
    s.sparkContext.setLogLevel("INFO")
    s.sparkContext.setCheckpointDir("hdfs:///spark_checkpoints")

    g.init_sql(s)
    pp(s.sparkContext.getConf().getAll())
    repl()
