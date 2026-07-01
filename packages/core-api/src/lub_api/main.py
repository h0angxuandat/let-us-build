"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from lub_store import create_engine, create_sessionmaker
from lub_store.seed import seed_default_agents

from lub_api.routes import agents, health, projects, requirements
from lub_api.settings import Settings, get_settings

__version__ = "0.0.0"


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    engine = create_engine(settings.database_url)
    app.state.engine = engine
    app.state.sessionmaker = create_sessionmaker(engine)
    if settings.seed_on_startup:
        await seed_default_agents(app.state.sessionmaker)
    try:
        yield
    finally:
        await engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI app. Orchestrator/WS routers are added from M4 onward."""
    app = FastAPI(title="let-us-build", version=__version__, lifespan=_lifespan)
    app.state.settings = settings or get_settings()
    app.include_router(health.router)
    app.include_router(projects.router)
    app.include_router(requirements.router)
    app.include_router(agents.router)
    return app
