"""Core API for let-us-build (FastAPI). REST + WebSocket gateway; hosts the orchestrator."""

from lub_api.main import create_app

__all__ = ["create_app"]
