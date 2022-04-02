from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SparkSession

conf = (
    SparkConf()
    .setMaster("yarn")
    .setAppName("getClosest")
    .set("spark.submit.deployMode", "client")
    .set("spark.yarn.archive", "hdfs://namenode:9000/spark/jars.tar.gz")
)

sc = SparkContext(conf=conf)
ss = SparkSession(sc)
nodes = ss.read.parquet("hdfs:///data/poland.osm.pbf.node.parquet")
print(nodes.count())
