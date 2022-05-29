# 3rd party
import sqlalchemy
from decouple import config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

DB_URL = f"postgresql://{config('DB_USER')}:{config('DB_PASS')}@{config('DB_URL')}:{config('DB_PORT')}/{config('DB_DBNAME')}"

__engine = sqlalchemy.create_engine(DB_URL)
DbSession = sessionmaker(autocommit=False, autoflush=False, bind=__engine)

Base = declarative_base()


def get_db():
    db = DbSession()
    try:
        yield db
    finally:
        db.close()
