"""Loeschlauf mit Vier-Augen-Freigabe (M7 Loeschkonzept, Nutzerentscheid 26.11.2026).

Ablauf: ``beantrage`` (aus der Loeschpruefung, nur heute loeschbare Saetze einer Kategorie) -> ``entscheide`` (eine
zweite Person; der Antragsteller und technische Konten/Agenten entscheiden nie) -> ``fuehre_aus`` (prueft die
Loeschbarkeit erneut, loescht nur noch loeschbare Saetze und schreibt den Loeschnachweis ohne Inhalte).

Freigeschaltet sind zunaechst nur Kategorien ohne Buchungsbezug: ``handelsbrief`` (Angebote, Auftraege,
Bestellungen) und ``lieferschein``. Gebuchte Rechnungen und das Journal haengen an GoBD-Archiv und Hash-Kette; ein
Auftrag dafuer wird abgewiesen, statt halb zu loeschen.
"""
from __future__ import annotations

import json
from datetime import date
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError, PermissionDeniedError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.services.freigabe_engine import technisches_konto
from app.services.loeschpruefung import pruefe

FREIGESCHALTET = frozenset({"handelsbrief", "lieferschein"})
#: Abhaengige Docflow-Tabellen eines Belegkopfs, in Loeschreihenfolge (Fremdschluessel).
BELEG_ABHAENGIGE = (
    "domain_docflow.document_status_history", "domain_docflow.document_command_log", "domain_docflow.document_items",
)


def _person(nutzer: Any) -> str:
    if not isinstance(nutzer, dict):
        raise PermissionDeniedError("Angemeldete Person fehlt")
    name = str(nutzer.get("sub") or nutzer.get("preferred_username") or nutzer.get("name") or "").strip()
    if not name:
        raise PermissionDeniedError("Angemeldete Person fehlt")
    return name


def _auftrag(db: Session, tenant_id: str, auftrag_id: str, *, sperren: bool = True) -> dict[str, Any]:
    zeile = db.execute(text(
        "SELECT * FROM domain_shared.loeschauftraege WHERE tenant_id = :t AND id = :id"
        + (" FOR UPDATE" if sperren else "")), {"t": tenant_id, "id": auftrag_id}).mappings().first()
    if zeile is None:
        raise EntityNotFoundError("Loeschauftrag nicht gefunden")
    return dict(zeile)


def beantrage(db: Session, tenant_id: str, kategorie: str, antragsteller: Any, *,
              heute: Optional[date] = None, festsetzungsfrist_offen_bis: Optional[date] = None) -> dict[str, Any]:
    if kategorie not in FREIGESCHALTET:
        raise ValidationFailedError(f"Loeschweg fuer Kategorie {kategorie} ist nicht freigeschaltet "
                                    "(gebuchte Belege und Journal: GoBD-Archiv und Hash-Kette)")
    person = _person(antragsteller)
    bericht = pruefe(db, tenant_id, heute=heute, festsetzungsfrist_offen_bis=festsetzungsfrist_offen_bis)
    if bericht.get("vorbehalt"):
        raise ValidationFailedError("Ohne Datum der offenen Festsetzungsfrist wird nicht geloescht "
                                    "(§ 147 Abs. 3 Satz 5 AO) - Datum mit dem Steuerberater klaeren")
    kat = next((k for k in bericht["kategorien"] if k["dokumenttyp"] == kategorie), None)
    ids = list(kat["loeschbar_ids"]) if kat else []
    if not ids:
        raise ValidationFailedError(f"In Kategorie {kategorie} ist heute nichts loeschbar")
    auftrag_id = str(uuid7())
    db.execute(text(
        "INSERT INTO domain_shared.loeschauftraege (id, tenant_id, kategorie, satz_ids, anzahl, beantragt_von) "
        "VALUES (:id, :t, :k, CAST(:ids AS JSONB), :n, :p)"),
        {"id": auftrag_id, "t": tenant_id, "k": kategorie, "ids": json.dumps(ids), "n": len(ids), "p": person})
    db.commit()
    return {"id": auftrag_id, "kategorie": kategorie, "anzahl": len(ids), "status": "beantragt"}


def entscheide(db: Session, tenant_id: str, auftrag_id: str, entscheider: Any, *, erteilt: bool,
               grund: Optional[str] = None) -> dict[str, Any]:
    if technisches_konto(entscheider):
        raise PermissionDeniedError("Technische Konten und Agenten entscheiden keine Loeschung")
    person = _person(entscheider)
    auftrag = _auftrag(db, tenant_id, auftrag_id)
    if auftrag["status"] != "beantragt":
        raise ConflictError(f"Loeschauftrag ist {auftrag['status']}, nicht beantragt")
    if person == auftrag["beantragt_von"]:
        raise ConflictError("Vier-Augen-Prinzip: Wer die Loeschung beantragt hat, entscheidet sie nicht")
    status = "freigegeben" if erteilt else "abgelehnt"
    db.execute(text(
        "UPDATE domain_shared.loeschauftraege SET status = :s, entschieden_von = :p, entschieden_am = now(), "
        "grund = :g WHERE tenant_id = :t AND id = :id"),
        {"s": status, "p": person, "g": grund, "t": tenant_id, "id": auftrag_id})
    db.commit()
    return {"id": auftrag_id, "status": status}


def _loesche_belege(db: Session, tenant_id: str, ids: list[str]) -> int:
    if not ids:
        return 0
    db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))  # unveraenderliche Historie
    for tabelle in BELEG_ABHAENGIGE:
        db.execute(text(f"DELETE FROM {tabelle} WHERE tenant_id = :t AND header_id = ANY(:ids)"),  # nosec B608 - Konstanten
                   {"t": tenant_id, "ids": ids})
    for tabelle in ("domain_docflow.document_links", "domain_docflow.document_header_links"):
        db.execute(text(f"DELETE FROM {tabelle} WHERE tenant_id = :t "  # nosec B608 - Konstanten
                        "AND (from_header_id = ANY(:ids) OR to_header_id = ANY(:ids))"), {"t": tenant_id, "ids": ids})
    return db.execute(text("DELETE FROM domain_docflow.document_headers WHERE tenant_id = :t AND id = ANY(:ids)"),
                      {"t": tenant_id, "ids": ids}).rowcount


def fuehre_aus(db: Session, tenant_id: str, auftrag_id: str, ausfuehrer: Any, *, heute: Optional[date] = None,
               festsetzungsfrist_offen_bis: Optional[date] = None) -> dict[str, Any]:
    person = _person(ausfuehrer)
    auftrag = _auftrag(db, tenant_id, auftrag_id)
    if auftrag["status"] != "freigegeben":
        raise ConflictError(f"Loeschauftrag ist {auftrag['status']} - nur freigegebene Auftraege werden ausgefuehrt")
    bericht = pruefe(db, tenant_id, heute=heute, festsetzungsfrist_offen_bis=festsetzungsfrist_offen_bis)
    kat = next((k for k in bericht["kategorien"] if k["dokumenttyp"] == auftrag["kategorie"]), None)
    noch_loeschbar = set(kat["loeschbar_ids"]) if kat else set()
    ids = [i for i in auftrag["satz_ids"] if i in noch_loeschbar]  # inzwischen gesperrte Saetze bleiben
    gebucht = {str(z[0]) for z in db.execute(text(
        "SELECT DISTINCT header_id FROM domain_docflow.document_postings WHERE header_id = ANY(:ids)"),
        {"ids": ids}).fetchall()} if ids else set()
    loeschen = [i for i in ids if i not in gebucht]  # mit Buchungsbezug (z. B. Bestandsbuchung) nie loeschen
    geloescht = _loesche_belege(db, tenant_id, loeschen)
    nachweis = {"beantragt": auftrag["anzahl"], "geloescht": geloescht,
                "nicht_mehr_loeschbar": len(auftrag["satz_ids"]) - len(ids),
                "mit_buchungsbezug_uebersprungen": len(gebucht), "geloeschte_ids": loeschen,
                "stichtag": bericht["stichtag"], "rechtsgrundlage": kat["rechtsgrundlage"] if kat else None}
    db.execute(text(
        "UPDATE domain_shared.loeschauftraege SET status = 'ausgefuehrt', ausgefuehrt_von = :p, ausgefuehrt_am = now(), "
        "nachweis = CAST(:n AS JSONB) WHERE tenant_id = :t AND id = :id"),
        {"p": person, "n": json.dumps(nachweis), "t": tenant_id, "id": auftrag_id})
    db.commit()
    return {"id": auftrag_id, "status": "ausgefuehrt", **nachweis}
