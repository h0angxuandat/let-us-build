"""Health check."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe used by the CLI boot sequence."""
    return {"status": "ok", "service": "let-us-build"}
