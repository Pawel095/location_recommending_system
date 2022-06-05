from typing import Callable, Dict, Optional, Sequence
from pyspark.sql import Row, types as t, DataFrame
import shapely.geometry
import pyspark.sql.functions as f


def toMap(key: str, value: str, decode=True) -> Callable[..., Optional[Dict[str, str]]]:
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


def distance_in_meters(p1: shapely.geometry.Point, p2: shapely.geometry.Point):
    from geographiclib.geodesic import Geodesic

    geodesic = Geodesic.WGS84
    return geodesic.Inverse(p1.x, p1.y, p2.x, p2.y)["s12"]


def drop_columns_and_mappify_tags(df: DataFrame) -> DataFrame:
    return df.drop("uid", "user_sid", "changeset", "version").withColumn(
        "tags", tupleUdf(f.col("tags"))
    )


tupleUdf = f.udf(toMap("key", "value"), t.MapType(t.StringType(), t.StringType()))
nodesUdf = f.udf(
    toMap("index", "nodeId", decode=False), t.MapType(t.IntegerType(), t.LongType())
)
distance_in_metersUdf = f.udf(distance_in_meters, t.DoubleType())
