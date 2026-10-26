"""Önemli mail süzme ve toplantı çıkarımı (mail + takvim)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, time

from zero.outlook.client import Event, Mail

_DEFAULT_KEYWORDS = ("toplantı", "acil", "son tarih", "deadline", "randevu")


@dataclass
class Meeting:
    title: str
    start: datetime
    source: str  # "mail" | "takvim"


def important_mails(
    mails: list[Mail], senders: list[str] = (), keywords: list[str] = ()
) -> list[Mail]:
    kws = [k.casefold() for k in (keywords or _DEFAULT_KEYWORDS)]
    sender_set = {s.casefold() for s in senders}
    out: list[Mail] = []
    for m in mails:
        hay = f"{m.subject} {m.body_preview}".casefold()
        if m.sender.casefold() in sender_set or any(k in hay for k in kws):
            out.append(m)
    return out


def _extract_time(text: str) -> time | None:
    m = re.search(r"\b(\d{1,2}):(\d{2})\b", text)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
    else:
        m = re.search(r"saat\s+(\d{1,2})", text, re.IGNORECASE)
        if not m:
            m = re.search(r"\b(\d{1,2})['’]?\s*(?:de|da|te|ta)\b", text, re.IGNORECASE)
        if not m:
            return None
        h, mi = int(m.group(1)), 0
    if 0 <= h <= 23 and 0 <= mi <= 59:
        return time(h, mi)
    return None


def meetings_from(mails: list[Mail], events: list[Event]) -> list[Meeting]:
    out: list[Meeting] = []
    for e in events:
        out.append(Meeting(title=e.subject, start=e.start, source="takvim"))

    today = datetime.now().date()
    for m in mails:
        t = _extract_time(f"{m.subject} {m.body_preview}")
        if t is None:
            continue
        out.append(Meeting(title=m.subject, start=datetime.combine(today, t), source="mail"))
    return out
