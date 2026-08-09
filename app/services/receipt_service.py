from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from app.database.repositories.settings_repository import SettingsRepository
from app.models.invoice import Invoice
from app.models.receipt import Receipt, ReceiptLineItem
from app.models.shop_settings import ShopSettings
from app.utils.number_words import rupees_in_words


@dataclass(frozen=True)
class ReceiptRenderData:
    receipt: Receipt
    html: str


class ReceiptService:
    def __init__(self, database_path: Path | None = None) -> None:
        self.settings_repository = SettingsRepository(database_path)

    def build_receipt(self, invoice: Invoice, shop_settings: ShopSettings | None = None) -> Receipt:
        settings = shop_settings or self.settings_repository.get_shop_settings()
        if settings is None:
            raise RuntimeError("Shop settings are required to build a receipt.")

        return Receipt(
            shop_name=settings.shop_name,
            address=settings.address,
            phone_1=settings.phone_1,
            phone_2=settings.phone_2,
            invoice_number=invoice.invoice_number,
            invoice_date=self._format_date(invoice.invoice_date),
            invoice_time=self._format_time(invoice.invoice_time),
            customer_name=invoice.customer_name,
            customer_mobile=invoice.customer_mobile,
            items=[
                ReceiptLineItem(
                    product_name=item.product_name,
                    quantity=item.quantity,
                    rate=item.rate,
                    amount=item.amount,
                )
                for item in invoice.items
            ],
            total=Decimal(str(invoice.total)),
            total_in_words=rupees_in_words(invoice.total),
        )

    def render_html(self, receipt: Receipt) -> str:
        rows = "".join(
            f"""
            <tr>
                <td class=\"name\">{self._escape(item.product_name)}</td>
                <td class=\"qty\">{item.quantity}</td>
                <td class=\"rate\">{self._format_amount(item.rate)}</td>
                <td class=\"amount\">{self._format_amount(item.amount)}</td>
            </tr>
            """
            for item in receipt.items
        ) or """
            <tr>
                <td class=\"name empty\" colspan=\"4\">No items</td>
            </tr>
        """

        customer_name = self._optional_text(receipt.customer_name)
        customer_mobile = self._optional_text(receipt.customer_mobile)

        return f"""
<html>
<head>
<style>
body {{
    margin: 0;
    padding: 0;
    font-family: "Segoe UI", Arial, sans-serif;
    color: #202124;
    background: #ffffff;
}}
.receipt {{
    width: 320px;
    margin: 0 auto;
    padding: 16px 14px 18px 14px;
    font-size: 12px;
    line-height: 1.35;
}}
.center {{ text-align: center; }}
.shop-name {{
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 4px;
}}
.muted {{ color: #555555; }}
.rule {{ border-top: 1px solid #202124; margin: 10px 0; }}
.meta {{ margin-bottom: 10px; }}
.meta div {{ margin: 1px 0; }}
table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
th, td {{ padding: 3px 0; vertical-align: top; }}
th {{ border-bottom: 1px solid #202124; font-weight: 700; }}
td, th {{ font-size: 11px; }}
.name {{ width: 48%; text-align: left; word-wrap: break-word; }}
.qty {{ width: 12%; text-align: center; }}
.rate {{ width: 20%; text-align: right; }}
.amount {{ width: 20%; text-align: right; }}
.total-row {{ margin-top: 10px; display: flex; justify-content: space-between; font-weight: 700; }}
.words {{ margin-top: 10px; font-style: italic; }}
.thanks {{ margin-top: 14px; text-align: center; font-weight: 700; }}
</style>
</head>
<body>
<div class=\"receipt\">
    <div class=\"center\">
        <div class=\"shop-name\">{self._escape(receipt.shop_name)}</div>
        <div class=\"muted\">{self._escape(receipt.address).replace(chr(10), '<br>')}</div>
        <div class=\"muted\">{self._escape(receipt.phone_1)} | {self._escape(receipt.phone_2)}</div>
    </div>

    <div class=\"rule\"></div>

    <div class=\"meta\">
        <div><strong>Invoice:</strong> #{self._escape(receipt.invoice_number)}</div>
        <div><strong>Date:</strong> {self._escape(receipt.invoice_date)}</div>
        <div><strong>Time:</strong> {self._escape(receipt.invoice_time)}</div>
        <div><strong>Customer:</strong> {customer_name}</div>
        <div><strong>Mobile:</strong> {customer_mobile}</div>
    </div>

    <div class=\"rule\"></div>

    <table>
        <thead>
            <tr>
                <th class=\"name\">Item</th>
                <th class=\"qty\">Qty</th>
                <th class=\"rate\">Rate</th>
                <th class=\"amount\">Amount</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>

    <div class=\"rule\"></div>

    <div class=\"total-row\">
        <div>TOTAL:</div>
        <div>{self._format_amount(receipt.total)}</div>
    </div>

    <div class=\"words\">{self._escape(receipt.total_in_words)}</div>

    <div class=\"rule\"></div>

    <div class=\"thanks\">{self._escape(receipt.thank_you_message)}</div>
</div>
</body>
</html>
"""

    @staticmethod
    def _format_amount(value: Decimal) -> str:
        return f"Rs. {Decimal(str(value)):,.0f}"

    @staticmethod
    def _format_date(value: str) -> str:
        parts = value.split("-")
        if len(parts) == 3:
            year, month, day = parts
            return f"{day}-{month}-{year}"
        return value

    @staticmethod
    def _format_time(value: str) -> str:
        return value[:5] if len(value) >= 5 else value

    @staticmethod
    def _optional_text(value: str | None) -> str:
        return value.strip() if value and value.strip() else "-"

    @staticmethod
    def _escape(value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )