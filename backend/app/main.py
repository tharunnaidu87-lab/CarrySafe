from contextlib import asynccontextmanager
from collections import defaultdict, deque
from time import monotonic
import logging
import asyncio
from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.staticfiles import StaticFiles
from sqlalchemy import text, delete
from pydantic import Field
from .config import settings
from .db import Session, engine
from .auth import login, authenticate, digest
from .models import LoginSession
from .schemas import Strict, READS, MODELS
from .service import execute, RuleError, row
from .mcp_server import server, mcp_app, MCPAuthentication, DESCRIPTIONS
from . import mcp_client, agent

log = logging.getLogger("carrysafe")


@asynccontextmanager
async def lifespan(app):
    if settings.environment == "production" and not settings.database_url.startswith(
        ("postgresql", "postgres://")
    ):
        raise RuntimeError("Production requires persistent PostgreSQL.")
    async with server.session_manager.run():
        yield


app = FastAPI(title="CarrySafe", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization", "X-CarrySafe-Intent"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts.split(","))


@app.exception_handler(RuleError)
async def rule_error(request, e):
    return JSONResponse({"rule": e.rule, "detail": e.message}, status_code=e.status)


buckets = defaultdict(deque)


@app.middleware("http")
async def boundaries(request, call_next):
    origin = request.headers.get("origin")
    if origin and origin not in settings.allowed_origins.split(","):
        return JSONResponse({"detail": "Origin not allowed"}, status_code=403)
    if (
        request.url.path.startswith("/api")
        and request.method == "POST"
        and not request.headers.get("authorization")
        and request.headers.get("x-carrysafe-intent") != "interactive"
    ):
        return JSONResponse({"detail": "Interactive request header required"}, status_code=403)
    if request.url.path.startswith(("/api", "/mcp")):
        key = (
            request.client.host if request.client else "unknown",
            "login" if request.url.path == "/api/login" else "api",
        )
        t = monotonic()
        bucket = buckets[key]
        while bucket and t - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= (15 if key[1] == "login" else 240):
            return JSONResponse({"detail": "Too many requests; retry shortly"}, status_code=429)
        bucket.append(t)
        if len(buckets) > 10000:
            for k in list(buckets):
                if not buckets[k] or t - buckets[k][-1] > 60:
                    del buckets[k]
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'"
    )
    if request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-store"
    return response


def token(request):
    a = request.headers.get("authorization", "")
    return a[7:] if a.startswith("Bearer ") else request.cookies.get("carrysafe_session", "")


def current(request: Request):
    u = authenticate(token(request))
    if not u:
        raise HTTPException(401, "Sign in required")
    return u


class Login(Strict):
    email: str = Field(max_length=180)
    password: str = Field(min_length=1, max_length=200)


@app.post("/api/login")
def sign_in(body: Login):
    t = login(body.email, body.password)
    if not t:
        raise HTTPException(401, "Invalid email or password")
    response = JSONResponse({"user": row(authenticate(t))})
    response.set_cookie(
        "carrysafe_session",
        t,
        httponly=True,
        secure=settings.environment == "production",
        samesite="strict",
        max_age=28800,
        path="/",
    )
    return response


@app.post("/api/logout")
def sign_out(request: Request, u=Depends(current)):
    with Session.begin() as db:
        db.execute(delete(LoginSession).where(LoginSession.token_hash == digest(token(request))))
    r = JSONResponse({"ok": True})
    r.delete_cookie("carrysafe_session")
    return r


@app.get("/api/me")
def me(u=Depends(current)):
    return {
        "user": row(u),
        "ai_enabled": agent.enabled(),
        "timezone": settings.timezone,
        "mode": settings.environment,
    }


@app.get("/api/health")
def health():
    try:
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        return JSONResponse({"status": "unavailable"}, status_code=503)


@app.get("/api/tools")
def tools(u=Depends(current)):
    return {
        name: {
            "schema": model.model_json_schema(),
            "write": name not in READS,
            "description": DESCRIPTIONS[name],
        }
        for name, model in MODELS.items()
    }


@app.get("/api/data/{name}")
def data(name: str, query: str = "", incident_id: str = "", state: str | None = None, u=Depends(current)):
    if name not in READS:
        raise HTTPException(404, "Read operation not found")
    args = (
        {"incident_id": incident_id}
        if name in ("get_incident", "get_incident_history")
        else {"query": query, "state": state}
        if name in ("list_open_incidents", "search_reference_incidents")
        else {}
    )
    return execute(u, name, args)


class Operation(Strict):
    payload: dict
    request_id: str = Field(min_length=1, max_length=100)
    confirmed: bool = False


@app.post("/api/operations/{name}")
async def operation(name: str, body: Operation, request: Request, u=Depends(current)):
    if name not in READS and not body.confirmed:
        raise HTTPException(409, "Explicit confirmation is required")
    result = await mcp_client.invoke(token(request), name, body.payload, body.request_id)
    if result["is_error"]:
        raise HTTPException(409, result["text"])
    return {**(result["data"] or {}), "_mcp": result}


@app.get("/api/mcp/tools")
async def mcp_tools(request: Request, u=Depends(current)):
    return await mcp_client.discover(token(request))


class Shortcut(Strict):
    command: str
    incident_id: str | None = None


@app.post("/api/assistant/shortcut")
async def shortcut(body: Shortcut, request: Request, u=Depends(current)):
    allowed = {
        "briefing": ["list_open_incidents", "list_overdue_controls", "get_shift_handover"],
        "integrity": ["get_integrity_flags"],
        "incident": ["get_incident", "get_incident_history"],
    }
    if body.command not in allowed:
        raise HTTPException(422, "Unknown shortcut")
    trace = []
    for name in allowed[body.command]:
        args = {"incident_id": body.incident_id} if body.command == "incident" else {}
        trace.append(await mcp_client.invoke(token(request), name, args))
    failed = any(x["is_error"] for x in trace)
    return {
        "answer": "Some records could not be retrieved; inspect the tool results."
        if failed
        else "Retrieved current records through MCP. Review the database facts below. Acknowledging receipt does not resolve any incident.",
        "trace": trace,
        "mode": "manual_mcp",
    }


class Chat(Strict):
    conversation_id: str | None = None
    message: str = Field(min_length=1, max_length=4000)


@app.post("/api/assistant/chat")
async def chat(body: Chat, request: Request, u=Depends(current)):
    try:
        async with asyncio.timeout(90):
            return await agent.chat(u, token(request), body.conversation_id, body.message)
    except TimeoutError:
        raise HTTPException(504, "Assistant timed out. Inspect pending proposals before retrying.") from None


@app.get("/api/conversations/{id}")
def get_conversation(id: str, u=Depends(current)):
    return agent.conversation(u, id)


class Confirm(Strict):
    conversation_id: str
    proposal_id: str
    approve: bool


@app.post("/api/assistant/confirm")
async def confirm(body: Confirm, request: Request, u=Depends(current)):
    return await agent.confirm(u, token(request), body.conversation_id, body.proposal_id, body.approve)


app.mount("/mcp", MCPAuthentication(mcp_app))
static = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if static.exists():
    app.mount("/assets", StaticFiles(directory=static / "assets"), name="assets")

    @app.get("/{path:path}")
    def frontend(path: str):
        if path.startswith(("api/", "mcp/")):
            raise HTTPException(404)
        return FileResponse(static / "index.html")
