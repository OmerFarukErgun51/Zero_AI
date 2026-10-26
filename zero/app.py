"""ZeRo orkestratörü: sohbet turu, brifing, dürtmeler, hatırlama. UI'yi tembel yükler."""

from __future__ import annotations

from datetime import date

from zero.briefing import compose_briefing
from zero.memory.retrieval import build_context
from zero.outlook.filters import meetings_from
from zero.planner.model import DayPlan
from zero.planner.parser import merge_meetings


class ZeroApp:
    def __init__(self, config, store, brain, outlook, notifier, scheduler, break_tracker):
        self.config = config
        self.store = store
        self.brain = brain
        self.outlook = outlook
        self.notifier = notifier
        self.scheduler = scheduler
        self.break_tracker = break_tracker

    def chat_turn(self, profile: str, user_text: str) -> str:
        status = self.brain.is_available()
        if not status.ok:
            self.store.add_message(profile, "user", user_text)
            return status.message

        ctx = build_context(self.store, self.brain, profile, user_text)
        reply = self.brain.chat(ctx)
        self.store.add_message(profile, "user", user_text)
        self.store.add_message(profile, "assistant", reply)
        return reply

    def todays_plan(self, profile: str) -> DayPlan:
        plan = DayPlan(date=date.today())
        if self.outlook.status().ok:
            meetings = meetings_from(self.outlook.unread_mails(), self.outlook.todays_events())
            merge_meetings(plan, meetings)
        return plan

    def startup_briefing(self, profile: str) -> str:
        plan = self.todays_plan(profile)
        brain_arg = self.brain if self.brain.is_available().ok else None
        return compose_briefing(
            self.outlook,
            plan,
            brain=brain_arg,
            profile_summary=self.store.get_profile_summary(profile),
        )

    def on_tick(self, profile: str):
        return self.break_tracker.tick() if self.break_tracker else []

    def remember(self, profile: str, key: str, value: str) -> None:
        self.store.set_fact(profile, key, value)


def main():  # pragma: no cover - canlı çalıştırma (UI + Ollama + Outlook gerektirir)
    from zero.config import Config
    from zero.memory.store import MemoryStore
    from zero.brain import Brain
    from zero.outlook.client import OutlookClient
    from zero.notify import Notifier
    from zero.planner.scheduler import ReminderScheduler
    from zero.health import BreakTracker

    config = Config.load(config_path())
    store = MemoryStore(config.memory_db_path)
    brain = Brain(config)
    notifier = Notifier()
    app = ZeroApp(
        config=config,
        store=store,
        brain=brain,
        outlook=OutlookClient(),
        notifier=notifier,
        scheduler=ReminderScheduler(notifier),
        break_tracker=BreakTracker(config),
    )

    from zero.ui.tray import run_ui

    run_ui(app)


def config_path():
    from pathlib import Path

    return Path.home() / ".zero" / "config.json"
