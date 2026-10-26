"""Günlük plan veri modeli."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date as _date, time


@dataclass
class PlanItem:
    time: time | None
    text: str
    source: str  # "kullanıcı" | "mail" | "takvim"


@dataclass
class DayPlan:
    date: _date
    items: list[PlanItem] = field(default_factory=list)

    def add(self, item: PlanItem) -> None:
        self.items.append(item)
        # Zamanlı olanlar saate göre önde; zamansızlar en sonda.
        self.items.sort(key=lambda i: (i.time is None, i.time or time(0, 0)))
