"""Agentenautonomie (ADR-086): Politikfreigabe, Delegation, Qualitaetsmodell, Entscheidungsprotokoll.

Alle Schreibwege nehmen nur Personen vor (kein Agent, kein technisches Konto); das prueft der Dienst
(``app/services/agent_autonomie.py``) aus der geprueften Anmeldung. Testnachweise darf zusaetzlich ein
technisches CI-Konto melden - nie der Agent ueber sich selbst.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_roles
from app.core.database import get_db
from app.core.exceptions import DomainError
from app.core.tenant import get_tenant_id
from app.services import agent_autonomie as dienst

# Lesen und Schreiben nur fuer Fuehrung, Finanzbuchhaltung und Controlling; die fachlichen Regeln (Person, Rolle
# fuer die Politikfreigabe, eigenes Recht beim Delegieren) prueft der Dienst zusaetzlich.
AUTONOMIE_ROLLEN = ("admin", "GESCHAEFTSFUEHRUNG", "FINANCE_ADMIN", "FINANCE_BEARBEITEN", "CONTROLLING", "controller",
                    "SALES_ADMIN", "CI_TESTNACHWEIS")
router = APIRouter(prefix="/agenten/autonomie", tags=["agenten", "autonomie"],
                   dependencies=[Depends(require_roles(*AUTONOMIE_ROLLEN))])


class PolitikOut(BaseModel):
    policy_id: str
    version: str
    abdruck: str
    adr: Optional[str] = None
    freigegeben: bool
    freigegeben_von: Optional[str] = None
    freigegeben_am: Optional[datetime] = None
    faehigkeiten: list[str]


class DelegationIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent_id: str = Field(min_length=1, max_length=100)
    faehigkeit: str = Field(min_length=1, max_length=120)
    max_brutto: Optional[Decimal] = Field(default=None, gt=0)
    gueltig_bis: Optional[datetime] = None


class GrundIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    grund: str = Field(min_length=3, max_length=1000)


class MesspunktIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent_id: str = Field(min_length=1, max_length=100)
    faehigkeit: str = Field(min_length=1, max_length=120)
    art: Literal["korrigiert", "test_bestanden", "test_fehlgeschlagen"]
    vorgang: Optional[str] = Field(default=None, max_length=64)
    detail: dict[str, Any] = Field(default_factory=dict)


def _fachlich(aufruf):
    try:
        return aufruf()
    except DomainError as fehler:
        raise HTTPException(status_code=422 if "Berechtigung" not in str(fehler) else 403, detail=str(fehler)) from fehler


@router.get("/politik", response_model=PolitikOut, summary="Autonomiepolitik und ihr Freigabestand im Mandanten")
def politik(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> PolitikOut:
    p = dienst.lade_politik()
    frei = dienst.politik_freigabe(db, tenant_id, p)
    return PolitikOut(policy_id=p.policy_id, version=p.version, abdruck=p.abdruck, adr=p.inhalt.get("adr"),
                      freigegeben=frei is not None, freigegeben_von=(frei or {}).get("approved_by"),
                      freigegeben_am=(frei or {}).get("approved_at"), faehigkeiten=sorted(p.inhalt.get("faehigkeiten") or {}))


@router.post("/politik/actions/freigeben", response_model=PolitikOut, summary="Diese Fassung fachlich freigeben")
def politik_freigeben(body: dict[str, Any] = Body(...), db: Session = Depends(get_db),
                      tenant_id: str = Depends(get_tenant_id), nutzer: Any = Depends(get_current_user)) -> PolitikOut:
    _fachlich(lambda: dienst.gib_politik_frei(db, tenant_id, nutzer, str(body.get("notiz") or "")))
    db.commit()
    return politik(db, tenant_id)


@router.post("/politik/actions/widerrufen", response_model=PolitikOut, summary="Freigabe der Politik widerrufen")
def politik_widerrufen(body: GrundIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                       nutzer: Any = Depends(get_current_user)) -> PolitikOut:
    _fachlich(lambda: dienst.widerrufe_politik(db, tenant_id, nutzer, body.grund))
    db.commit()
    return politik(db, tenant_id)


@router.post("/delegationen/actions/anlegen", summary="Faehigkeit an einen Agenten delegieren")
def delegation_anlegen(body: DelegationIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                       nutzer: Any = Depends(get_current_user)) -> dict:
    ergebnis = _fachlich(lambda: dienst.delegiere(db, tenant_id, nutzer, agent_id=body.agent_id,
                                                  faehigkeit=body.faehigkeit, max_brutto=body.max_brutto,
                                                  gueltig_bis=body.gueltig_bis))
    db.commit()
    return ergebnis


@router.post("/delegationen/{delegation_id}/actions/widerrufen", summary="Delegation widerrufen")
def delegation_widerrufen(delegation_id: str, body: GrundIn, db: Session = Depends(get_db),
                          tenant_id: str = Depends(get_tenant_id), nutzer: Any = Depends(get_current_user)) -> dict:
    wer = _fachlich(lambda: dienst._person(nutzer, "Der Widerruf einer Delegation"))
    if not dienst.widerrufe_delegation(db, tenant_id, delegation_id, durch=wer, grund=body.grund):
        raise HTTPException(404, "Keine aktive Delegation mit dieser Kennung")
    db.commit()
    return {"id": delegation_id, "widerrufen": True}


@router.get("/delegationen", summary="Delegationen des Mandanten")
def delegationen(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> list[dict]:
    return [dict(z) for z in db.execute(text(
        "SELECT id, agent_id, capability, owner, max_brutto, valid_until, created_at, revoked_at, revoked_by, "
        "revoke_reason FROM domain_shared.agent_delegations WHERE tenant_id = :t ORDER BY created_at DESC"),
        {"t": tenant_id}).mappings().fetchmany(500)]


@router.post("/qualitaet/actions/erfassen", summary="Qualitaetsmesspunkt erfassen (Korrektur, Testnachweis)")
def messpunkt(body: MesspunktIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
              nutzer: Any = Depends(get_current_user)) -> dict:
    from app.services.freigabe_engine import technisches_konto

    wer = str((nutzer or {}).get("sub") or "").strip()
    if not wer:
        raise HTTPException(403, "Gepruefter Bearbeiter fehlt")
    # Eine Korrektur stellt nur eine Person fest; einen Testnachweis darf auch die CI melden.
    if body.art in dienst.ART_VON_MENSCHEN and technisches_konto(nutzer):
        raise HTTPException(403, "Eine Korrektur einer Agentenbuchung meldet nur eine Person.")
    _fachlich(lambda: dienst.erfasse(db, tenant_id, agent_id=body.agent_id, faehigkeit=body.faehigkeit, art=body.art,
                                     durch=wer, vorgang=body.vorgang, detail=body.detail))
    q = dienst.pruefe_qualitaet_und_entziehe(db, tenant_id, body.agent_id, body.faehigkeit)
    db.commit()
    return {"erfasst": True, "qualitaet": q.als_dict()}


@router.get("/qualitaet", summary="Qualitaetsmodell eines Agenten fuer eine Faehigkeit")
def qualitaet(agent_id: str = Query(..., max_length=100), faehigkeit: str = Query(..., max_length=120),
              db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict:
    return dienst.qualitaet(db, tenant_id, agent_id, faehigkeit).als_dict()


@router.get("/entscheidungen", summary="Protokoll der Autonomieentscheidungen")
def entscheidungen(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> list[dict]:
    return [dict(z) for z in db.execute(text(
        "SELECT id, agent_id, capability, subject_id, policy_version, outcome, risk, reasons, decided_at "
        "FROM domain_shared.agent_autonomy_decisions WHERE tenant_id = :t ORDER BY decided_at DESC"),
        {"t": tenant_id}).mappings().fetchmany(500)]


@router.get("/vertrauen", summary="Vertrauensstufe A0-A2 eines Agenten fuer eine Faehigkeit (Agent Trust)")
def vertrauen(agent_id: str = Query(..., max_length=100), faehigkeit: str = Query(..., max_length=120),
              db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict:
    return dienst.vertrauen(db, tenant_id, agent_id, faehigkeit)


@router.get("/lernvorschlaege", summary="Vorschlaege zur Weiterentwicklung der Politik (nie selbst wirksam)")
def lernvorschlaege(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> list[dict]:
    return dienst.lernvorschlaege(db, tenant_id)
