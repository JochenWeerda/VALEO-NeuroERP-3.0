"""Purchase-order save implementation and its canonical input schema."""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
from app.services.procurement_service import EntityNotFoundError
from typing import Any, Callable
from fastapi import HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.services.mask_action_runtime_service import MaskActionResult, parse_action_body

class BestellungCreate(BaseModel):
    __module__ = "app.api.v1.endpoints.einkauf_bestellvorschlag"  # Preserve public OpenAPI schema identity.
    lieferant_id: str
    bestelldatum: date
    niederlassung_id: Optional[str] = None
    lieferdatum_wunsch: Optional[date] = None
    lieferdatum_zugesagt: Optional[date] = None
    versand_art: str = "email"
    kontrakt_id: Optional[str] = None
    unsere_referenz: Optional[str] = None
    ihre_referenz: Optional[str] = None
    freitext_kopf: Optional[str] = None
    freitext_fuss: Optional[str] = None
    notiz: Optional[str] = None
    bestellfall: Optional[str] = "bestand_abgleich"
    ansprechpartner: Optional[str] = None
    kreditor_konto: Optional[str] = None
    lieferant_nr: Optional[str] = None
    kostenstelle: Optional[str] = None
    kommission: Optional[str] = None
    ladetermin: Optional[date] = None
    ladetermin_ab: Optional[date] = None
    lade_datum: Optional[date] = None
    incoterms: Optional[str] = None
    lieferadresse: Optional[str] = None
    zahlungsbedingung: Optional[str] = None
    skonto1_tage: Optional[int] = None
    skonto1_prozent: Optional[float] = None
    skonto2_tage: Optional[int] = None
    skonto2_prozent: Optional[float] = None
    netto_tage: Optional[int] = None
    fremdwaehrung: Optional[str] = None
    umrechnungsfaktor: Optional[float] = None
    anfrage_nr: Optional[str] = None
    angebot_nr: Optional[str] = None
    auftrag_nr: Optional[str] = None
    abverkauf_horizont: Optional[str] = None
    bedarfsmenge: Optional[float] = None
    mindestbestellmenge: Optional[float] = None
    maximalbestellmenge: Optional[float] = None
    artikelgruppe: Optional[str] = None
    lagerplatz_opt: Optional[bool] = None
    fracht_opt: Optional[bool] = None
    opportunitaetskostensatz: Optional[float] = None
    palettenstellplatz_kosten: Optional[float] = None
    lagerkosten_satz: Optional[float] = None
    verkaufsbeleg_id: Optional[str] = None
    kunden_id: Optional[str] = None
    direktlieferung: Optional[bool] = None
    ueberschlag_lager: Optional[bool] = None
    neuer_artikel: Optional[bool] = None
    innovationshinweis: Optional[str] = None
    positionen: list[dict[str, Any]] = []


def action_bestellung_speichern(bestellung_id: str, request: Request, body: dict[str, Any], db: Session, tenant_id: str, *, ProcurementService: Callable, _PO_SAVE_ALLOWED: frozenset) -> MaskActionResult:
    """CE fuer einkauf/purchase-order:speichern — dryRun ohne UPDATE; Token-Mandant."""
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return MaskActionResult(
            actionKey="speichern",
            mode="invalid",
            success=False,
            error="Unbekannter Aktionsmodus.",
            validationErrors=[
                {"field": "_mode", "message": "Ungueltiger Aktionsmodus", "severity": "blocking"}
            ],
        )

    # Fremde Identitaetsfelder aus Payload nie uebernehmen (parse_action_body strippt tenant_*).
    patch = {k: v for k, v in payload.items() if k in _PO_SAVE_ALLOWED}
    if not patch:
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=False,
            error="Keine erlaubten Bestellfelder zum Speichern.",
            validationErrors=[
                {"field": "_entity", "message": "Mindestens ein Kopf-Feld erforderlich", "severity": "blocking"}
            ],
        )

    resolved = db.execute(
        text("""
            SELECT id::text AS id, bestellnummer, status
            FROM domain_einkauf.bestellungen
            WHERE tenant_id::text = :tenant
              AND (id::text = :bid OR bestellnummer = :bid)
            FOR SHARE
            LIMIT 1
        """),
        {"tenant": tenant_id, "bid": bestellung_id},
    ).mappings().first()
    if not resolved:
        db.rollback()
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=False,
            error="Bestellung nicht gefunden.",
            validationErrors=[
                {"field": "bestellung_id", "message": "Nicht im Authentifizierungs-Mandanten", "severity": "blocking"}
            ],
        )
    entity_id = str(resolved["id"])
    preview = {
        "bestellung_id": entity_id,
        "bestellnummer": resolved.get("bestellnummer"),
        "status": resolved.get("status"),
        "patch": patch,
        "tenant_id": tenant_id,
    }
    db.rollback()

    if mode != "execute":
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=True,
            summary="Bestellung wuerde gespeichert — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )

    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox
        from sqlalchemy.orm import Session as SASession

        with SASession(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            updated = ProcurementService(child, tenant_id).update_bestellung(entity_id, patch)
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="speichern",
            entity_type="einkauf_bestellung",
            entity_id=entity_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Bestellung {resolved.get('bestellnummer') or entity_id} gespeichert",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="einkauf.bestellung.updated",
            aggregate_id=entity_id,
            payload={"id": entity_id, "tenant_id": tenant_id, "fields": sorted(patch)},
        )
        db.commit()
    except EntityNotFoundError:
        db.rollback()
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=False,
            error="Bestellung nicht gefunden.",
        )
    except Exception:
        db.rollback()
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=False,
            error="Bestellung konnte nicht gespeichert werden.",
        )

    return MaskActionResult(
        actionKey="speichern",
        mode=mode,
        success=True,
        summary=f"Bestellung {resolved.get('bestellnummer') or entity_id} gespeichert.",
        affectedIds=[entity_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[{**preview, "updated": updated}],
    )


