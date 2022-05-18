#%%
from fileinput import close
import geomesa_pyspark as g
from geomesa_pyspark import types, spark
from pyspark.find_spark_home import _find_spark_home as fsh
import json
import shapely
from geographiclib.geodesic import Geodesic

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
s.sparkContext.setCheckpointDir("hdfs:///spark_checkpoints")
s.sparkContext.setLogLevel("INFO")

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


def prepare_and_filter_nodes():
    s.read.parquet("hdfs:///data/lodzkie.osm.pbf.node.parquet").transform(
        drop_columns_and_mappify_tags
    ).createOrReplaceTempView("nodes")
    nodes = s.sql(
        """select *,st_point(latitude,longitude) as geom from nodes"""
    ).repartitionByRange(16, "id")
    nodes.write.parquet(HDFS_BASE_ADDRESS + "/nodes")
    nodes = s.read.parquet(HDFS_BASE_ADDRESS + "/nodes")

    ways = s.read.parquet(
        "hdfs:///data/lodzkie.osm.pbf.way.parquet"
    ).repartitionByRange(16, "id")
    ways = ways.transform(drop_columns_and_mappify_tags)
    ways = (
        ways.withColumn("nodes", nodesUdf(f.col("nodes")))
        .withColumn("nid", f.explode(f.map_values(f.col("nodes"))))
        .repartitionByRange(16, "nid")
    )
    ways.write.parquet(HDFS_BASE_ADDRESS + "/ways_with_nids")
    ways = s.read.parquet(HDFS_BASE_ADDRESS + "/ways_with_nids")

    nodes = (
        nodes.alias("n")
        .join(ways.alias("w"), nodes.id == ways.nid, how="FULL")
        .withColumn("tags_concat", f.map_concat("n.tags", "w.tags"))
        .select("n.*")
        .withColumnRenamed("tags_concat", "tags")
        .filter(COMBINED_TAG_FILTER)
    )
    nodes.write.parquet(HDFS_BASE_ADDRESS + "/n_filtered")


# TODO: update to use unfiltered nodes
def filter_city_centers():
    city_centers = s.sql(
        """select * from nodes where (nodes.tags.place == "village" or nodes.tags.plade == "town" or nodes.tags.place == "city") and tags.name is not null """
    )
    city_centers.write.parquet(HDFS_BASE_ADDRESS + "/city_centers")


def prepare_test_data():
    test_data = s.read.parquet("hdfs:///test_data")
    test_data.createOrReplaceTempView("test_data")
    test_data = s.sql(
        """select *,st_point(latitude,longitude) as geom from test_data"""
    )
    test_data.write.parquet(HDFS_BASE_ADDRESS + "/geom_test_data")


# Use theese 3 functions to load and prepare data

# prepare_and_filter_nodes()
# s.read.parquet(HDFS_BASE_ADDRESS + "/n_filtered").createOrReplaceTempView("nodes")
# filter_city_centers()
# prepare_test_data()


#%%


nodes = s.read.parquet(HDFS_BASE_ADDRESS + "/n_filtered")
nodes.createOrReplaceTempView("nodes")
#%%

test_data = s.read.parquet(HDFS_BASE_ADDRESS + "/geom_test_data")
test_data.createOrReplaceTempView("test_data")

s.sparkContext.setLogLevel("WARN")
repl()


joined = s.sql(
    """
select
    n.id as nid,
    n.tags as ntags,
    n.geom as npoint,
    td.id as tid,
    td.accuracy as taccuracy,
    td.altitude as taltitude,
    td.geom as tpoint
from nodes as n
cross join test_data as td
"""
).repartitionByRange(16, "nid")
joined.write.parquet(HDFS_BASE_ADDRESS + "/distances_temp")
joined = s.read.parquet(HDFS_BASE_ADDRESS + "/distances_temp")
joined.createOrReplaceTempView("joined")


s.sql(
    """
select
    *,
    st_distance(npoint,tpoint) as latlon_dist
    from joined
"""
).createOrReplaceTempView("distances")

mindist = s.sql(
    "select *, MIN(latlon_dist) over (partition by tid) as mindist from distances"
)
matched = mindist.filter("latlon_dist == mindist").repartitionByRange(16, "nid")
matched.write.parquet(HDFS_BASE_ADDRESS + "/matched_test_data")
matched = s.read.parquet(HDFS_BASE_ADDRESS + "/matched_test_data")

close_to_nodes = matched.withColumn(
    "dist_meters", distance_in_metersUdf(f.col("npoint"), f.col("tpoint"))
).filter("dist_meters < 10")
close_to_nodes.write.json("/asd")


#%%

# TEMPORARY CACHE.


# distances = s.sql(
#     """
# select
#     n.id as nid,
#     td.id as tdid,
#     st_distance(n.geom,td.geom) as d
# from nodes as n
# cross join geom_test_data as td
# """
# )
# distances.cache()


# points = nodes.limit(5).cache()
# points.createOrReplaceTempView("nodes")
# points.show()


# cw = city_centers.limit(5).cache()
# cw.show()


# cw.createOrReplaceTempView("city_centers")
# distances = s.sql(
#     """
#     select
#         n.id as nid,
#         cc.id as cid,
#         cc.tags as cctags,
#         st_distance(n.geom,cc.geom) as d
#     from nodes as n
#     cross join city_centers as cc"""
# ).cache()
# distances.createOrReplaceTempView("d")
# mindist = s.sql("""select *, MIN(D) over (partition by nid order by d) as mindist from d""").cache()


# mindist.createOrReplaceTempView("md")
# s.sql("select nid, cctags.name from md where d=mindist").show()

# TODO: Uzyj google collaba aby przeliczyć jaki node jest najbliżej jakiego centrum. wstawić nodes i city centers jako parquet, prezliczyć na collabie
# TODO: do tego powyżej. na collabie będzie trzeba bez geomesa, bo nie działa na yarnie


# a = s.read.format("geomesa").options(**{"fs.path":"hdfs://namenode:9000/geomesa_poland_n","geomesa.feature":"node"}).load()
# b = s.read.format("geomesa").options(**{"fs.path":"hdfs://namenode:9000/geomesa_poland_w","geomesa.feature":"ways"}).load()
