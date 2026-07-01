"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lub_store import create_engine, create_sessionmaker
from lub_store.seed import seed_default_agents

from lub_api.events import EventBus
from lub_api.routes import agents, health, projects, requirements, tickets, ws
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
    """Build the FastAPI app. Orchestrator routers are added from M4 onward."""
    resolved = settings or get_settings()
    app = FastAPI(title="let-us-build", version=__version__, lifespan=_lifespan)
    app.state.settings = resolved
    app.state.events = EventBus()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(projects.router)
    app.include_router(requirements.router)
    app.include_router(agents.router)
    app.include_router(tickets.router)
    app.include_router(ws.router)
    return app
