from datetime import datetime, timedelta

from zero.outlook.client import Mail, Event
from zero.outlook.filters import important_mails, meetings_from


def _mail(subject="", sender="", body=""):
    return Mail(subject=subject, sender=sender, received=datetime.now(), body_preview=body)


def test_important_by_keyword():
    mails = [_mail(subject="Toplantı yarın"), _mail(subject="kedi videosu")]
    kept = important_mails(mails)
    assert [m.subject for m in kept] == ["Toplantı yarın"]


def test_important_by_sender():
    mails = [_mail(subject="selam", sender="patron@firma.com")]
    kept = important_mails(mails, senders=["patron@firma.com"])
    assert len(kept) == 1


def test_meetings_from_calendar():
    now = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0)
    events = [Event("Sprint", now, now + timedelta(hours=1), "")]
    meetings = meetings_from([], events)
    assert len(meetings) == 1
    assert meetings[0].title == "Sprint"
    assert meetings[0].source == "takvim"


def test_meeting_time_parsed_from_mail():
    m = _mail(subject="plan", body="yarın değil bugün saat 14:00 toplantı var")
    meetings = meetings_from([m], [])
    assert len(meetings) == 1
    assert meetings[0].start.hour == 14
    assert meetings[0].start.minute == 0
    assert meetings[0].source == "mail"


def test_unparseable_mail_skipped():
    m = _mail(subject="merhaba", body="nasılsın bugün")
    assert meetings_from([m], []) == []
