from contextvars import ContextVar
import inspect
from typing import Any
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import JSONResponse
from .auth import authenticate
from .config import settings
from .schemas import MODELS
from .service import execute, RuleError

identity = ContextVar("authenticated_mcp_identity", default=None)
server = MCPServer(
    "CarrySafe",
    version="0.1.0",
    instructions="Workplace recordkeeping only. No physical safety certification. All changes use backend authorization and integrity rules.",
)
DESCRIPTIONS = {
    "create_incident": "Record a confirmed workplace report with a known location and shift. Only supervisors may assign another worker.",
    "get_incident": "Retrieve current incident facts, owner, version, controls and closure requests.",
    "list_open_incidents": "Search unresolved incidents in the authenticated organization.",
    "get_shift_handover": "Retrieve handover snapshots, current case states and recipient acknowledgments.",
    "list_overdue_controls": "List active temporary measures whose review deadlines have passed.",
    "add_temporary_control": "Record a temporary measure and explicit future review deadline.",
    "record_control_review": "Record an observation; supervisors can retire a measure after review.",
    "assign_incident": "Supervisor assigns responsibility; the owner must then accept.",
    "accept_ownership": "Assigned worker explicitly accepts responsibility.",
    "record_incident_progress": "Preserve observations; contradictory structured claims flag disputes.",
    "create_handover": "Carry all unresolved incidents into an incoming shift for a designated recipient.",
    "acknowledge_handover": "Designated recipient acknowledges receipt without resolving any hazard.",
    "request_incident_closure": "Submit evidence for independent supervisor review; this does not close the case.",
    "review_closure_request": "Independent supervisor reviews evidence and verification reference. Approval requires retired controls and no unresolved dispute.",
    "get_incident_history": "Retrieve attributable history including rejected changes.",
    "search_reference_incidents": "Search historical reference descriptions; these are not live workplace incidents.",
    "get_integrity_flags": "Explain overdue reviews, missing ownership, conflicts and missing acknowledgments.",
    "get_directory": "List known users, locations and shifts in this organization. Use before choosing identifiers.",
    "get_dashboard": "Retrieve actual database counts and recent audit activity.",
}


def register(name, model):
    async def run(payload, request_id=None):
        user = identity.get()
        if user is None:
            raise ToolError("AUTHENTICATION: verified identity required")
        try:
            return execute(user, name, payload.model_dump(mode="json"), request_id)
        except RuleError as e:
            raise ToolError(f"{e.rule}: {e.message}") from None

    run.__signature__ = inspect.Signature(
        [
            inspect.Parameter("payload", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=model),
            inspect.Parameter(
                "request_id", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str | None, default=None
            ),
        ],
        return_annotation=dict[str, Any],
    )
    run.__annotations__ = {"payload": model, "request_id": str | None, "return": dict[str, Any]}
    server.add_tool(run, name=name, description=DESCRIPTIONS[name], structured_output=True)


for name, model in MODELS.items():
    register(name, model)

mcp_app = server.streamable_http_app(
    streamable_http_path="/",
    stateless_http=True,
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[h + ":*" for h in settings.allowed_hosts.split(",")]
        + settings.allowed_hosts.split(","),
        allowed_origins=settings.allowed_origins.split(","),
    ),
)


class MCPAuthentication:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        auth = headers.get(b"authorization", b"").decode()
        user = authenticate(auth[7:]) if auth.startswith("Bearer ") else None
        if not user:
            return await JSONResponse({"error": "Authentication required"}, status_code=401)(
                scope, receive, send
            )
        marker = identity.set(user)
        try:
            await self.app(scope, receive, send)
        finally:
            identity.reset(marker)
