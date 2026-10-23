from uuid import uuid4
from datetime import timedelta
import pytest
from app.service import execute, RuleError
from app.db import Session, now
from app.models import Incident, TemporaryControl


def call(u, name, **args):
    return execute(u, name, args, str(uuid4()))


def create(u):
    return call(
        u,
        "create_incident",
        description="Pipe leaking near loading bay",
        location_id=1,
        shift_id=1,
        owner_id=u.id,
    )


def v(i, **kw):
    return dict(incident_id=i["id"], expected_version=i["version"], **kw)


def test_create_read_restart_persistence(users):
    i = create(users[0])
    assert call(users[1], "get_incident", incident_id=i["id"])["description"] == i["description"]
    with Session() as db:
        assert db.get(Incident, i["id"]).state == "open"


@pytest.mark.parametrize(
    "field,value", [("description", "x"), ("location_id", 2), ("owner_id", 4), ("role", "supervisor")]
)
def test_invalid_and_tenant_inputs(users, field, value):
    a = dict(description="A pipe has a leak", location_id=1, shift_id=1)
    a[field] = value
    with pytest.raises(RuleError):
        call(users[0], "create_incident", **a)


def test_cross_tenant_read_and_write(users):
    i = create(users[0])
    for tool, args in [
        ("get_incident", {"incident_id": i["id"]}),
        ("record_incident_progress", v(i, note="Cannot edit another site", condition="unresolved")),
    ]:
        with pytest.raises(RuleError):
            call(users[3], tool, **args)


def test_assign_accept_and_worker_denial(users):
    i = create(users[0])
    with pytest.raises(RuleError):
        call(users[0], "assign_incident", **v(i, owner_id=2))
    i = call(users[2], "assign_incident", **v(i, owner_id=2))
    assert not i["owner_accepted"]
    i = call(users[1], "accept_ownership", **v(i))
    assert i["owner_accepted"]


def test_idempotency_and_stale_version(users):
    a = dict(description="Repeated incident creation", location_id=1, shift_id=1)
    i = execute(users[0], "create_incident", a, "same")
    assert execute(users[0], "create_incident", a, "same")["id"] == i["id"]
    with pytest.raises(RuleError):
        execute(users[0], "create_incident", {**a, "description": "Different body content"}, "same")
    call(
        users[0],
        "record_incident_progress",
        **v(i, note="Still requires maintenance", condition="unresolved"),
    )
    with pytest.raises(RuleError) as err:
        call(
            users[0],
            "record_incident_progress",
            **v(i, note="A stale competing update", condition="unresolved"),
        )
    assert err.value.rule == "CONCURRENT_UPDATE"


def test_control_handover_continuity(users):
    i = create(users[0])
    i = call(
        users[0],
        "add_temporary_control",
        **v(
            i,
            description="Temporary collection tray",
            responsible_id=1,
            review_due=(now() + timedelta(hours=1)).isoformat(),
        ),
    )
    with Session.begin() as db:
        db.get(TemporaryControl, i["controls"][0]["id"]).review_due = now() - timedelta(hours=1)
    assert len(call(users[0], "list_overdue_controls")["controls"]) == 1
    h = call(users[0], "create_handover", outgoing_id=1, incoming_id=2, recipient_id=2)
    with pytest.raises(RuleError):
        call(users[0], "acknowledge_handover", handover_id=h["id"])
    call(users[1], "acknowledge_handover", handover_id=h["id"])
    assert call(users[1], "get_incident", incident_id=i["id"])["controls"][0]["state"] == "active"
    h2 = call(users[1], "create_handover", outgoing_id=2, incoming_id=3, recipient_id=1)
    assert i["id"] in h2["incident_ids"]


def test_protected_closure_full_journey(users):
    w, _, s, _ = users
    i = create(w)
    i = call(
        w,
        "add_temporary_control",
        **v(
            i,
            description="Containment below pipe",
            responsible_id=1,
            review_due=(now() + timedelta(hours=1)).isoformat(),
        ),
    )
    with pytest.raises(RuleError):
        call(w, "request_incident_closure", **v(i, evidence=""))
    i = call(w, "request_incident_closure", **v(i, evidence="Maintenance ticket DEMO-123: pipe replaced"))
    r = i["closure_requests"][0]["id"]
    review = dict(
        request_id=r,
        approve=True,
        reason="Checked the maintenance record",
        verification_reference="DEMO inspection 123 verified by supervisor",
    )
    with pytest.raises(RuleError) as err:
        call(w, "review_closure_request", **v(i, **review))
    assert err.value.rule == "AUTHORIZATION"
    with pytest.raises(RuleError) as err:
        call(s, "review_closure_request", **v(i, **review))
    assert err.value.rule == "ACTIVE_CONTROL"
    i = call(
        s,
        "record_control_review",
        **v(
            i,
            control_id=i["controls"][0]["id"],
            result="retired",
            observation="Inspection completed; containment removed",
        ),
    )
    i = call(s, "review_closure_request", **v(i, **review))
    assert i["state"] == "closed"
    with pytest.raises(RuleError):
        call(w, "record_incident_progress", **v(i, note="Post-closure mutation", condition="unresolved"))
    history = call(w, "get_incident_history", incident_id=i["id"])["events"]
    assert any(x["action"] == "rejected:review_closure_request" for x in history)
    assert any(x["action"] == "review_closure_request" for x in history)


def test_conflicting_updates_preserved(users):
    i = create(users[0])
    for condition in ["unresolved", "reported_repaired"]:
        i = call(
            users[0],
            "record_incident_progress",
            **v(i, note="Observation: " + condition, condition=condition),
        )
    assert i["disputed"]
    assert i["description"] == "Pipe leaking near loading bay"
    with pytest.raises(RuleError):
        call(
            users[0],
            "record_incident_progress",
            **v(i, note="Worker attempts to clear dispute", condition="clarified"),
        )
    i = call(
        users[2],
        "record_incident_progress",
        **v(i, note="Inspection clarified the conflicting observations", condition="clarified"),
    )
    assert not i["disputed"]


def test_independent_supervisor_review(users):
    i = create(users[2])
    i = call(
        users[2], "request_incident_closure", **v(i, evidence="Maintenance ticket with completion evidence")
    )
    with pytest.raises(RuleError) as err:
        call(
            users[2],
            "review_closure_request",
            **v(
                i,
                request_id=i["closure_requests"][0]["id"],
                approve=True,
                reason="Attempt self approval",
                verification_reference="Inspection ticket evidence",
            ),
        )
    assert err.value.rule == "INDEPENDENT_REVIEW"
