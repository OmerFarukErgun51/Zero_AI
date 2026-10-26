"""Bağlam kurucu: sistem komutu + profil + ilgili geçmiş parçalar + yeni mesaj.

Model tüm geçmişi aynı anda tutamaz; bu yüzden gönderilen içerik max_chars ile
sınırlanır (en eski parçalardan başlanarak kırpılır)."""

from __future__ import annotations

import math

from zero.persona import SYSTEM_PROMPT


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _system_content(store, profile: str) -> str:
    parts = [SYSTEM_PROMPT]
    summary = store.get_profile_summary(profile)
    if summary:
        parts.append(f"\nÖmer hakkında bildiklerin:\n{summary}")
    facts = store.get_facts(profile)
    if facts:
        satirlar = "\n".join(f"- {k}: {v}" for k, v in facts.items())
        parts.append(f"\nKalıcı notlar:\n{satirlar}")
    return "\n".join(parts)


def build_context(
    store,
    brain,
    profile: str,
    user_message: str,
    recent_n: int = 12,
    top_k: int = 5,
    max_chars: int = 6000,
) -> list[dict]:
    system_content = _system_content(store, profile)

    recent = store.recent_messages(profile, limit=recent_n) if recent_n > 0 else []
    recent_ids = {m.id for m in recent}

    # İlgili eski parçaları semantik olarak getir (recent ile çakışanları çıkar).
    snippets = []
    candidates = [
        (m, v) for (m, v) in store.messages_with_embeddings(profile) if m.id not in recent_ids
    ]
    if candidates and top_k > 0:
        q = brain.embed(user_message)
        scored = sorted(candidates, key=lambda mv: cosine(q, mv[1]), reverse=True)
        chosen = [m for (m, v) in scored[:top_k]]
        snippets = sorted(chosen, key=lambda m: m.id)  # eskiden yeniye

    middle = [{"role": m.role, "content": m.text} for m in snippets]
    middle += [{"role": m.role, "content": m.text} for m in recent]

    # max_chars sınırı: sistem + son kullanıcı mesajı korunur; orta kısım en
    # eskiden başlanarak kırpılır.
    base = len(system_content) + len(user_message)
    while middle and base + sum(len(x["content"]) for x in middle) > max_chars:
        middle.pop(0)

    return (
        [{"role": "system", "content": system_content}]
        + middle
        + [{"role": "user", "content": user_message}]
    )
