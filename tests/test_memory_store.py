from zero.memory.store import MemoryStore


def _store(tmp_path):
    return MemoryStore(tmp_path / "zero.sqlite3")


def test_add_and_recent(tmp_path):
    s = _store(tmp_path)
    s.add_message("omer", "user", "bir")
    s.add_message("omer", "assistant", "iki")
    s.add_message("omer", "user", "uc")
    recent = s.recent_messages("omer", limit=2)
    assert [m.text for m in recent] == ["iki", "uc"]


def test_profiles_isolated(tmp_path):
    s = _store(tmp_path)
    s.add_message("omer", "user", "gizli")
    assert s.recent_messages("ayse") == []


def test_facts_upsert(tmp_path):
    s = _store(tmp_path)
    s.set_fact("omer", "renk", "mavi")
    s.set_fact("omer", "renk", "kirmizi")
    assert s.get_facts("omer")["renk"] == "kirmizi"


def test_profile_summary_default_empty(tmp_path):
    s = _store(tmp_path)
    assert s.get_profile_summary("new") == ""


def test_embedding_roundtrip(tmp_path):
    s = _store(tmp_path)
    mid = s.add_message("omer", "user", "vektor")
    s.set_embedding(mid, [0.1, 0.2, 0.3])
    pairs = s.messages_with_embeddings("omer")
    assert len(pairs) == 1
    msg, vec = pairs[0]
    assert msg.text == "vektor"
    assert all(abs(a - b) < 1e-9 for a, b in zip(vec, [0.1, 0.2, 0.3]))
