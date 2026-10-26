"""Windows açılışında otomatik başlatma — Startup klasörüne bir launcher yazar.

.lnk yerine .cmd kullanılır: pywin32/COM bağımlılığı olmadan, test edilebilir ve
aynı işi görür."""

from __future__ import annotations

import os
from pathlib import Path

_LAUNCHER_NAME = "ZeRo.cmd"


def _startup_dir(startup_dir: Path | None = None) -> Path:
    if startup_dir is not None:
        return Path(startup_dir)
    return Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _launcher_path(startup_dir: Path | None = None) -> Path:
    return _startup_dir(startup_dir) / _LAUNCHER_NAME


def enable(python_exe: Path, script: Path, startup_dir: Path | None = None) -> Path:
    path = _launcher_path(startup_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'@echo off\r\nstart "" "{python_exe}" "{script}"\r\n', encoding="utf-8")
    return path


def disable(startup_dir: Path | None = None) -> None:
    path = _launcher_path(startup_dir)
    if path.exists():
        path.unlink()


def is_enabled(startup_dir: Path | None = None) -> bool:
    return _launcher_path(startup_dir).exists()
