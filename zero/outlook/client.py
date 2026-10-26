"""Klasik Outlook'tan (COM) salt-okunur mail + takvim okuma.

Hiçbir COM hatası çağırana sızmaz; hatalar status() üzerinden görünür.
Kurumsal hesap COM'u engellerse ZeRo çökmez, nazikçe devre dışı kalır."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

_OL_FOLDER_INBOX = 6
_OL_FOLDER_CALENDAR = 9

_DEGRADED_MSG = (
    "Outlook'a şu an ulaşamıyorum. Klasik Outlook açık mı, yoksa şirket "
    "politikası erişimi engelliyor olabilir. Mail/takvim özellikleri şimdilik "
    "devre dışı; gerisi çalışmaya devam ediyor."
)


@dataclass
class Mail:
    subject: str
    sender: str
    received: datetime
    body_preview: str


@dataclass
class Event:
    subject: str
    start: datetime
    end: datetime
    location: str


@dataclass
class OutlookStatus:
    ok: bool
    message: str


def _default_factory():
    import win32com.client  # yalnızca gerçek kullanımda içe aktarılır

    return win32com.client.Dispatch("Outlook.Application")


def _as_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime(value.year, value.month, value.day, value.hour, value.minute)


class OutlookClient:
    def __init__(self, app_factory=None):
        self._factory = app_factory or _default_factory

    def _namespace(self):
        app = self._factory()
        return app.GetNamespace("MAPI")

    def status(self) -> OutlookStatus:
        try:
            self._namespace()
        except Exception:
            return OutlookStatus(False, _DEGRADED_MSG)
        return OutlookStatus(True, "Outlook bağlantısı hazır.")

    def unread_mails(self, limit: int = 20) -> list[Mail]:
        try:
            folder = self._namespace().GetDefaultFolder(_OL_FOLDER_INBOX)
            out: list[Mail] = []
            for item in folder.Items:
                if not getattr(item, "UnRead", False):
                    continue
                body = getattr(item, "Body", "") or ""
                out.append(
                    Mail(
                        subject=item.Subject,
                        sender=getattr(item, "SenderName", ""),
                        received=_as_datetime(item.ReceivedTime),
                        body_preview=body[:200],
                    )
                )
                if len(out) >= limit:
                    break
            return out
        except Exception:
            return []

    def find_item_by_subject(self, subject: str):
        """Konusu eşleşen gelen kutusu öğesini (COM) döndürür; yoksa None.
        COM erişilemezse Exception yükseltir (çağıran yakalar)."""
        folder = self._namespace().GetDefaultFolder(_OL_FOLDER_INBOX)
        for item in folder.Items:
            if getattr(item, "Subject", None) == subject:
                return item
        return None

    def todays_events(self) -> list[Event]:
        try:
            folder = self._namespace().GetDefaultFolder(_OL_FOLDER_CALENDAR)
            today = datetime.now().date()
            out: list[Event] = []
            for item in folder.Items:
                start = _as_datetime(item.Start)
                if start.date() != today:
                    continue
                out.append(
                    Event(
                        subject=item.Subject,
                        start=start,
                        end=_as_datetime(item.End),
                        location=getattr(item, "Location", "") or "",
                    )
                )
            return out
        except Exception:
            return []
