from __future__ import annotations

import sqlite3
from decimal import Decimal
from pathlib import Path

from app.database.connection import connect, get_connection
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem


class InvoiceRepository:
    def __init__(self, database_path: Path | None = None) -> None:
        self.database_path = database_path

    def add(self, invoice: Invoice) -> int:
        with get_connection(self.database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO invoices (
                    invoice_number,
                    customer_name,
                    customer_mobile,
                    invoice_date,
                    invoice_time,
                    total
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    invoice.invoice_number,
                    invoice.customer_name,
                    invoice.customer_mobile,
                    invoice.invoice_date,
                    invoice.invoice_time,
                    str(invoice.total),
                ),
            )
            invoice_id = int(cursor.lastrowid)

            for item in invoice.items:
                connection.execute(
                    """
                    INSERT INTO invoice_items (
                        invoice_id,
                        product_id,
                        product_shortcut,
                        product_name,
                        quantity,
                        rate,
                        amount
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        invoice_id,
                        item.product_id,
                        item.product_shortcut,
                        item.product_name,
                        item.quantity,
                        str(item.rate),
                        str(item.amount),
                    ),
                )

            return invoice_id

    def save_with_next_number(self, invoice: Invoice) -> Invoice:
        """Save invoice and items atomically with the next sequential number."""
        connection = connect(self.database_path)
        try:
            connection.execute("BEGIN IMMEDIATE")
            next_number = self._next_invoice_number(connection)
            cursor = connection.execute(
                """
                INSERT INTO invoices (
                    invoice_number,
                    customer_name,
                    customer_mobile,
                    invoice_date,
                    invoice_time,
                    total
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    next_number,
                    invoice.customer_name,
                    invoice.customer_mobile,
                    invoice.invoice_date,
                    invoice.invoice_time,
                    str(invoice.total),
                ),
            )
            invoice_id = int(cursor.lastrowid)

            for item in invoice.items:
                connection.execute(
                    """
                    INSERT INTO invoice_items (
                        invoice_id,
                        product_id,
                        product_shortcut,
                        product_name,
                        quantity,
                        rate,
                        amount
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        invoice_id,
                        item.product_id,
                        item.product_shortcut,
                        item.product_name,
                        item.quantity,
                        str(item.rate),
                        str(item.amount),
                    ),
                )

            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        return Invoice(
            id=invoice_id,
            invoice_number=next_number,
            customer_name=invoice.customer_name,
            customer_mobile=invoice.customer_mobile,
            invoice_date=invoice.invoice_date,
            invoice_time=invoice.invoice_time,
            total=invoice.total,
            items=[
                InvoiceItem(
                    id=item.id,
                    invoice_id=invoice_id,
                    product_id=item.product_id,
                    product_shortcut=item.product_shortcut,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    rate=item.rate,
                    amount=item.amount,
                )
                for item in invoice.items
            ],
        )

    def count(self) -> int:
        with get_connection(self.database_path) as connection:
            return int(connection.execute("SELECT COUNT(*) FROM invoices").fetchone()[0])

    def total_sales(self) -> Decimal:
        with get_connection(self.database_path) as connection:
            value = connection.execute("SELECT COALESCE(SUM(total), 0) FROM invoices").fetchone()[0]
        return Decimal(str(value))

    def get_by_number(self, invoice_number: str) -> Invoice | None:
        with get_connection(self.database_path) as connection:
            invoice_row = connection.execute(
                """
                SELECT id, invoice_number, customer_name, customer_mobile,
                       invoice_date, invoice_time, total, created_at
                FROM invoices
                WHERE invoice_number = ?
                """,
                (invoice_number,),
            ).fetchone()
            if invoice_row is None:
                return None
            item_rows = connection.execute(
                """
                SELECT id, invoice_id, product_id, product_shortcut, product_name,
                       quantity, rate, amount
                FROM invoice_items
                WHERE invoice_id = ?
                ORDER BY id
                """,
                (invoice_row["id"],),
            ).fetchall()

        return Invoice(
            id=int(invoice_row["id"]),
            invoice_number=str(invoice_row["invoice_number"]),
            customer_name=invoice_row["customer_name"],
            customer_mobile=invoice_row["customer_mobile"],
            invoice_date=str(invoice_row["invoice_date"]),
            invoice_time=str(invoice_row["invoice_time"]),
            total=Decimal(str(invoice_row["total"])),
            created_at=str(invoice_row["created_at"]),
            items=[self._row_to_item(row) for row in item_rows],
        )

    def search(
        self,
        search_text: str = "",
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[Invoice]:
        clauses: list[str] = []
        params: list[object] = []
        text = search_text.strip()
        if text:
            clauses.append(
                """
                (
                    invoice_number LIKE ?
                    OR LOWER(COALESCE(customer_name, '')) LIKE LOWER(?)
                    OR COALESCE(customer_mobile, '') LIKE ?
                )
                """
            )
            pattern = f"%{text}%"
            params.extend([pattern, pattern, pattern])
        if from_date:
            clauses.append("invoice_date >= ?")
            params.append(from_date)
        if to_date:
            clauses.append("invoice_date <= ?")
            params.append(to_date)

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with get_connection(self.database_path) as connection:
            rows = connection.execute(
                f"""
                SELECT id, invoice_number, customer_name, customer_mobile,
                       invoice_date, invoice_time, total, created_at
                FROM invoices
                {where_sql}
                ORDER BY invoice_date DESC, invoice_time DESC, id DESC
                """,
                tuple(params),
            ).fetchall()

        return [
            Invoice(
                id=int(row["id"]),
                invoice_number=str(row["invoice_number"]),
                customer_name=row["customer_name"],
                customer_mobile=row["customer_mobile"],
                invoice_date=str(row["invoice_date"]),
                invoice_time=str(row["invoice_time"]),
                total=Decimal(str(row["total"])),
                created_at=str(row["created_at"]),
                items=[],
            )
            for row in rows
        ]

    @staticmethod
    def _next_invoice_number(connection: sqlite3.Connection) -> str:
        value = connection.execute(
            "SELECT COALESCE(MAX(CAST(invoice_number AS INTEGER)), 0) + 1 FROM invoices"
        ).fetchone()[0]
        return str(int(value))

    @staticmethod
    def _row_to_item(row: sqlite3.Row) -> InvoiceItem:
        return InvoiceItem(
            id=int(row["id"]),
            invoice_id=int(row["invoice_id"]),
            product_id=row["product_id"],
            product_shortcut=int(row["product_shortcut"]),
            product_name=str(row["product_name"]),
            quantity=int(row["quantity"]),
            rate=Decimal(str(row["rate"])),
            amount=Decimal(str(row["amount"])),
        )
