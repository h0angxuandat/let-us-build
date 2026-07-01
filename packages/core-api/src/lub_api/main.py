"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from lub_api.routes import health
from lub_api.settings import get_settings

__version__ = "0.0.0"


def create_app() -> FastAPI:
    """Build the FastAPI app. Routers for projects/tickets/agents/ws are added from M1 onward."""
    settings = get_settings()
    app = FastAPI(title="let-us-build", version=__version__)
    app.state.settings = settings
    app.include_router(health.router)
    return app
