from __future__ import annotations

from datetime import datetime


def current_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def current_date() -> str:
    return datetime.now().date().isoformat()


def current_time() -> str:
    return datetime.now().time().isoformat(timespec="seconds")
