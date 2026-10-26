from zero.config import Config
from zero.memory.store import MemoryStore
from zero.memory.retrieval import build_context, cosine
from zero.persona import SYSTEM_PROMPT


class FakeBrain:
    def __init__(self, query_vec):
        self._q = query_vec

    def embed(self, text):
        return self._q


def _store(tmp_path):
    return MemoryStore(tmp_path / "zero.sqlite3")


def test_empty_memory_returns_system_plus_user(tmp_path):
    ctx = build_context(_store(tmp_path), FakeBrain([1.0]), "omer", "selam")
    assert ctx[0]["role"] == "system"
    assert "ZeRo" in ctx[0]["content"]
    assert ctx[-1] == {"role": "user", "content": "selam"}


def test_profile_summary_injected(tmp_path):
    s = _store(tmp_path)
    s.set_profile_summary("omer", "Kısa cevap sever.")
    ctx = build_context(s, FakeBrain([1.0]), "omer", "selam")
    assert "Kısa cevap sever." in ctx[0]["content"]


def test_relevant_snippet_retrieved(tmp_path):
    s = _store(tmp_path)
    close = s.add_message("omer", "user", "YAKIN konu")
    far = s.add_message("omer", "user", "UZAK konu")
    s.set_embedding(close, [1.0, 0.0])
    s.set_embedding(far, [0.0, 1.0])
    ctx = build_context(s, FakeBrain([1.0, 0.0]), "omer", "soru", recent_n=0, top_k=1)
    contents = [m["content"] for m in ctx]
    assert "YAKIN konu" in contents
    assert "UZAK konu" not in contents


def test_context_bounded(tmp_path):
    s = _store(tmp_path)
    for i in range(20):
        s.add_message("omer", "user", "X" * 500)
    max_chars = len(SYSTEM_PROMPT) + 300
    ctx = build_context(s, FakeBrain([1.0]), "omer", "soru", recent_n=20, max_chars=max_chars)
    total = sum(len(m["content"]) for m in ctx)
    assert total <= max_chars
    assert ctx[-1] == {"role": "user", "content": "soru"}


def test_build_context_includes_knowledge(tmp_path):
    from zero.rag import ingest

    s = _store(tmp_path)
    brain = FakeBrain([1.0, 0.0])
    ingest(s, brain, "omer", "notlar.txt", "ZeRo tamamen offline çalışır")
    ctx = build_context(s, brain, "omer", "ZeRo nasıl çalışır?")
    assert "offline" in ctx[0]["content"]


def test_cosine_basic():
    assert cosine([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert cosine([1.0, 0.0], [0.0, 1.0]) == 0.0
