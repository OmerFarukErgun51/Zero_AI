from zero.tools import find_files, system_info, list_directory, dispatch


def test_find_files_matches_name(tmp_path):
    (tmp_path / "rapor_2026.txt").write_text("x", encoding="utf-8")
    (tmp_path / "foto.png").write_text("x", encoding="utf-8")
    res = find_files("rapor", roots=[str(tmp_path)])
    assert any("rapor_2026.txt" in r for r in res)
    assert all("foto.png" not in r for r in res)


def test_find_files_empty_when_no_match(tmp_path):
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    assert find_files("bulunmayan", roots=[str(tmp_path)]) == []


def test_find_files_respects_limit(tmp_path):
    for i in range(10):
        (tmp_path / f"dosya_{i}.txt").write_text("x", encoding="utf-8")
    res = find_files("dosya", roots=[str(tmp_path)], limit=3)
    assert len(res) == 3


def test_system_info_mentions_ram():
    info = system_info()
    assert "RAM" in info
    assert "Windows" in info or "İşletim" in info


def test_list_directory(tmp_path):
    (tmp_path / "x.txt").write_text("1", encoding="utf-8")
    (tmp_path / "alt").mkdir()
    listed = list_directory(str(tmp_path))
    assert any("x.txt" in item for item in listed)
    assert any("alt" in item for item in listed)


def test_dispatch_find_files(tmp_path):
    (tmp_path / "rapor.txt").write_text("x", encoding="utf-8")
    out = dispatch("find_files", {"query": "rapor", "roots": [str(tmp_path)]})
    assert "rapor.txt" in out


def test_dispatch_unknown_tool():
    out = dispatch("olmayan_arac", {})
    assert "bilinmeyen" in out.lower() or "bulunamadı" in out.lower()
