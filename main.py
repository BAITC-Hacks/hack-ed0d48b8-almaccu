from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file(ROOT / ".env")

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

CATALOG_PATH = ROOT / os.getenv("CATALOG_PATH", "data/catalog.json")
TERMS_PATH = ROOT / "data" / "purchase_terms.json"

EKT_API_BASE = os.getenv("EKT_API_BASE", "https://ekt.kz/api")
EKT_API_USER = os.getenv("EKT_API_USER", "")
EKT_API_PASSWORD = os.getenv("EKT_API_PASSWORD", "")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-haiku-4-5-20251001")

# Ограничения
MAX_MESSAGE_CHARS = 1000
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_SPEC_ROWS = 200
CONFIRM_TTL_SECONDS = 10 * 60