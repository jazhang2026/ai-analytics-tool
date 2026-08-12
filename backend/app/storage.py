"""Embedded database (SQLite) connection, settings, and persistence bootstrap."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DB_PATH = os.getenv("DB_PATH", str(Path(__file__).resolve().parent.parent / "data" / "app.db"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(Path(__file__).resolve().parent.parent / "data" / "uploads"))
BACKUP_DIR = os.getenv("BACKUP_DIR", str(Path(__file__).resolve().parent.parent / "backups"))

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Safe to call on every startup."""
    from . import models  # noqa: F401  ensure models are imported
    models.Base.metadata.create_all(bind=engine)

    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)
