from pathlib import Path

from zero.autostart import enable, disable, is_enabled


def test_enable_creates_entry(tmp_path):
    enable(Path("C:/py/pythonw.exe"), Path("C:/zero/run_zero.py"), startup_dir=tmp_path)
    assert is_enabled(startup_dir=tmp_path) is True
    assert any(tmp_path.iterdir())


def test_disable_removes_entry(tmp_path):
    enable(Path("C:/py/pythonw.exe"), Path("C:/zero/run_zero.py"), startup_dir=tmp_path)
    disable(startup_dir=tmp_path)
    assert is_enabled(startup_dir=tmp_path) is False
