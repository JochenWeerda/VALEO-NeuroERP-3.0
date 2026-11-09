"""Partnerstamm-Pflege in der Studio-Maske ``crm/customer-360`` (09.11.2026).

Die Untertabellen des Kunden (Anschriften, Ansprechpartner, CPD-Konten, Rabatte, Preisvereinbarungen,
Chef-Anweisungen) liess die Studio-Maske nur lesen; gepflegt wurde im handgebauten Kundenstamm
``verkauf/kunden-stamm`` (2.506 Zeilen, 15 eigene Schreibwege). Hier dieselben Fachwege des
``BusinessPartnerService`` als Kommandowege ``.../actions/<aktion>`` ueber ``run_delegated_mask_action``: Pruefung in
jedem Modus, Audit, Outbox, Wiederholungsschutz - fuer Maske, CLI und MCP.

* Anlegen haengt am Kunden (``/crm/customers/{entity_id}/actions/<bereich>_anlegen``); der Partner ist der
  Geschaeftspartner des Kunden (``customers.business_partner_id``).
* Aendern und Entfernen haengen an der Zeile (``/crm/kunden-stamm/<bereich>/{entity_id}/actions/aendern``).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from fastapi import APIRouter, Body, Depends
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

router = APIRouter(tags=["crm", "mask-actions"])


@dataclass(frozen=True)
class Bereich:
    key: str
    label: str
    tabelle: str
    schema: str  # Create-Schema in app.api.v1.endpoints.business_partners
    dienst: str  # Methodenstamm im BusinessPartnerService (create_/update_/delete_)
    felder: tuple[tuple[str, str, str], ...]  # (key, label, typ) der Eingabe; Auswahlwerte in AUSWAHL


BEREICHE: dict[str, Bereich] = {b.key: b for b in (
    Bereich("anschrift", "Anschrift", "business_partner_addresses", "AddressCreate", "address", (
        ("address_type", "Anschriftsart", "select"), ("name_1", "Name 1", "text"), ("name_2", "Name 2", "text"),
        ("street", "Straße", "text"), ("house_number", "Hausnummer", "text"), ("postal_code", "PLZ", "text"),
        ("city", "Ort", "text"), ("country", "Land", "text"), ("phone", "Telefon", "text"),
        ("email", "E-Mail", "text"))),
    Bereich("ansprechpartner", "Ansprechpartner", "business_partner_contacts", "ContactCreate", "contact", (
        ("salutation", "Anrede", "text"), ("first_name", "Vorname", "text"), ("last_name", "Nachname", "text"),
        ("position", "Funktion", "text"), ("department", "Abteilung", "text"), ("phone_1", "Telefon", "text"),
        ("mobile", "Mobil", "text"), ("email", "E-Mail", "text"))),
    Bereich("cpd", "CPD-Konto", "business_partner_cpd_accounts", "CpdAccountCreate", "cpd_account", (
        ("cpd_customer_number", "CPD-Kundennummer", "text"), ("debtor_account", "Debitorenkonto", "text"),
        ("name_1", "Name 1", "text"), ("street", "Straße", "text"), ("postal_code", "PLZ", "text"),
        ("city", "Ort", "text"), ("email", "E-Mail", "text"))),
    Bereich("rabatt", "Rabatt", "business_partner_discount_items", "DiscountItemCreate", "discount_item", (
        ("article_number", "Artikelnummer", "text"), ("description", "Bezeichnung", "text"),
        ("discount_percent", "Rabatt %", "number"), ("valid_from", "Gültig ab", "date"),
        ("valid_to", "Gültig bis", "date"))),
    Bereich("preis", "Preisvereinbarung", "business_partner_price_agreements", "PriceAgreementCreate",
            "price_agreement", (
        ("article_number", "Artikelnummer", "text"), ("description", "Bezeichnung", "text"),
        ("price_net", "Nettopreis", "currency"), ("price_unit", "Preiseinheit", "text"),
        ("valid_from", "Gültig ab", "date"), ("valid_to", "Gültig bis", "date"))),
    Bereich("anweisung", "Chef-Anweisung", "business_partner_instructions", "InstructionCreate", "instruction", (
        ("instruction_text", "Anweisung", "textarea"), ("instruction_priority", "Priorität", "text"),
        ("valid_from", "Gültig ab", "date"), ("valid_to", "Gültig bis", "date"))),
)}


# Feste Auswahlen der Create-Schemas (Feldname -> [(Wert, Bezeichnung)]).
AUSWAHL: dict[str, list[tuple[str, str]]] = {
    "address_type": [("customer", "Kundenanschrift"), ("invoice", "Rechnungsanschrift"),
                     ("shipping", "Lieferanschrift"), ("postal", "Postanschrift")],
}


def eingabefelder(bereich: Bereich) -> list[dict[str, Any]]:
    """Eingabefelder der Maske fuer einen Bereich (eine Quelle fuer ScreenDefinition, CLI und MCP)."""
    felder = []
    for key, label, typ in bereich.felder:
        feld: dict[str, Any] = {"key": key, "label": label, "type": typ}
        if typ == "select":
            feld["options"] = [{"value": wert, "label": text_} for wert, text_ in AUSWAHL[key]]
        felder.append(feld)
    return felder


def _blockiert(meldung: str, feld: str = "_entity") -> list[dict]:
    return [{"field": feld, "message": meldung, "severity": "blocking"}]


def _partner_des_kunden(session: Session, tid: str, kunde: str) -> str | None:
    return session.execute(text(
        "SELECT business_partner_id::text FROM domain_crm.customers WHERE tenant_id = :t "
        "AND (id::text = :k OR customer_number = :k OR business_partner_id::text = :k) LIMIT 1"),
        {"t": tid, "k": kunde}).scalar()


def _zeile_da(session: Session, tid: str, bereich: Bereich, zeile: str) -> bool:
    return bool(session.execute(text(
        f"SELECT 1 FROM domain_crm.{bereich.tabelle} WHERE tenant_id = :t AND id::text = :z"),  # nosec B608  # reviewed-safe: Tabelle aus der festen Bereichsliste
        {"t": tid, "z": zeile}).scalar())


def _eingabe(bereich: Bereich, payload: dict) -> dict:
    """Nur die deklarierten Felder, geprueft gegen das Create-Schema des Fachwegs; leere Werte fallen weg."""
    from app.api.v1.endpoints import business_partners as bp

    erlaubt = {key for key, _label, _typ in bereich.felder}
    werte = {k: v for k, v in payload.items() if k in erlaubt and v not in (None, "")}
    modell = getattr(bp, bereich.schema)
    return modell.model_validate(werte).model_dump(exclude_unset=True)


def _dienst(session: Session, tid: str):
    from app.services.business_partner_service import BusinessPartnerService

    return BusinessPartnerService(session, tid)


def _anlegen_fuer(bereich: Bereich) -> Callable:
    async def anlegen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                      db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
        def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
            if not _partner_des_kunden(session, tid, eid):
                return _blockiert("Kunde ohne Geschäftspartner - zuerst den Partner zuordnen.")
            try:
                if not _eingabe(bereich, payload):
                    return _blockiert("Keine Angaben.", "_input")
            except ValidationError as fehler:
                return _blockiert(fehler.errors()[0].get("msg", "Ungültige Angabe."), "_input")
            return []

        def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
            partner = _partner_des_kunden(session, tid, eid) or ""
            getattr(_dienst(session, tid), f"create_{bereich.dienst}")(partner, _eingabe(bereich, payload))
            return f"{bereich.label} angelegt."

        return await run_delegated_mask_action(
            db, action_key=f"{bereich.key}_anlegen", entity_type="kunde", entity_id=entity_id, tenant_id=tenant_id,
            body=body, check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type=f"crm.kunde.{bereich.key}_angelegt")

    return anlegen


def _zeilenaktion_fuer(bereich: Bereich, aktion: str) -> Callable:
    async def zeilenaktion(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                           db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
        def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
            if not _zeile_da(session, tid, bereich, eid):
                return _blockiert(f"{bereich.label} nicht gefunden.")
            if aktion == "aendern":
                try:
                    if not _eingabe(bereich, payload):
                        return _blockiert("Keine Änderung angegeben.", "_input")
                except ValidationError as fehler:
                    return _blockiert(fehler.errors()[0].get("msg", "Ungültige Angabe."), "_input")
            return []

        def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
            dienst = _dienst(session, tid)
            if aktion == "aendern":
                getattr(dienst, f"update_{bereich.dienst}")(eid, _eingabe(bereich, payload))
                return f"{bereich.label} geändert."
            getattr(dienst, f"delete_{bereich.dienst}")(eid)
            return f"{bereich.label} entfernt."

        return await run_delegated_mask_action(
            db, action_key=aktion, entity_type=f"kunde_{bereich.key}", entity_id=entity_id, tenant_id=tenant_id,
            body=body, check_fn=pruefen, delegate_fn=ausfuehren,
            outbox_event_type=f"crm.kunde.{bereich.key}_{'geaendert' if aktion == 'aendern' else 'entfernt'}",
            require_audit_reason=aktion == "entfernen")

    return zeilenaktion


for _b in BEREICHE.values():
    router.add_api_route(f"/crm/customers/{{entity_id}}/actions/{_b.key}_anlegen", _anlegen_fuer(_b),
                         methods=["POST"], response_model=MaskActionResult, summary=f"{_b.label} zum Kunden anlegen",
                         dependencies=SCHREIBEN["CRM"], name=f"kunde_{_b.key}_anlegen")
    for _aktion, _verb in (("aendern", "ändern"), ("entfernen", "entfernen")):
        router.add_api_route(f"/crm/kunden-stamm/{_b.key}/{{entity_id}}/actions/{_aktion}",
                             _zeilenaktion_fuer(_b, _aktion), methods=["POST"], response_model=MaskActionResult,
                             summary=f"{_b.label} {_verb}", dependencies=SCHREIBEN["CRM"],
                             name=f"kunde_{_b.key}_{_aktion}")
