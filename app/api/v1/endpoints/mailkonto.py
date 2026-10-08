"""Postfaecher des Mandanten — Einrichtung, Freigaben, Testmail, Anmeldung bei Google/Microsoft.

Fachlogik in :mod:`app.services.mailkonto_service`. Einrichten nur ``admin``; die
Absenderwahl (``/verfuegbar``) darf jeder angemeldete Nutzer abfragen — sie zeigt
nur, woraus er senden darf. Passwort bzw. Google-Zugang wird nie zurueckgegeben.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_roles
from app.core.database import get_db
from app.core.geheimnis import GeheimnisNichtEingerichtet, GeheimnisUngueltig
from app.core.tenant import get_tenant_id
from app.services import mailkonto_service as konto
from app.services.mail_versand import MailVersandFehler, MailVersandNichtEingerichtet, MailVersandVerweigert

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
