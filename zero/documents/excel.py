"""Excel (.xlsx) üretimi — openpyxl ile, tamamen offline."""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font


def make_excel(path: Path, title: str, headers: list[str], rows: list[list]) -> Path:
    path = Path(path)
    wb = Workbook()
    ws = wb.active
    ws.title = title[:31] or "Sayfa1"

    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for row in rows:
        ws.append(list(row))

    wb.save(path)
    return path
