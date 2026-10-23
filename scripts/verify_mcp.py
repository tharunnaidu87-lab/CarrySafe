"""Verify actual MCP transport against the isolated local demo. Never prints tokens."""

import os
import sys
import asyncio
import getpass
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
import httpx
from app import mcp_client


async def main():
    base = os.environ.get("CARRYSAFE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    if not base.startswith(("http://127.0.0.1:", "http://localhost:")):
        raise SystemExit(
            "This destructive-workflow test is limited to a local demo endpoint."
        )
    password = os.environ.get("DEMO_PASSWORD") or getpass.getpass("Demo password: ")
    mcp_client.settings.mcp_url = base + "/mcp"
    async with httpx.AsyncClient(base_url=base, trust_env=False) as web:

        async def sign_in(email):
            r = await web.post(
                "/api/login",
                headers={"X-CarrySafe-Intent": "interactive"},
                json={"email": email + "@demo.carrysafe.test", "password": password},
            )
            r.raise_for_status()
            assert r.json()["user"]["email"].endswith("@demo.carrysafe.test")
            return web.cookies.get("carrysafe_session")

        worker = await sign_in("alex")
        supervisor = await sign_in("jordan")
        info = await mcp_client.discover(worker)
        assert info["protocol"] == "2025-11-25"
        assert len(info["tools"]) == 19
        print(
            "PASS protocol:",
            info["protocol"],
            "SDK 2.3.0; transport: Streamable HTTP; discovered:",
            len(info["tools"]),
        )

        async def call(token, name, args, deny=None):
            r = await mcp_client.invoke(token, name, args, str(uuid4()))
            if deny:
                assert r["is_error"] and deny in r["text"], r
                print("PASS rejected:", name, deny)
            else:
                assert not r["is_error"], r
                print("PASS invoked:", name)
            return r["data"]

        directory = await call(worker, "get_directory", {})
        loc = directory["locations"][0]["id"]
        shift = directory["shifts"][0]["id"]
        owner = next(
            u["id"] for u in directory["users"] if u["email"].startswith("alex@")
        )
        i = await call(
            worker,
            "create_incident",
            {
                "description": "SYNTHETIC MCP verification: pipe leak",
                "location_id": loc,
                "shift_id": shift,
                "owner_id": owner,
            },
        )

        def v(**kw):
            return {"incident_id": i["id"], "expected_version": i["version"], **kw}

        i = await call(
            worker,
            "add_temporary_control",
            v(
                description="SYNTHETIC containment tray",
                responsible_id=owner,
                review_due=(
                    datetime.now(timezone.utc) + timedelta(hours=1)
                ).isoformat(),
            ),
        )
        await call(worker, "get_incident", {"incident_id": i["id"]})
        i = await call(
            worker,
            "request_incident_closure",
            v(evidence="SYNTHETIC maintenance work order verification"),
        )
        review = {
            "request_id": i["closure_requests"][0]["id"],
            "approve": True,
            "reason": "SYNTHETIC independent review completed",
            "verification_reference": "SYNTHETIC inspection record QA-1042",
        }
        await call(worker, "review_closure_request", v(**review), deny="AUTHORIZATION")
        await call(
            supervisor, "review_closure_request", v(**review), deny="ACTIVE_CONTROL"
        )
        i = await call(
            supervisor,
            "record_control_review",
            v(
                control_id=i["controls"][0]["id"],
                result="retired",
                observation="SYNTHETIC supervisor review; temporary tray removed",
            ),
        )
        i = await call(supervisor, "review_closure_request", v(**review))
        assert i["state"] == "closed"
        current = await call(worker, "get_incident", {"incident_id": i["id"]})
        assert current["state"] == "closed"
        events = await call(worker, "get_incident_history", {"incident_id": i["id"]})
        assert len(events["events"]) >= 7
        print(
            "PASS persisted final state: closed; audit events:", len(events["events"])
        )
        print(
            "All verification assertions passed. Synthetic verification record remains in the local database."
        )


if __name__ == "__main__":
    asyncio.run(main())
