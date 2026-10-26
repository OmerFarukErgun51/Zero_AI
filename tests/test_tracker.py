from datetime import date, datetime

from zero.memory.store import MemoryStore
from zero.tracker import ActivityTracker


def _store(tmp_path):
    return MemoryStore(tmp_path / "zero.sqlite3")


def test_sample_records_foreground(tmp_path):
    store = _store(tmp_path)
    now = datetime(2026, 10, 26, 10, 0)
    tracker = ActivityTracker(
        store, "omer", foreground_fn=lambda: ("EXCEL.EXE", "Bütçe.xlsx"), now_fn=lambda: now
    )
    tracker.sample()
    samples = store.activity_for_day("omer", date(2026, 10, 26))
    assert len(samples) == 1
    assert samples[0].app == "EXCEL.EXE"
    assert samples[0].title == "Bütçe.xlsx"


def test_paused_skips(tmp_path):
    store = _store(tmp_path)
    now = datetime(2026, 10, 26, 10, 0)
    tracker = ActivityTracker(
        store, "omer", foreground_fn=lambda: ("X", "Y"), now_fn=lambda: now
    )
    tracker.paused = True
    tracker.sample()
    assert store.activity_for_day("omer", date(2026, 10, 26)) == []
