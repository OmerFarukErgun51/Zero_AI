from zero.config import Config
from zero.memory.store import MemoryStore
from zero.brain import BrainStatus
from zero.outlook.client import OutlookStatus
from zero.app import ZeroApp


class FakeBrain:
    def __init__(self, available=True, reply="Buyur Ömer."):
        self._available = available
        self.reply = reply

    def is_available(self):
        return BrainStatus(self._available, "ZeRo hazır." if self._available else "Ollama kapalı, lütfen başlat.")

    def chat(self, messages, **kwargs):
        return self.reply

    def embed(self, text):
        return [0.0]


class FakeOutlook:
    def status(self):
        return OutlookStatus(False, "ulaşılamıyor")

    def todays_events(self):
        return []

    def unread_mails(self, limit=20):
        return []


def _app(tmp_path, brain=None):
    store = MemoryStore(tmp_path / "zero.sqlite3")
    return ZeroApp(
        config=Config(memory_root=tmp_path),
        store=store,
        brain=brain or FakeBrain(),
        outlook=FakeOutlook(),
        notifier=None,
        scheduler=None,
        break_tracker=None,
    )


def test_chat_turn_persists_and_replies(tmp_path):
    app = _app(tmp_path)
    reply = app.chat_turn("omer", "selam")
    assert reply == "Buyur Ömer."
    roles = [m.role for m in app.store.all_messages("omer")]
    assert roles == ["user", "assistant"]


def test_chat_turn_brain_unavailable(tmp_path):
    app = _app(tmp_path, brain=FakeBrain(available=False))
    reply = app.chat_turn("omer", "selam")
    assert "Ollama" in reply
    assert [m.role for m in app.store.all_messages("omer")] == ["user"]


def test_startup_briefing_runs_with_empty_memory(tmp_path):
    text = _app(tmp_path).startup_briefing("omer")
    assert text.strip() != ""


def test_remember_sets_fact(tmp_path):
    app = _app(tmp_path)
    app.remember("omer", "favori_renk", "mavi")
    assert app.store.get_facts("omer")["favori_renk"] == "mavi"


def test_read_screen_delegates(tmp_path):
    app = _app(tmp_path)
    out = app.read_screen(ocr=lambda img: "ekranda bu var", grab=lambda: "img")
    assert out == "ekranda bu var"


def test_import_file_summarizes(tmp_path):
    p = tmp_path / "mail.txt"
    p.write_text("uzun mail içeriği", encoding="utf-8")
    app = _app(tmp_path)  # FakeBrain.chat → "Buyur Ömer."
    assert app.import_file(p) == "Buyur Ömer."


def test_end_of_day_report_runs(tmp_path):
    app = _app(tmp_path)
    report = app.end_of_day_report("omer")
    assert set(report.fields.keys()) == {"yaptıklarım", "notlar", "yarına"}
