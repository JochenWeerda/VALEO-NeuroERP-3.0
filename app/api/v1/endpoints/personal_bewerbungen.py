"""Bewerbermanagement — die Recruiting-Pipeline.

Herausgenommen aus `personal.py` am 06.10.2026 (Godfile-Ratsche). Die Zerlegung
hat den Code unveraendert uebernommen und die Maengel ausdruecklich benannt; der
Slice BEWERBERMANAGEMENT-ORDNUNG-20261006 behebt sie:

* ``except Exception: raise HTTPException(503, "applications table not available")``
  machte aus **jedem** Fehler eine Tabellenaussage — auch aus einem Rechtefehler
  oder einer verletzten Pruefbedingung. Jetzt deutet `fehler_deuten` den Fehler:
  eine fehlende Tabelle oder Spalte ist ein 503 mit Migrationshinweis, alles
  andere ein 409 mit dem Grund.
* Die Stufen waren ein ``set`` ohne Uebergaenge: Eine **abgelehnte** Bewerbung
  liess sich auf ``EINGESTELLT`` setzen. Jetzt gilt eine Uebergangstabelle, und
  `EINGESTELLT`/`ABGELEHNT` sind endgueltig.
* Eine Ablehnung braucht einen Grund (§ 22 AGG) — im Weg und in der Datenbank.
* Die Liste ist begrenzt, die Antwortmodelle sind typisiert, die Kennung ist
  `uuid7`.

Entscheidungen: ``docs/quality-assurance/bewerbermanagement-ordnung-20261006.md``.
"""

from __future__ import annotations

import logging
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session

from app.api.v1.schemas.personal_bewerbung_schemas import (
    AufbewahrungIn,
    AufbewahrungOut,
    BewerbungIn,
    BewerbungOut,
    EinwilligungIn,
    EinwilligungStandOut,
    EinwilligungVorgangOut,
    ErklaerungIn,
    ErklaerungOut,
    LoeschlaufIn,
    LoeschlaufOut,
    StufeIn,
    TrockenlaufOut,
)
from app.auth.deps import require_roles
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.services import bewerbung_einwilligung_service as einwilligung
from app.services import bewerbung_loeschlauf_service as loeschlauf
from app.services import bewerbung_service as dienst
from app.services.mask_action_runtime_service import MaskActionResult, parse_action_body

logger = logging.getLogger(__name__)

# Fachrollen ergaenzen die vorhandenen globalen Administrator-/Managerrollen.
# Aufbewahrung, Loeschung und verbindliche Fassungen verlangen Verwaltung.
personal_read = require_roles("PERSONAL_LESEN", "PERSONAL_BEARBEITEN", "PERSONAL_ADMIN", "admin", "manager")
personal_write = require_roles("PERSONAL_BEARBEITEN", "PERSONAL_ADMIN", "admin", "manager")
personal_admin = require_roles("PERSONAL_ADMIN", "admin")

router = APIRouter(prefix="/personal", tags=["personal", "hr", "recruiting"])


@router.get("/applications", response_model=List[BewerbungOut],
            summary="Bewerbungen auflisten", dependencies=[Depends(personal_read)])
async def list_applications(
    status: Optional[str] = Query(None, description="EINGANG | VORAUSWAHL | … | ABGELEHNT"),
    position_id: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Die Bewerbungen des Mandanten, optional nach Stufe oder Stelle gefiltert."""
    try:
        return dienst.auflisten(db, tenant_id, status, position_id, limit, offset)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Bewerbungen lesen", tenant_id) from fehler


@router.post("/applications", status_code=201, response_model=BewerbungOut,
             summary="Bewerbung erfassen", dependencies=[Depends(personal_write)])
async def create_application(
    payload: BewerbungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Erfasst eine Bewerbung im Stand `EINGANG`."""
    try:
        ergebnis = dienst.anlegen(db, tenant_id, str(uuid7()), payload)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Bewerbung anlegen", tenant_id) from fehler
    return ergebnis


# ── Speicherbegrenzung (Art. 5 Abs. 1 lit. e DSGVO) ──────────────────────────
# Diese vier Wege stehen **vor** ``/applications/{application_id}``. Stuenden sie
# danach, wuerde der Platzhalter ``aufbewahrung`` und ``loeschlaeufe`` als
# Bewerbungskennung lesen und 404 antworten. Ein Vertrag haelt die Reihenfolge fest.


@router.get("/applications/aufbewahrung", response_model=AufbewahrungOut,
            summary="Aufbewahrungsfrist für Bewerberdaten lesen", dependencies=[Depends(personal_read)])
async def get_bewerbung_aufbewahrung(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Die beschlossene Frist — oder 404, wenn keine beschlossen ist.

    Kein Standardwert: Eine Frist, die niemand beschlossen hat, ist keine
    Grundlage, um Daten zu vernichten.
    """
    try:
        regel = loeschlauf.regel(db, tenant_id)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Aufbewahrungsfrist lesen", tenant_id) from fehler
    if not regel:
        raise loeschlauf.ohne_regel(tenant_id)
    if regel.get("beschluss_am") is not None and hasattr(regel["beschluss_am"], "isoformat"):
        regel["beschluss_am"] = regel["beschluss_am"].isoformat()
    regel["aktiv"] = True
    return regel


@router.put("/applications/aufbewahrung", response_model=AufbewahrungOut,
            summary="Aufbewahrungsfrist für Bewerberdaten festlegen", dependencies=[Depends(personal_admin)])
async def set_bewerbung_aufbewahrung(
    payload: AufbewahrungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Legt die Frist fest. Je Mandant gilt **eine**.

    Die Frist ist eine Entscheidung des Hauses und wird deshalb nicht geraten.
    Ueblich sind 180 Tage nach der Entscheidung — zwei Monate Geltendmachung nach
    § 15 Abs. 4 AGG plus Zustellung und Klagefrist-Puffer.
    """
    try:
        ergebnis = loeschlauf.regel_setzen(db, tenant_id, str(uuid7()), payload)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(
            db, fehler, "Aufbewahrungsfrist festlegen", tenant_id
        ) from fehler
    return ergebnis


@router.get("/applications/loeschlauf/faellig", response_model=TrockenlaufOut,
            summary="Trockenlauf: was gelöscht würde", dependencies=[Depends(personal_read)])
async def get_loeschlauf_faellig(
    limit: int = Query(1000, ge=1, le=5000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Zeigt, was faellig waere — und aendert nichts.

    Personenbezogene Daten unbesehen zu vernichten ist leichtfertig; deshalb gibt
    es den Trockenlauf vor dem Lauf. Er nennt auch, **warum** eine Zeile bleibt:
    eine Loeschsperre (die Daten sind Beweismittel) oder eine Einwilligung.
    """
    try:
        regel = loeschlauf.regel(db, tenant_id)
        if not regel:
            raise loeschlauf.ohne_regel(tenant_id)
        tage = int(regel["aufbewahrung_tage"])
        faellige = loeschlauf.faellige(db, tenant_id, tage, limit)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Trockenlauf", tenant_id) from fehler
    return {
        "aufbewahrung_tage": tage,
        "stichtag": loeschlauf.stichtag(tage).isoformat(),
        "gesetzliche_grundlage": regel["gesetzliche_grundlage"],
        "geprueft": len(faellige),
        "wird_geloescht": sum(1 for z in faellige if z["wird_geloescht"]),
        "uebersprungen_sperre": sum(
            1 for z in faellige if z["bleibt_wegen"] == "LOESCHSPERRE"
        ),
        "uebersprungen_einwilligung": sum(
            1 for z in faellige if z["bleibt_wegen"] == "EINWILLIGUNG"
        ),
        "weitere_faellig": len(faellige) >= limit,
        "faellige": faellige,
    }


@router.get("/applications/loeschlaeufe", response_model=List[LoeschlaufOut],
            summary="Durchgeführte Löschläufe", dependencies=[Depends(personal_read)])
async def list_loeschlaeufe(
    limit: int = Query(100, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Der Nachweis gegenüber der Aufsicht: Zahlen, keine Namen."""
    try:
        return loeschlauf.laeufe(db, tenant_id, limit)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Loeschlaeufe lesen", tenant_id) from fehler


@router.post("/applications/loeschlauf", status_code=201, response_model=LoeschlaufOut,
             summary="Löschlauf durchführen", dependencies=[Depends(personal_admin)])
async def post_loeschlauf(
    payload: LoeschlaufIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Loescht die faelligen Bewerbungen und schreibt den Nachweis.

    Loeschung und Protokoll liegen in **einer** Transaktion: Ein Protokoll ohne
    Loeschung waere eine falsche Zusage, eine Loeschung ohne Protokoll ein
    unbelegter Eingriff.

    Offene Bewerbungen bleiben unberuehrt (ihnen fehlt der Fristanker), eine aktive
    Loeschsperre und eine laufende Einwilligung schuetzen vor Loeschung und
    erscheinen als uebersprungen.
    """
    try:
        regel = loeschlauf.regel(db, tenant_id)
        if not regel:
            raise loeschlauf.ohne_regel(tenant_id)
        ergebnis = loeschlauf.lauf_ausfuehren(
            db, tenant_id, str(uuid7()), regel, payload.durchgefuehrt_durch, payload.limit
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Loeschlauf", tenant_id) from fehler
    logger.info(
        "Loeschlauf %s (Mandant %s): %s geprueft, %s geloescht, %s gesperrt, %s eingewilligt",
        ergebnis["id"], tenant_id, ergebnis["geprueft"], ergebnis["geloescht"],
        ergebnis["uebersprungen_sperre"], ergebnis["uebersprungen_einwilligung"],
    )
    return ergebnis


# ── Die Einwilligungserklaerung in Fassungen ─────────────────────────────────
# Erteilt wird gegen eine **Fassung**, nicht gegen freien Text. Eine Fassung ist
# unveraenderlich (die Datenbank haelt das), deshalb gibt es kein PUT, PATCH oder
# DELETE: Ein neuer Wortlaut ist eine neue Fassung.
#
# Auch diese Wege stehen **vor** ``/applications/{application_id}``; sonst laese
# der Platzhalter "einwilligungserklaerungen" als Bewerbungskennung.


@router.get("/applications/einwilligungserklaerungen", response_model=List[ErklaerungOut],
            summary="Fassungen der Einwilligungserklärung", dependencies=[Depends(personal_read)])
async def list_erklaerungen(
    limit: int = Query(200, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Die Fassungen des Mandanten, neueste zuerst."""
    try:
        return einwilligung.erklaerungen_auflisten(db, tenant_id, limit)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Erklaerungen lesen", tenant_id) from fehler


@router.post("/applications/einwilligungserklaerungen", status_code=201,
             response_model=ErklaerungOut, summary="Neue Fassung der Einwilligungserklärung", dependencies=[Depends(personal_admin)])
async def post_erklaerung(
    payload: ErklaerungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Legt die naechste Fassung an.

    Derselbe Wortlaut ist **eine** Fassung: Ein zweites Anlegen antwortet 409 und
    nennt die vorhandene Nummer.
    """
    try:
        ergebnis = einwilligung.erklaerung_anlegen(
            db, tenant_id, str(uuid7()), payload.wortlaut, payload.erstellt_durch
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Erklaerung anlegen", tenant_id) from fehler
    return ergebnis


@router.get("/applications/einwilligungserklaerungen/{fassung}", response_model=ErklaerungOut,
            summary="Eine Fassung der Einwilligungserklärung", dependencies=[Depends(personal_read)])
async def get_erklaerung(
    fassung: int,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return einwilligung.erklaerung_lesen(db, tenant_id, fassung)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Erklaerung lesen", tenant_id) from fehler


@router.get("/applications/{application_id}", response_model=BewerbungOut,
            summary="Bewerbung abrufen", dependencies=[Depends(personal_read)])
async def get_application(
    application_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return dienst.als_dict(dienst.holen(db, tenant_id, application_id))
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Bewerbung lesen", tenant_id) from fehler


@router.patch("/applications/{application_id}/stage", response_model=BewerbungOut,
              summary="Stufe wechseln", dependencies=[Depends(personal_write)])
async def update_application_stage(
    application_id: str,
    payload: StufeIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Wechselt die Pipelinestufe.

    `EINGESTELLT` und `ABGELEHNT` sind endgueltig; eine Ablehnung braucht einen
    Grund. Vorher pruefte der Weg nur, ob die Stufe **existiert** — eine abgelehnte
    Bewerbung liess sich damit einstellen.
    """
    try:
        ergebnis = dienst.stufe_setzen(
            db, tenant_id, application_id, payload.stage,
            note=payload.note,
            ablehnungsgrund=payload.ablehnungsgrund,
            entschieden_durch=payload.entschieden_durch,
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Stufenwechsel", tenant_id) from fehler
    return ergebnis


@router.delete(
    "/applications/{application_id}",
    status_code=204,
    response_class=Response,
    response_model=None,
    summary="Bewerbung löschen",
 dependencies=[Depends(personal_admin)])
async def delete_application(
    application_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Löscht eine Bewerbung (nur eigener Mandant).

    Der Weg stammt von einem anderen Agenten (`f7fcbdd7c`) und bleibt in der Sache,
    wie er war; nur die Fehlerdeutung ist jetzt dieselbe wie bei den anderen Wegen.
    """
    try:
        dienst.loeschen(db, tenant_id, application_id)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Bewerbung loeschen", tenant_id) from fehler
    return None


# ── Die Einwilligung zur laengeren Aufbewahrung ───────────────────────────────
# Art. 6 Abs. 1 lit. a DSGVO (Talentpool). Der Loeschlauf achtete sie schon, aber es
# gab keinen Weg, sie zu erteilen oder zu widerrufen: Die Spalten waren da und
# niemand konnte sie fuellen.
#
# Diese drei Wege liegen **unter** `/applications/{application_id}` und koennen vom
# Platzhalter nicht verschluckt werden — ihr Pfad hat ein Segment mehr.


@router.get(
    "/applications/{application_id}/einwilligung",
    response_model=EinwilligungStandOut,
    summary="Einwilligung: Stand und Verzeichnis",
 dependencies=[Depends(personal_read)])
async def get_einwilligung(
    application_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Der heutige Stand **und** alle Vorgaenge.

    `laeuft` sagt, ob die Erlaubnis heute noch gilt; ein blosses Datum liesse das
    offen, und eine abgelaufene Einwilligung schuetzt nicht mehr vor dem Loeschlauf.
    """
    try:
        return einwilligung.stand(db, tenant_id, application_id)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Einwilligung lesen", tenant_id) from fehler


@router.post(
    "/applications/{application_id}/einwilligung",
    status_code=201,
    response_model=EinwilligungVorgangOut,
    summary="Einwilligung erteilen",
 dependencies=[Depends(personal_write)])
async def post_einwilligung(
    application_id: str,
    payload: EinwilligungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Erteilt die Einwilligung.

    Verzeichniszeile **und** operativer Stand in **einer** Transaktion: Eine
    Verzeichniszeile ohne Stand waere ein Nachweis ohne Wirkung — der Loeschlauf
    nimmt die Daten trotzdem mit.
    """
    try:
        ergebnis = einwilligung.erteilen(
            db, tenant_id, application_id, str(uuid7()), payload
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Einwilligung erteilen", tenant_id) from fehler
    return ergebnis


@router.delete(
    "/applications/{application_id}/einwilligung",
    status_code=201,
    response_model=EinwilligungVorgangOut,
    summary="Einwilligung widerrufen",
 dependencies=[Depends(personal_write)])
async def delete_einwilligung(
    application_id: str,
    erfasst_durch: Optional[str] = Query(None, max_length=120),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Widerruft die Einwilligung — **ohne Rumpf, ohne Grund, jederzeit**.

    Art. 7 Abs. 3 DSGVO: Der Widerruf darf nicht schwerer sein als die Erteilung.
    Deshalb verlangt dieser Weg nichts ausser der Bewerbung; `erfasst_durch` ist
    freiwillig.

    Die Erteilung bleibt im Verzeichnis stehen. Der Widerruf ist eine **neue** Zeile:
    Wer die Erteilung ueberschreibt, vernichtet den Nachweis, den Art. 7 Abs. 1
    verlangt.

    **Folge:** Die Bewerbung ist danach wieder loeschfaehig; der naechste Loeschlauf
    nimmt sie mit, wenn die Frist abgelaufen ist.
    """
    try:
        ergebnis = einwilligung.widerrufen(
            db, tenant_id, application_id, str(uuid7()), erfasst_durch
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Einwilligung widerrufen", tenant_id) from fehler
    return ergebnis


@router.post(
    "/applications/actions/speichern",
    response_model=MaskActionResult,
    summary="Bewerbung speichern als Masken-CommandEndpoint",
    dependencies=[Depends(personal_write)],
)
def action_bewerbung_speichern(
    request: Request,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    """CE fuer personal/bewerbungen:speichern — dryRun ohne INSERT; Token-Mandant."""
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
    try:
        opened = BewerbungIn.model_validate(payload)
    except Exception as exc:  # noqa: BLE001
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=False,
            error="Ungueltige Bewerbungsdaten.",
            validationErrors=[
                {"field": "_entity", "message": str(exc), "severity": "blocking"}
            ],
        )
    preview = {
        "applicant_name": opened.applicant_name,
        "applicant_email": opened.applicant_email,
        "position_title": opened.position_title,
        "source": opened.source,
        "tenant_id": tenant_id,
    }
    if mode != "execute":
        db.rollback()
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=True,
            summary="Bewerbung wuerde erfasst — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )
    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        created = dienst.anlegen(db, tenant_id, str(uuid7()), opened)
        entity_id = str(created["id"])
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="speichern",
            entity_type="hr_application",
            entity_id=entity_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Bewerbung {opened.applicant_name} erfasst",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="personal.bewerbung.created",
            aggregate_id=entity_id,
            payload={"id": entity_id, "tenant_id": tenant_id},
        )
        db.commit()
    except HTTPException as exc:
        db.rollback()
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return MaskActionResult(actionKey="speichern", mode=mode, success=False, error=detail)
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        try:
            raise dienst.fehler_deuten(db, fehler, "Bewerbung anlegen", tenant_id) from fehler
        except HTTPException as exc:
            detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
            return MaskActionResult(actionKey="speichern", mode=mode, success=False, error=detail)
    return MaskActionResult(
        actionKey="speichern",
        mode=mode,
        success=True,
        summary=f"Bewerbung {opened.applicant_name} erfasst.",
        affectedIds=[entity_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[preview],
    )


@router.post(
    "/applications/einwilligungserklaerungen/actions/anlegen",
    response_model=MaskActionResult,
    summary="Einwilligungserklaerung anlegen als Masken-CommandEndpoint",
    dependencies=[Depends(personal_admin)],
)
def action_erklaerung_anlegen(
    request: Request,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    """CE fuer personal/einwilligungserklaerungen:anlegen — dryRun ohne INSERT."""
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return MaskActionResult(
            actionKey="anlegen",
            mode="invalid",
            success=False,
            error="Unbekannter Aktionsmodus.",
            validationErrors=[
                {"field": "_mode", "message": "Ungueltiger Aktionsmodus", "severity": "blocking"}
            ],
        )
    try:
        opened = ErklaerungIn.model_validate(payload)
    except Exception as exc:  # noqa: BLE001
        return MaskActionResult(
            actionKey="anlegen",
            mode=mode,
            success=False,
            error="Ungueltiger Wortlaut.",
            validationErrors=[
                {"field": "wortlaut", "message": str(exc), "severity": "blocking"}
            ],
        )
    actor = request.headers.get("X-User-ID") or opened.erstellt_durch or "personal-user"
    preview = {
        "wortlaut": opened.wortlaut[:120],
        "erstellt_durch": actor,
        "tenant_id": tenant_id,
    }
    if mode != "execute":
        db.rollback()
        return MaskActionResult(
            actionKey="anlegen",
            mode=mode,
            success=True,
            summary="Fassung wuerde angelegt — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )
    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        created = einwilligung.erklaerung_anlegen(
            db, tenant_id, str(uuid7()), opened.wortlaut, actor
        )
        entity_id = str(created.get("id") or created.get("fassung") or "")
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="anlegen",
            entity_type="hr_consent_text",
            entity_id=entity_id or tenant_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Einwilligungsfassung angelegt by {actor}",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="personal.einwilligungserklaerung.created",
            aggregate_id=entity_id or tenant_id,
            payload={"id": entity_id, "tenant_id": tenant_id, "fassung": created.get("fassung")},
        )
        db.commit()
    except HTTPException as exc:
        db.rollback()
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return MaskActionResult(actionKey="anlegen", mode=mode, success=False, error=detail)
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        try:
            raise dienst.fehler_deuten(db, fehler, "Erklaerung anlegen", tenant_id) from fehler
        except HTTPException as exc:
            detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
            return MaskActionResult(actionKey="anlegen", mode=mode, success=False, error=detail)
    return MaskActionResult(
        actionKey="anlegen",
        mode=mode,
        success=True,
        summary="Einwilligungsfassung angelegt.",
        affectedIds=[entity_id] if entity_id else [],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[preview],
    )
