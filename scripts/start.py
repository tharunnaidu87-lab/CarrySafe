from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
python = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
if not python.exists():
    raise SystemExit("Run python scripts/setup.py first.")
subprocess.run(
    [
        str(python),
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ],
    cwd=ROOT / "backend",
    check=True,
)
