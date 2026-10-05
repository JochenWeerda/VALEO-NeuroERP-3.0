"""Druck-/Exportformat für Schlaginfo (ASK-FLD-002 Bericht)."""
from __future__ import annotations

from typing import Any


def _fmt_money(v: Any) -> str:
    try:
        return f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return str(v)


def render_schlaginfo_text(info: dict[str, Any]) -> str:
    schlag = info.get("schlag") or {}
    kosten = info.get("kosten") or {}
    lines = [
        f"Schlaginformation — {schlag.get('name', '?')}",
        f"Wirtschaftsjahr: {info.get('wirtschaftsjahr', '–')}",
        f"FLIK: {schlag.get('flik') or '–'} | Fläche: {schlag.get('flaecheHa', '–')} ha | Kultur: {schlag.get('kultur') or '–'}",
        "",
        f"Aussaat: {len(info.get('aussaat') or [])}",
        f"Düngung: {len(info.get('duengung') or [])}",
        f"Pflanzenschutz: {len(info.get('pflanzenschutz') or [])}",
        f"Beregnung: {len(info.get('beregnung') or [])}",
        f"Ernte: {len(info.get('ernte') or [])}",
        f"AUM/Sonstiges: {len(info.get('sonstiges') or [])}",
        "",
        "Kosten / Leistung",
        f"  Direktkosten: {_fmt_money(kosten.get('direktkostenEur'))} EUR",
        f"  Erlöse: {_fmt_money(kosten.get('erloesEur'))} EUR",
        f"  Direktkostenfreie Leistung: {_fmt_money(kosten.get('direktkostenfreieLeistungEur'))} EUR",
        f"  je ha: {_fmt_money(kosten.get('direktkostenfreieLeistungEurHa'))} EUR/ha",
    ]
    return "\n".join(lines)
