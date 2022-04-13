from typing import Dict, Optional, Sequence
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SparkSession, Row, types as t, DataFrame
import pyspark.sql.functions as f
from sedona.utils import SedonaKryoRegistrator, KryoSerializer
from sedona.register import SedonaRegistrator
from pprint import pp
from sedona.utils.adapter import Adapter

def repl():
    from ptpython.repl import embed

    embed(globals(), locals())


def toMap(tupleArray: Sequence[Row]) -> Optional[Dict[str, str]]:
    if tupleArray is None:
        return
    return {e["key"].decode("utf-8"): e["value"].decode("utf-8") for e in tupleArray}


def toWktPoint(lat, lon) -> str:
    return f"POINT ({lat} {lon})"


toMapUdf = f.udf(toMap, t.MapType(t.StringType(), t.StringType()))
toWktPointUdf = f.udf(toWktPoint, t.StringType())


def process(df: DataFrame) -> DataFrame:
    return df.drop("uid", "user_sid", "changeset", "version").withColumn(
        "tags", toMapUdf(f.col("tags"))
    )


EXTRA_JARS = [
    "org.apache.sedona:sedona-python-adapter-3.0_2.12:1.1.1-incubating",
    "org.apache.sedona:sedona-viz-3.0_2.12:1.1.1-incubating",
    "org.datasyslab:geotools-wrapper:1.1.0-25.2",
]

conf = (
    SparkConf()
    .setAppName("getClosest")
    .setMaster("yarn")
    .set("spark.submit.deployMode", "client")
    .set("spark.driver.memory", "20G")
    .set("spark.yarn.archive", "hdfs://namenode:9000/spark/jars.tar")
    .set("spark.jars.packages", ",".join(EXTRA_JARS))
    .set("spark.serializer", KryoSerializer.getName)
    .set("spark.kryo.registrator", SedonaKryoRegistrator.getName)
)
sc = SparkContext(conf=conf)
ss = SparkSession(sc)
SedonaRegistrator.registerAll(ss)
pp(sc.getConf().getAll())

# a = (
#     ss.read.parquet("hdfs:///data/poland.osm.pbf.way.parquet")
#     .transform(process)
#     .withColumn("nodes", toMapUdf(f.col("nodes")))
# )
# b = ss.read.parquet("hdfs:///data/poland.osm.pbf.relation.parquet").transform(process)
c = (
    ss.read.parquet("hdfs:///data/poland.osm.pbf.node.parquet")
    .transform(process)
    .limit(200)
)
repl()
c = c.withColumn("wkt", toWktPointUdf(f.col("latitude"), f.col("longitude")))
c.createOrReplaceTempView("c")
c.show()
spatial = ss.sql("select ST_GeomFromWKT(wkt) as geom, * from c")
spatial.show()


# a.printSchema()
# b.printSchema()
c.printSchema()

# a.write.parquet("hdfs:///temp/wayMap")
# b.write.parquet("hdfs:///temp/relationMap")
# c.write.parquet("hdfs:///temp/nodeMap")
