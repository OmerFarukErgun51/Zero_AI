"""Gün boyu hafif etkinlik takibi — ön plandaki pencere/uygulamayı örnekler.

Sürekli OCR DEĞİL; yalnızca pencere başlığı. Duraklatılabilir."""

from __future__ import annotations

from datetime import datetime


def _default_foreground() -> tuple[str, str]:
    import win32gui
    import win32process
    import win32api

    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd) or ""
    app = ""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        handle = win32api.OpenProcess(0x0410, False, pid)  # QUERY_INFORMATION|VM_READ
        app = win32process.GetModuleFileNameEx(handle, 0).split("\\")[-1]
    except Exception:
        app = title
    return app, title


class ActivityTracker:
    def __init__(self, store, profile: str, foreground_fn=None, now_fn=None):
        self.store = store
        self.profile = profile
        self.paused = False
        self._foreground = foreground_fn or _default_foreground
        self._now = now_fn or datetime.now

    def sample(self) -> None:
        if self.paused:
            return
        app, title = self._foreground()
        self.store.add_activity_sample(self.profile, app, title, self._now())
