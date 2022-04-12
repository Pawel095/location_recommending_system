from typing import Dict, Optional, Sequence
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SparkSession, Row, types as t, DataFrame
import pyspark.sql.functions as f
from sedona.utils import SedonaKryoRegistrator, KryoSerializer
from sedona.register import SedonaRegistrator
from pprint import pp


def toMap(tupleArray: Sequence[Row]) -> Optional[Dict[str, str]]:
    if tupleArray is None:
        return
    return {e["key"].decode("utf-8"): e["value"].decode("utf-8") for e in tupleArray}


toMapUdf = f.udf(toMap, t.MapType(t.StringType(), t.StringType()))


def process(df: DataFrame) -> DataFrame:
    return df.drop("uid", "user_sid", "changeset", "version").withColumn(
        "tags", toMapUdf(f.col("tags"))
    )


ADDITIONAL_JARS = [
    "org.apache.sedona:sedona-python-adapter-3.0_2.12:1.1.1-incubating",
    "org.datasyslab:geotools-wrapper:1.1.0-25.2",
]

conf = (
    SparkConf()
    .setAppName("getClosest")
    .setMaster("yarn")
    .set("spark.jars.packages", ",".join(ADDITIONAL_JARS))
    .set("spark.submit.deployMode", "client")
    .set("spark.yarn.archive", "hdfs://namenode:9000/spark/jars.tar.gz")
    .set("spark.driver.memory", "20G")
    .set("spark.serializer", KryoSerializer.getName)
    .set("spark.kryo.registrator", SedonaKryoRegistrator.getName)
)
sc = SparkContext(conf=conf)
ss = SparkSession(sc)
SedonaRegistrator.registerAll(ss)
pp(sc.getConf().getAll())
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

# a.write.parquet("hdfs:///temp/wayMap")
# b.write.parquet("hdfs:///temp/relationMap")
# c.write.parquet("hdfs:///temp/nodeMap")
