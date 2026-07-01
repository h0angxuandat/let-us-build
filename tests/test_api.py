"""M1 API CRUD tests (projects, requirements, agents) + default-agent seeding."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_default_agents_seeded(client: TestClient) -> None:
    resp = client.get("/agents")
    assert resp.status_code == 200
    roles = {a["role"] for a in resp.json()}
    assert roles == {"pm", "ba", "designer", "tech_lead", "developer", "qe"}


def test_project_crud(client: TestClient) -> None:
    created = client.post("/projects", json={"name": "Demo", "description": "d"})
    assert created.status_code == 201
    pid = created.json()["id"]

    assert client.get(f"/projects/{pid}").json()["name"] == "Demo"
    assert any(p["id"] == pid for p in client.get("/projects").json())


def test_get_missing_project_404(client: TestClient) -> None:
    missing = "00000000-0000-0000-0000-000000000000"
    assert client.get(f"/projects/{missing}").status_code == 404


def test_requirement_nested_under_project(client: TestClient) -> None:
    pid = client.post("/projects", json={"name": "P"}).json()["id"]
    r = client.post(
        f"/projects/{pid}/requirements",
        json={"kind": "brief", "content": "Build a todo app"},
    )
    assert r.status_code == 201
    listing = client.get(f"/projects/{pid}/requirements").json()
    assert len(listing) == 1
    assert listing[0]["content"] == "Build a todo app"


def test_requirement_on_missing_project_404(client: TestClient) -> None:
    missing = "00000000-0000-0000-0000-000000000000"
    r = client.post(f"/projects/{missing}/requirements", json={"content": "x"})
    assert r.status_code == 404


def test_agent_update(client: TestClient) -> None:
    agent = client.get("/agents").json()[0]
    resp = client.patch(f"/agents/{agent['id']}", json={"model": "gpt-5", "provider": "openai"})
    assert resp.status_code == 200
    assert resp.json()["model"] == "gpt-5"
    assert resp.json()["provider"] == "openai"
