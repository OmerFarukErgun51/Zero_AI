from datetime import date, datetime, time

from zero.outlook.filters import Meeting
from zero.planner.model import PlanItem, DayPlan
from zero.planner.parser import parse_free_text, from_form, merge_meetings, CLARIFY_TEXT


class FakeBrain:
    def __init__(self, reply):
        self.reply = reply

    def chat(self, messages, **kwargs):
        return self.reply


def test_parse_free_text_times():
    brain = FakeBrain('[{"time":"10:00","text":"rapor"},{"time":"14:00","text":"toplantı"}]')
    items = parse_free_text(brain, "bugün 10 rapor 2 toplantı", date(2026, 10, 26))
    assert [i.text for i in items] == ["rapor", "toplantı"]
    assert items[0].time == time(10, 0)


def test_parse_untimed():
    brain = FakeBrain('[{"time":null,"text":"alışveriş"}]')
    items = parse_free_text(brain, "alışveriş yapılacak", date(2026, 10, 26))
    assert items[0].time is None


def test_parse_garbage_asks_clarify():
    brain = FakeBrain("bunu anlamadım, kod bloğu falan değil")
    items = parse_free_text(brain, "asdf", date(2026, 10, 26))
    assert len(items) == 1
    assert items[0].text == CLARIFY_TEXT


def test_from_form_blank_time():
    items = from_form([("", "spor"), ("09:30", "kahvaltı")])
    assert items[0].time is None
    assert items[1].time == time(9, 30)


def test_merge_dedups():
    plan = DayPlan(date=date(2026, 10, 26))
    plan.add(PlanItem(time(14, 0), "Sprint", "takvim"))
    m = Meeting("Sprint", datetime(2026, 10, 26, 14, 0), "takvim")
    merge_meetings(plan, [m])
    assert sum(1 for i in plan.items if i.text == "Sprint") == 1


def test_dayplan_sorted():
    plan = DayPlan(date=date(2026, 10, 26))
    plan.add(PlanItem(None, "sonraya", "kullanıcı"))
    plan.add(PlanItem(time(9, 0), "sabah", "kullanıcı"))
    assert plan.items[0].text == "sabah"
    assert plan.items[-1].text == "sonraya"
