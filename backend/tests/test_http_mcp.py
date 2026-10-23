import os
import asyncio
import socket
import subprocess
import sys
from uuid import uuid4
from fastapi.testclient import TestClient
import httpx
import pytest
from app.main import app, buckets
from app import mcp_client
from app.auth import login
from app.db import Session
from app.models import Incident


@pytest.fixture(scope="module")
def client():
    buckets.clear()
    with TestClient(app) as c:
        yield c


def test_http_auth_csrf_and_invalid_data(client):
    assert client.get("/api/me").status_code == 401
    assert (
        client.post(
            "/api/login", json={"email": "u1@demo.test", "password": "Testing-password-42!"}
        ).status_code
        == 403
    )
    headers = {"X-CarrySafe-Intent": "interactive"}
    assert (
        client.post(
            "/api/login", headers=headers, json={"email": "u1@demo.test", "password": "Testing-password-42!"}
        ).status_code
        == 200
    )
    assert client.get("/api/me").json()["user"]["role"] == "worker"
    assert client.get("/api/me", headers={"origin": "http://localhost:8000"}).status_code == 200
    assert client.get("/api/me", headers={"origin": "http://127.0.0.1:8000"}).status_code == 200
    assert client.get("/api/me", headers={"origin": "https://evil.invalid"}).status_code == 403
    assert (
        client.post(
            "/api/operations/create_incident",
            headers=headers,
            json={
                "payload": {"description": "A leaking pipe reported", "location_id": 1, "shift_id": 1},
                "request_id": "test",
            },
        ).status_code
        == 409
    )
    assert client.post("/api/logout", headers=headers).status_code == 200
    assert client.get("/api/me").status_code == 401


def test_missing_llm_manual_fallback(client):
    headers = {"Authorization": "Bearer " + login("u1@demo.test", "Testing-password-42!")}
    response = client.post("/api/assistant/chat", headers=headers, json={"message": "Report a leak"})
    assert response.status_code == 200
    assert response.json()["mode"] == "manual"
    assert response.json()["trace"] == []


@pytest.mark.asyncio
async def test_real_streamable_http_mcp_full_workflow(users):
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env={**os.environ, "MCP_URL": f"http://127.0.0.1:{port}/mcp"},
    )
    old = mcp_client.settings.mcp_url
    mcp_client.settings.mcp_url = f"http://127.0.0.1:{port}/mcp"
    try:
        for _ in range(80):
            try:
                if httpx.get(f"http://127.0.0.1:{port}/api/health", trust_env=False).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            await asyncio.sleep(0.1)
        else:
            process.terminate()
            process.wait(timeout=10)
            raise RuntimeError("MCP test server failed: " + process.stderr.read().decode())
        token = login("u1@demo.test", "Testing-password-42!")
        async with httpx.AsyncClient(base_url=f"http://127.0.0.1:{port}", trust_env=False) as web:
            headers = {"Authorization": "Bearer " + token}
            creation = await web.post(
                "/api/operations/create_incident",
                headers=headers,
                json={
                    "payload": {
                        "description": "Form submitted via real MCP",
                        "location_id": 1,
                        "shift_id": 1,
                    },
                    "request_id": str(uuid4()),
                    "confirmed": True,
                },
            )
            assert creation.status_code == 200, creation.text
            assert creation.json()["_mcp"]["protocol"] == "2025-11-25"
            briefing = await web.post(
                "/api/assistant/shortcut", headers=headers, json={"command": "briefing"}
            )
            assert briefing.status_code == 200, briefing.text
            assert len(briefing.json()["trace"]) == 3
            assert not any(t["is_error"] for t in briefing.json()["trace"])
        discovery = await mcp_client.discover(token)
        assert discovery["protocol"] == "2025-11-25"
        assert len(discovery["tools"]) == 19
        assert httpx.post(f"http://127.0.0.1:{port}/mcp/", json={}, trust_env=False).status_code == 401
        result = await mcp_client.invoke(
            token,
            "create_incident",
            {"description": "Real MCP test pipe leak", "location_id": 1, "shift_id": 1, "owner_id": 1},
            str(uuid4()),
        )
        assert not result["is_error"], result
        i = result["data"]
        assert i["id"].startswith("CS-")
        with Session() as db:
            assert db.get(Incident, i["id"]).description == "Real MCP test pipe leak"
        read = await mcp_client.invoke(token, "get_incident", {"incident_id": i["id"]})
        assert read["data"]["owner_id"] == 1
        denied = await mcp_client.invoke(
            token,
            "review_closure_request",
            {
                "incident_id": i["id"],
                "expected_version": i["version"],
                "request_id": 1,
                "approve": True,
                "reason": "Attempt unauthorized approval",
                "verification_reference": "Synthetic inspection reference",
            },
            str(uuid4()),
        )
        assert denied["is_error"] and "AUTHORIZATION" in denied["text"]
        invalid = await mcp_client.invoke(
            token, "create_incident", {"description": "x", "location_id": 1, "shift_id": 1}, str(uuid4())
        )
        assert invalid["is_error"]
        other = login("u4@demo.test", "Testing-password-42!")
        isolated = await mcp_client.invoke(other, "get_incident", {"incident_id": i["id"]})
        assert isolated["is_error"] and "NOT_FOUND" in isolated["text"]
        assert (await mcp_client.invoke(token, "get_incident", {"incident_id": i["id"]}))["data"][
            "state"
        ] == "open"
    finally:
        mcp_client.settings.mcp_url = old
        process.terminate()
        process.wait(timeout=10)
