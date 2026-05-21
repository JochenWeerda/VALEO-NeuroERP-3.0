"""
Agrar Feldbuch — ERP-interne Endpoints (Landhandel-Mitarbeiter)

Schläge: CRUD per Kunde
Maßnahmen: CRUD (Spritztagebuch / Ackerschlagkartei)
from-lieferschein: Maßnahme aus Lieferschein erzeugen
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.infrastructure.models.agrar_models import (
    Duenger,
    FeldbuchMassnahme,
    FeldbuchSchlag,
    PSM,
    Saatgut,
)
from modules.agrar.services.feldbuch_service import (
    create_massnahme_from_lieferschein,
    validate_psm_compliance,
)

router = APIRouter(tags=["agrar", "feldbuch"])


# ────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ────────────────────────────────────────────────────────────────────────────

class SchlagCreate(BaseModel):
    customer_id: str
    name: str
    flik: Optional[str] = None
    flaeche: float
    kultur: Optional[str] = None
    vorkultur: Optional[str] = None
    gemeinde: Optional[str] = None
    gemarkung: Optional[str] = None
    bodenart: Optional[str] = None
    ackerzahl: Optional[float] = None
    status: str = "aktiv"
    created_by: Optional[str] = None


class SchlagUpdate(BaseModel):
    name: Optional[str] = None
    flik: Optional[str] = None
    flaeche: Optional[float] = None
    kultur: Optional[str] = None
    vorkultur: Optional[str] = None
    gemeinde: Optional[str] = None
    gemarkung: Optional[str] = None
    bodenart: Optional[str] = None
    ackerzahl: Optional[float] = None
    status: Optional[str] = None


class MassnahmeCreate(BaseModel):
    customer_id: str
    schlag_id: Optional[str] = None
    datum: datetime
    uhrzeit: Optional[str] = None
    typ: str
    bezeichnung: Optional[str] = None
    mittel: Optional[str] = None
    mittel_id: Optional[str] = None
    mittel_typ: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    flaeche: Optional[float] = None
    anwender: Optional[str] = None
    quelle: str = "erp_service"
    lieferschein_id: Optional[str] = None
    auflagen: Optional[list[str]] = None
    wartezeit_tage: Optional[int] = None
    windgeschwindigkeit: Optional[float] = None
    temperatur: Optional[float] = None
    compliant: bool = True
    bemerkung: Optional[str] = None


class MassnahmeUpdate(BaseModel):
    schlag_id: Optional[str] = None
    datum: Optional[datetime] = None
    uhrzeit: Optional[str] = None
    typ: Optional[str] = None
    bezeichnung: Optional[str] = None
    mittel: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    flaeche: Optional[float] = None
    anwender: Optional[str] = None
    auflagen: Optional[list[str]] = None
    wartezeit_tage: Optional[int] = None
    windgeschwindigkeit: Optional[float] = None
    temperatur: Optional[float] = None
    compliant: Optional[bool] = None
    bemerkung: Optional[str] = None


class FromLieferscheinCreate(BaseModel):
    lieferschein_id: str
    lieferschein_datum: datetime
    customer_id: str
    schlag_id: str
    artikel_name: str
    menge: float
    einheit: str
    flaeche: float
    anwender: str = "VALEO NeuroERP"


class MassnahmeBulkDeleteIn(BaseModel):
    ids: list[str] = Field(default_factory=list, min_length=1, max_length=100)


class MassnahmeBulkDeleteErrorOut(BaseModel):
    id: str
    detail: str


class MassnahmeBulkDeleteOut(BaseModel):
    requested: int
    deleted: int
    missing_ids: list[str] = Field(default_factory=list)
    errors: list[MassnahmeBulkDeleteErrorOut] = Field(default_factory=list)


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

def _schlag_to_dict(s: FeldbuchSchlag) -> dict[str, Any]:
    return {
        "id": s.id,
        "tenant_id": s.tenant_id,
        "customer_id": s.customer_id,
        "name": s.name,
        "flik": s.flik,
        "flaeche": s.flaeche,
        "kultur": s.kultur,
        "vorkultur": s.vorkultur,
        "gemeinde": s.gemeinde,
        "gemarkung": s.gemarkung,
        "bodenart": s.bodenart,
        "ackerzahl": s.ackerzahl,
        "status": s.status,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "created_by": s.created_by,
    }


def _massnahme_to_dict(m: FeldbuchMassnahme) -> dict[str, Any]:
    schlag_name = m.schlag.name if m.schlag else None
    return {
        "id": m.id,
        "tenant_id": m.tenant_id,
        "schlag_id": m.schlag_id,
        "schlag_name": schlag_name,
        "customer_id": m.customer_id,
        "datum": m.datum.date().isoformat() if m.datum else None,
        "uhrzeit": m.uhrzeit,
        "typ": m.typ,
        "bezeichnung": m.bezeichnung,
        "mittel": m.mittel,
        "mittel_id": m.mittel_id,
        "mittel_typ": m.mittel_typ,
        "menge": m.menge,
        "einheit": m.einheit,
        "flaeche": m.flaeche,
        "anwender": m.anwender,
        "quelle": m.quelle,
        "lieferschein_id": m.lieferschein_id,
        "auflagen": m.auflagen,
        "wartezeit_tage": m.wartezeit_tage,
        "windgeschwindigkeit": m.windgeschwindigkeit,
        "temperatur": m.temperatur,
        "compliant": m.compliant,
        "exportiert": m.exportiert,
        "exportiert_am": m.exportiert_am.isoformat() if m.exportiert_am else None,
        "bemerkung": m.bemerkung,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


# ────────────────────────────────────────────────────────────────────────────
# Schläge Endpoints
# ────────────────────────────────────────────────────────────────────────────

@router.get("/schlaege")
async def list_schlaege(
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    q = db.query(FeldbuchSchlag).filter(FeldbuchSchlag.tenant_id == tenant_id)
    if customer_id:
        q = q.filter(FeldbuchSchlag.customer_id == customer_id)
    if status:
        q = q.filter(FeldbuchSchlag.status == status)
    return [_schlag_to_dict(s) for s in q.order_by(FeldbuchSchlag.name).all()]


@router.post("/schlaege", status_code=201)
async def create_schlag(
    data: SchlagCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    schlag = FeldbuchSchlag(
        id=uuid7(),
        tenant_id=tenant_id,
        **data.model_dump(),
    )
    db.add(schlag)
    db.commit()
    db.refresh(schlag)
    return _schlag_to_dict(schlag)


@router.get("/schlaege/{schlag_id}")
async def get_schlag(
    schlag_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    schlag = (
        db.query(FeldbuchSchlag)
        .filter(FeldbuchSchlag.id == schlag_id, FeldbuchSchlag.tenant_id == tenant_id)
        .first()
    )
    if not schlag:
        raise HTTPException(status_code=404, detail="Schlag nicht gefunden")
    return _schlag_to_dict(schlag)


@router.put("/schlaege/{schlag_id}")
async def update_schlag(
    schlag_id: str,
    data: SchlagUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    schlag = (
        db.query(FeldbuchSchlag)
        .filter(FeldbuchSchlag.id == schlag_id, FeldbuchSchlag.tenant_id == tenant_id)
        .first()
    )
    if not schlag:
        raise HTTPException(status_code=404, detail="Schlag nicht gefunden")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(schlag, field, value)
    db.commit()
    db.refresh(schlag)
    return _schlag_to_dict(schlag)


@router.delete("/schlaege/{schlag_id}", status_code=204, response_class=Response, response_model=None)
async def deactivate_schlag(
    schlag_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    schlag = (
        db.query(FeldbuchSchlag)
        .filter(FeldbuchSchlag.id == schlag_id, FeldbuchSchlag.tenant_id == tenant_id)
        .first()
    )
    if not schlag:
        raise HTTPException(status_code=404, detail="Schlag nicht gefunden")
    schlag.status = "stillgelegt"
    db.commit()
    return Response(status_code=204)


# ────────────────────────────────────────────────────────────────────────────
# Maßnahmen Endpoints
# ────────────────────────────────────────────────────────────────────────────

@router.get("/feldbuch/massnahmen")
async def list_massnahmen(
    schlag_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    typ: Optional[str] = Query(None),
    von: Optional[str] = Query(None),   # ISO date string
    bis: Optional[str] = Query(None),   # ISO date string
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    q = (
        db.query(FeldbuchMassnahme)
        .filter(FeldbuchMassnahme.tenant_id == tenant_id)
    )
    if schlag_id:
        q = q.filter(FeldbuchMassnahme.schlag_id == schlag_id)
    if customer_id:
        q = q.filter(FeldbuchMassnahme.customer_id == customer_id)
    if typ:
        q = q.filter(FeldbuchMassnahme.typ == typ)
    if von:
        q = q.filter(FeldbuchMassnahme.datum >= datetime.fromisoformat(von))
    if bis:
        q = q.filter(FeldbuchMassnahme.datum <= datetime.fromisoformat(bis))
    return [_massnahme_to_dict(m) for m in q.order_by(FeldbuchMassnahme.datum.desc()).all()]


@router.post("/feldbuch/massnahmen", status_code=201)
async def create_massnahme(
    data: MassnahmeCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    # AGR-COM-02: PSM-Compliance-Prüfung vor dem Speichern
    compliance = validate_psm_compliance(
        typ=data.typ,
        datum=data.datum,
        mittel=data.mittel,
        menge=data.menge,
        einheit=data.einheit,
        flaeche=data.flaeche,
        anwender=data.anwender,
        auflagen=data.auflagen,
        wartezeit_tage=data.wartezeit_tage,
        windgeschwindigkeit=data.windgeschwindigkeit,
        temperatur=data.temperatur,
    )

    massnahme = FeldbuchMassnahme(
        id=uuid7(),
        tenant_id=tenant_id,
        compliant=compliance["compliant"],
        **data.model_dump(exclude={"compliant"}),
    )
    db.add(massnahme)
    db.commit()
    db.refresh(massnahme)

    result = _massnahme_to_dict(massnahme)
    result["compliance"] = compliance
    return result


@router.put("/feldbuch/massnahmen/{massnahme_id}")
async def update_massnahme(
    massnahme_id: str,
    data: MassnahmeUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    massnahme = (
        db.query(FeldbuchMassnahme)
        .filter(FeldbuchMassnahme.id == massnahme_id, FeldbuchMassnahme.tenant_id == tenant_id)
        .first()
    )
    if not massnahme:
        raise HTTPException(status_code=404, detail="Maßnahme nicht gefunden")

    update_data = data.model_dump(exclude_none=True)
    for field, value in update_data.items():
        if field != "compliant":
            setattr(massnahme, field, value)

    # AGR-COM-02: Re-validate compliance after update
    compliance = validate_psm_compliance(
        typ=massnahme.typ,
        datum=massnahme.datum,
        mittel=massnahme.mittel,
        menge=massnahme.menge,
        einheit=massnahme.einheit,
        flaeche=massnahme.flaeche,
        anwender=massnahme.anwender,
        auflagen=massnahme.auflagen,
        wartezeit_tage=massnahme.wartezeit_tage,
        windgeschwindigkeit=massnahme.windgeschwindigkeit,
        temperatur=massnahme.temperatur,
    )
    massnahme.compliant = compliance["compliant"]

    db.commit()
    db.refresh(massnahme)

    result = _massnahme_to_dict(massnahme)
    result["compliance"] = compliance
    return result


@router.delete("/feldbuch/massnahmen/{massnahme_id}", status_code=204, response_class=Response, response_model=None)
async def delete_massnahme(
    massnahme_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    massnahme = (
        db.query(FeldbuchMassnahme)
        .filter(FeldbuchMassnahme.id == massnahme_id, FeldbuchMassnahme.tenant_id == tenant_id)
        .first()
    )
    if not massnahme:
        raise HTTPException(status_code=404, detail="Maßnahme nicht gefunden")
    db.delete(massnahme)
    db.commit()
    return Response(status_code=204)


@router.post("/feldbuch/massnahmen/bulk-delete", response_model=MassnahmeBulkDeleteOut)
async def bulk_delete_massnahmen(
    payload: MassnahmeBulkDeleteIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MassnahmeBulkDeleteOut:
    ids = [massnahme_id for massnahme_id in payload.ids if massnahme_id]
    if not ids:
        raise HTTPException(status_code=400, detail="Keine Maßnahmen-IDs übergeben")

    found_massnahmen = (
        db.query(FeldbuchMassnahme)
        .filter(FeldbuchMassnahme.tenant_id == tenant_id, FeldbuchMassnahme.id.in_(ids))
        .all()
    )
    found_by_id = {str(massnahme.id): massnahme for massnahme in found_massnahmen}
    deleted = 0
    errors: list[MassnahmeBulkDeleteErrorOut] = []

    for massnahme_id in ids:
        massnahme = found_by_id.get(massnahme_id)
        if massnahme is None:
            continue
        try:
            db.delete(massnahme)
            deleted += 1
        except Exception as exc:
            errors.append(MassnahmeBulkDeleteErrorOut(id=massnahme_id, detail=str(exc)))

    if deleted > 0:
        db.commit()
    else:
        db.rollback()

    missing_ids = [massnahme_id for massnahme_id in ids if massnahme_id not in found_by_id]
    return MassnahmeBulkDeleteOut(
        requested=len(ids),
        deleted=deleted,
        missing_ids=missing_ids,
        errors=errors,
    )


@router.post("/feldbuch/massnahmen/from-lieferschein", status_code=201)
async def massnahme_from_lieferschein(
    data: FromLieferscheinCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """
    Erzeugt eine Feldbuch-Maßnahme aus einem Lieferschein mit PSM-Dienstleistung.
    Verhindert Duplikate (lieferschein_id unique per tenant).
    """
    massnahme = create_massnahme_from_lieferschein(
        db,
        lieferschein_id=data.lieferschein_id,
        lieferschein_datum=data.lieferschein_datum,
        customer_id=data.customer_id,
        schlag_id=data.schlag_id,
        artikel_name=data.artikel_name,
        menge=data.menge,
        einheit=data.einheit,
        flaeche=data.flaeche,
        anwender=data.anwender,
        tenant_id=tenant_id,
    )
    db.commit()
    db.refresh(massnahme)
    return _massnahme_to_dict(massnahme)


# ────────────────────────────────────────────────────────────────────────────
# AGR-COM-01: Düngebilanz
# ────────────────────────────────────────────────────────────────────────────

# Vereinfachte N-Gehalte gängiger Dünger (kg N pro kg bzw. l Produkt)
_DUENGER_N_GEHALT: dict[str, float] = {
    "kas": 0.27,             # Kalkammonsalpeter 27% N
    "harnstoff": 0.46,       # 46% N
    "an": 0.335,             # Ammoniumnitrat 33.5% N
    "npk 15-15-15": 0.15,    # NPK
    "ams": 0.26,             # Ammonsulfatsalpeter
    "guelle_rind": 0.004,    # ca. 4 kg N/m³
    "guelle_schwein": 0.006, # ca. 6 kg N/m³
}


@router.get("/feldbuch/duengebilanz")
async def get_duengebilanz(
    customer_id: Optional[str] = Query(None),
    schlag_id: Optional[str] = Query(None),
    jahr: int = Query(default=datetime.now().year),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """
    AGR-COM-01: Berechnet die Nährstoffbilanz (N) für ein Jahr.
    Basiert auf dokumentierten Düngemaßnahmen im Feldbuch.
    """
    from sqlalchemy import extract

    q = (
        db.query(FeldbuchMassnahme)
        .filter(
            FeldbuchMassnahme.tenant_id == tenant_id,
            FeldbuchMassnahme.typ == "duengung",
            extract("year", FeldbuchMassnahme.datum) == jahr,
        )
    )
    if customer_id:
        q = q.filter(FeldbuchMassnahme.customer_id == customer_id)
    if schlag_id:
        q = q.filter(FeldbuchMassnahme.schlag_id == schlag_id)

    massnahmen = q.all()

    bilanz_per_schlag: dict[str, dict[str, Any]] = {}
    gesamt_n = 0.0
    gesamt_flaeche = 0.0

    for m in massnahmen:
        sid = m.schlag_id or "unbekannt"
        if sid not in bilanz_per_schlag:
            schlag_name = m.schlag.name if m.schlag else sid
            bilanz_per_schlag[sid] = {
                "schlag_id": sid,
                "schlag_name": schlag_name,
                "flaeche_ha": m.schlag.flaeche if m.schlag else 0.0,
                "n_gesamt_kg": 0.0,
                "massnahmen_count": 0,
                "details": [],
            }

        # N-Gehalt ableiten (vereinfacht nach Mittel-Name)
        mittel_key = (m.mittel or "").lower().strip()
        n_faktor = next(
            (v for k, v in _DUENGER_N_GEHALT.items() if k in mittel_key),
            0.0,
        )
        n_menge = (m.menge or 0.0) * (m.flaeche or 0.0) * n_faktor

        bilanz_per_schlag[sid]["n_gesamt_kg"] += n_menge
        bilanz_per_schlag[sid]["massnahmen_count"] += 1
        bilanz_per_schlag[sid]["details"].append({
            "datum": m.datum.date().isoformat() if m.datum else None,
            "mittel": m.mittel,
            "menge": m.menge,
            "einheit": m.einheit,
            "flaeche_ha": m.flaeche,
            "n_kg_berechnet": round(n_menge, 2),
        })

        gesamt_n += n_menge
        if m.flaeche:
            gesamt_flaeche += m.flaeche

    # DüV-Grenzwert: 170 kg N/ha (organisch) bzw. bedarfsgerecht (mineralisch)
    grenzwert_n_ha = 170.0

    schlag_bilanzen = []
    ueberschreitungen = 0
    for sb in bilanz_per_schlag.values():
        ha = sb["flaeche_ha"] or 1.0
        n_pro_ha = sb["n_gesamt_kg"] / ha if ha > 0 else 0.0
        sb["n_pro_ha"] = round(n_pro_ha, 2)
        sb["n_gesamt_kg"] = round(sb["n_gesamt_kg"], 2)
        sb["grenzwert_n_ha"] = grenzwert_n_ha
        sb["ueberschreitung"] = n_pro_ha > grenzwert_n_ha
        if sb["ueberschreitung"]:
            ueberschreitungen += 1
        schlag_bilanzen.append(sb)

    return {
        "jahr": jahr,
        "tenant_id": tenant_id,
        "customer_id": customer_id,
        "gesamt_n_kg": round(gesamt_n, 2),
        "gesamt_flaeche_ha": round(gesamt_flaeche, 2),
        "durchschnitt_n_pro_ha": round(gesamt_n / gesamt_flaeche, 2) if gesamt_flaeche > 0 else 0.0,
        "grenzwert_n_pro_ha": grenzwert_n_ha,
        "ueberschreitungen": ueberschreitungen,
        "compliant": ueberschreitungen == 0,
        "schlaege": schlag_bilanzen,
    }


# ────────────────────────────────────────────────────────────────────────────
# AGR-COM-03: Cross-Compliance-Bericht
# ────────────────────────────────────────────────────────────────────────────

@router.get("/feldbuch/cross-compliance")
async def get_cross_compliance_report(
    customer_id: Optional[str] = Query(None),
    jahr: int = Query(default=datetime.now().year),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """
    AGR-COM-03: Zusammenfassender Cross-Compliance-Bericht.
    Prüft: Spritztagebuch-Vollständigkeit, Düngebilanz, Schlag-Dokumentation.
    """
    from sqlalchemy import extract

    # 1. Spritztagebuch: alle PSM-Maßnahmen im Jahr
    psm_q = db.query(FeldbuchMassnahme).filter(
        FeldbuchMassnahme.tenant_id == tenant_id,
        FeldbuchMassnahme.typ == "psm",
        extract("year", FeldbuchMassnahme.datum) == jahr,
    )
    if customer_id:
        psm_q = psm_q.filter(FeldbuchMassnahme.customer_id == customer_id)

    psm_total = psm_q.count()
    psm_compliant = psm_q.filter(FeldbuchMassnahme.compliant == True).count()
    psm_non_compliant = psm_total - psm_compliant

    # 2. Düngemaßnahmen
    dueng_q = db.query(FeldbuchMassnahme).filter(
        FeldbuchMassnahme.tenant_id == tenant_id,
        FeldbuchMassnahme.typ == "duengung",
        extract("year", FeldbuchMassnahme.datum) == jahr,
    )
    if customer_id:
        dueng_q = dueng_q.filter(FeldbuchMassnahme.customer_id == customer_id)
    dueng_total = dueng_q.count()

    # 3. Schlag-Dokumentation
    schlag_q = db.query(FeldbuchSchlag).filter(
        FeldbuchSchlag.tenant_id == tenant_id,
        FeldbuchSchlag.status == "aktiv",
    )
    if customer_id:
        schlag_q = schlag_q.filter(FeldbuchSchlag.customer_id == customer_id)

    schlaege = schlag_q.all()
    schlaege_total = len(schlaege)
    schlaege_ohne_kultur = sum(1 for s in schlaege if not s.kultur)
    schlaege_ohne_flaeche = sum(1 for s in schlaege if not s.flaeche or s.flaeche <= 0)

    # 4. Gesamtbewertung
    findings: list[dict[str, Any]] = []

    if psm_non_compliant > 0:
        findings.append({
            "bereich": "Spritztagebuch",
            "severity": "error",
            "text": f"{psm_non_compliant} von {psm_total} PSM-Anwendungen nicht vollständig dokumentiert (§11 PflSchG)",
        })

    if psm_total == 0:
        findings.append({
            "bereich": "Spritztagebuch",
            "severity": "info",
            "text": "Keine PSM-Anwendungen im Berichtsjahr dokumentiert",
        })

    if schlaege_ohne_kultur > 0:
        findings.append({
            "bereich": "Schlagkartei",
            "severity": "warning",
            "text": f"{schlaege_ohne_kultur} Schläge ohne Kulturangabe",
        })

    if schlaege_ohne_flaeche > 0:
        findings.append({
            "bereich": "Schlagkartei",
            "severity": "warning",
            "text": f"{schlaege_ohne_flaeche} Schläge ohne gültige Flächenangabe",
        })

    if dueng_total == 0 and schlaege_total > 0:
        findings.append({
            "bereich": "Düngebilanz",
            "severity": "info",
            "text": "Keine Düngemaßnahmen dokumentiert — Stoffstrombilanz nicht berechenbar",
        })

    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = sum(1 for f in findings if f["severity"] == "warning")

    return {
        "jahr": jahr,
        "tenant_id": tenant_id,
        "customer_id": customer_id,
        "status": "nicht_bestanden" if errors > 0 else "bestanden_mit_hinweisen" if warnings > 0 else "bestanden",
        "zusammenfassung": {
            "spritztagebuch": {
                "gesamt": psm_total,
                "compliant": psm_compliant,
                "non_compliant": psm_non_compliant,
            },
            "duengung": {
                "massnahmen": dueng_total,
            },
            "schlagkartei": {
                "gesamt": schlaege_total,
                "ohne_kultur": schlaege_ohne_kultur,
                "ohne_flaeche": schlaege_ohne_flaeche,
            },
        },
        "findings": findings,
        "errors": errors,
        "warnings": warnings,
    }


# ────────────────────────────────────────────────────────────────────────────
# AGR-OPS-04: Feldkalender
# ────────────────────────────────────────────────────────────────────────────

@router.get("/feldbuch/calendar")
async def get_feldkalender(
    von: str = Query(..., description="Startdatum (YYYY-MM-DD)"),
    bis: str = Query(..., description="Enddatum (YYYY-MM-DD)"),
    customer_id: Optional[str] = Query(None),
    schlag_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """
    AGR-OPS-04: Feldkalender — geplante und durchgeführte Maßnahmen nach Datum.
    """
    from datetime import datetime as dt
    von_dt = dt.fromisoformat(von)
    bis_dt = dt.fromisoformat(bis)

    q = (
        db.query(FeldbuchMassnahme)
        .filter(
            FeldbuchMassnahme.tenant_id == tenant_id,
            FeldbuchMassnahme.datum >= von_dt,
            FeldbuchMassnahme.datum <= bis_dt,
        )
    )
    if customer_id:
        q = q.filter(FeldbuchMassnahme.customer_id == customer_id)
    if schlag_id:
        q = q.filter(FeldbuchMassnahme.schlag_id == schlag_id)

    massnahmen = q.order_by(FeldbuchMassnahme.datum).all()
    by_date: dict[str, list[dict[str, Any]]] = {}
    for m in massnahmen:
        d = m.datum.date().isoformat() if m.datum else ""
        if d not in by_date:
            by_date[d] = []
        by_date[d].append(_massnahme_to_dict(m))

    return {
        "von": von,
        "bis": bis,
        "tenant_id": tenant_id,
        "total": len(massnahmen),
        "by_date": by_date,
    }


# ────────────────────────────────────────────────────────────────────────────
# AGR-COM-04/05: QS-Export, LEA-Export (Stubs)
# ────────────────────────────────────────────────────────────────────────────

_FELDBLOCKFINDER_URLS: dict[str, str] = {
    "DE-BY": "https://www.landwirtschaft.bayern.de/agrarmarkt/32497/index.php",
    "DE-NW": "https://www.landwirtschaftskammer.de/landwirtschaft/feldblockfinder/",
    "DE-NI": "https://www.lwk-niedersachsen.de/index.cfm/portal/6/nav/338.html",
    "DE-BW": "https://www.landwirtschaft-bw.de/",
    "default": "https://www.feldblockfinder.de/",
}


@router.get("/config/feldblockfinder")
async def get_feldblockfinder_config() -> dict[str, Any]:
    """
    AGR-FLD-03: Feldblockfinder-URLs pro Bundesland für iframe-Integration.
    """
    return {
        "urls": _FELDBLOCKFINDER_URLS,
        "default": _FELDBLOCKFINDER_URLS["default"],
    }


@router.post("/compliance/qs-export")
async def qs_export(
    jahr: int = Query(default=datetime.now().year),
    format: str = Query("json", description="json | csv"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """
    AGR-COM-04: QS/GQS-Export-Stub für Qualitätssicherung.
    Liefert strukturierte Feldbuch-Daten für QS-Audits.
    """
    from sqlalchemy import extract
    q = db.query(FeldbuchMassnahme).filter(
        FeldbuchMassnahme.tenant_id == tenant_id,
        extract("year", FeldbuchMassnahme.datum) == jahr,
    )
    items = [_massnahme_to_dict(m) for m in q.order_by(FeldbuchMassnahme.datum).all()]
    return {"jahr": jahr, "format": format, "count": len(items), "data": items}


@router.post("/compliance/lea-export")
async def lea_export(
    jahr: int = Query(default=datetime.now().year),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """
    AGR-COM-05: LEA-Export-Stub (Förderanträge).
    Liefert aggregierte Flächen- und Kulturdaten für LEA-Anträge.
    """
    schlaege = db.query(FeldbuchSchlag).filter(
        FeldbuchSchlag.tenant_id == tenant_id,
        FeldbuchSchlag.status == "aktiv",
    ).all()
    flaechen = [
        {"schlag_id": s.id, "name": s.name, "flaeche_ha": s.flaeche, "kultur": s.kultur}
        for s in schlaege
    ]
    gesamt_ha = sum(s.flaeche for s in schlaege)
    return {"jahr": jahr, "schlaege": len(schlaege), "gesamt_ha": gesamt_ha, "details": flaechen}


# ────────────────────────────────────────────────────────────────────────────
# AGR-INV-04: Mindestbestand-Warnung (Betriebsmittel)
# ────────────────────────────────────────────────────────────────────────────

@router.get("/inventory/low-stock")
async def get_low_stock_warnings(
    threshold: float = Query(0, ge=0, description="Schwellwert: Artikel mit Bestand <= threshold"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """
    AGR-INV-04: Artikel mit Bestand unter/am Schwellwert (Saatgut, Dünger, PSM).
    """
    items: list[dict[str, Any]] = []

    for model, typ in [(Saatgut, "saatgut"), (Duenger, "duenger"), (PSM, "psm")]:
        q = db.query(model).filter(
            model.tenant_id == tenant_id,
            model.ist_aktiv == True,  # noqa: E712
        )
        for row in q.all():
            val = float(row.lagerbestand or 0)
            if val <= threshold:
                items.append({
                    "typ": typ,
                    "id": row.id,
                    "artikelnummer": row.artikelnummer,
                    "name": row.name,
                    "bestand": val,
                    "threshold": threshold,
                })

    return {"threshold": threshold, "count": len(items), "items": items}
