from __future__ import annotations

import sys
from pathlib import Path


def project_root() -> Path:
    """Return the application root for source and future bundled runs."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
