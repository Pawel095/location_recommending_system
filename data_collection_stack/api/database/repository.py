# 3rd party
from typing import List
from sqlalchemy.orm.session import Session

from . import models
from . import schemas



def get_gps_scanpoint(db: Session, id: int):
    return db.query(models.GpsScanpoint).filter(models.GpsScanpoint.id == id).first()


def get_many_gps_scanpoints(db: Session, limit: int = 100):
    return db.query(models.GpsScanpoint).limit(limit).all()


def create_gps_scanpoint(db: Session, scanpoint_models: List[schemas.GpsScanpoint]):
    for m in scanpoint_models:
        mdl = m.model()
        db.add(mdl)
    db.commit()

