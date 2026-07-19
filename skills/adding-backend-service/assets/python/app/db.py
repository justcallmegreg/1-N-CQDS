# db.py — engine + session factory. Engine-parameterized so tests use SQLite and
# prod uses Postgres with the SAME code. No global session; sessions are per-unit-of-work.
import os

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import load_settings

class Base(DeclarativeBase):
    pass

def make_engine(url: str) -> Engine:
    return create_engine(url, future=True)

def make_session_factory(engine: Engine):
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)

# Prod singletons (a pool, not mutable app state).
_settings = None
def _get_settings():
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings

engine = make_engine(_get_settings().database_url) if os.environ.get("DATABASE_URL") else None

def get_session():
    sf = make_session_factory(engine)
    with sf() as s:
        yield s
