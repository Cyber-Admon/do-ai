import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase


def get_database_url() -> str:
    url = os.environ["DATABASE_URL"]
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


engine = create_engine(get_database_url(), pool_pre_ping=True)


class Base(DeclarativeBase):
    pass