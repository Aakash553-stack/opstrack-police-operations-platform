import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://opstrack:opstrack_dev_pw@localhost:5432/opstrack_test",
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.main import app
from app.models import Base


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(settings.DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    outer_transaction = connection.begin()
    # join_transaction_mode="create_savepoint" lets application code call
    # session.commit() (as the CRUD layer does) without ending the outer
    # transaction, so the whole test rolls back cleanly at teardown.
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    def override_get_db():
        try:
            yield session
        except Exception:
            # Mirror production get_db: a failed request (e.g. an
            # IntegrityError from a CHECK/UNIQUE violation) must roll back
            # before the next request reuses this session/savepoint.
            session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    yield session
    app.dependency_overrides.clear()
    session.close()
    outer_transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    with TestClient(app) as c:
        yield c
