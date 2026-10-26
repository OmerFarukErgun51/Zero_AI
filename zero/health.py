"""Mola / su / göz dinlendirme dürtmeleri — nazik öneriler."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

_IDLE_RESET_SECONDS = 300  # 5 dk+ boşta → aktif sayaç sıfırlanır

_BREAK_MSG = "Bir süredir çalışıyorsun, kısa bir mola iyi gelebilir. 🌿"
_WATER_MSG = "Su içmeyi unutma, bir bardak iyi gider. 💧"


@dataclass
class Nudge:
    kind: str  # "break" | "water"
    message: str


class BreakTracker:
    def __init__(self, config, now_fn=None, idle_fn=None):
        self._config = config
        self._now = now_fn or datetime.now
        self._idle_fn = idle_fn or (lambda: 0.0)
        start = self._now()
        self._last_break = start
        self._last_water = start

    def tick(self) -> list[Nudge]:
        now = self._now()
        if self._idle_fn() >= _IDLE_RESET_SECONDS:
            # Kullanıcı uzakta/molada: aktif çalışma sayacını sıfırla.
            self._last_break = now
            return []

        nudges: list[Nudge] = []
        if (now - self._last_break).total_seconds() >= self._config.break_interval_min * 60:
            nudges.append(Nudge("break", _BREAK_MSG))
            self._last_break = now
        if (now - self._last_water).total_seconds() >= self._config.water_interval_min * 60:
            nudges.append(Nudge("water", _WATER_MSG))
            self._last_water = now
        return nudges
