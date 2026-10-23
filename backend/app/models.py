from datetime import datetime
from sqlalchemy import String, ForeignKey, JSON, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base, now


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(180))
    synthetic: Mapped[bool] = mapped_column(default=False)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('worker','supervisor')"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(180), unique=True)
    role: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(String(255))


class LoginSession(Base):
    __tablename__ = "sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Location(Base):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))


class Shift(Base):
    __tablename__ = "shifts"
    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (CheckConstraint("state IN ('open','review_pending','closed')"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), index=True)
    shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id"))
    description: Mapped[str] = mapped_column(String(4000))
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    owner_accepted: Mapped[bool] = mapped_column(default=False)
    state: Mapped[str] = mapped_column(String(30), default="open", index=True)
    disputed: Mapped[bool] = mapped_column(default=False)
    version: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __mapper_args__ = {"version_id_col": version}


class TemporaryControl(Base):
    __tablename__ = "controls"
    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"), index=True)
    description: Mapped[str] = mapped_column(String(2000))
    responsible_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    review_due: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    state: Mapped[str] = mapped_column(String(30), default="active")
    last_reviewed: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    result: Mapped[str | None] = mapped_column(String(30), nullable=True)


class ControlReview(Base):
    __tablename__ = "control_reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    control_id: Mapped[int] = mapped_column(ForeignKey("controls.id"))
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    observation: Mapped[str] = mapped_column(String(2000))
    result: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Handover(Base):
    __tablename__ = "handovers"
    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    outgoing_id: Mapped[int] = mapped_column(ForeignKey("shifts.id"))
    incoming_id: Mapped[int] = mapped_column(ForeignKey("shifts.id"))
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    incident_ids: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Acknowledgment(Base):
    __tablename__ = "acknowledgments"
    __table_args__ = (UniqueConstraint("handover_id", "user_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    handover_id: Mapped[int] = mapped_column(ForeignKey("handovers.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class ClosureRequest(Base):
    __tablename__ = "closure_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"), index=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    evidence: Mapped[str] = mapped_column(String(2000))
    status: Mapped[str] = mapped_column(String(30), default="pending")
    reason: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[str] = mapped_column(String(60), index=True)
    before: Mapped[dict] = mapped_column(JSON, default=dict)
    after: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Receipt(Base):
    __tablename__ = "receipts"
    key: Mapped[str] = mapped_column(String(180), primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64))
    result: Mapped[dict] = mapped_column(JSON)


class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    messages: Mapped[list] = mapped_column(JSON, default=list)
    pending: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    version: Mapped[int] = mapped_column(default=1)
    __mapper_args__ = {"version_id_col": version}


class ReferenceIncident(Base):
    __tablename__ = "reference_incidents"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(String(4000))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
