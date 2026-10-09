"""SQLAlchemy connection pool. Identity is never cached here."""
from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

@lru_cache(maxsize=1)
def get_engine():
    if not DATABASE_URL:
        raise RuntimeError("[database].url is missing from Streamlit secrets")
    url = str(DATABASE_URL).replace("postgresql://", "postgresql+psycopg://", 1)
    return create_engine(url, pool_pre_ping=True, pool_recycle=300)

@lru_cache(maxsize=1)
def get_session_factory():
    return sessionmaker(bind=get_engine(), expire_on_commit=False)
