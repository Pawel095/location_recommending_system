#%%
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
    .set("spark.driver.memory", "20G")
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

g.init_sql(s)
pp(s.sparkContext.getConf().getAll())


def prepare_and_filter_nodes():
    nodes = s.read.parquet("hdfs:///data/lodzkie.osm.pbf.node.parquet").transform(
        drop_columns_and_mappify_tags
    )
    nodes.write.parquet(HDFS_BASE_ADDRESS + "/n_mappified")

    nodes = s.read.parquet(HDFS_BASE_ADDRESS + "/n_mappified")
    nodes.createOrReplaceTempView("nodes")
    nodes = s.sql("""select *,st_point(latitude,longitude) as geom from nodes""")
    nodes.write.parquet(HDFS_BASE_ADDRESS + "/n_withPoints")

    nodes = s.read.parquet(HDFS_BASE_ADDRESS + "/n_withPoints")
    nodes.createOrReplaceTempView("nodes")

    nodes = s.sql(
        """
    select
        *
    from nodes
    where
        tags.shop is not null OR
        tags.leisure is not null OR
        tags.amenity is not null
    """
    )
    nodes.write.parquet(HDFS_BASE_ADDRESS + "/n_filtered")


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
# filter_city_centers()
# prepare_test_data()


#%%


nodes = s.read.parquet(HDFS_BASE_ADDRESS + "/n_filtered")
nodes.createOrReplaceTempView("nodes")


city_centers = s.read.parquet(HDFS_BASE_ADDRESS + "/city_centers")
#%%

test_data = s.read.parquet(HDFS_BASE_ADDRESS + "/geom_test_data")
test_data.createOrReplaceTempView("test_data")


repl()

repa_distances = s.sql(
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
""").repartition(16,f.col("nid"))
repa_distances.write.parquet("hdfs:///distances_temp")
repa_distances = s.read.parquet("hdfs:///distances_temp")

dist_meters = repa_distances.withColumn("dist_meters", distance_in_metersUdf(f.col("npoint"), f.col("tpoint")))



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


# a = s.read.format("geomesa").options(**{"fs.path":"hdfs://namenode:9000/geomesa_poland_n","geomesa.feature":"node"}).load()
# b = s.read.format("geomesa").options(**{"fs.path":"hdfs://namenode:9000/geomesa_poland_w","geomesa.feature":"ways"}).load()
