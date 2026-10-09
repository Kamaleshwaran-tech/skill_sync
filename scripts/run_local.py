"""Launch one local service in the correct working directory.

Two terminals: python scripts/run_local.py api / web.
web verifies/rebuilds the frontend before serving it, with /api proxying to the local API.
For editing: use 'web-dev' (higher RAM consumption).
"""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("service", choices=["api", "web", "web-dev"])
parser.add_argument("--port", type=int, help="Override the default port (8000 / 5173)")
args = parser.parse_args()
python = (
    ROOT
    / "backend"
    / ".venv"
    / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
)
if not python.exists():
    raise SystemExit("Run scripts/setup_local.py with Python 3.12 first.")
env = os.environ.copy()
if args.service == "api":
    cwd = ROOT / "backend"
    command = [
        str(python),
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(args.port or 8000),
    ]
else:
    cwd = ROOT / "frontend"
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        raise SystemExit("npm was not found. Install Node.js first.")
    if not (cwd / "node_modules/vite/package.json").exists():
        raise SystemExit(
            "Frontend dependencies missing. Run setup_local.py or 'npm ci' in frontend first."
        )
    print(f"Serving frontend source from: {cwd}", flush=True)
    print(
        "Expected footer: Interface: screenshot-fixes-v1. Preview rebuilds stale source automatically.",
        flush=True,
    )
    command = [
        npm,
        "run",
        "dev" if args.service == "web-dev" else "preview",
        "--",
        "--host",
        "0.0.0.0",
        "--port",
        str(args.port or 5173),
        "--strictPort",
    ]
try:
    raise SystemExit(subprocess.call(command, cwd=cwd, env=env))
except KeyboardInterrupt:
    # The terminal/process manager sends SIGINT to the child as well.
    sys.exit(130)
