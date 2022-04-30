import geomesa_pyspark
from pyspark.find_spark_home import _find_spark_home as fsh
import json

conf = (
    geomesa_pyspark.configure(
        spark_home=fsh(),
        jars=[
            "/packages/geomesa-fs-spark-runtime_2.12-3.4.0.jar",
        ],
    )
    .setAppName("getClosest")
    .set("spark.driver.memory", "20G")
)

from typing import Dict, Optional, Sequence
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession, Row, types as t, DataFrame
import pyspark.sql.functions as f
from pprint import pp


def toMap(tupleArray: Sequence[Row]) -> Optional[Dict[str, str]]:
    if tupleArray is None:
        return
    return {e["key"].decode("utf-8"): e["value"].decode("utf-8") for e in tupleArray}


def repl():
    from ptpython.repl import embed

    embed(globals(), locals())


toMapUdf = f.udf(toMap, t.MapType(t.StringType(), t.StringType()))


def process(df: DataFrame) -> DataFrame:
    return df.drop("uid", "user_sid", "changeset", "version").withColumn(
        "tags", toMapUdf(f.col("tags"))
    )


s = SparkSession.builder.config(conf=conf).getOrCreate()
geomesa_pyspark.init_sql(s)
pp(s.sparkContext.getConf().getAll())

a = (
    s.read.parquet("hdfs:///data/poland.osm.pbf.node.parquet")
    .limit(200)
    .transform(process)
)

a.printSchema()
a.show(1)

wp = s.sql("""select *, st_point(latitude,longitude) as point from a""")

# BROKEN WIP, FIGURE OUT AND FIX

# a.write.format("geomesa").options(
#     **{
#         "fs.path": "hdfs://namenode:9000/geomesa_data/a",
#         "geomesa.feature": "asd",
#         "geomesa.fs.scheme": json.dumps(
#             {"name": "z2-2bits", "options": {"geom-attribute": "point"}}
#         ),
#     }
# ).save()

repl()
