import json
from pathlib import Path

from zero.config import Config


def test_defaults_when_no_file(tmp_path):
    cfg = Config.load(tmp_path / "missing.json")
    assert cfg.model == "qwen3:4b"
    assert cfg.keep_alive == "5m"


def test_reads_overrides(tmp_path):
    p = tmp_path / "config.json"
    p.write_text(json.dumps({"model": "gemma3:4b", "break_interval_min": 45}), encoding="utf-8")
    cfg = Config.load(p)
    assert cfg.model == "gemma3:4b"
    assert cfg.break_interval_min == 45


def test_memory_db_path(tmp_path):
    cfg = Config(memory_root=tmp_path)
    assert cfg.memory_db_path == tmp_path / "zero.sqlite3"
