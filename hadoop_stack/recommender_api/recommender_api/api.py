from fastapi import FastAPI, Depends
import uvicorn
from decouple import config
import pyspark.sql.functions as f
import recommender_api.spark as spark_dep
from pyspark.sql import SparkSession, DataFrame
from pyspark.mllib.recommendation import MatrixFactorizationModel, Rating
import asyncio

app = FastAPI()


class StartupHelper:
    def __init__(self):
        self.healthckeck_received = False

    async def run(self):
        print("waiting until docker's healtcheck is received before starting spark.")
        while not self.healthckeck_received:
            await asyncio.sleep(1)
        print("Healtcheck received, starting spark")
        spark_dep.start_spark()


startup_helper = StartupHelper()


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(startup_helper.run())


@app.on_event("shutdown")
def shutdown_event():
    spark_dep.stop_spark()


def processRecomendaton(
    results: list[Rating],
    s: SparkSession,
    nodes: DataFrame,
    recmap: DataFrame,
):
    for r in results:
        name = recmap.filter(f.col("nid") == r.product).first().asDict()["name"]
        a = 1


@app.get("/healthcheck")
def healthckeck():
    startup_helper.healthckeck_received = True
    return "ok"


@app.get("/{user:int}")
def index(
    user: int,
    recmodel: MatrixFactorizationModel = Depends(spark_dep.model),
    s: SparkSession = Depends(spark_dep.get_spark),
    nodes: DataFrame = Depends(spark_dep.get_nodes),
    recmap: DataFrame = Depends(spark_dep.get_recmap),
) -> list[Rating]:
    results = recmodel.recommendProducts(user, config("NUMBER_RECOMENDED", cast=int))
    processRecomendaton(results, s, nodes, recmap)
    return results


def run():
    uvicorn.run("recommender_api.api:app", host="0.0.0.0", port=8888, reload=True)
