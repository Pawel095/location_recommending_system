# Builtins
from typing import List

# 3rd party
from pydantic import BaseModel

# Local
from database import models


class GpsScanpoint(BaseModel):
    latitude: str
    longitude: str
    timestamp: str
    accuracy: str
    altitude: str

    class Config:
        orm_mode = True

    def model(self):
        return models.GpsScanpoint(**self.dict())
