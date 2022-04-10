from math import fabs
from typing import Dict, Optional, Sequence
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SparkSession, Row, types as t, DataFrame
import pyspark.sql.functions as f


def toMap(tupleArray: Sequence[Row]) -> Optional[Dict[str, str]]:
    if tupleArray is None:
        return
    return {e["key"].decode("utf-8"): e["value"].decode("utf-8") for e in tupleArray}


toMapUdf = f.udf(toMap, t.MapType(t.StringType(), t.StringType()))


def process(df: DataFrame) -> DataFrame:
    return df.drop("uid", "user_sid", "changeset", "version").withColumn(
        "tags", toMapUdf(f.col("tags"))
    )


conf = (
    SparkConf().setAppName("getClosest")
    # .setMaster("yarn")
    # .set("spark.submit.deployMode", "client")
    # .set("spark.yarn.archive", "hdfs://namenode:9000/spark/jars.tar.gz")
)

sc = SparkContext(conf=conf)
ss = SparkSession(sc)
a = (
    ss.read.parquet("hdfs:///data/poland.osm.pbf.way.parquet")
    .transform(process)
    .withColumn("nodes", toMapUdf(f.col("nodes")))
)
b = ss.read.parquet("hdfs:///data/poland.osm.pbf.relation.parquet").transform(process)
c = ss.read.parquet("hdfs:///data/poland.osm.pbf.node.parquet").transform(process)

a.printSchema()
b.printSchema()
c.printSchema()

a.repartition(1).write.parquet("hdfs:///temp/wayMap")
b.repartition(1).write.parquet("hdfs:///temp/relationMap")
c.repartition(1).write.parquet("hdfs:///temp/nodeMap")
