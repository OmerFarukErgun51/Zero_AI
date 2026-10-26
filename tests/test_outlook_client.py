from datetime import datetime, timedelta

from zero.outlook.client import OutlookClient


class FakeItem:
    def __init__(self, subject, sender, received, body, unread=True):
        self.Subject = subject
        self.SenderName = sender
        self.ReceivedTime = received
        self.Body = body
        self.UnRead = unread


class FakeAppt:
    def __init__(self, subject, start, end, location=""):
        self.Subject = subject
        self.Start = start
        self.End = end
        self.Location = location


class FakeFolder:
    def __init__(self, items):
        self.Items = items


class FakeNamespace:
    def __init__(self, inbox, calendar):
        self._inbox = inbox
        self._calendar = calendar

    def GetDefaultFolder(self, n):
        return self._inbox if n == 6 else self._calendar


class FakeApp:
    def __init__(self, ns):
        self._ns = ns

    def GetNamespace(self, _):
        return self._ns


def _factory(inbox=(), calendar=()):
    def make():
        return FakeApp(FakeNamespace(FakeFolder(list(inbox)), FakeFolder(list(calendar))))

    return make


def test_status_degrades_when_dispatch_fails():
    def boom():
        raise RuntimeError("COM engellendi")

    c = OutlookClient(app_factory=boom)
    st = c.status()
    assert st.ok is False
    assert "Outlook" in st.message
    assert c.unread_mails() == []


def test_unread_mails_mapped():
    now = datetime(2026, 10, 26, 9, 0)
    inbox = [
        FakeItem("Toplantı", "Ayşe", now, "gövde metni", unread=True),
        FakeItem("Okunmuş", "Veli", now, "x", unread=False),
        FakeItem("Acil", "Can", now, "y", unread=True),
    ]
    c = OutlookClient(app_factory=_factory(inbox=inbox))
    mails = c.unread_mails()
    assert [m.subject for m in mails] == ["Toplantı", "Acil"]
    assert mails[0].sender == "Ayşe"


def test_todays_events_filtered_to_today():
    today = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    cal = [
        FakeAppt("Bugünkü", today, today + timedelta(hours=1)),
        FakeAppt("Yarınki", tomorrow, tomorrow + timedelta(hours=1)),
    ]
    c = OutlookClient(app_factory=_factory(calendar=cal))
    events = c.todays_events()
    assert [e.subject for e in events] == ["Bugünkü"]
