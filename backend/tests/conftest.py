"""Shared pytest fixtures and env loading for AgentForge Quest tests."""
import os
from pathlib import Path

# Load .env files (frontend has REACT_APP_BACKEND_URL, backend has UNLOCK_ALL)
def _load_env_file(path: Path):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

_load_env_file(Path("/app/frontend/.env"))
_load_env_file(Path("/app/backend/.env"))
