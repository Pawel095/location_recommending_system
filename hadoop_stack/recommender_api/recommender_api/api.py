from math import prod
from fastapi import FastAPI, Depends
import uvicorn
from decouple import config
import pyspark.sql.functions as f
import recommender_api.spark as spark_dep
from pyspark.sql import SparkSession, DataFrame
from pyspark.mllib.recommendation import MatrixFactorizationModel, Rating
import asyncio
import sys
from pydantic import BaseModel

app = FastAPI()

# detects if debugger is attached
DEBUG = sys.gettrace() is not None


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
    if DEBUG:
        print("DEBUG MODE: starting spark instantly")
        spark_dep.start_spark()
    else:
        asyncio.create_task(startup_helper.run())

@app.get("/healthcheck")
def healthckeck():
    startup_helper.healthckeck_received = True
    return "ok"

@app.on_event("shutdown")
def shutdown_event():
    spark_dep.stop_spark()




def processRecomendaton(
    results: list[Rating],
    wkt: str,
    nodes: DataFrame,
    recmap: DataFrame,
):
    points: list[RecomendationResponse] = []
    for r in results:
        name = recmap.filter(f.col("nid") == r.product).first().asDict()["aname"]
        point = (
            nodes.filter(f.col("tags.name") == name)
            .withColumn("wkt", f.lit(wkt))
            .selectExpr(["*", "st_geomFromWKT(wkt) as cur_pos"])
            .selectExpr(["*", "st_distance(geom,cur_pos) as dist"])
            .orderBy("dist")
            .first()
            .asDict()["geom"]
        )
        points.append(
            RecomendationResponse(
                x=point.x,
                y=point.y,
                product=r.product,
                rating=r.rating,
            )
        )
    return points


class RequestBody(BaseModel):
    wkt: str


class RecomendationResponse(BaseModel):
    x: float
    y: float
    product: int
    rating: float


@app.post("/recomend/{user:int}")
def recommend(
    user: int,
    body: RequestBody,
    recmodel: MatrixFactorizationModel = Depends(spark_dep.model),
    nodes: DataFrame = Depends(spark_dep.get_nodes),
    recmap: DataFrame = Depends(spark_dep.get_recmap),
) -> list[RecomendationResponse]:
    results = recmodel.recommendProducts(user, config("NUMBER_RECOMENDED", cast=int))
    return processRecomendaton(results, body.wkt, nodes, recmap)


def run():
    uvicorn.run("recommender_api.api:app", host="0.0.0.0", port=8888, reload=True)
