from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

conf = (
    SparkConf()
    .setMaster("yarn")
    .setAppName("getClosest")
    .set("spark.submit.deployMode", "client")
    .set("spark.yarn.archive", "hdfs://namenode:9000/spark/jars.tar.gz")
)

sc = SparkContext(conf=conf)
ss = SparkSession(sc)
# nodes = ss.read.parquet("hdfs:///data/poland.osm.pbf.node.parquet")
# filtered1 = nodes.withColumn("tag_count", size(col("tags"))).where(col("tag_count") >= 1)
# filtered1.write.parquet("hdfs:///temp/hastags.parquet")
# cleaner = ss.read.parquet("hdfs:///temp/hastags.parquet").where(col("id") == 2003243218)
# cleaner.write.parquet("hdfs:///temp/cleaner.parquet")
filtered = ss.read.parquet("hdfs:///temp/hastags.parquet")
cleaner = ss.read.parquet("hdfs:///temp/cleaner.parquet")
cleaner.where()
result = cleaner
result.show(1, truncate=False)
