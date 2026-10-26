from datetime import date, datetime, time

from zero.notify import Notifier
from zero.planner.model import PlanItem, DayPlan
from zero.planner.scheduler import ReminderScheduler


class FakeToaster:
    def __init__(self):
        self.shown = []

    def show(self, title, body):
        self.shown.append((title, body))


class FakeScheduler:
    def __init__(self):
        self.jobs = []  # (func, run_date, id)

    def add_job(self, func, trigger=None, run_date=None, id=None, **kwargs):
        self.jobs.append((func, run_date, id))

    def remove_all_jobs(self):
        self.jobs = []


def _plan():
    p = DayPlan(date=date(2026, 10, 26))
    p.add(PlanItem(time(9, 0), "sabah işi", "kullanıcı"))
    p.add(PlanItem(time(15, 0), "öğleden sonra", "kullanıcı"))
    p.add(PlanItem(None, "zamansız", "kullanıcı"))
    return p


def _sched(notifier, scheduler):
    now = datetime(2026, 10, 26, 12, 0)
    return ReminderScheduler(notifier, scheduler=scheduler, now_fn=lambda: now)


def test_schedules_future_timed_items():
    fs = FakeScheduler()
    count = _sched(Notifier(toaster=FakeToaster()), fs).schedule_plan(_plan())
    # 09:00 geçmiş (now 12:00) atlanır; 15:00 planlanır; zamansız planlanmaz
    assert count == 1
    assert fs.jobs[0][1] == datetime(2026, 10, 26, 15, 0)


def test_skips_past_times():
    fs = FakeScheduler()
    _sched(Notifier(toaster=FakeToaster()), fs).schedule_plan(_plan())
    assert all(rd > datetime(2026, 10, 26, 12, 0) for (_, rd, _) in fs.jobs)


def test_firing_sends_toast():
    fs = FakeScheduler()
    toaster = FakeToaster()
    _sched(Notifier(toaster=toaster), fs).schedule_plan(_plan())
    func = fs.jobs[0][0]
    func()
    assert any("öğleden sonra" in body for (_, body) in toaster.shown)


def test_notifier_send_calls_toaster():
    toaster = FakeToaster()
    Notifier(toaster=toaster).send("ZeRo", "mola zamanı")
    assert toaster.shown == [("ZeRo", "mola zamanı")]
