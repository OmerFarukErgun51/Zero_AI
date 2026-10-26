"""RAG: kullanıcının belgelerini öğrenme ve soruyla ilgili parçaları getirme.

Tamamen offline (yerel embedding). Beyni büyütmeden ZeRo'yu 'senin dünyanı
bilen' bir asistana çevirir."""

from __future__ import annotations

import math


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def chunk_text(text: str, size: int = 500) -> list[str]:
    """Metni ~size karakterlik, kelime sınırında parçalara böler."""
    words = text.split()
    chunks: list[str] = []
    current = ""
    for w in words:
        if current and len(current) + 1 + len(w) > size:
            chunks.append(current)
            current = w
        else:
            current = f"{current} {w}".strip()
    if current:
        chunks.append(current)
    return chunks or [text]


def ingest(store, brain, profile: str, source: str, text: str, size: int = 500) -> int:
    """Belgeyi parçalara bölüp her parçayı embed'leyerek bilgi deposuna yazar."""
    count = 0
    for chunk in chunk_text(text, size):
        if not chunk.strip():
            continue
        vector = brain.embed(chunk)
        store.add_knowledge(profile, source, chunk, vector)
        count += 1
    return count


def retrieve(
    store, brain, profile: str, query: str, top_k: int = 3, max_chars: int = 1500
) -> list[str]:
    """Soruyla en ilgili bilgi parçalarını döndürür (yoksa boş liste)."""
    chunks = store.knowledge_chunks(profile)
    if not chunks:
        return []
    q = brain.embed(query)
    scored = sorted(chunks, key=lambda cv: _cosine(q, cv[1]), reverse=True)
    out: list[str] = []
    total = 0
    for text, _vec in scored[:top_k]:
        if total + len(text) > max_chars:
            break
        out.append(text)
        total += len(text)
    return out
