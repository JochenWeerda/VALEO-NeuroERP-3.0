"""Bearbeiten nativer Objektmasken als Fachaktion fuer Maske, CLI und MCP (STAMMDATEN-BEARBEITEN-20261019).

Elf Objektmasken hatten einen Bearbeiten-Knopf ohne Wirkung (MASK-COMMANDS-ROLLOUT, Schritt 4: entfernt). Hier
bekommt jede einen Kommandoweg ``.../{entity_id}/actions/bearbeiten`` im Maskenformat. Er delegiert an den
**bestehenden** Aenderungsweg des Objekts (eine Fachaktion, mehrere Zugaenge) und legt den gemeinsamen Rahmen um
ihn (``app.services.mask_commands.bearbeiten``): deklarierte Felder, Trockenlauf, Wiederholung, Audit, Savepoint.

Die Auftragsbestaetigung ist ein Lieferantenbeleg — ihr Inhalt wird nicht bearbeitet; sie bekommt ihre
Zustandsschritte Pruefen und Bestaetigen. Die Reklamation aendert Zustaendigkeit und Frist mit Audit-Eintrag.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.api.v1.endpoints.leads import write_leads
from app.auth.deps import get_current_user, require_roles
from app.core.akteur import gepruefter_akteur_aus_request
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult
from app.services.mask_commands import bearbeiten, statusaktion, zeile_per_sql

router = APIRouter(tags=["mask-actions"])


def _gleich(*felder: str) -> dict[str, str]:
    """Maskenfeld und Feld des Aenderungsmodells heissen gleich."""
    return {feld: feld for feld in felder}


# --------------------------------------------------------------------------- Verkauf

@router.post("/sales/orders/{entity_id}/actions/bearbeiten", response_model=MaskActionResult,
             summary="Auftragskopf bearbeiten", dependencies=SCHREIBEN["VERKAUF"])
async def auftrag_bearbeiten(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                             db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    from app.api.v1.endpoints.sales_orders import SalesOrderUpdate, update_sales_order

    async def aendern(session: Session, werte: Any, eid: str, tid: str) -> None:
        await update_sales_order(eid, werte, tenant_id=tid, db=session)

    return await bearbeiten(
        db, entity_type="sales_order", entity_id=entity_id, tenant_id=tenant_id, body=body,
        felder=_gleich("subject", "delivery_date", "contact_person", "shipping_method", "payment_terms",
                       "delivery_address", "notes"),
        modell=SalesOrderUpdate, erlaubt={"open", "confirmed"},
        lesen=zeile_per_sql("SELECT status FROM domain_crm.sales_orders "
                            "WHERE id::text = :id AND tenant_id = :tid AND deleted_at IS NULL"),
        aendern=aendern, event_type="sales.order.updated")


# --------------------------------------------------------------------------- Kontrakt

# Dieselben Rollen wie die Kontraktaenderung selbst (``kontrakte.update_kontrakt``: KONTRAKT_BEARBEITEN/_ADMIN).
@router.post("/kontrakte/{entity_id}/actions/bearbeiten", response_model=MaskActionResult,
             summary="Kontrakt bearbeiten",
             dependencies=[Depends(require_roles("KONTRAKT_BEARBEITEN", "KONTRAKT_ADMIN"))])
async def kontrakt_bearbeiten(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                              db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                              user: dict = Depends(get_current_user)):
    from app.api.v1.endpoints.kontrakte import update_kontrakt
    from app.api.v1.schemas.kontrakte_schemas import KonContractIn
    from app.domains.operations.models import KonContract

    def ergaenzen(session: Session, eingabe: dict, eid: str, tid: str) -> dict[str, Any]:
        # Pflichtfelder des Kontraktmodells aus dem Ist-Stand; der Fachweg uebernimmt nur gesetzte Felder.
        k = session.query(KonContract).filter(KonContract.tenant_id == tid, KonContract.contract_id == eid).first()
        return {"contract_type": k.contract_type, "party_id": k.party_id} if k else {}

    async def aendern(session: Session, werte: Any, eid: str, tid: str) -> None:
        await update_kontrakt(eid, werte, db=session, tenant_id=tid, user=user)

    return await bearbeiten(
        db, entity_type="kontrakt", entity_id=entity_id, tenant_id=tenant_id, body=body,
        felder=_gleich("contract_date", "valid_from", "valid_to", "total_quantity", "unit", "payment_terms",
                       "notes"),
        modell=KonContractIn, erlaubt={"OFFEN"}, ergaenzen=ergaenzen,
        lesen=zeile_per_sql("SELECT status FROM domain_ops.kon_contract "
                            "WHERE contract_id::text = :id AND tenant_id = :tid"),
        aendern=aendern, event_type="kontrakt.updated")


# --------------------------------------------------------------------------- CRM

@router.post("/crm/opportunities/{entity_id}/actions/bearbeiten", response_model=MaskActionResult,
             summary="Verkaufschance bearbeiten", dependencies=SCHREIBEN["CRM"])
async def chance_bearbeiten(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                            db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    from app.api.v1.endpoints.opportunities import OpportunityUpdate, _opportunity_im_mandanten, update_opportunity

    async def lesen(session: Session, eid: str, tid: str) -> Optional[dict[str, Any]]:
        # crm-sales oder die lokale Pipeline-Tabelle, wie beim Lesen der Maske.
        try:
            return await _opportunity_im_mandanten(session, eid, tid)
        except HTTPException as exc:
            if exc.status_code == 404:
                return None
            raise

    async def aendern(session: Session, werte: Any, eid: str, tid: str) -> None:
        await update_opportunity(eid, werte, db=session, tenant_id=tid)

    return await bearbeiten(
        db, entity_type="opportunity", entity_id=entity_id, tenant_id=tenant_id, body=body,
        felder=_gleich("name", "assigned_to", "stage", "amount", "probability", "expected_close_date",
                       "lead_source"),
        modell=OpportunityUpdate, lesen=lesen, aendern=aendern, event_type="crm.opportunity.updated")


# Dieselben Rollen wie der Lead-Aenderungsweg (``leads.write_leads``: nur CRM-Rollen).
@router.post("/crm/leads/{entity_id}/actions/bearbeiten", response_model=MaskActionResult,
             summary="Lead bearbeiten", dependencies=[Depends(write_leads)])
async def lead_bearbeiten(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                          db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    from app.api.v1.endpoints.leads import LeadUpdate
    from app.services import crm_lead_service

    async def aendern(session: Session, werte: Any, eid: str, tid: str) -> None:
        crm_lead_service.update(session, tid, eid, werte.model_dump(exclude_unset=True))
        session.commit()

    return await bearbeiten(
        db, entity_type="lead", entity_id=entity_id, tenant_id=tenant_id, body=body,
        felder=_gleich("company_name", "contact_person", "email", "phone", "source", "estimated_value",
                       "priority", "assigned_to"),
        modell=LeadUpdate,
        lesen=zeile_per_sql("SELECT status FROM public.crm_leads WHERE id::text = :id AND tenant_id = :tid"),
        aendern=aendern, event_type="crm.lead.updated")


# --------------------------------------------------------------------------- Einkauf

@router.post("/einkauf/anfragen/{entity_id}/actions/bearbeiten", response_model=MaskActionResult,
             summary="Anfrage bearbeiten", dependencies=SCHREIBEN["EINKAUF"])
async def anfrage_bearbeiten(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                             db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    from app.einkauf.router import update_anfrage
    from app.einkauf.schemas import AnfrageUpdate

    async def aendern(session: Session, werte: Any, eid: str, tid: str) -> None:
        await update_anfrage(eid, werte, db=session, tenant_id=tid)

    return await bearbeiten(
        db, entity_type="anfrage", entity_id=entity_id, tenant_id=tenant_id, body=body,
        felder=_gleich("anforderer", "abteilung", "prioritaet", "artikel", "menge", "einheit", "begruendung",
                       "notizen"),
        modell=AnfrageUpdate,
        lesen=zeile_per_sql("SELECT status FROM einkauf_anfragen "
                            "WHERE (id = :id OR anfrage_nummer = :id) AND tenant_id = :tid"),
        aendern=aendern, event_type="einkauf.anfrage.updated")


_AB_STATUS = "SELECT status FROM einkauf_auftragsbestaetigungen WHERE (id = :id OR ab_nummer = :id) AND tenant_id = :tid"


async def _ab_schritt(db: Session, entity_id: str, tenant_id: str, body: dict[str, Any], *, schritt: str,
                      aktion: str, gesperrt: set[str], event_type: str) -> MaskActionResult:
    from app.services.einkauf_compat_service import EinkaufCompatService

    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        ergebnis = EinkaufCompatService(session, tenant_id).transition_auftragsbestaetigung(entity_id, schritt)
        return f"Auftragsbestaetigung {ergebnis['bestaetigungsNummer']}: {ergebnis['status']}."

    return await statusaktion(
        db, action_key=aktion, entity_type="auftragsbestaetigung", entity_id=entity_id, tenant_id=tenant_id,
        body=body, status_sql=_AB_STATUS, erlaubt=None, ausfuehren=ausfuehren, event_type=event_type,
        begruendung_pflicht=False,
        zusatzpruefung=lambda zeile: f"Bereits {zeile['status']}." if zeile["status"] in gesperrt else None)


@router.post("/einkauf/auftragsbestaetigungen/{entity_id}/actions/pruefen", response_model=MaskActionResult,
             summary="Auftragsbestaetigung pruefen", dependencies=SCHREIBEN["EINKAUF"])
async def ab_pruefen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                     db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await _ab_schritt(db, entity_id, tenant_id, body, schritt="review", aktion="pruefen",
                             gesperrt={"GEPRUEFT", "BESTAETIGT"}, event_type="einkauf.auftragsbestaetigung.reviewed")


@router.post("/einkauf/auftragsbestaetigungen/{entity_id}/actions/bestaetigen", response_model=MaskActionResult,
             summary="Auftragsbestaetigung bestaetigen", dependencies=SCHREIBEN["EINKAUF"])
async def ab_bestaetigen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                         db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await _ab_schritt(db, entity_id, tenant_id, body, schritt="confirm", aktion="bestaetigen",
                             gesperrt={"BESTAETIGT"}, event_type="einkauf.auftragsbestaetigung.confirmed")


# --------------------------------------------------------------------------- Finanzen

@router.post("/banken/konten/{entity_id}/actions/bearbeiten", response_model=MaskActionResult,
             summary="Bankkonto bearbeiten", dependencies=SCHREIBEN["FINANZ"])
async def bankkonto_bearbeiten(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                               db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    from app.api.v1.endpoints.banken import BankKontoUpdate, update_bankkonto

    async def aendern(session: Session, werte: Any, eid: str, tid: str) -> None:
        await update_bankkonto(eid, werte, db=session, tenant_id=tid)

    # Kein Saldo: er kommt aus den Kontoauszuegen, nie von Hand. IBAN/BIC aendern heisst neues Konto.
    return await bearbeiten(
        db, entity_type="bankkonto", entity_id=entity_id, tenant_id=tenant_id, body=body,
        felder={"bank": "bank_name", "kontoart": "kontoart", "ist_aktiv": "ist_aktiv"},
        modell=BankKontoUpdate, begruendung_pflicht=True,
        lesen=zeile_per_sql("SELECT status FROM domain_ops.ops_bankkonten WHERE id::text = :id AND tenant_id = :tid"),
        aendern=aendern, event_type="finance.bankkonto.updated")


@router.post("/finance/debitoren/{entity_id}/actions/bearbeiten", response_model=MaskActionResult,
             summary="Debitor bearbeiten", dependencies=SCHREIBEN["FINANZ"])
async def debitor_bearbeiten(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                             db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    from app.api.v1.endpoints.finance_stammdaten import DebitorPatch, patch_debitor

    async def aendern(session: Session, werte: Any, eid: str, tid: str) -> None:
        await patch_debitor(eid, werte, db=session, tenant_id=tid)

    return await bearbeiten(
        db, entity_type="debitor", entity_id=entity_id, tenant_id=tenant_id, body=body,
        felder=_gleich("credit_limit", "is_active"), modell=DebitorPatch, begruendung_pflicht=True,
        lesen=zeile_per_sql("SELECT CASE WHEN is_active THEN 'aktiv' ELSE 'gesperrt' END AS status "
                            "FROM domain_crm.customers WHERE id::text = :id AND tenant_id = :tid"),
        aendern=aendern, event_type="finance.debitor.updated")


@router.post("/finance/kreditoren/{entity_id}/actions/bearbeiten", response_model=MaskActionResult,
             summary="Kreditor bearbeiten", dependencies=SCHREIBEN["FINANZ"])
async def kreditor_bearbeiten(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                              db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    from app.api.v1.endpoints.finance_stammdaten import CreditorWrite, update_kreditor

    async def aendern(session: Session, werte: Any, eid: str, tid: str) -> None:
        await update_kreditor(eid, werte, db=session, tenant_id=tid)

    return await bearbeiten(
        db, entity_type="kreditor", entity_id=entity_id, tenant_id=tenant_id, body=body,
        felder=_gleich("company_name", "contact_person", "street", "postal_code", "city", "country", "phone",
                       "email", "vat_id", "tax_number", "payment_terms_days", "is_active", "notes"),
        modell=CreditorWrite, begruendung_pflicht=True,
        lesen=zeile_per_sql("SELECT CASE WHEN aktiv THEN 'aktiv' ELSE 'gesperrt' END AS status "
                            "FROM domain_einkauf.lieferanten WHERE id::text = :id AND tenant_id = :tid"),
        aendern=aendern, event_type="finance.kreditor.updated")


# --------------------------------------------------------------------------- Futtermittel

_MISCHFUTTER_FELDER = ("produkt_code", "name", "tierart", "leistungsstufe", "protein", "energie", "beschreibung")


@router.post("/futter/mischfuttermittel/{entity_id}/actions/bearbeiten", response_model=MaskActionResult,
             summary="Mischfuttermittel bearbeiten", dependencies=SCHREIBEN["FUTTERMITTEL"])
async def mischfutter_bearbeiten(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                                 db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    from app.api.v1.endpoints.futter_stamm import Mischfuttermittel, MischfuttermittelIn, update_mischfuttermittel

    def ergaenzen(session: Session, eingabe: dict, eid: str, tid: str) -> dict[str, Any]:
        # Der PUT ersetzt den ganzen Datensatz: nicht geaenderte Felder aus dem Ist-Stand, sonst wuerden sie geleert.
        m = session.query(Mischfuttermittel).filter(Mischfuttermittel.id == eid,
                                                    Mischfuttermittel.tenant_id == tid).first()
        return {feld: getattr(m, feld) for feld in _MISCHFUTTER_FELDER} if m else {}

    async def aendern(session: Session, werte: Any, eid: str, tid: str) -> None:
        await update_mischfuttermittel(eid, werte, tenant_id=tid, db=session)

    return await bearbeiten(
        db, entity_type="mischfuttermittel", entity_id=entity_id, tenant_id=tenant_id, body=body,
        felder=_gleich("name", "tierart", "leistungsstufe", "protein", "energie", "beschreibung"),
        modell=MischfuttermittelIn, ergaenzen=ergaenzen,
        lesen=zeile_per_sql("SELECT CASE WHEN aktiv THEN 'aktiv' ELSE 'inaktiv' END AS status "
                            "FROM domain_shared.futtermittel_mischfutter WHERE id::text = :id AND tenant_id = :tid"),
        aendern=aendern, event_type="futtermittel.mischfutter.updated")


# --------------------------------------------------------------------------- Qualitaet

class ReklamationAenderung(BaseModel):
    zustaendiger: Optional[str] = Field(default=None, min_length=1, max_length=200)
    frist_datum: Optional[date] = None


@router.post("/reklamationen/{entity_id}/actions/bearbeiten", response_model=MaskActionResult,
             summary="Reklamation: Zustaendigkeit und Frist", dependencies=SCHREIBEN["QUALITAET"])
async def reklamation_bearbeiten(entity_id: str, request: Request, body: dict[str, Any] = Body(default_factory=dict),
                                 db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    from app.api.v1.endpoints.reklamation_api import _add_audit, _query_reklamation
    from app.core.reklamation import ReklamationsStatus

    async def aendern(session: Session, werte: Any, eid: str, tid: str) -> None:
        zeile = _query_reklamation(session, eid, tid)
        neu = werte.model_dump(exclude_unset=True)
        vorher = {"zustaendiger": zeile.zustaendiger, "frist_datum": str(zeile.frist_datum)}
        for feld, wert in neu.items():
            setattr(zeile, feld, wert)
        _add_audit(zeile, "bearbeitet", gepruefter_akteur_aus_request(request), body.get("_auditReason"),
                   {"vorher": vorher, "nachher": {k: str(v) for k, v in neu.items()}})
        session.commit()

    return await bearbeiten(
        db, entity_type="reklamation", entity_id=entity_id, tenant_id=tenant_id, body=body,
        felder=_gleich("zustaendiger", "frist_datum"), modell=ReklamationAenderung,
        erlaubt={s.value for s in ReklamationsStatus if s is not ReklamationsStatus.GESCHLOSSEN},
        lesen=zeile_per_sql("SELECT status FROM domain_ops.reklamationen "
                            "WHERE reklamation_id::text = :id AND tenant_id = :tid"),
        aendern=aendern, event_type="qualitaet.reklamation.updated")
