"""Austauschbare Käufergruppen-Klassifikatoren (regelbasiert | KI).

Die Klassifikation darf keine Blackbox sein: jeder Klassifikator liefert Gruppe +
Confidence + Begründung. Der LLM-Klassifikator (Claude über httpx, kein SDK-Zwang)
fällt bei fehlendem Key/Guthaben oder Fehler deterministisch auf den regelbasierten
Klassifikator zurück — die UI markiert die Quelle (rule_based | ai_suggested).
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Protocol, Tuple

import httpx

from app.services.kaeufergruppe import (
    GRUPPEN,
    BuyingGroup,
    Klassifikation,
    Verhaltenssignale,
    klassifiziere,
)

logger = logging.getLogger(__name__)

_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")


class Klassifikator(Protocol):
    """Einheitliche Schnittstelle — austauschbar (regelbasiert, KI, künftig ML)."""

    name: str

    def klassifiziere(self, s: Verhaltenssignale) -> Klassifikation: ...


class RuleBasedKlassifikator:
    name = "rule_based"

    def klassifiziere(self, s: Verhaltenssignale) -> Klassifikation:
        return klassifiziere(s)


class LLMKlassifikator:
    """Claude-gestützte Klassifikation mit regelbasiertem Fallback."""

    name = "ai_suggested"

    def __init__(self, fallback: Klassifikator | None = None) -> None:
        self._fallback = fallback or RuleBasedKlassifikator()

    def _katalog_text(self) -> str:
        return "\n".join(
            f"- {g.value}: {p.label} (Zielanteil {int(p.ziel_anteil_min*100)}-{int(p.ziel_anteil_max*100)} %)"
            for g, p in GRUPPEN.items() if g is not BuyingGroup.UNBEKANNT
        )

    def klassifiziere(self, s: Verhaltenssignale) -> Klassifikation:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            return self._fallback.klassifiziere(s)
        try:
            prompt = (
                "Du bist Vertriebsanalyst im Agrarhandel. Ordne den Betrieb anhand seines "
                "Einkaufsverhaltens EINER Käufergruppe zu. Antworte NUR als JSON "
                '{"gruppe":"<key>","confidence":0.0-1.0,"begruendung":"kurz, faktenbasiert"}.\n\n'
                f"Mögliche Gruppen:\n{self._katalog_text()}\n\n"
                f"Signale (rollierend 12 M):\n"
                f"- Angebote: {s.angebote_12m}\n- Preisabfragen: {s.preisabfragen_12m}\n"
                f"- Abschlussquote: {s.abschlussquote:.2f}\n- Ø Rabatt: {s.rabatt_schnitt:.3f}\n"
                f"- Kauffrequenz: {s.kauffrequenz_12m}\n- Gesamt-Deckungsgrad: {s.deckung_gesamt_pct:.0f} %\n"
                f"- Mehrlieferanten-Wahrscheinlichkeit: {s.multi_lieferant_wahrsch:.2f}\n"
                f"- Saisonkonzentration: {s.saison_konzentration:.2f}\n- Jahresbedarf: {s.bedarf_gesamt_eur:.0f} €\n\n"
                "Beachte: bewusste Lieferantenstreuung ist ein legitimes Kundenmerkmal; "
                "100 % Deckung ist kein Standardziel."
            )
            resp = httpx.post(
                _ANTHROPIC_URL,
                headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={"model": _MODEL, "max_tokens": 400, "messages": [{"role": "user", "content": prompt}]},
                timeout=30.0,
            )
            resp.raise_for_status()
            out = resp.json()["content"][0]["text"].strip()
            out = re.sub(r"^```(?:json)?|```$", "", out.strip()).strip()
            data = json.loads(out)
            gruppe = BuyingGroup(data["gruppe"]) if data.get("gruppe") in {g.value for g in BuyingGroup} else BuyingGroup.UNBEKANNT
            conf = max(0.0, min(1.0, float(data.get("confidence", 0.6))))
            reason = str(data.get("begruendung") or "").strip() or "KI-Einschätzung ohne Begründung."
            return Klassifikation(gruppe, conf, f"KI: {reason}")
        except Exception as exc:  # pragma: no cover - Netzwerk/Key/Guthaben
            logger.warning("llm_klassifikation_fehlgeschlagen: %s — fallback rule_based", exc)
            return self._fallback.klassifiziere(s)


def get_klassifikator(prefer_ai: bool = False) -> Klassifikator:
    return LLMKlassifikator() if prefer_ai else RuleBasedKlassifikator()


def klassifiziere_mit(s: Verhaltenssignale, prefer_ai: bool = False) -> Tuple[Klassifikation, str]:
    """Gibt (Klassifikation, tatsächlich genutzte Quelle) zurück.

    Bei prefer_ai aber fehlendem Key/Fehler ist die Quelle 'rule_based' (Fallback),
    sonst 'ai_suggested'. So bildet die gespeicherte Quelle die Realität ab.
    """
    if prefer_ai and os.environ.get("ANTHROPIC_API_KEY"):
        kl = LLMKlassifikator().klassifiziere(s)
        source = "ai_suggested" if kl.begruendung.startswith("KI:") else "rule_based"
        return kl, source
    return RuleBasedKlassifikator().klassifiziere(s), "rule_based"
