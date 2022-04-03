from math import fabs
from typing import Dict, Optional, Sequence
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SparkSession, Row, types as t
import pyspark.sql.functions as f


def toMap(tupleArray: Sequence[Row]) -> Optional[Dict[str, str]]:
    if tupleArray is None:
        return
    return {e["key"].decode("utf-8"): e["value"].decode("utf-8") for e in tupleArray}


toMapUdf = f.udf(toMap, t.MapType(t.StringType(), t.StringType()))

conf = (
    SparkConf().setAppName("getClosest")
    # .setMaster("yarn")
    # .set("spark.submit.deployMode", "client")
    # .set("spark.yarn.archive", "hdfs://namenode:9000/spark/jars.tar.gz")
)

sc = SparkContext(conf=conf)
ss = SparkSession(sc)
nodes = ss.read.parquet("hdfs:///data/poland.osm.pbf.node.parquet")
nodes.write.parquet("hdfs:///temp/nodesmapped")
# nodes = ss.read.parquet("hdfs:///temp/nodes5k")
mapped = nodes.withColumn("tags", toMapUdf(f.col("tags")))
mapped.printSchema()
# mapped.where(f.col("tags.name")=="	Cleaner").show(2, truncate=False)
