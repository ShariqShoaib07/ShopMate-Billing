from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShopSettings:
    id: int | None
    shop_name: str
    address: str
    phone_1: str
    phone_2: str
    created_at: str | None = None
    updated_at: str | None = None
