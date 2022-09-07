#%%
from fileinput import close
import geomesa_pyspark as g
from geomesa_pyspark import types, spark
from pyspark.find_spark_home import _find_spark_home as fsh
import json
import shapely
from geographiclib.geodesic import Geodesic

import pyspark.sql.functions as f
from pyspark.mllib.recommendation import ALS, Rating
from pyspark.sql.utils import AnalysisException
from pprint import pp

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
    .set("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0")
)

from typing import Dict, Optional, Sequence
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession, Row, types as t, DataFrame
import pyspark.sql.functions as f
from pprint import pp

HDFS_BASE_ADDRESS = "hdfs:///data_checkpoints/"


#%%
def toMap(key: str, value: str, decode=True) -> Optional[Dict[str, str]]:
    def __proc(tupleArray: Sequence[Row]):
        if tupleArray is None:
            return
        return {
            e[key].decode("utf-8")
            if decode
            else e[key]: e[value].decode("utf-8")
            if decode
            else e[value]
            for e in tupleArray
        }

    return __proc


tupleUdf = f.udf(toMap("key", "value"), t.MapType(t.StringType(), t.StringType()))
nodesUdf = f.udf(
    toMap("index", "nodeId", decode=False), t.MapType(t.IntegerType(), t.LongType())
)
#%%


def distance_in_meters(p1: shapely.geometry.Point, p2: shapely.geometry.Point):
    from geographiclib.geodesic import Geodesic

    geodesic = Geodesic.WGS84
    return geodesic.Inverse(p1.x, p1.y, p2.x, p2.y)["s12"]


distance_in_metersUdf = f.udf(distance_in_meters, t.DoubleType())


#%%


def drop_columns_and_mappify_tags(df: DataFrame) -> DataFrame:
    return df.drop("uid", "user_sid", "changeset", "version").withColumn(
        "tags", tupleUdf(f.col("tags"))
    )


def repl():
    from ptpython.repl import embed

    embed(globals(), locals())


s = SparkSession.builder.config(conf=conf).getOrCreate()
s.sparkContext.setLogLevel("INFO")
s.sparkContext.setCheckpointDir("hdfs:///spark_checkpoints")

g.init_sql(s)
pp(s.sparkContext.getConf().getAll())
COMBINED_TAG_FILTER = (
    f.col("tags.amenity").isin(
        [
            "bar",
            "biergarten",
            "cafe",
            "fast_food",
            "food_court",
            "ice_cream",
            "pub",
            "restaurant",
            "arts_centre",
            "casino",
            "cinema",
            "community_centre",
            "conference_centre",
            "events_venue",
            "pharmacy",
            "planetarium",
            "studio",
            "gym",
            "internet_cafe",
        ]
    )
    | f.col("tags.leisure").isin(
        [
            "adult_gaming_centre",
            "amusement_arcade",
            "beach_resort",
            "bowling_alley",
            "disc_golf_course",
            "dog_park",
            "escape_game",
            "fitness_centre",
            "golf_course",
            "hackerspace",
            "ice_rink",
            "miniature_golf",
            "resort",
            "sports_centre",
            "sports_hall",
            "swimming_area",
            "swimming_pool",
            "water_park",
        ]
    )
    | f.col("tags.shop").isNotNull()
) & f.col("tags.name").isNotNull()


s.sparkContext.setLogLevel("ERROR")
repl()
