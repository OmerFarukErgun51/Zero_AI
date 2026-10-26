from datetime import datetime

from zero.outlook.client import Mail, OutlookClient
from zero.outlook.drafts import compose_reply_text, save_draft


class FakeBrain:
    def __init__(self):
        self.calls = []

    def chat(self, messages, **kwargs):
        self.calls.append(messages)
        return "Merhaba, teşekkürler."


class FakeReply:
    def __init__(self):
        self.Body = ""
        self.saved = False
        self.sent = False

    def Save(self):
        self.saved = True

    def Send(self):
        self.sent = True


class FakeMailItem:
    def __init__(self, subject):
        self.Subject = subject
        self.UnRead = True
        self.ReceivedTime = datetime.now()
        self.SenderName = "Biri"
        self.Body = "orijinal"
        self.reply = FakeReply()

    def Reply(self):
        return self.reply


class FakeFolder:
    def __init__(self, items):
        self.Items = items


class FakeNamespace:
    def __init__(self, inbox):
        self._inbox = inbox

    def GetDefaultFolder(self, n):
        return self._inbox


class FakeApp:
    def __init__(self, ns):
        self._ns = ns

    def GetNamespace(self, _):
        return self._ns


def _mail(subject="Konu"):
    return Mail(subject=subject, sender="Biri", received=datetime.now(), body_preview="x")


def test_compose_uses_instruction():
    brain = FakeBrain()
    compose_reply_text(brain, _mail("Toplantı daveti"), "kibarca reddet")
    blob = " ".join(m["content"] for m in brain.calls[0])
    assert "Toplantı daveti" in blob
    assert "kibarca reddet" in blob


def test_save_draft_calls_save_not_send():
    item = FakeMailItem("Konu")
    outlook = OutlookClient(app_factory=lambda: FakeApp(FakeNamespace(FakeFolder([item]))))
    result = save_draft(outlook, _mail("Konu"), "taslak gövdesi")
    assert result.ok is True
    assert item.reply.saved is True
    assert item.reply.sent is False


def test_save_draft_degraded_when_com_fails():
    def boom():
        raise RuntimeError("engellendi")

    outlook = OutlookClient(app_factory=boom)
    result = save_draft(outlook, _mail("Konu"), "gövde")
    assert result.ok is False
    assert "taslak" in result.message.lower() or "outlook" in result.message.lower()
