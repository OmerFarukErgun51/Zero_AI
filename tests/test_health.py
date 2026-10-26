from datetime import datetime, timedelta

from zero.config import Config
from zero.activity import idle_seconds
from zero.health import BreakTracker


class Clock:
    def __init__(self, start):
        self._t = start

    def now(self):
        return self._t

    def advance(self, **kw):
        self._t = self._t + timedelta(**kw)


def _tracker(clock, idle=0.0):
    return BreakTracker(Config(), now_fn=clock.now, idle_fn=lambda: idle)


def test_break_after_interval():
    clock = Clock(datetime(2026, 10, 26, 9, 0))
    t = _tracker(clock, idle=0.0)
    clock.advance(minutes=61)
    nudges = t.tick()
    breaks = [n for n in nudges if n.kind == "break"]
    assert len(breaks) == 1
    assert "mola" in breaks[0].message.lower()


def test_no_break_before_interval():
    clock = Clock(datetime(2026, 10, 26, 9, 0))
    t = _tracker(clock, idle=0.0)
    clock.advance(minutes=30)
    assert [n for n in t.tick() if n.kind == "break"] == []


def test_idle_resets_active_timer():
    clock = Clock(datetime(2026, 10, 26, 9, 0))
    t = BreakTracker(Config(), now_fn=clock.now, idle_fn=lambda: t._idle)
    t._idle = 0.0
    clock.advance(minutes=61)
    t._idle = 400.0  # 5 dk+ boşta → sayaç sıfırlanır
    assert t.tick() == []
    t._idle = 0.0
    clock.advance(minutes=30)  # sıfırlamadan sonra 30 dk < 60
    assert [n for n in t.tick() if n.kind == "break"] == []


def test_water_interval():
    clock = Clock(datetime(2026, 10, 26, 9, 0))
    t = _tracker(clock, idle=0.0)
    clock.advance(minutes=91)
    assert any(n.kind == "water" for n in t.tick())


def test_idle_seconds_uses_getter():
    assert idle_seconds(getter=lambda: 12.5) == 12.5
