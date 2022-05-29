from fastapi import FastAPI, Depends
import uvicorn
from decouple import config
import recommender_api.spark as spark_dep
from pyspark.mllib.recommendation import MatrixFactorizationModel

app = FastAPI()


@app.on_event("startup")
def on_startup():
    spark_dep.start_spark()


@app.on_event("shutdown")
def shutdown_event():
    spark_dep.stop_spark()


@app.get("/{user}")
def index(user: int, recmodel: MatrixFactorizationModel = Depends(spark_dep.model)) -> str:
    return recmodel.recommendProducts(user, config("NUMBER_RECOMENDED", cast=bool))


def run():
    uvicorn.run("recommender_api.api:app", host="0.0.0.0", port=8888, reload=True)
