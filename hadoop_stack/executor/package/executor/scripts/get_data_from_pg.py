import pandas as pd
from pyspark.sql import SparkSession
from sqlalchemy import create_engine


def repl():
    from ptpython.repl import embed

    embed(globals(), locals())


def run():
    appName = "test data import"
    master = "yarn"

    spark = SparkSession.builder.master(master).appName(appName).getOrCreate()

    engine = create_engine(
        "postgresql+psycopg2://fastapi:passwd@192.168.2.7:5432/data_collection_db?client_encoding=utf8"
    )
    pdf = pd.read_sql('select * from "GpsScanpoint"', engine)

    # Convert Pandas dataframe to spark DataFrame
    df = spark.createDataFrame(pdf)
    print(df.schema)
    df.show()

    # repl()

    df = df.selectExpr(
        "id",
        "cast(latitude as double) as latitude",
        "cast(longitude as double) as longitude",
        "timestamp",
        "cast(accuracy as double) as accuracy",
        "cast(altitude as double) as altitude",
    )
    df.write.parquet("hdfs:///data/test_data")


if __name__ == "__main__":
    run()
