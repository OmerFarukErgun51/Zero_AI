from datetime import date, datetime, time

from zero.memory.store import MemoryStore, ActivitySample
from zero.planner.model import PlanItem, DayPlan
from zero.daily_report import per_app_durations, build_report


def _store(tmp_path):
    return MemoryStore(tmp_path / "zero.sqlite3")


def test_per_app_durations():
    samples = [ActivitySample("omer", "EXCEL", "x", datetime(2026, 10, 26, 10, i)) for i in range(10)]
    durations = per_app_durations(samples, sample_interval_s=60)
    assert durations["EXCEL"] == 10.0


def test_build_report_includes_done_items(tmp_path):
    store = _store(tmp_path)
    plan = DayPlan(date=date(2026, 10, 26))
    plan.add(PlanItem(time(10, 0), "rapor yaz", "kullanıcı"))
    report = build_report(store, "omer", date(2026, 10, 26), plan, sample_interval_s=60)
    assert "rapor yaz" in report.done_items


def test_build_report_empty_day(tmp_path):
    store = _store(tmp_path)
    plan = DayPlan(date=date(2026, 10, 26))
    report = build_report(store, "omer", date(2026, 10, 26), plan, sample_interval_s=60)
    assert set(report.fields.keys()) == {"yaptıklarım", "notlar", "yarına"}
    assert report.app_minutes == {}
