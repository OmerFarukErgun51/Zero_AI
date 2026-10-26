"""Kullanıcının boşta kalma süresi — Windows son girdi zamanından."""

from __future__ import annotations


def _default_getter() -> float:
    import win32api

    millis = win32api.GetTickCount() - win32api.GetLastInputInfo()
    return millis / 1000.0


def idle_seconds(getter=None) -> float:
    return (getter or _default_getter)()
