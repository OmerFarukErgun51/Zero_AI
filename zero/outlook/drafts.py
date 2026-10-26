"""Yapay zeka destekli cevap taslağı — yalnızca KAYDEDER, asla göndermez."""

from __future__ import annotations

from dataclasses import dataclass

from zero.outlook.client import Mail

_PROMPT = (
    "Aşağıdaki maile Türkçe, kibar ve kısa bir cevap TASLAĞI yaz. Sadece cevabın "
    "gövdesini yaz; selam/imza ekleyebilirsin ama başka açıklama yazma."
)


@dataclass
class DraftResult:
    ok: bool
    message: str


def compose_reply_text(brain, mail: Mail, instruction: str) -> str:
    content = (
        f"Gelen mail konusu: {mail.subject}\n"
        f"Gönderen: {mail.sender}\n"
        f"İçerik: {mail.body_preview}\n\n"
        f"İstediğim: {instruction}"
    )
    messages = [
        {"role": "system", "content": _PROMPT},
        {"role": "user", "content": content},
    ]
    return brain.chat(messages).strip()


def save_draft(outlook, mail: Mail, body: str) -> DraftResult:
    try:
        item = outlook.find_item_by_subject(mail.subject)
        if item is None:
            return DraftResult(False, "İlgili mail bulunamadı; taslak oluşturulamadı.")
        reply = item.Reply()
        existing = getattr(reply, "Body", "") or ""
        reply.Body = f"{body}\n\n{existing}"
        reply.Save()  # SADECE kaydet — asla Send() çağırma
        return DraftResult(True, "Cevap taslağı kaydedildi (gönderilmedi).")
    except Exception:
        return DraftResult(
            False,
            "Outlook'a ulaşamadığım için taslak kaydedilemedi; mail özelliği şu an devre dışı.",
        )
