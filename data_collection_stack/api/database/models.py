# 3rd party
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


from .__ctl import Base


class GpsScanpoint(Base):
    __tablename__ = "GpsScanpoint"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(String)
    longitude = Column(String)
    timestamp = Column(String)
    accuracy = Column(String)
    altitude = Column(String)
