from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PrintJob:
    title: str
    content: str


class ReceiptPrinter(Protocol):
    def print_receipt(self, job: PrintJob) -> None:
        """Print a receipt job using a concrete printer implementation."""


class PrintService:
    """Printer-agnostic print facade for future receipt printing."""

    def __init__(self, printer: ReceiptPrinter | None = None) -> None:
        self._printer = printer

    def preview_receipt(self, job: PrintJob) -> str:
        return job.content

    def print_receipt(self, job: PrintJob) -> None:
        if self._printer is None:
            raise NotImplementedError(
                "Printer integration will be added after the printer model and paper size are known."
            )
        self._printer.print_receipt(job)
