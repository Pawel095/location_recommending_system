# Builtins
from typing import List

# 3rd party
from fastapi import Depends
from fastapi import FastAPI
from fastapi import requests
from sqlalchemy.orm.session import Session

# Local
from database import get_db
from database.repository import create_gps_scanpoint
from database.repository import get_many_gps_scanpoints
from database.schemas import GpsScanpoint

app = FastAPI()

try:
    db: Session = next(get_db())
except:
    pass
finally:
    db.close()


@app.get("/")
async def index():
    return "OK"


@app.post("/scanpoint")
async def add_scanpoint(scanpointList: List[GpsScanpoint], db: Session = Depends(get_db)):
    create_gps_scanpoint(db, scanpointList)
    return "OK"


@app.get("/scanpoint")
async def get_scanpoints(limit: int, db: Session = Depends(get_db)):
    if limit >= 100:
        limit = 100
    return get_many_gps_scanpoints(db, limit)
