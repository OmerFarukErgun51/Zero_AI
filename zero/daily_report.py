"""Gün sonu raporu: uygulama süreleri + planı birleştiren düzenlenebilir form."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date as _date

from zero.planner.model import DayPlan


@dataclass
class ReportForm:
    date: _date
    app_minutes: dict
    done_items: list
    fields: dict = field(default_factory=dict)


def per_app_durations(samples, sample_interval_s: int) -> dict:
    counts = Counter(s.app for s in samples)
    return {app: n * sample_interval_s / 60.0 for app, n in counts.items()}


def build_report(
    store, profile: str, day: _date, plan: DayPlan, sample_interval_s: int, brain=None
) -> ReportForm:
    samples = store.activity_for_day(profile, day)
    app_minutes = per_app_durations(samples, sample_interval_s)
    done_items = [item.text for item in plan.items]

    yaptiklarim = ""
    if brain is not None and (app_minutes or done_items):
        ozet_girdi = (
            f"Uygulama süreleri: {app_minutes}\nPlan maddeleri: {done_items}"
        )
        yaptiklarim = brain.chat(
            [
                {
                    "role": "system",
                    "content": "Aşağıdaki gün verisinden ZeRo'nun sakin üslubuyla "
                    "'bugün neler yaptın' özetini kısa yaz.",
                },
                {"role": "user", "content": ozet_girdi},
            ]
        ).strip()

    fields = {"yaptıklarım": yaptiklarim, "notlar": "", "yarına": ""}
    return ReportForm(date=day, app_minutes=app_minutes, done_items=done_items, fields=fields)
