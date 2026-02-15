import os
from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db_session
from app.main import app


@pytest.fixture(scope="session")
def test_database_url() -> str:
    database_url = os.getenv("KLUG_TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("KLUG_TEST_DATABASE_URL is not set; skipping integration tests")
    return database_url


@pytest.fixture(scope="session")
def integration_engine(test_database_url: str):
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", test_database_url)
    command.upgrade(alembic_config, "head")

    engine = create_engine(test_database_url, pool_pre_ping=True)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(autouse=True)
def clean_tables(integration_engine) -> None:
    with integration_engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE "
                "app.watch_event_tag, "
                "app.watch_event, "
                "app.media_version, "
                "app.media_item, "
                "app.users "
                "RESTART IDENTITY CASCADE"
            )
        )


@pytest.fixture
def integration_session_factory(integration_engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=integration_engine, autoflush=False, autocommit=False, class_=Session
    )


@pytest.fixture
def integration_client(
    integration_session_factory: sessionmaker[Session],
) -> Generator[TestClient, None, None]:
    def override_get_db_session() -> Generator[Session, None, None]:
        session = integration_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = override_get_db_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
