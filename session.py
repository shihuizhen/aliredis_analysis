from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import cmdb, redismontir
import contextlib
import influxdb

engine = create_engine("mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4".format(
    **cmdb), pool_pre_ping=True, max_overflow=5)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = sessionmaker(bind=engine)
# 装饰后可以with方式调用


@contextlib.contextmanager
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@contextlib.contextmanager
def get_influxdb() -> Generator:
    try:
        db = influxdb.InfluxDBClient(**redismontir)
        yield db
    finally:
        db.close()
