from zero.memory.store import MemoryStore
from zero.rag import chunk_text, ingest, retrieve


class FakeBrain:
    """Metindeki anahtar kelimeye göre sabit vektör döndürür (deterministik test)."""

    def embed(self, text):
        t = text.lower()
        if "elma" in t:
            return [1.0, 0.0]
        if "araba" in t:
            return [0.0, 1.0]
        return [0.5, 0.5]


def _store(tmp_path):
    return MemoryStore(tmp_path / "zero.sqlite3")


def test_chunk_text_splits_long_text():
    text = "kelime " * 300  # ~2100 karakter
    chunks = chunk_text(text, size=500)
    assert len(chunks) > 1
    assert all(len(c) <= 600 for c in chunks)


def test_chunk_text_short_stays_one():
    assert chunk_text("kısa metin", size=500) == ["kısa metin"]


def test_ingest_stores_chunks(tmp_path):
    s = _store(tmp_path)
    n = ingest(s, FakeBrain(), "omer", "notlar.txt", "elma hakkında " * 100)
    assert n >= 1
    assert len(s.knowledge_chunks("omer")) == n


def test_retrieve_relevant_chunk(tmp_path):
    s = _store(tmp_path)
    ingest(s, FakeBrain(), "omer", "a.txt", "elma yemek sağlıklıdır")
    ingest(s, FakeBrain(), "omer", "b.txt", "araba sürmek dikkat ister")
    results = retrieve(s, FakeBrain(), "omer", "elma hakkında bilgi", top_k=1)
    assert len(results) == 1
    assert "elma" in results[0].lower()


def test_retrieve_empty_when_no_knowledge(tmp_path):
    s = _store(tmp_path)
    assert retrieve(s, FakeBrain(), "omer", "soru") == []
