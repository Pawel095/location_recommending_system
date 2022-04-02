from pyspark import SparkConf
from pyspark import SparkContext

conf = (
    SparkConf()
    .setMaster("yarn")
    .setAppName("getClosest")
    .set("spark.submit.deployMode", "client")
    .set("spark.yarn.archive","hdfs://namenode:9000/spark/jars.tar.gz")
)

sc = SparkContext(conf=conf)
rdd = sc.parallelize([1, 2, 3])
count = rdd.count()
print(sc.master)
print(count)
