import pandas as pd
from pyspark.sql import SparkSession
from sqlalchemy import create_engine


def repl():
    from ptpython.repl import embed

    embed(globals(), locals())


def run():
    appName = "PySpark PostgreSQL Example - via psycopg2"
    master = "local"

    spark = SparkSession.builder.master(master).appName(appName).getOrCreate()

    engine = create_engine(
        "postgresql+psycopg2://fastapi:passwd@192.168.2.1:5432/random_demos?client_encoding=utf8"
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
    df.write.parquet("hdfs:///fromPostgres")


if __name__ == "__main__":
    run()
