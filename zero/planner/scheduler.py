"""Plan maddelerini zamanlanmış bildirimlere bağlayan hatırlatıcı."""

from __future__ import annotations

from datetime import datetime

from zero.planner.model import DayPlan

_JOB_PREFIX = "zero-plan-"


def _default_scheduler():
    from apscheduler.schedulers.background import BackgroundScheduler

    s = BackgroundScheduler()
    s.start()
    return s


class ReminderScheduler:
    def __init__(self, notifier, scheduler=None, now_fn=None):
        self._notifier = notifier
        self._scheduler = scheduler if scheduler is not None else _default_scheduler()
        self._now = now_fn or datetime.now

    def schedule_plan(self, plan: DayPlan) -> int:
        count = 0
        now = self._now()
        for idx, item in enumerate(plan.items):
            if item.time is None:
                continue
            run_date = datetime.combine(plan.date, item.time)
            if run_date <= now:
                continue
            self._scheduler.add_job(
                self._make_callback(item.text),
                trigger="date",
                run_date=run_date,
                id=f"{_JOB_PREFIX}{idx}",
            )
            count += 1
        return count

    def _make_callback(self, text: str):
        def fire():
            self._notifier.send("ZeRo", f"Planında: {text}")

        return fire

    def clear(self) -> None:
        self._scheduler.remove_all_jobs()
