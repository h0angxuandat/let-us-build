"""M3: running the BA agent on a ticket produces a BRD artifact (offline TemplateRouter)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _ticket(client: TestClient) -> tuple[str, str]:
    pid = client.post("/projects", json={"name": "P"}).json()["id"]
    tid = client.post(
        f"/projects/{pid}/tickets",
        json={"title": "User login", "description": "Users sign in with email + password"},
    ).json()["id"]
    return pid, tid


def test_run_ba_produces_brd_and_advances_lane(client: TestClient) -> None:
    _, tid = _ticket(client)

    run = client.post(f"/tickets/{tid}/run")
    assert run.status_code == 200
    assert run.json()["lane"] == "done"

    artifacts = client.get(f"/tickets/{tid}/artifacts").json()
    assert len(artifacts) == 1
    art = artifacts[0]
    assert art["type"] == "BRD"
    assert art["produced_by"] == "ba"
    assert "Business Requirements" in (art["inline"] or "")
    # The offline router echoes the ticket context into the BRD.
    assert "email" in (art["inline"] or "")


def test_run_missing_ticket_404(client: TestClient) -> None:
    missing = "00000000-0000-0000-0000-000000000000"
    assert client.post(f"/tickets/{missing}/run").status_code == 404
