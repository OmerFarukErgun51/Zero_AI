"""Kullanıcı profili özetleyici — konuşmalardan zamanla 'kim bu kişi' çıkarımı.

Her mesajda değil, ara sıra (oturum sonu / periyodik) çağrılır; sistemi yormasın."""

from __future__ import annotations

_PROMPT = (
    "Aşağıda Ömer ile yapılmış konuşmalar var. Bunlardan Ömer hakkında kısa, "
    "maddeler halinde KALICI bir profil çıkar (tercihleri, ilgi alanları, "
    "çalışma alışkanlıkları, iletişim tarzı). Sadece profili yaz, başka bir şey "
    "ekleme."
)


def update_profile(store, brain, profile: str, max_messages: int = 100) -> str:
    messages = store.recent_messages(profile, limit=max_messages)
    if not messages:
        return store.get_profile_summary(profile)

    konusma = "\n".join(f"{m.role}: {m.text}" for m in messages)
    chat_messages = [
        {"role": "system", "content": _PROMPT},
        {"role": "user", "content": konusma},
    ]
    summary = brain.chat(chat_messages).strip()
    store.set_profile_summary(profile, summary)
    return summary
