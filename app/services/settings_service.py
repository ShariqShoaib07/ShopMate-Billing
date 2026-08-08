from __future__ import annotations

from pathlib import Path

from app.database.repositories.settings_repository import SettingsRepository
from app.models.shop_settings import ShopSettings


class ShopSettingsValidationError(ValueError):
    """Raised when shop settings cannot be saved."""


class SettingsService:
    def __init__(self, database_path: Path | None = None) -> None:
        self.repository = SettingsRepository(database_path)

    def get_shop_settings(self) -> ShopSettings | None:
        return self.repository.get_shop_settings()

    def save_shop_settings(
        self,
        shop_name: str,
        address: str,
        phone_1: str,
        phone_2: str,
    ) -> ShopSettings:
        clean_shop_name = self._validate_required(shop_name, "Shop name")
        clean_address = self._validate_required(address, "Address")
        clean_phone_1 = self._validate_required(phone_1, "Phone 1")
        clean_phone_2 = self._validate_required(phone_2, "Phone 2")

        existing = self.repository.get_shop_settings()
        settings = ShopSettings(
            id=existing.id if existing is not None else None,
            shop_name=clean_shop_name,
            address=clean_address,
            phone_1=clean_phone_1,
            phone_2=clean_phone_2,
            created_at=existing.created_at if existing is not None else None,
            updated_at=existing.updated_at if existing is not None else None,
        )
        return self.repository.save_shop_settings(settings)

    @staticmethod
    def _validate_required(value: str, field_name: str) -> str:
        clean_value = value.strip()
        if not clean_value:
            raise ShopSettingsValidationError(f"{field_name} is required.")
        return clean_value