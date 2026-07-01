"""M0 smoke tests: packages import cleanly and the API health endpoint works."""

from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient
from lub_api import create_app

PACKAGES = [
    "lub_store",
    "lub_llm",
    "lub_memory",
    "lub_agents",
    "lub_orchestrator",
    "lub_improvement",
    "lub_workspace",
    "lub_api",
]


@pytest.mark.parametrize("name", PACKAGES)
def test_package_imports(name: str) -> None:
    assert importlib.import_module(name) is not None


def test_health_ok() -> None:
    client = TestClient(create_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_agent_registry_has_six_roles() -> None:
    from lub_agents.registry import _REGISTRY

    assert len(_REGISTRY) == 6
