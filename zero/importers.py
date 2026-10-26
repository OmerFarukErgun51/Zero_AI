"""Dışa aktarılmış sohbet/dosya okuma ve özetleme (WhatsApp .txt, kaydedilmiş mail)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# "12.10.2026 14:03 - Ömer: mesaj"
_WA_LINE = re.compile(r"^(\d{1,2}\.\d{1,2}\.\d{2,4})\s+(\d{1,2}:\d{2})\s+-\s+([^:]+):\s?(.*)$")


@dataclass
class ChatLine:
    ts: datetime | None
    sender: str
    text: str


def _parse_ts(d: str, t: str) -> datetime | None:
    for fmt in ("%d.%m.%Y %H:%M", "%d.%m.%y %H:%M"):
        try:
            return datetime.strptime(f"{d} {t}", fmt)
        except ValueError:
            continue
    return None


def read_whatsapp_export(path: Path) -> list[ChatLine]:
    lines: list[ChatLine] = []
    for raw in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        m = _WA_LINE.match(raw)
        if m:
            d, t, sender, text = m.groups()
            lines.append(ChatLine(_parse_ts(d, t), sender.strip(), text))
        elif lines:
            # Başlıksız satır → önceki mesajın devamı
            lines[-1].text += "\n" + raw
    return lines


def read_text_file(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def summarize(brain, content: str, instruction: str = "") -> str:
    ek = f" {instruction}" if instruction else ""
    messages = [
        {
            "role": "system",
            "content": "Aşağıdaki içeriği Türkçe, kısa ve öz biçimde özetle." + ek,
        },
        {"role": "user", "content": content},
    ]
    return brain.chat(messages).strip()
