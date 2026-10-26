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

    def chat_stream(self, messages):
        for part in ["Buy", "ur ", "Ömer."]:
            yield part

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


def test_chat_turn_stream(tmp_path):
    app = _app(tmp_path)
    chunks = []
    full = app.chat_turn_stream("omer", "selam", on_chunk=chunks.append)
    assert "".join(chunks) == full
    assert full == "Buyur Ömer."
    assert [m.role for m in app.store.all_messages("omer")] == ["user", "assistant"]


def test_chat_turn_stream_unavailable(tmp_path):
    app = _app(tmp_path, brain=FakeBrain(available=False))
    chunks = []
    full = app.chat_turn_stream("omer", "selam", on_chunk=chunks.append)
    assert "Ollama" in full
    assert [m.role for m in app.store.all_messages("omer")] == ["user"]


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


# --- Final review fix pass ---------------------------------------------------

from datetime import datetime, timedelta

from zero.outlook.client import OutlookStatus, Event, Mail


class FakeScheduler:
    def __init__(self):
        self.jobs = []

    def add_job(self, func, trigger=None, run_date=None, id=None, **kw):
        self.jobs.append((func, run_date, id))

    def remove_all_jobs(self):
        self.jobs = []


class FakeOutlookOk:
    def __init__(self, events=(), mails=()):
        self._events = list(events)
        self._mails = list(mails)

    def status(self):
        return OutlookStatus(True, "ok")

    def todays_events(self):
        return self._events

    def unread_mails(self, limit=20):
        return self._mails


def test_chat_turn_stores_embedding(tmp_path):
    app = _app(tmp_path)  # FakeBrain.embed -> [0.0]
    app.chat_turn("omer", "selam")
    assert len(app.store.messages_with_embeddings("omer")) == 2  # user + assistant


def test_learn_updates_profile(tmp_path):
    app = _app(tmp_path)
    app.store.add_message("omer", "user", "futbolu severim")
    app.learn("omer")
    assert app.store.get_profile_summary("omer") == "Buyur Ömer."


def test_todays_plan_only_important_mails(tmp_path):
    spam = Mail("15:00 indirim bülteni", "shop", datetime.now(), "")  # zamanlı ama önemsiz
    outlook = FakeOutlookOk(mails=[spam])
    store = MemoryStore(tmp_path / "zero.sqlite3")
    from zero.config import Config as C
    app = ZeroApp(C(memory_root=tmp_path), store, FakeBrain(), outlook, None, None, None)
    plan = app.todays_plan("omer")
    assert all(i.source != "mail" for i in plan.items)


def test_set_plan_from_text_schedules(tmp_path):
    from datetime import datetime as _dt
    from zero.notify import Notifier
    from zero.planner.scheduler import ReminderScheduler

    brain = FakeBrain(reply='[{"time":"23:59","text":"gece işi"}]')
    backend = FakeScheduler()
    # Saat sabitlensin ki 23:59 her zaman gelecekte olsun
    reminder = ReminderScheduler(
        Notifier(toaster=type("T", (), {"show": lambda self, a, b: None})()),
        scheduler=backend,
        now_fn=lambda: _dt(2026, 10, 26, 8, 0),
    )
    store = MemoryStore(tmp_path / "zero.sqlite3")
    from zero.config import Config as C
    app = ZeroApp(C(memory_root=tmp_path), store, brain, FakeOutlookOk(), None, reminder, None)
    plan = app.set_plan_from_text("omer", "gece 23:59 iş")
    assert any(i.text == "gece işi" for i in plan.items)
    assert len(backend.jobs) == 1


def test_warmup_runs_when_available(tmp_path):
    app = _app(tmp_path)
    app.warmup()  # hata vermemeli; modelleri ısıtmak için chat+embed çağırır


def test_warmup_safe_when_unavailable(tmp_path):
    app = _app(tmp_path, brain=FakeBrain(available=False))
    app.warmup()  # model yokken sessizce geçmeli, patlamamalı


def test_make_presentation_creates_file(tmp_path):
    brain = FakeBrain(reply='[{"title":"Giriş","bullets":["a","b"]}]')
    store = MemoryStore(tmp_path / "zero.sqlite3")
    from zero.config import Config as C
    app = ZeroApp(C(memory_root=tmp_path), store, brain, FakeOutlookOk(), None, None, None)
    path = app.make_presentation("Proje")
    assert path.exists()
    assert path.suffix == ".pptx"
