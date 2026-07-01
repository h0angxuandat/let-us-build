"""M2 ticket endpoint tests (manual add-to-plan, list, get, patch lane)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _project(client: TestClient) -> str:
    return client.post("/projects", json={"name": "P"}).json()["id"]


def test_add_ticket_lands_in_plan_with_key(client: TestClient) -> None:
    pid = _project(client)
    r = client.post(f"/projects/{pid}/tickets", json={"title": "First"})
    assert r.status_code == 201
    body = r.json()
    assert body["lane"] == "plan"
    assert body["created_by"] == "user"
    assert body["key"] == "LUB-1"


def test_ticket_keys_increment_per_project(client: TestClient) -> None:
    pid = _project(client)
    client.post(f"/projects/{pid}/tickets", json={"title": "A"})
    second = client.post(f"/projects/{pid}/tickets", json={"title": "B"})
    assert second.json()["key"] == "LUB-2"


def test_list_and_patch_lane(client: TestClient) -> None:
    pid = _project(client)
    tid = client.post(f"/projects/{pid}/tickets", json={"title": "Move me"}).json()["id"]

    assert len(client.get(f"/projects/{pid}/tickets").json()) == 1

    moved = client.patch(f"/tickets/{tid}", json={"lane": "processing"})
    assert moved.status_code == 200
    assert moved.json()["lane"] == "processing"


def test_add_ticket_missing_project_404(client: TestClient) -> None:
    missing = "00000000-0000-0000-0000-000000000000"
    assert client.post(f"/projects/{missing}/tickets", json={"title": "x"}).status_code == 404
