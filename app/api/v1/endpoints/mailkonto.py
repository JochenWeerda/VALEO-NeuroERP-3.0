"""Postfaecher des Mandanten — Einrichtung, Freigaben, Testmail, Anmeldung bei Google/Microsoft.

Fachlogik in :mod:`app.services.mailkonto_service`. Einrichten nur ``admin``; die
Absenderwahl (``/verfuegbar``) darf jeder angemeldete Nutzer abfragen — sie zeigt
nur, woraus er senden darf. Passwort bzw. Google-Zugang wird nie zurueckgegeben.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_roles
from app.core.database import get_db
from app.core.geheimnis import GeheimnisNichtEingerichtet, GeheimnisUngueltig
from app.core.tenant import get_tenant_id
from app.services import mailkonto_service as konto
from app.services.mail_versand import MailVersandFehler, MailVersandNichtEingerichtet, MailVersandVerweigert
from app.services.mask_action_runtime_service import MaskActionResult, parse_action_body

router = APIRouter(prefix="/admin/postfaecher", tags=["admin", "mailkonto"])

verwaltung = require_roles("admin")


class PostfachOut(BaseModel):
    id: str
    kennung: str
    bezeichnung: Optional[str] = None
    anbieter: str
    anmeldung: str
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    sicherheit: Optional[str] = None
    benutzer: Optional[str] = None
    absender_email: str
    absender_name: Optional[str] = None
    zugang_von: Optional[str] = None
    ist_standard: bool = False
    verwendungen: list[str] = Field(default_factory=list)
    rollen: list[str] = Field(default_factory=list)
    benutzer_freigabe: list[str] = Field(default_factory=list)
    persoenlich_fuer: Optional[str] = None
    hat_geheimnis: bool = False
    status: str
    geprueft_am: Optional[str] = None
    letzter_fehler: Optional[str] = None
    updated_at: Optional[str] = None
    testmail_an: Optional[str] = None


class PostfachIn(BaseModel):
    kennung: str = Field(..., description="z. B. info, dispo, fibu, zentrale")
    bezeichnung: Optional[str] = None
    anbieter: str = Field("smtp", description="ionos | google | microsoft | smtp | alias")
    anmeldung: str = Field("passwort", description="passwort (auch App-Passwort) | oauth2 (Google, Microsoft 365)")
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    sicherheit: Optional[str] = Field(None, description="starttls | ssl")
    benutzer: Optional[str] = None
    absender_email: str
    absender_name: Optional[str] = None
    passwort: Optional[str] = Field(None, description="Nur schreiben; leer laesst das bisherige stehen")
    zugang_von: Optional[str] = Field(None, description="Bei Alias: Postfach, dessen Anmeldung genutzt wird")
    ist_standard: bool = False
    verwendungen: list[str] = Field(default_factory=list)
    rollen: list[str] = Field(default_factory=list)
    benutzer_freigabe: list[str] = Field(default_factory=list)
    persoenlich_fuer: Optional[str] = None


class VerwendungOut(BaseModel):
    key: str
    label: str


class AbsenderOut(BaseModel):
    id: str
    kennung: str
    absender_email: str
    absender_name: Optional[str] = None
    ist_standard: bool
    passt: bool


class TestmailIn(BaseModel):
    empfaenger: Optional[str] = None


class AnmeldungStartOut(BaseModel):
    url: str


class AnmeldungAbschlussIn(BaseModel):
    code: str
    state: str


def _fachfehler(fehler: Exception) -> HTTPException:
    if isinstance(fehler, GeheimnisNichtEingerichtet):
        return HTTPException(status_code=503, detail=str(fehler))
    if isinstance(fehler, konto.MailkontoFehler) and str(fehler) == "Postfach nicht gefunden.":
        return HTTPException(status_code=404, detail=str(fehler))
    return HTTPException(status_code=422, detail=str(fehler))


@router.get("", response_model=list[PostfachOut], summary="Postfaecher des Mandanten")
def postfaecher(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
                _: dict = Depends(verwaltung)) -> list[dict]:
    return konto.liste(db, tenant_id)


@router.get("/verwendungen", response_model=list[VerwendungOut], summary="Moegliche Verwendungen")
def verwendungen() -> list[dict]:
    return [{"key": k, "label": v} for k, v in konto.VERWENDUNGEN.items()]


@router.get("/verfuegbar", response_model=list[AbsenderOut], summary="Postfaecher, aus denen ich senden darf")
def verfuegbar(verwendung: Optional[str] = Query(None), tenant_id: str = Depends(get_tenant_id),
               db: Session = Depends(get_db), nutzer: dict = Depends(get_current_user)) -> list[dict]:
    return konto.verfuegbar(db, tenant_id, nutzer, verwendung)


@router.post("", response_model=PostfachOut, status_code=201, summary="Postfach anlegen")
def postfach_anlegen(daten: PostfachIn, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
                     nutzer: dict = Depends(verwaltung)) -> dict:
    try:
        return konto.speichern(db, tenant_id, daten.model_dump(), von=nutzer.get("sub"))
    except (konto.MailkontoFehler, GeheimnisNichtEingerichtet) as fehler:
        db.rollback()
        raise _fachfehler(fehler) from fehler


@router.post(
    "/actions/speichern",
    response_model=MaskActionResult,
    summary="Postfach speichern als Masken-CommandEndpoint",
)
def action_postfach_speichern(
    request: Request,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(verwaltung),
) -> MaskActionResult:
    """CE fuer admin/postfaecher:speichern — dryRun ohne INSERT/UPDATE; Token-Mandant."""
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
    postfach_id = str(payload.pop("postfach_id", "") or "").strip() or None
    try:
        opened = PostfachIn.model_validate(payload)
    except Exception as exc:  # noqa: BLE001
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=False,
            error="Ungueltige Postfachdaten.",
            validationErrors=[
                {"field": "_entity", "message": str(exc), "severity": "blocking"}
            ],
        )
    preview = {
        "kennung": opened.kennung,
        "absender_email": opened.absender_email,
        "anbieter": opened.anbieter,
        "postfach_id": postfach_id,
        "tenant_id": tenant_id,
        "hat_passwort": bool(opened.passwort),
    }
    if postfach_id:
        try:
            konto.lesen(db, tenant_id, postfach_id)
        except konto.MailkontoFehler:
            db.rollback()
            return MaskActionResult(
                actionKey="speichern",
                mode=mode,
                success=False,
                error="Postfach nicht gefunden.",
                validationErrors=[
                    {
                        "field": "postfach_id",
                        "message": "Nicht im Authentifizierungs-Mandanten",
                        "severity": "blocking",
                    }
                ],
            )
    if mode != "execute":
        db.rollback()
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=True,
            summary="Postfach wuerde gespeichert — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )
    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        saved = konto.speichern(
            db,
            tenant_id,
            opened.model_dump(),
            postfach_id=postfach_id,
            von=nutzer.get("sub") or request.headers.get("X-User-ID"),
        )
        entity_id = str(saved["id"])
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="speichern",
            entity_type="mailkonto",
            entity_id=entity_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Postfach {opened.kennung} gespeichert",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="admin.postfach.saved",
            aggregate_id=entity_id,
            payload={"id": entity_id, "kennung": opened.kennung, "tenant_id": tenant_id},
        )
        # speichern() committed already; audit/outbox need another commit
        db.commit()
    except (konto.MailkontoFehler, GeheimnisNichtEingerichtet) as fehler:
        db.rollback()
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=False,
            error=str(fehler),
        )
    except Exception:
        db.rollback()
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=False,
            error="Postfach konnte nicht gespeichert werden.",
        )
    return MaskActionResult(
        actionKey="speichern",
        mode=mode,
        success=True,
        summary=f"Postfach {opened.kennung} gespeichert.",
        affectedIds=[entity_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[preview],
    )


@router.put("/{postfach_id}", response_model=PostfachOut, summary="Postfach aendern")
def postfach_aendern(postfach_id: str, daten: PostfachIn, tenant_id: str = Depends(get_tenant_id),
                     db: Session = Depends(get_db), nutzer: dict = Depends(verwaltung)) -> dict:
    try:
        return konto.speichern(db, tenant_id, daten.model_dump(), postfach_id=postfach_id, von=nutzer.get("sub"))
    except (konto.MailkontoFehler, GeheimnisNichtEingerichtet) as fehler:
        db.rollback()
        raise _fachfehler(fehler) from fehler


@router.post("/{postfach_id}/testen", response_model=PostfachOut, summary="Testmail ueber das Postfach senden")
def postfach_testen(postfach_id: str, daten: TestmailIn, tenant_id: str = Depends(get_tenant_id),
                    db: Session = Depends(get_db), nutzer: dict = Depends(verwaltung)) -> dict:
    try:
        return konto.pruefen(db, tenant_id, postfach_id, daten.empfaenger, nutzer=nutzer)
    except konto.MailkontoFehler as fehler:
        raise _fachfehler(fehler) from fehler
    except MailVersandNichtEingerichtet as fehler:
        raise HTTPException(status_code=503, detail=str(fehler)) from fehler
    except MailVersandVerweigert as fehler:
        raise HTTPException(status_code=403, detail=str(fehler)) from fehler
    except (MailVersandFehler, GeheimnisUngueltig) as fehler:
        raise HTTPException(status_code=502, detail=str(fehler)) from fehler


@router.post("/{postfach_id}/anmeldung/start", response_model=AnmeldungStartOut,
             summary="Anmeldung bei Google oder Microsoft starten")
def anmeldung_start(postfach_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
                    _: dict = Depends(verwaltung)) -> dict:
    try:
        return konto.anmeldung_starten(db, tenant_id, postfach_id)
    except (konto.MailkontoFehler, GeheimnisNichtEingerichtet) as fehler:
        raise _fachfehler(fehler) from fehler


@router.post("/anmeldung/abschluss", response_model=PostfachOut, summary="Anmeldung beim Anbieter abschliessen")
def anmeldung_abschluss(daten: AnmeldungAbschlussIn, tenant_id: str = Depends(get_tenant_id),
                        db: Session = Depends(get_db), nutzer: dict = Depends(verwaltung)) -> dict:
    try:
        return konto.anmeldung_abschliessen(db, tenant_id, daten.code, daten.state, von=nutzer.get("sub"))
    except (konto.MailkontoFehler, GeheimnisNichtEingerichtet) as fehler:
        db.rollback()
        raise _fachfehler(fehler) from fehler


@router.delete("/{postfach_id}", status_code=204, response_class=Response, response_model=None,
               summary="Postfach entfernen")
def postfach_entfernen(postfach_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
                       _: dict = Depends(verwaltung)) -> Response:
    try:
        konto.entfernen(db, tenant_id, postfach_id)
    except konto.MailkontoFehler as fehler:
        raise _fachfehler(fehler) from fehler
    return Response(status_code=204)
