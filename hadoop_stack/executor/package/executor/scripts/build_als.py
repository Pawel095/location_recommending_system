import geomesa_pyspark as g
from pyspark.find_spark_home import _find_spark_home as fsh

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

from pyspark.sql import SparkSession
import pyspark.sql.functions as f
from pyspark.mllib.recommendation import ALS, Rating
from pyspark.sql.utils import AnalysisException
from pprint import pp

HDFS_BASE_ADDRESS = "hdfs:///data_checkpoints/"


s = SparkSession.builder.config(conf=conf).getOrCreate()
s.sparkContext.setCheckpointDir("hdfs:///spark_checkpoints")

g.init_sql(s)
pp(s.sparkContext.getConf().getAll())


def build_and_test(r, model):
    testdata = r.map(lambda p: (p[0], p[1]))
    predictions = model.predictAll(testdata).map(lambda r: ((r[0], r[1]), r[2]))
    ratesAndPreds = r.map(lambda r: ((r[0], r[1]), r[2])).join(predictions)
    MSE = ratesAndPreds.map(lambda r: (r[1][0] - r[1][1]) ** 2).mean()
    print("Mean Squared Error = " + str(MSE))


def run():
    all_names = (
        s.read.parquet(HDFS_BASE_ADDRESS + "/n_filtered")
        .withColumn("name", f.col("tags.name"))
        .select("name")
        .distinct()
        .withColumn("count", f.lit(0))
        .withColumnRenamed("name", "aname")
        .withColumn("nid", f.monotonically_increasing_id())
    )
    try:
        all_names.write.parquet("/recomender_name_id_map")
    except AnalysisException:
        filename = "/recomender_name_id_map"
        print(f"File exists: {filename=}")

    rank_df = (
        s.read.parquet("/recommender_data")
        .select(["nid", "ntags", "npoint"])
        .withColumn("name", f.col("ntags.name"))
        .groupBy("name")
        .count()
        .orderBy("count", ascending=False)
        .alias("c")
        .join(all_names.alias("an"), f.col("c.name") == f.col("an.aname"), "right")
        .selectExpr(["c.count as count", "nid as id"])
        .fillna(0)
        .orderBy("count", ascending=False)
        .withColumn("user", f.lit(0))
    )

    r = rank_df.rdd.map(lambda row: Rating(row[2], row[1], row[0]))

    a = ALS.trainImplicit(r, 10, 10, blocks=16)
    build_and_test(r, a)
    a.save(s.sparkContext, "/als_built")
