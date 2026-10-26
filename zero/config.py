"""ZeRo yapılandırması: yollar ve ayarlanabilir varsayılanlar."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, fields
from pathlib import Path


def _default_memory_root() -> Path:
    return Path.home() / ".zero"


@dataclass
class Config:
    memory_root: Path = field(default_factory=_default_memory_root)
    model: str = "qwen3:4b"
    embed_model: str = "nomic-embed-text"
    keep_alive: str = "5m"
    break_interval_min: int = 60
    water_interval_min: int = 90
    sample_interval_s: int = 60
    report_hour: int = 18

    @classmethod
    def load(cls, path: Path | None = None) -> "Config":
        """config.json varsa oku; yoksa varsayılanları döndür."""
        if path is None or not Path(path).exists():
            return cls()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        known = {f.name for f in fields(cls)}
        kwargs = {}
        for key, value in data.items():
            if key not in known:
                continue
            kwargs[key] = Path(value) if key == "memory_root" else value
        return cls(**kwargs)

    @property
    def memory_db_path(self) -> Path:
        return self.memory_root / "zero.sqlite3"
