from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator
from loguru import logger

from app.config.app_config import app_config

engine = create_engine(
    app_config.db_url,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
    connect_args={
        "options": f"-c search_path={app_config.db_schema}",
        "prepare_threshold": None,  # Disable prepared statements for Supabase pooler
    },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@event.listens_for(engine, "connect")
def set_search_path(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute(f"SET search_path TO {app_config.db_schema}")
    cursor.close()


def get_db() -> Generator[Session, None, None]:
    """Yields a database session for dependency injection."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
