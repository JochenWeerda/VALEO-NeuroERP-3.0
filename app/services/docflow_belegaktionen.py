"""Aktionen der Belegmaske auf den Kommandos von DocFlow und der Approval Engine (BELEG-021).

Die Belegmaske loest eine Aktion aus, indem sie ihren Schluessel aus dem Belegvertrag nennt (``buchen``,
``umwandeln:sales_invoice``, ``freigabe_anfordern:post`` …). Hier wird daraus der Aufruf des einen Fachkommandos —
mit Idempotenzschluessel, Version, Mengen und dem Akteur aus der Anmeldung. Eigene Fachlogik gibt es nicht:

* **Ob** die Aktion geht, sagt der Belegvertrag (Zustand, Recht des Lesers, Freigabe) — dieselbe Auskunft, an der
  der Knopf der Maske haengt. Was dort gesperrt ist, wird hier mit demselben Grund abgelehnt.
* **Was** geschieht, tut ``DocflowService`` bzw. ``DocflowFreigabe``; ihre Pruefungen gelten unveraendert.

Der Idempotenzschluessel entsteht aus Beleg, Aktion und Belegversion: Derselbe Klick auf denselben Stand hat
dieselbe Wirkung genau einmal.
"""
from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from app.auth.beleg_roles import darf
from app.core.belegvertrag import BELEGARTEN, Beleg, Belegaktion
from app.core.exceptions import ConflictError, ValidationFailedError
from app.services.docflow_belegadapter import lies_beleg
from app.services.docflow_freigabe import DocflowFreigabe
from app.services.docflow_service import TRANSITIONS, DocflowService


def _sub(nutzer: Any) -> str:
    return str(nutzer.get("sub") or "").strip() if isinstance(nutzer, dict) else ""


def lies_fuer(db: Session, tenant_id: str, belegart: str, beleg_id: str, nutzer: Any) -> Optional[Beleg]:
    beleg = lies_beleg(DocflowService(db, tenant_id), beleg_id, lambda recht, art: darf(nutzer, recht, art), _sub(nutzer))
    return beleg if beleg is not None and beleg.belegart == belegart else None


def pruefe(db: Session, tenant_id: str, belegart: str, beleg_id: str, aktion: str, nutzer: Any,
           eingaben: dict[str, Any]) -> list[dict[str, Any]]:
    """Was der Ausfuehrung entgegensteht — leer, wenn nichts. Schreibt nicht."""
    def fehler(text: str, feld: str = "_entity") -> list[dict[str, Any]]:
        return [{"field": feld, "message": text, "severity": "blocking"}]

    beleg = lies_fuer(db, tenant_id, belegart, beleg_id, nutzer)
    if beleg is None:
        return fehler("Beleg nicht gefunden.")
    angebot: Optional[Belegaktion] = next((a for a in beleg.aktionen if a.key == aktion), None)
    if aktion.startswith("freigabe_ablehnen:"):
        # Ablehnen darf, wer erteilen duerfte.
        angebot = next((a for a in beleg.aktionen if a.key == aktion.replace("freigabe_ablehnen:", "freigabe_erteilen:")), None)
    if angebot is None:
        return fehler(f"Die Aktion ist für diesen Beleg im Stand „{beleg.status}“ nicht möglich.")
    if not angebot.erlaubt:
        return fehler(angebot.grund or "Die Aktion ist gesperrt.")
    version = eingaben.get("version")
    if version not in (None, "") and int(version) != beleg.version:
        return fehler("Der Beleg wurde inzwischen geändert. Bitte neu laden.", "version")
    if aktion == "stornieren" and len(str(eingaben.get("grund") or "").strip()) < 3:
        return fehler("Ein Storno braucht einen Grund.", "grund")
    return []


def fuehre_aus(db: Session, tenant_id: str, belegart: str, beleg_id: str, aktion: str, nutzer: Any,
               eingaben: dict[str, Any]) -> str:
    """Ruft das Fachkommando. Gibt in einem Satz zurueck, was geschehen ist."""
    akteur = _sub(nutzer)
    svc = DocflowService(db, tenant_id, akteur)
    kopf = svc.fetch_header(beleg_id)
    if not kopf or str(kopf["doc_type"]) != belegart:
        raise ValidationFailedError("Beleg nicht gefunden.")
    version = int(kopf.get("version") or 1)
    bezeichnung = BELEGARTEN[belegart].bezeichnung
    # Import hier: Die Anfragemodelle gehoeren dem DocFlow-Endpunkt; so bleibt es bei einer Definition.
    from app.api.v1.endpoints.docflow import (
        DocflowConvertRequest, DocflowPostRequest, DocflowReverseRequest,
    )

    def schluessel(was: str) -> str:
        return f"maske-{was}-{beleg_id}-v{version}"[:120]

    kern, _, ziel = aktion.partition(":")
    if kern == "freigeben":
        ergebnis = svc.release(beleg_id, schluessel("freigeben"), version, None)
        return f"{bezeichnung} freigegeben: {ergebnis.get('doc_number') or kopf['doc_number']}."
    if kern == "buchen":
        svc.post_document(beleg_id, DocflowPostRequest(idempotency_key=schluessel("buchen"), expected_version=version))
        return f"{bezeichnung} {kopf['doc_number']} gebucht."
    if kern == "stornieren":
        svc.reverse_document(beleg_id, DocflowReverseRequest(
            idempotency_key=schluessel("storno"), expected_version=version, reason=str(eingaben.get("grund") or "").strip()))
        return f"{bezeichnung} {kopf['doc_number']} storniert."
    if kern == "umwandeln":
        relation = TRANSITIONS.get(belegart, {}).get(ziel)
        if not relation:
            raise ValidationFailedError(f"{ziel} ist kein Folgebeleg von {bezeichnung}.")
        # Der ganze Rest je Position, ausdruecklich: Ein blosser Wiederholungsaufruf erzeugt keinen zweiten Folgebeleg.
        schon = svc.umgewandelte_mengen(beleg_id, relation)
        mengen = {}
        for position in svc.fetch_items(beleg_id):
            rest = float(position.get("quantity") or 0) - float(schon.get(str(position["id"]), 0))
            if rest > 0:
                mengen[str(position["id"])] = rest
        if not mengen:
            raise ConflictError("Alle Mengen sind bereits übernommen.")
        ergebnis = svc.convert(beleg_id, DocflowConvertRequest(
            target_doc_type=ziel, idempotency_key=schluessel(f"umwandeln-{ziel}"), expected_version=version,
            quantities_by_source_item_id=mengen))
        return f"{BELEGARTEN[ziel].bezeichnung} erstellt aus {bezeichnung} {kopf['doc_number']} (Beleg {ergebnis.get('target_doc_id')})."

    engine = DocflowFreigabe(db, tenant_id)
    if kern == "freigabe_anfordern":
        anfrage = engine.beantrage(beleg_id, ziel, akteur, str(eingaben.get("grund") or "").strip() or None)
        return f"Freigabe angefragt ({anfrage['risk']}) für {bezeichnung} {kopf['doc_number']}."
    if kern in ("freigabe_erteilen", "freigabe_ablehnen"):
        offene = engine.offene(kopf, ziel)
        if offene is None:
            raise ConflictError("Es gibt keine offene Freigabeanfrage für diesen Stand des Belegs.")
        erteilt = kern == "freigabe_erteilen"
        engine.entscheide(beleg_id, str(offene["id"]), nutzer, erteilt, str(eingaben.get("grund") or "").strip() or None)
        return f"Freigabe {'erteilt' if erteilt else 'abgelehnt'} für {bezeichnung} {kopf['doc_number']}."
    raise ValidationFailedError(f"Unbekannte Aktion: {aktion}")
