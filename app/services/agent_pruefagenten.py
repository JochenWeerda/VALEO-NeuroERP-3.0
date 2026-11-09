"""Unabhaengige Pruefagenten (ADR-086): zusaetzliche fachliche Kontrolle vor einer autonomen Ausfuehrung.

Ein Pruefagent sieht den Vorgang, bevor ein ausfuehrender Agent ihn autonom bucht, und kann **nur Einwaende**
erheben - nie freigeben, nie eine Pruefung der Risiko-Engine ersetzen. Ein Einwand fuehrt zur menschlichen Freigabe
und zaehlt im Qualitaetsmodell des ausfuehrenden Agenten.

Unabhaengigkeit: Ein Pruefagent hat eine eigene Kennung; er prueft keinen Vorgang, den er selbst ausfuehrt
(``pruefe`` lehnt das ab). Welche Pruefagenten je Faehigkeit laufen, steht in der Autonomiepolitik.

Registriert ist der deterministische ``plausibilitaet``-Pruefer. Ein KI-Pruefagent schliesst sich ueber
``registriere`` an (z. B. ein Sprachmodell mit eigener Maschinenidentitaet); er liefert dieselbe Form: eine Liste
von Einwaenden. Faellt ein Pruefagent aus, gilt das als Einwand (fail-closed), nie als Zustimmung.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class Pruefkontext:
    tenant: str
    faehigkeit: str
    agent_id: str          # wer ausfuehren will
    vorgang: str
    brutto: Decimal
    daten: dict[str, Any]  # was der Pruefer ueber den Vorgang wissen darf


Pruefer = Callable[[Session, Pruefkontext], list[str]]


@dataclass(frozen=True)
class Pruefagent:
    kennung: str
    pruefe_vorgang: Pruefer


_REGISTER: dict[str, Pruefagent] = {}


def registriere(name: str, agent: Pruefagent) -> None:
    _REGISTER[name] = agent


def entferne(name: str) -> None:
    _REGISTER.pop(name, None)


def pruefe(db: Session, namen: list[str], kontext: Pruefkontext) -> list[str]:
    """Alle genannten Pruefagenten; jeder Ausfall und jede fehlende Unabhaengigkeit ist ein Einwand."""
    einwaende: list[str] = []
    for name in namen:
        agent = _REGISTER.get(name)
        if agent is None:
            einwaende.append(f"Pruefagent {name} ist nicht verfuegbar.")
            continue
        if agent.kennung == kontext.agent_id:
            einwaende.append(f"Pruefagent {name} prueft keinen eigenen Vorgang.")
            continue
        try:
            einwaende += [f"{name}: {e}" for e in agent.pruefe_vorgang(db, kontext)]
        except Exception as fehler:  # noqa: BLE001 - fail-closed: ein Ausfall ist ein Einwand, keine Zustimmung
            einwaende.append(f"Pruefagent {name} ist ausgefallen ({type(fehler).__name__}).")
    return einwaende


# ── Deterministischer Plausibilitaetspruefer fuer Gutschriften ──────────────────────────────────────────────────

def _gutschrift_plausibel(db: Session, k: Pruefkontext) -> list[str]:
    einwaende: list[str] = []
    bezug: Optional[dict[str, Any]] = db.execute(text(
        "SELECT q.id, q.doc_number, q.total_gross, q.status FROM domain_docflow.document_header_links l "
        "JOIN domain_docflow.document_headers q ON q.id = l.from_header_id AND q.tenant_id = l.tenant_id "
        "WHERE l.tenant_id = :t AND l.to_header_id = :z AND l.relation_type = 'invoice_to_credit_memo' LIMIT 1"),
        {"t": k.tenant, "z": k.vorgang}).mappings().first()
    if bezug is None:
        einwaende.append("Gutschrift ohne Bezugsrechnung.")
        return einwaende
    bisher = Decimal(str(db.execute(text(
        "SELECT COALESCE(SUM(g.total_gross), 0) FROM domain_docflow.document_header_links l "
        "JOIN domain_docflow.document_headers g ON g.id = l.to_header_id AND g.tenant_id = l.tenant_id "
        "WHERE l.tenant_id = :t AND l.from_header_id = :r AND l.relation_type = 'invoice_to_credit_memo' "
        "AND g.status = 'posted' AND g.id <> :z"), {"t": k.tenant, "r": bezug["id"], "z": k.vorgang}).scalar() or 0))
    rechnung = Decimal(str(bezug["total_gross"] or 0))
    if bisher + k.brutto > rechnung:
        einwaende.append(f"Gutschriften zur Rechnung {bezug['doc_number']} ueberstiegen deren Betrag "
                         f"({bisher + k.brutto} > {rechnung} EUR).")
    return einwaende


registriere("plausibilitaet", Pruefagent(kennung="pruefagent:plausibilitaet", pruefe_vorgang=_gutschrift_plausibel))
