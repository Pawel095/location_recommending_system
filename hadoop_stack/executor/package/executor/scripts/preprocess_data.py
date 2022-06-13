import geomesa_pyspark as g
from pyspark.find_spark_home import _find_spark_home as fsh
from executor.udf import *

print("Geomesa Init")

conf = (
    g.configure(
        spark_home=fsh(),
        jars=[
            "/opt/geomesa-fs_2.12-3.4.0/dist/spark/geomesa-fs-spark-runtime_2.12-3.4.0.jar",
        ],
    )
    .setAppName("data preprocessing")
    .set("spark.executor.memory", "15G")
    .set("spark.executor.cores", "16")
)

from pyspark.sql import SparkSession
import pyspark.sql.functions as f
from pyspark.sql.utils import AnalysisException
from pprint import pp

HDFS_BASE_ADDRESS = "hdfs:///data_checkpoints/"

print("Spark init")
s = SparkSession.builder.config(conf=conf).getOrCreate()
s.sparkContext.setCheckpointDir("hdfs:///spark_checkpoints")
# s.sparkContext.setLogLevel("DEBUG")
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
    print("nodes read and preprocess")
    try:
        s.read.parquet("hdfs:///data/lodzkie.osm.pbf.node.parquet").transform(
            drop_columns_and_mappify_tags
        ).createOrReplaceTempView("nodes")
        nodes = s.sql(
            """select *,st_point(latitude,longitude) as geom from nodes"""
        ).repartitionByRange(16, "id")
        nodes.write.parquet(HDFS_BASE_ADDRESS + "/nodes")
    except AnalysisException:
        # traceback.print_exc()
        filename = HDFS_BASE_ADDRESS + "/nodes"
        print(f"File exists: {filename=}")
    nodes = s.read.parquet(HDFS_BASE_ADDRESS + "/nodes")

    print("Ways preprocessing")
    try:
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
    except AnalysisException:
        # traceback.print_exc()
        filename = HDFS_BASE_ADDRESS + "/ways_with_nids"
        print(f"File exists: {filename=}")
    ways = s.read.parquet(HDFS_BASE_ADDRESS + "/ways_with_nids")

    print("combining nodes and ways")
    try:
        nodes = (
            nodes.alias("n")
            .join(ways.alias("w"), nodes.id == ways.nid, how="FULL")
            .withColumn("tags_concat", f.map_concat("n.tags", "w.tags"))
            .select("n.*")
            .withColumnRenamed("tags_concat", "tags")
            .filter(COMBINED_TAG_FILTER)
            .repartitionByRange(16, "id")
        )
        nodes.write.parquet(HDFS_BASE_ADDRESS + "/n_filtered")
    except AnalysisException:
        # traceback.print_exc()
        filename = HDFS_BASE_ADDRESS + "/n_filtered"
        print(f"File exists: {filename=}")


def prepare_test_data():
    print("Processing pg test data snapshot")
    try:
        test_data = s.read.parquet("hdfs:///data/test_data")
        test_data.createOrReplaceTempView("test_data")
        test_data = s.sql(
            """select *,st_point(latitude,longitude) as geom from test_data"""
        ).repartitionByRange(16, "id")
        test_data.write.parquet(HDFS_BASE_ADDRESS + "/geom_test_data")
    except AnalysisException:
        # traceback.print_exc()
        filename = HDFS_BASE_ADDRESS + "/geom_test_data"
        print(f"File exists: {filename=}")


def run():
    prepare_and_filter_nodes()
    nodes = s.read.parquet(HDFS_BASE_ADDRESS + "/n_filtered")
    nodes.createOrReplaceTempView("nodes")

    prepare_test_data()
    test_data = s.read.parquet(HDFS_BASE_ADDRESS + "/geom_test_data")
    test_data.createOrReplaceTempView("test_data")

    print("Joining test data and nodes")
    try:
        joined = (
            nodes.alias("n")
            .join(test_data.alias("td"), how="cross")
            .selectExpr(
                [
                    "n.id as nid",
                    "n.tags as ntags",
                    "n.geom as npoint",
                    "td.id as tid",
                    "td.accuracy as taccuracy",
                    "td.altitude as taltitude",
                    "td.geom as tpoint",
                ]
            )
        )
        joined.write.parquet(HDFS_BASE_ADDRESS + "/distances_temp")
    except AnalysisException:
        # traceback.print_exc()
        filename = HDFS_BASE_ADDRESS + "/distances_temp"
        print(f"File exists: {filename=}")

    joined = s.read.parquet(HDFS_BASE_ADDRESS + "/distances_temp")
    joined.createOrReplaceTempView("joined")

    print("calculating distances")
    try:
        s.sql(
            """
            select 
                *, 
                st_distance(npoint,tpoint) as latlon_dist 
            from 
                joined"""
        ).createOrReplaceTempView("distances")
        mindist = s.sql(
            """
            select 
                *, 
                MIN(latlon_dist) 
                    over (partition by tid) 
                    as mindist 
            from
                distances"""
        )
        matched = mindist.filter("latlon_dist == mindist").repartitionByRange(16, "nid")
        matched.write.parquet(HDFS_BASE_ADDRESS + "/matched_test_data")
    except AnalysisException:
        # traceback.print_exc()
        filename = HDFS_BASE_ADDRESS + "/matched_test_data"
        print(f"File exists: {filename=}")
    matched = s.read.parquet(HDFS_BASE_ADDRESS + "/matched_test_data")

    print("Filtering for closest")
    try:
        close_to_nodes = matched.withColumn(
            "dist_meters", distance_in_metersUdf(f.col("npoint"), f.col("tpoint"))
        ).filter("dist_meters < taccuracy + 3")
        close_to_nodes.write.parquet("/recommender_data")
    except AnalysisException:
        # traceback.print_exc()
        filename = "/recommender_data"
        print(f"File exists: {filename=}")
    print("Done!")


if __name__ == "__main__":
    run()
