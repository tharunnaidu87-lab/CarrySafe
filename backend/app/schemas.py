from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, AwareDatetime


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CreateIncident(Strict):
    description: str = Field(min_length=10, max_length=4000)
    location_id: int
    shift_id: int
    owner_id: int | None = None


class Versioned(Strict):
    incident_id: str = Field(max_length=36)
    expected_version: int = Field(ge=1)


class Assign(Versioned):
    owner_id: int


class AddControl(Versioned):
    description: str = Field(min_length=5, max_length=2000)
    responsible_id: int
    review_due: AwareDatetime


class ReviewControl(Versioned):
    control_id: int
    observation: str = Field(min_length=10, max_length=2000)
    result: Literal["effective", "needs_attention", "retired"]
    next_review_due: AwareDatetime | None = None


class Progress(Versioned):
    note: str = Field(min_length=5, max_length=2000)
    condition: Literal["unresolved", "reported_repaired", "disputed", "clarified"]


class RequestClosure(Versioned):
    evidence: str = Field(min_length=10, max_length=2000)


class ReviewClosure(Versioned):
    request_id: int
    approve: bool
    reason: str = Field(min_length=10, max_length=2000)
    verification_reference: str = Field(min_length=10, max_length=2000)


class CreateHandover(Strict):
    outgoing_id: int
    incoming_id: int
    recipient_id: int


class Acknowledge(Strict):
    handover_id: int


class GetIncident(Strict):
    incident_id: str


class Search(Strict):
    state: Literal["open", "review_pending"] | None = None
    query: str = Field(default="", max_length=200)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)


class Empty(Strict):
    pass


MODELS = {
    "create_incident": CreateIncident,
    "assign_incident": Assign,
    "accept_ownership": Versioned,
    "add_temporary_control": AddControl,
    "record_control_review": ReviewControl,
    "record_incident_progress": Progress,
    "request_incident_closure": RequestClosure,
    "review_closure_request": ReviewClosure,
    "create_handover": CreateHandover,
    "acknowledge_handover": Acknowledge,
    "get_incident": GetIncident,
    "get_incident_history": GetIncident,
    "list_open_incidents": Search,
    "search_reference_incidents": Search,
    "list_overdue_controls": Empty,
    "get_shift_handover": Empty,
    "get_integrity_flags": Empty,
    "get_directory": Empty,
    "get_dashboard": Empty,
}
READS = {
    "get_incident",
    "get_incident_history",
    "list_open_incidents",
    "search_reference_incidents",
    "list_overdue_controls",
    "get_shift_handover",
    "get_integrity_flags",
    "get_directory",
    "get_dashboard",
}
