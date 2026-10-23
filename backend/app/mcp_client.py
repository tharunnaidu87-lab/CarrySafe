from contextlib import asynccontextmanager
import httpx2
from mcp.client import ClientSession
from mcp.client.streamable_http import streamable_http_client
from .config import settings
from .service import RuleError


@asynccontextmanager
async def connection(token):
    async with httpx2.AsyncClient(
        headers={"Authorization": "Bearer " + token}, follow_redirects=True, timeout=30, trust_env=False
    ) as http:
        async with streamable_http_client(settings.mcp_url + "/", http_client=http) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=30) as client:
                info = await client.initialize()
                yield client, info


async def _discover(token):
    async with connection(token) as (client, info):
        result = await client.list_tools()
        return {
            "protocol": info.protocol_version,
            "tools": [t.model_dump(by_alias=True) for t in result.tools],
        }


async def _invoke(token, name, payload, request_id=None):
    async with connection(token) as (client, info):
        result = await client.call_tool(name, {"payload": payload, "request_id": request_id})
        return {
            "tool": name,
            "protocol": info.protocol_version,
            "is_error": result.is_error,
            "data": result.structured_content,
            "text": "\n".join(c.text for c in result.content if hasattr(c, "text")),
        }


async def discover(token):
    try:
        return await _discover(token)
    except Exception:
        raise RuleError(
            "MCP_UNAVAILABLE", "MCP connection failed. Check the server and try again.", 503
        ) from None


async def invoke(token, name, payload, request_id=None):
    try:
        return await _invoke(token, name, payload, request_id)
    except Exception:
        return {
            "tool": name,
            "protocol": None,
            "is_error": True,
            "data": None,
            "text": "MCP_UNAVAILABLE: The result could not be confirmed. Retry with the same request ID to avoid duplicate changes.",
        }
