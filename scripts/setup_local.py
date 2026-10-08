"""Portable local setup, from the project root. Requires Python 3.12 and Node 20.19+/22.12+.
Windows: py -3.12 scripts/setup_local.py
Linux/macOS: python3.12 scripts/setup_local.py
No model, demo jobs, or default accounts are installed.
"""

import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]


def run(command, cwd):
    print("+ " + " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), cwd=cwd, check=True)


def main():
    if sys.version_info[:2] != (3, 12):
        raise SystemExit("Use Python 3.12: Windows: py -3.12 scripts/setup_local.py")
    node = shutil.which("node")
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not node or not npm:
        raise SystemExit("Install Node.js 20.19+ or 22.12+ LTS, then retry.")
    version = (
        subprocess.check_output([node, "--version"], text=True).strip().lstrip("v")
    )
    major, minor, *_ = map(int, version.split("."))
    if not (
        (major == 20 and minor >= 19) or (major == 22 and minor >= 12) or major > 22
    ):
        raise SystemExit("Node version is too old.")
    backend = ROOT / "backend"
    frontend = ROOT / "frontend"
    python = (
        backend / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    )
    if not python.exists():
        venv.EnvBuilder(with_pip=True).create(backend / ".venv")
    version = subprocess.check_output(
        [
            str(python),
            "-c",
            "import sys; print('.'.join(map(str,sys.version_info[:2])))",
        ],
        text=True,
    ).strip()
    if version != "3.12":
        raise SystemExit(
            "Rename/remove backend/.venv created with another Python version, then retry."
        )
    if subprocess.run(
        [str(python), "-m", "pip", "--version"], capture_output=True
    ).returncode:
        run([python, "-m", "ensurepip", "--upgrade"], backend)
    run(
        [python, "-m", "pip", "install", "--require-hashes", "-r", "requirements.lock"],
        backend,
    )
    run([python, "-m", "pip", "check"], backend)
    config = backend / ".env"
    if not config.exists():
        content = (
            (backend / ".env.example")
            .read_text()
            .replace(
                "REPLACE_WITH_RANDOM_SECRET_OR_USE_BOOTSTRAP", secrets.token_hex(48)
            )
        )
        fd = os.open(config, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write(content)
        print(
            "Created backend/.env with a random JWT secret; it will be preserved on reruns."
        )
    else:
        print("Keeping existing .env and database. Back up data before migrations.")
    run([python, "-m", "alembic", "upgrade", "head"], backend)
    run([npm, "ci"], frontend)
    run([npm, "run", "build"], frontend)
    print(
        "\nSetup complete. Add your own ADZUNA_APP_ID and ADZUNA_API_KEY to backend/.env.\n"
        "Start API and web in separate terminals: python scripts/run_local.py api / web\n"
        "Then open http://localhost:5173. No Gemini/local-model server is needed.\n"
        "Missing Adzuna credentials are shown as a configuration error, not as fake jobs."
    )


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(
            f"Setup stopped because the command above failed (exit {error.returncode})."
        ) from error
