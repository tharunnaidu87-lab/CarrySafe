"""Portable local setup. Run with Python 3.12 from the repository root."""

from pathlib import Path
import getpass
import os
import shutil
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]


def run(args, cwd=ROOT, env=None):
    subprocess.run([str(x) for x in args], cwd=cwd, env=env, check=True)


def main():
    if sys.version_info[:2] != (3, 12):
        raise SystemExit("Use Python 3.12: py -3.12 scripts/setup.py")
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        raise SystemExit("Install Node.js 22 LTS or newer, then reopen your terminal.")
    python = (
        ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    )
    if not python.exists():
        venv.create(ROOT / ".venv", with_pip=True)
    run([python, "-m", "pip", "install", "-r", "backend/requirements.lock"])
    run([npm, "ci"], ROOT / "frontend")
    run([npm, "run", "build"], ROOT / "frontend")
    run([python, "-m", "alembic", "upgrade", "head"], ROOT / "backend")
    # Existing data is never reset by setup.
    password = getpass.getpass(
        "Choose a LOCAL DEMO password (12+ characters; existing accounts unchanged): "
    )
    if len(password) < 12:
        raise SystemExit("Password too short. Re-run setup.")
    run(
        [python, "-m", "app.seed"],
        ROOT / "backend",
        {**os.environ, "DEMO_PASSWORD": password},
    )
    print(
        "Setup complete. Run: python scripts/start.py\nOpen http://localhost:8000\nDemo emails: alex@demo.carrysafe.test, sam@demo.carrysafe.test, jordan@demo.carrysafe.test"
    )


if __name__ == "__main__":
    main()
