"""Shared pytest fixtures — in-memory database and test client."""

import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="function")
def engine():
    """In-memory SQLite engine — StaticPool shares one DB across connections."""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield eng


@pytest.fixture(scope="function")
def db_session(engine):
    """In-memory SQLite session — fresh per test."""
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(engine, db_session):
    """FastAPI TestClient wired to the in-memory DB."""
    from app import main  # noqa: E402
    from app import storage  # noqa: E402
    from app.models import Base  # noqa: E402

    # Replace the app's lifespan so init_db uses the test engine
    @main.asynccontextmanager
    async def test_lifespan(app):
        Base.metadata.create_all(bind=engine)
        yield

    main.app.router.lifespan_context = test_lifespan

    # Override get_db to return the test session
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    main.app.dependency_overrides[storage.get_db] = override_get_db
    with TestClient(main.app) as tc:
        yield tc
    main.app.dependency_overrides.clear()
