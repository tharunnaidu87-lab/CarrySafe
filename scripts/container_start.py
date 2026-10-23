import os
import subprocess
import sys

port = os.environ.get("PORT", "8000")
os.environ["MCP_URL"] = "http://127.0.0.1:" + port + "/mcp"
subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)
os.execv(
    sys.executable,
    [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        port,
    ],
)
