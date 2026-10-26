"""Plan ayrıştırma: serbest metin (brain) + form; takvim/mail toplantılarını birleştirme."""

from __future__ import annotations

import json
from datetime import date as _date, time

from zero.planner.model import DayPlan, PlanItem

CLARIFY_TEXT = "Planını tam anlayamadım, biraz daha açar mısın?"

_PROMPT = (
    "Kullanıcının gün planını AŞAĞIDAKİ kesin JSON biçiminde çıkar: bir liste, "
    'her öğe {"time": "SS:DD" veya null, "text": "iş"} . Sadece JSON yaz, başka '
    "hiçbir şey ekleme."
)


def _parse_time(value) -> time | None:
    if not value or not isinstance(value, str):
        return None
    try:
        h, m = value.split(":")
        h, m = int(h), int(m)
    except (ValueError, AttributeError):
        return None
    if 0 <= h <= 23 and 0 <= m <= 59:
        return time(h, m)
    return None


def parse_free_text(brain, text: str, day: _date) -> list[PlanItem]:
    raw = brain.chat(
        [{"role": "system", "content": _PROMPT}, {"role": "user", "content": text}]
    ).strip()
    try:
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        return [PlanItem(None, CLARIFY_TEXT, "kullanıcı")]

    items: list[PlanItem] = []
    for entry in data:
        if not isinstance(entry, dict) or "text" not in entry:
            continue
        items.append(PlanItem(_parse_time(entry.get("time")), str(entry["text"]), "kullanıcı"))
    if not items:
        return [PlanItem(None, CLARIFY_TEXT, "kullanıcı")]
    return items


def from_form(entries: list[tuple[str, str]]) -> list[PlanItem]:
    return [PlanItem(_parse_time(t), text, "kullanıcı") for (t, text) in entries]


def merge_meetings(plan: DayPlan, meetings) -> DayPlan:
    existing = {(i.time, i.text) for i in plan.items}
    for m in meetings:
        t = m.start.time()
        key = (t, m.title)
        if key in existing:
            continue
        plan.add(PlanItem(t, m.title, m.source))
        existing.add(key)
    return plan
