from __future__ import annotations

from contextlib import contextmanager
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    pass


def get_engine(db_url: str | None = None):
    url = db_url or os.getenv("DATABASE_URL") or "sqlite:///./data.db"
    # check_same_thread False for SQLite in multi-threaded FastAPI
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, future=True)


def get_session_factory(db_url: str | None = None):
    engine = get_engine(db_url)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@contextmanager
def session_scope(SessionLocal) -> Generator:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
