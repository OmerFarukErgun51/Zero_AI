"""Sabah brifingi: bugünkü toplantılar, önemli mailler, günün planı.

Outlook devre dışıysa mail/toplantı satırları atlanır; ZeRo çökmez."""

from __future__ import annotations

from zero.outlook.filters import important_mails
from zero.planner.model import DayPlan


def compose_briefing(outlook, plan: DayPlan, brain=None, profile_summary: str = "") -> str:
    lines: list[str] = ["Günaydın! İşte bugünün özeti:"]

    status = outlook.status()
    if status.ok:
        events = outlook.todays_events()
        if events:
            basliklar = ", ".join(e.subject for e in events)
            lines.append(f"• Bugün {len(events)} toplantın var: {basliklar}")
        important = important_mails(outlook.unread_mails())
        if important:
            basliklar = ", ".join(m.subject for m in important)
            lines.append(f"• {len(important)} önemli okunmamış mailin var: {basliklar}")
    else:
        lines.append("• Maillerine şu an ulaşamıyorum (Outlook kapalı ya da izin yok).")

    if plan.items:
        lines.append("• Planın:")
        for item in plan.items:
            saat = item.time.strftime("%H:%M") if item.time else "—"
            lines.append(f"   {saat}  {item.text}")
    else:
        lines.append("• Bugün için planın boş görünüyor. Güzel bir gün olsun!")

    text = "\n".join(lines)

    if brain is not None:
        ozet_ek = f"\nÖmer hakkında: {profile_summary}" if profile_summary else ""
        return brain.chat(
            [
                {
                    "role": "system",
                    "content": "Aşağıdaki brifingi ZeRo'nun sakin, cana yakın üslubuyla "
                    "kısa bir paragrafa dönüştür." + ozet_ek,
                },
                {"role": "user", "content": text},
            ]
        ).strip()

    return text
