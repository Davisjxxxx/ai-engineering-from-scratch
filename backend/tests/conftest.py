"""Shared pytest fixtures and env loading for AgentForge Quest tests."""
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

def _load_env_file(path: Path):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

_load_env_file(BACKEND_DIR / ".env")
_load_env_file(BACKEND_DIR.parent / "frontend" / ".env")
