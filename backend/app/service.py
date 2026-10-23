import hashlib
import json
from uuid import uuid4
from datetime import timedelta
from sqlalchemy import select, func
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from .db import Session, now, utc
from .models import (
    User,
    Location,
    Shift,
    Incident,
    TemporaryControl,
    ControlReview,
    Handover,
    Acknowledgment,
    ClosureRequest,
    AuditEvent,
    Receipt,
    ReferenceIncident,
)
from .schemas import MODELS, READS


class RuleError(Exception):
    def __init__(self, rule, message, status=409):
        self.rule, self.message, self.status = rule, message, status


def fail(rule, message, status=409):
    raise RuleError(rule, message, status)


def row(obj):
    if obj is None:
        return None
    return {
        c.name: (utc(v).isoformat() if hasattr(v, "tzinfo") else v)
        for c in obj.__table__.columns
        if c.name not in ("password_hash",)
        for v in [getattr(obj, c.name)]
    }


def scoped(db, cls, id, user):
    obj = db.get(cls, id)
    if not obj or obj.org_id != user.org_id:
        fail("NOT_FOUND", "Record not found in your organization.", 404)
    return obj


def supervisor(user):
    if user.role != "supervisor":
        fail("AUTHORIZATION", "This action requires a supervisor.", 403)


def audit(db, user, action, entity, before=None, after=None):
    db.add(
        AuditEvent(
            org_id=user.org_id,
            user_id=user.id,
            action=action,
            entity_id=str(entity),
            before=before or {},
            after=after or {},
        )
    )


def details(db, incident):
    data = row(incident)
    data["location"] = db.get(Location, incident.location_id).name
    data["owner"] = db.get(User, incident.owner_id).name if incident.owner_id else None
    data["controls"] = [
        row(x)
        for x in db.scalars(
            select(TemporaryControl)
            .where(TemporaryControl.incident_id == incident.id)
            .order_by(TemporaryControl.id)
        )
    ]
    data["closure_requests"] = [
        row(x)
        for x in db.scalars(
            select(ClosureRequest)
            .where(ClosureRequest.incident_id == incident.id)
            .order_by(ClosureRequest.id)
        )
    ]
    return data


def flags(db, user):
    result = []
    incidents = list(
        db.scalars(select(Incident).where(Incident.org_id == user.org_id, Incident.state != "closed"))
    )
    for i in incidents:

        def add(rule, message):
            result.append({"incident_id": i.id, "rule": rule, "message": message})

        if not i.owner_id or not i.owner_accepted:
            add("MISSING_OWNER", "Responsibility has not been assigned and accepted.")
        if i.disputed:
            add("CONFLICTING_INFORMATION", "Reports disagree. A supervisor must record a clarification.")
        if utc(i.updated_at) < now() - timedelta(hours=24):
            add("STALE_UPDATE", "No recorded update in the last 24 hours.")
        for c in db.scalars(
            select(TemporaryControl).where(
                TemporaryControl.incident_id == i.id, TemporaryControl.state == "active"
            )
        ):
            if utc(c.review_due) < now():
                add(
                    "OVERDUE_REVIEW",
                    f"Control #{c.id} needs a recorded review. This does not prove physical failure.",
                )
            if c.result == "needs_attention":
                add("CONTROL_ATTENTION", f"Control #{c.id} was reported as needing attention.")
    for h in db.scalars(select(Handover).where(Handover.org_id == user.org_id)):
        if not db.scalar(
            select(Acknowledgment).where(
                Acknowledgment.handover_id == h.id, Acknowledgment.user_id == h.recipient_id
            )
        ):
            result.append(
                {
                    "handover_id": h.id,
                    "rule": "UNACKNOWLEDGED_HANDOVER",
                    "message": "The incoming recipient has not acknowledged this handover.",
                }
            )
    for a in db.scalars(
        select(AuditEvent)
        .where(AuditEvent.org_id == user.org_id, AuditEvent.action == "rejected:review_closure_request")
        .order_by(AuditEvent.id.desc())
        .limit(20)
    ):
        result.append(
            {
                "incident_id": a.entity_id,
                "rule": "REJECTED_CLOSURE",
                "message": a.after.get("message", "Closure rejected."),
            }
        )
    return result


def execute(user, name, payload, request_id=None):
    if name not in MODELS:
        fail("UNKNOWN_TOOL", "Unknown operation.", 404)
    try:
        args = MODELS[name].model_validate(payload).model_dump()
    except ValidationError as e:
        fail("VALIDATION", str(e), 422)
    writing = name not in READS
    if writing and (not request_id or len(request_id) > 100):
        fail("IDEMPOTENCY", "A request ID of at most 100 characters is required.", 422)
    fingerprint = hashlib.sha256(
        json.dumps([name, payload], sort_keys=True, default=str).encode()
    ).hexdigest()
    key = f"{user.org_id}:{user.id}:{request_id}"
    try:
        with Session.begin() as db:
            if writing:
                receipt = db.get(Receipt, key)
                if receipt:
                    if receipt.fingerprint != fingerprint:
                        fail("IDEMPOTENCY", "Request ID was already used for different input.")
                    return receipt.result
            result = dispatch(db, user, name, args)
            db.flush()
            if writing:
                db.add(Receipt(key=key, fingerprint=fingerprint, result=result))
            return result
    except (StaleDataError, IntegrityError):
        # A concurrent identical retry may have committed; recover its receipt.
        with Session() as db:
            receipt = db.get(Receipt, key) if writing else None
            if receipt and receipt.fingerprint == fingerprint:
                return receipt.result
        fail("CONCURRENT_UPDATE", "The record changed. Refresh and review before retrying.")
    except RuleError as e:
        if writing:
            with Session.begin() as db:
                # Do not reveal cross-tenant record IDs in audit events.
                entity = payload.get("incident_id", "operation")
                if e.rule == "NOT_FOUND":
                    entity = "operation"
                audit(db, user, "rejected:" + name, entity, after={"rule": e.rule, "message": e.message})
        raise


def dispatch(db, u, name, a):
    if name == "get_directory":
        return {
            "users": [row(x) for x in db.scalars(select(User).where(User.org_id == u.org_id))],
            "locations": [row(x) for x in db.scalars(select(Location).where(Location.org_id == u.org_id))],
            "shifts": [row(x) for x in db.scalars(select(Shift).where(Shift.org_id == u.org_id))],
        }
    if name == "list_open_incidents":
        q = select(Incident).where(Incident.org_id == u.org_id, Incident.state != "closed")
        if a.get("state"):
            q = q.where(Incident.state == a["state"])
        if a["query"]:
            q = q.where(
                Incident.description.icontains(a["query"], autoescape=True)
                | Incident.id.icontains(a["query"], autoescape=True)
            )
        return {
            "incidents": [
                details(db, x)
                for x in db.scalars(
                    q.order_by(Incident.created_at.desc(), Incident.id).offset(a["offset"]).limit(a["limit"])
                )
            ]
        }
    if name == "get_dashboard":
        items = list(db.scalars(select(Incident).where(Incident.org_id == u.org_id)))
        fs = flags(db, u)
        return {
            "active": sum(x.state != "closed" for x in items),
            "closed": sum(x.state == "closed" for x in items),
            "pending": sum(x.state == "review_pending" for x in items),
            "unassigned": sum(
                x.state != "closed" and (not x.owner_id or not x.owner_accepted) for x in items
            ),
            "active_controls": db.scalar(
                select(func.count())
                .select_from(TemporaryControl)
                .join(Incident)
                .where(Incident.org_id == u.org_id, TemporaryControl.state == "active")
            ),
            "overdue": sum(x["rule"] == "OVERDUE_REVIEW" for x in fs),
            "unacknowledged": sum(x["rule"] == "UNACKNOWLEDGED_HANDOVER" for x in fs),
            "recent": [
                row(x)
                for x in db.scalars(
                    select(AuditEvent)
                    .where(AuditEvent.org_id == u.org_id)
                    .order_by(AuditEvent.id.desc())
                    .limit(12)
                )
            ],
        }
    if name == "get_integrity_flags":
        return {"flags": flags(db, u)}
    if name == "list_overdue_controls":
        return {
            "controls": [
                row(x)
                for x in db.scalars(
                    select(TemporaryControl)
                    .join(Incident)
                    .where(
                        Incident.org_id == u.org_id,
                        TemporaryControl.state == "active",
                        TemporaryControl.review_due < now(),
                    )
                    .order_by(TemporaryControl.review_due)
                    .limit(100)
                )
            ]
        }
    if name == "search_reference_incidents":
        return {
            "source_type": "historical_reference",
            "references": [
                row(x)
                for x in db.scalars(
                    select(ReferenceIncident)
                    .where(ReferenceIncident.description.icontains(a["query"], autoescape=True))
                    .offset(a["offset"])
                    .limit(a["limit"])
                )
            ],
        }
    if name == "get_shift_handover":
        result = []
        for h in db.scalars(
            select(Handover).where(Handover.org_id == u.org_id).order_by(Handover.id.desc()).limit(50)
        ):
            result.append(
                {
                    **row(h),
                    "outgoing": db.get(Shift, h.outgoing_id).name,
                    "incoming": db.get(Shift, h.incoming_id).name,
                    "acknowledged": bool(
                        db.scalar(
                            select(Acknowledgment).where(
                                Acknowledgment.handover_id == h.id, Acknowledgment.user_id == h.recipient_id
                            )
                        )
                    ),
                    "current_incidents": [details(db, scoped(db, Incident, id, u)) for id in h.incident_ids],
                }
            )
        return {"handovers": result}
    if name == "create_handover":
        for id in [a["outgoing_id"], a["incoming_id"]]:
            scoped(db, Shift, id, u)
        scoped(db, User, a["recipient_id"], u)
        if a["outgoing_id"] == a["incoming_id"]:
            fail("SHIFT_CONTINUITY", "Choose a different incoming shift.", 422)
        ids = list(
            db.scalars(
                select(Incident.id)
                .where(Incident.org_id == u.org_id, Incident.state != "closed")
                .order_by(Incident.id)
            )
        )
        h = Handover(org_id=u.org_id, incident_ids=ids, **a)
        db.add(h)
        db.flush()
        audit(db, u, name, h.id, after=row(h))
        return row(h)
    if name == "acknowledge_handover":
        h = scoped(db, Handover, a["handover_id"], u)
        if h.recipient_id != u.id:
            fail("AUTHORIZATION", "Only the designated incoming recipient may acknowledge.", 403)
        if not db.scalar(
            select(Acknowledgment).where(Acknowledgment.handover_id == h.id, Acknowledgment.user_id == u.id)
        ):
            db.add(Acknowledgment(handover_id=h.id, user_id=u.id))
            audit(db, u, name, h.id, after={"acknowledged": True})
        return {
            "handover_id": h.id,
            "acknowledged": True,
            "message": "Receipt acknowledged. Incident and control states are unchanged.",
        }
    if name == "create_incident":
        scoped(db, Location, a["location_id"], u)
        scoped(db, Shift, a["shift_id"], u)
        if a["owner_id"]:
            scoped(db, User, a["owner_id"], u)
            if a["owner_id"] != u.id:
                supervisor(u)
        i = Incident(
            id="CS-" + uuid4().hex[:10].upper(),
            org_id=u.org_id,
            reporter_id=u.id,
            owner_accepted=a["owner_id"] == u.id,
            **a,
        )
        db.add(i)
        db.flush()
        audit(db, u, name, i.id, after=row(i))
        possible = list(
            db.scalars(
                select(Incident.id)
                .where(
                    Incident.org_id == u.org_id,
                    Incident.location_id == i.location_id,
                    Incident.state != "closed",
                    Incident.id != i.id,
                    Incident.created_at > now() - timedelta(hours=24),
                )
                .limit(5)
            )
        )
        return {
            **details(db, i),
            "possible_duplicates": possible,
            "duplicate_note": "Same location within 24h; human comparison required. No records were merged.",
        }
    i = scoped(db, Incident, a["incident_id"], u)
    if name == "get_incident":
        return details(db, i)
    if name == "get_incident_history":
        return {
            "events": [
                row(x)
                for x in db.scalars(
                    select(AuditEvent)
                    .where(AuditEvent.org_id == u.org_id, AuditEvent.entity_id == i.id)
                    .order_by(AuditEvent.id)
                    .limit(200)
                )
            ]
        }
    if i.version != a["expected_version"]:
        fail("CONCURRENT_UPDATE", f"Record changed: current version is {i.version}. Refresh before retrying.")
    if i.state == "closed":
        fail("STATE_TRANSITION", "Closed records cannot be changed through this workflow.")
    before = row(i)
    if name == "assign_incident":
        supervisor(u)
        scoped(db, User, a["owner_id"], u)
        i.owner_id = a["owner_id"]
        i.owner_accepted = False
    elif name == "accept_ownership":
        if i.owner_id != u.id:
            fail("AUTHORIZATION", "Only the assigned owner can accept responsibility.", 403)
        i.owner_accepted = True
    elif name == "add_temporary_control":
        scoped(db, User, a["responsible_id"], u)
        if a["responsible_id"] != u.id:
            supervisor(u)
        if utc(a["review_due"]) <= now():
            fail("REVIEW_DEADLINE", "New review deadlines must be in the future.", 422)
        db.add(
            TemporaryControl(
                incident_id=i.id,
                description=a["description"],
                responsible_id=a["responsible_id"],
                review_due=a["review_due"],
            )
        )
    elif name == "record_control_review":
        c = db.get(TemporaryControl, a["control_id"])
        if not c or c.incident_id != i.id:
            fail("NOT_FOUND", "Control not found.", 404)
        if c.state != "active":
            fail("STATE_TRANSITION", "This control is already retired.")
        if u.id != c.responsible_id:
            supervisor(u)
        if a["result"] == "retired":
            supervisor(u)
            c.state = "retired"
        else:
            if not a["next_review_due"] or utc(a["next_review_due"]) <= now():
                fail("REVIEW_DEADLINE", "An active control needs a future review deadline.", 422)
            c.review_due = a["next_review_due"]
        c.last_reviewed = now()
        c.result = a["result"]
        db.add(
            ControlReview(control_id=c.id, reviewer_id=u.id, observation=a["observation"], result=a["result"])
        )
    elif name == "record_incident_progress":
        if a["condition"] == "clarified":
            supervisor(u)
            i.disputed = False
        elif a["condition"] == "disputed":
            i.disputed = True
        else:
            previous = db.scalars(
                select(AuditEvent)
                .where(AuditEvent.org_id == u.org_id, AuditEvent.entity_id == i.id, AuditEvent.action == name)
                .order_by(AuditEvent.id.desc())
                .limit(20)
            )
            last = next(
                (
                    x.after.get("condition")
                    for x in previous
                    if x.after.get("condition") in ("unresolved", "reported_repaired", "clarified")
                ),
                None,
            )
            if {last, a["condition"]} == {"unresolved", "reported_repaired"}:
                i.disputed = True
        # Keep original report immutable; observations live in the audit history.
    elif name == "request_incident_closure":
        if i.state != "open":
            fail("STATE_TRANSITION", "A closure review is already pending.")
        if not i.owner_id or not i.owner_accepted:
            fail("MISSING_OWNER", "An owner must accept responsibility before requesting closure.")
        db.add(ClosureRequest(incident_id=i.id, requester_id=u.id, evidence=a["evidence"]))
        i.state = "review_pending"
    elif name == "review_closure_request":
        supervisor(u)
        r = db.get(ClosureRequest, a["request_id"])
        if not r or r.incident_id != i.id:
            fail("NOT_FOUND", "Closure request not found.", 404)
        if r.status != "pending" or i.state != "review_pending":
            fail("STATE_TRANSITION", "This request is no longer pending.")
        if r.requester_id == u.id:
            fail("INDEPENDENT_REVIEW", "A different supervisor must review your own closure request.", 403)
        if a["approve"]:
            if i.disputed:
                fail("CONFLICTING_INFORMATION", "Clarify conflicting reports before approval.")
            if not i.owner_id or not i.owner_accepted:
                fail("MISSING_OWNER", "An accepted responsible owner is required.")
            if db.scalar(
                select(TemporaryControl).where(
                    TemporaryControl.incident_id == i.id, TemporaryControl.state == "active"
                )
            ):
                fail("ACTIVE_CONTROL", "Review and retire every temporary measure before final closure.")
        r.status = "approved" if a["approve"] else "rejected"
        r.reason = a["reason"]
        r.reviewer_id = u.id
        i.state = "closed" if a["approve"] else "open"
    else:
        fail("UNKNOWN_TOOL", "Unsupported operation.", 404)
    i.updated_at = now()
    db.flush()
    audit(
        db,
        u,
        name,
        i.id,
        before=before,
        after={
            **row(i),
            **{
                k: v
                for k, v in a.items()
                if k not in ("incident_id", "expected_version") and not hasattr(v, "tzinfo")
            },
        },
    )
    return details(db, i)
