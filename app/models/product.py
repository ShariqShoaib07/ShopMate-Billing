from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Product:
    id: int | None
    shortcut: int
    name: str
    default_price: Decimal
    active: bool = True
    created_at: str | None = None
    updated_at: str | None = None
