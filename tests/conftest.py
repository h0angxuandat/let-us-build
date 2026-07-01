"""Test fixtures. API + repositories run against an ephemeral file-backed SQLite DB.

A file (not :memory:) is used so the schema created here is visible to the app's own async
engine built in the lifespan. Schema is created directly from the models (alembic is verified
separately against Postgres).
"""

from __future__ import annotations

from collections.abc import Iterator

import lub_store.models  # noqa: F401  (registers tables on Base.metadata)
import pytest
from fastapi.testclient import TestClient
from lub_api.main import create_app
from lub_api.settings import Settings
from lub_store.db import Base
from sqlalchemy import create_engine


@pytest.fixture
def client(tmp_path) -> Iterator[TestClient]:  # type: ignore[no-untyped-def]
    db_file = tmp_path / "test.db"
    sync_engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()

    settings = Settings(
        database_url=f"sqlite+aiosqlite:///{db_file}", seed_on_startup=True
    )
    with TestClient(create_app(settings)) as test_client:
        yield test_client
