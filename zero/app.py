"""ZeRo orkestratörü: sohbet turu, brifing, dürtmeler, hatırlama. UI'yi tembel yükler."""

from __future__ import annotations

from datetime import date

from zero.briefing import compose_briefing
from zero.memory.profile import update_profile
from zero.memory.retrieval import build_context
from zero.outlook.filters import important_mails, meetings_from
from zero.planner.model import DayPlan
from zero.planner.parser import merge_meetings, parse_free_text


class ZeroApp:
    def __init__(
        self, config, store, brain, outlook, notifier, scheduler, break_tracker,
        activity_tracker=None,
    ):
        self.config = config
        self.store = store
        self.brain = brain
        self.outlook = outlook
        self.notifier = notifier
        self.scheduler = scheduler
        self.break_tracker = break_tracker
        self.activity_tracker = activity_tracker
        self.paused = False

    def chat_turn(self, profile: str, user_text: str) -> str:
        status = self.brain.is_available()
        if not status.ok:
            self.store.add_message(profile, "user", user_text)
            return status.message

        ctx = build_context(self.store, self.brain, profile, user_text)
        reply = self.brain.chat(ctx)
        uid = self.store.add_message(profile, "user", user_text)
        aid = self.store.add_message(profile, "assistant", reply)
        self._embed_quietly(uid, user_text)
        self._embed_quietly(aid, reply)
        return reply

    def _embed_quietly(self, message_id: int, text: str) -> None:
        # Embedding başarısız olursa sohbet bozulmasın.
        try:
            self.store.set_embedding(message_id, self.brain.embed(text))
        except Exception:
            pass

    def learn(self, profile: str) -> str:
        """Konuşmalardan kullanıcı profilini güncelle (ara sıra çağrılır)."""
        return update_profile(self.store, self.brain, profile)

    def todays_plan(self, profile: str) -> DayPlan:
        plan = DayPlan(date=date.today())
        if self.outlook.status().ok:
            onemli = important_mails(self.outlook.unread_mails())
            meetings = meetings_from(onemli, self.outlook.todays_events())
            merge_meetings(plan, meetings)
        return plan

    def set_plan_from_text(self, profile: str, text: str) -> DayPlan:
        """Serbest metinden günlük planı kurar, toplantılarla birleştirir, hatırlatmaları zamanlar."""
        plan = self.todays_plan(profile)
        for item in parse_free_text(self.brain, text, date.today()):
            plan.add(item)
        if self.scheduler is not None:
            self.scheduler.schedule_plan(plan)
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

    def read_screen(self, ocr=None, grab=None) -> str:
        from zero.screen import read_screen

        return read_screen(ocr=ocr, grab=grab)

    def import_file(self, path, instruction: str = "") -> str:
        from zero.importers import read_text_file, summarize

        return summarize(self.brain, read_text_file(path), instruction)

    def make_presentation(self, topic: str, out_path=None):
        """Brain'den konu başlıklarını JSON olarak alır, offline bir .pptx üretir."""
        import json
        from pathlib import Path

        from zero.documents.powerpoint import make_powerpoint, Slide

        raw = self.brain.chat(
            [
                {
                    "role": "system",
                    "content": 'Verilen konu için sunum taslağını KESİN JSON olarak yaz: '
                    'liste, her öğe {"title": "...", "bullets": ["...", "..."]}. Sadece JSON.',
                },
                {"role": "user", "content": topic},
            ]
        ).strip()
        try:
            data = json.loads(raw)
            slides = [Slide(d.get("title", ""), list(d.get("bullets", []))) for d in data]
        except Exception:
            slides = [Slide(topic, ["(içerik üretilemedi)"])]

        if out_path is None:
            docs = Path(self.config.memory_root) / "documents"
            docs.mkdir(parents=True, exist_ok=True)
            out_path = docs / f"{topic}.pptx"
        return make_powerpoint(out_path, topic, slides)

    def draft_for(self, mail, instruction: str):
        """Bir maile cevap taslağı hazırlar ve Outlook'a KAYDEDER (göndermez)."""
        from zero.outlook.drafts import compose_reply_text, save_draft

        body = compose_reply_text(self.brain, mail, instruction)
        return save_draft(self.outlook, mail, body)

    def end_of_day_report(self, profile: str):
        from datetime import date as _date

        from zero.daily_report import build_report

        brain_arg = self.brain if self.brain.is_available().ok else None
        return build_report(
            self.store,
            profile,
            _date.today(),
            self.todays_plan(profile),
            self.config.sample_interval_s,
            brain=brain_arg,
        )


def main():  # pragma: no cover - canlı çalıştırma (UI + Ollama + Outlook gerektirir)
    from zero.config import Config
    from zero.memory.store import MemoryStore
    from zero.brain import Brain
    from zero.outlook.client import OutlookClient
    from zero.notify import Notifier
    from zero.planner.scheduler import ReminderScheduler
    from zero.health import BreakTracker
    from zero.tracker import ActivityTracker

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
        activity_tracker=ActivityTracker(store, "omer"),
    )

    from zero.ui.tray import run_ui

    run_ui(app)


def config_path():
    from pathlib import Path

    return Path.home() / ".zero" / "config.json"
