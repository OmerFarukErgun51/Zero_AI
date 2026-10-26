from datetime import date, datetime, time, timedelta

from zero.outlook.client import Event, Mail, OutlookStatus
from zero.planner.model import PlanItem, DayPlan
from zero.briefing import compose_briefing


class FakeOutlook:
    def __init__(self, ok=True, events=(), mails=()):
        self._ok = ok
        self._events = list(events)
        self._mails = list(mails)

    def status(self):
        return OutlookStatus(self._ok, "" if self._ok else "ulaşılamıyor")

    def todays_events(self):
        return self._events

    def unread_mails(self, limit=20):
        return self._mails


def _plan(items=()):
    p = DayPlan(date=date(2026, 10, 26))
    for it in items:
        p.add(it)
    return p


def test_briefing_includes_meetings_and_plan():
    now = datetime(2026, 10, 26, 15, 0)
    outlook = FakeOutlook(events=[Event("Sprint", now, now + timedelta(hours=1), "")])
    plan = _plan([PlanItem(time(10, 0), "rapor yaz", "kullanıcı")])
    text = compose_briefing(outlook, plan)
    assert "Sprint" in text
    assert "rapor yaz" in text


def test_briefing_mentions_unread_count():
    mails = [
        Mail("Toplantı", "a", datetime.now(), ""),
        Mail("Acil durum", "b", datetime.now(), ""),
        Mail("son tarih yaklaşıyor", "c", datetime.now(), ""),
    ]
    text = compose_briefing(FakeOutlook(mails=mails), _plan())
    assert "3" in text


def test_briefing_when_outlook_degraded():
    plan = _plan([PlanItem(time(9, 0), "spor", "kullanıcı")])
    text = compose_briefing(FakeOutlook(ok=False), plan)
    assert "spor" in text
    assert "mail" in text.lower()


def test_briefing_empty_everything():
    text = compose_briefing(FakeOutlook(ok=False), _plan())
    assert text.strip() != ""
