"""Saatzucht-Modul — certified seed / seed breeding management stub."""

from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.saatzucht_schemas import SaatzuchtOut


router = APIRouter(prefix="/saatzucht", tags=["saatzucht", "agrar", "saatgut"])

# ── Schemas ───────────────────────────────────────────────────────────────────

class SaatgutPartieCreate(BaseModel):
    partie_nr: Optional[str] = None
    sorte_bezeichnung: str
    art_code: str  # WW/WR/WG/SS/RA
    z_stufe: str   # Z1/Z2/Z3/ZA
    vermehrungsbetrieb: str
    anbauflaeche_ha: float
    saatgutmenge_kg: float
    keimfaehigkeit_prozent: Optional[float] = None
    sortenreinheit_prozent: Optional[float] = None
    tkg_gramm: Optional[float] = None
    anerkennungsnr: Optional[str] = None
    anerkennungsdatum: Optional[str] = None
    status: str = "ANBAU"  # ANBAU/ERNTE/AUFBEREITUNG/ANERKANNT/VERKAUFT/GESPERRT


class SaatgutPartieOut(SaatgutPartieCreate):
    id: str
    erstellt_am: str


class SaatgutEtikett(BaseModel):
    partie_nr: str
    sorte: str
    art_code: str
    z_stufe: str
    anerkennungsnr: Optional[str]
    netto_kg: float
    los_nr: str
    druckdatum: str


# In-memory fallback store
_store: dict[str, dict] = {}
_seq: dict[str, int] = {}


def _gen_partie_nr() -> str:
    yr = date.today().year
    _seq[str(yr)] = _seq.get(str(yr), 0) + 1
    return f"SZ-{yr}-{_seq[str(yr)]:05d}"


def _dict_to_out(d: dict) -> SaatgutPartieOut:
    return SaatgutPartieOut(**d)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/partien", response_model=list[SaatgutPartieOut], summary="Partien auflisten")
def list_partien(
    art_code: Optional[str] = Query(default=None),
    z_stufe: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        where = "WHERE tenant_id = :tid"
        params: dict = {"tid": tenant_id}
        if art_code:
            where += " AND art_code = :art"
            params["art"] = art_code
        if z_stufe:
            where += " AND z_stufe = :z"
            params["z"] = z_stufe
        if status:
            where += " AND status = :st"
            params["st"] = status
        rows = db.execute(
            text(f"SELECT * FROM domain_agrar.saatgut_partien {where} ORDER BY erstellt_am DESC LIMIT 200"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
            params,
        ).fetchall()
        return [
            SaatgutPartieOut(
                id=str(r.id),
                partie_nr=r.partie_nr,
                sorte_bezeichnung=r.sorte_bezeichnung,
                art_code=r.art_code,
                z_stufe=r.z_stufe,
                vermehrungsbetrieb=r.vermehrungsbetrieb,
                anbauflaeche_ha=float(r.anbauflaeche_ha),
                saatgutmenge_kg=float(r.saatgutmenge_kg),
                keimfaehigkeit_prozent=float(r.keimfaehigkeit_prozent) if r.keimfaehigkeit_prozent else None,
                sortenreinheit_prozent=float(r.sortenreinheit_prozent) if r.sortenreinheit_prozent else None,
                tkg_gramm=float(r.tkg_gramm) if r.tkg_gramm else None,
                anerkennungsnr=r.anerkennungsnr,
                anerkennungsdatum=str(r.anerkennungsdatum) if r.anerkennungsdatum else None,
                status=r.status,
                erstellt_am=str(r.erstellt_am),
            )
            for r in rows
        ]
    except Exception:
        items = list(_store.values())
        if art_code:
            items = [i for i in items if i.get("art_code") == art_code]
        if z_stufe:
            items = [i for i in items if i.get("z_stufe") == z_stufe]
        if status:
            items = [i for i in items if i.get("status") == status]
        return [SaatgutPartieOut(**i) for i in items]


@router.post("/partien", response_model=SaatgutPartieOut, status_code=201, summary="Partie anlegen")
def create_partie(
    payload: SaatgutPartieCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    new_id = str(uuid4())
    partie_nr = payload.partie_nr or _gen_partie_nr()
    now = datetime.utcnow().isoformat()
    record = SaatgutPartieOut(
        id=new_id,
        partie_nr=partie_nr,
        sorte_bezeichnung=payload.sorte_bezeichnung,
        art_code=payload.art_code,
        z_stufe=payload.z_stufe,
        vermehrungsbetrieb=payload.vermehrungsbetrieb,
        anbauflaeche_ha=payload.anbauflaeche_ha,
        saatgutmenge_kg=payload.saatgutmenge_kg,
        keimfaehigkeit_prozent=payload.keimfaehigkeit_prozent,
        sortenreinheit_prozent=payload.sortenreinheit_prozent,
        tkg_gramm=payload.tkg_gramm,
        anerkennungsnr=payload.anerkennungsnr,
        anerkennungsdatum=payload.anerkennungsdatum,
        status=payload.status,
        erstellt_am=now,
    )
    # Always populate in-memory store so fallback reads work
    _store[new_id] = record.model_dump()
    try:
        db.execute(
            text(
                "INSERT INTO domain_agrar.saatgut_partien "
                "(id, tenant_id, partie_nr, sorte_bezeichnung, art_code, z_stufe, "
                "vermehrungsbetrieb, anbauflaeche_ha, saatgutmenge_kg, "
                "keimfaehigkeit_prozent, sortenreinheit_prozent, tkg_gramm, "
                "anerkennungsnr, anerkennungsdatum, status, erstellt_am) "
                "VALUES (:id, :tid, :pnr, :sorte, :art, :z, :betrieb, :ha, :kg, "
                ":keim, :rein, :tkg, :anr, :adt, :status, :now)"
            ),
            {
                "id": new_id, "tid": tenant_id, "pnr": partie_nr,
                "sorte": payload.sorte_bezeichnung, "art": payload.art_code,
                "z": payload.z_stufe, "betrieb": payload.vermehrungsbetrieb,
                "ha": payload.anbauflaeche_ha, "kg": payload.saatgutmenge_kg,
                "keim": payload.keimfaehigkeit_prozent,
                "rein": payload.sortenreinheit_prozent,
                "tkg": payload.tkg_gramm,
                "anr": payload.anerkennungsnr,
                "adt": payload.anerkennungsdatum,
                "status": payload.status, "now": now,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        _store[new_id] = record.model_dump()
    return record


@router.get("/partien/{id}", response_model=SaatgutPartieOut, summary="Partie abrufen")
def get_partie(
    id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        row = db.execute(
            text("SELECT * FROM domain_agrar.saatgut_partien WHERE id=:id AND tenant_id=:tid"),
            {"id": id, "tid": tenant_id},
        ).fetchone()
        if row:
            return SaatgutPartieOut(
                id=str(row.id),
                partie_nr=row.partie_nr,
                sorte_bezeichnung=row.sorte_bezeichnung,
                art_code=row.art_code,
                z_stufe=row.z_stufe,
                vermehrungsbetrieb=row.vermehrungsbetrieb,
                anbauflaeche_ha=float(row.anbauflaeche_ha),
                saatgutmenge_kg=float(row.saatgutmenge_kg),
                keimfaehigkeit_prozent=float(row.keimfaehigkeit_prozent) if row.keimfaehigkeit_prozent else None,
                sortenreinheit_prozent=float(row.sortenreinheit_prozent) if row.sortenreinheit_prozent else None,
                tkg_gramm=float(row.tkg_gramm) if row.tkg_gramm else None,
                anerkennungsnr=row.anerkennungsnr,
                anerkennungsdatum=str(row.anerkennungsdatum) if row.anerkennungsdatum else None,
                status=row.status,
                erstellt_am=str(row.erstellt_am),
            )
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass
    if id in _store:
        return SaatgutPartieOut(**_store[id])
    raise HTTPException(status_code=404, detail="Partie nicht gefunden")


@router.patch("/partien/{id}", response_model=SaatgutPartieOut, summary="Partie aktualisieren")
def update_partie(
    id: str,
    payload: dict,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Partial update (status, Qualitätswerte)."""
    allowed = {
        "status", "keimfaehigkeit_prozent", "sortenreinheit_prozent",
        "tkg_gramm", "anerkennungsnr", "anerkennungsdatum", "saatgutmenge_kg",
    }
    updates = {k: v for k, v in payload.items() if k in allowed}
    if updates:
        set_clause = ", ".join(f"{k}=:{k}" for k in updates)
        params = {**updates, "id": id, "tid": tenant_id}
        try:
            db.execute(
                text(f"UPDATE domain_agrar.saatgut_partien SET {set_clause} WHERE id=:id AND tenant_id=:tid"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
                params,
            )
            db.commit()
        except Exception:
            db.rollback()
            if id in _store:
                _store[id].update(updates)
    return get_partie(id, db, tenant_id)


@router.post("/partien/{id}/anerkennung", response_model=SaatgutPartieOut, summary="Anerkennung")
def anerkennung(
    id: str,
    body: dict,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Record official certification."""
    anerkennungsnr = body.get("anerkennungsnr", "")
    anerkennungsdatum = body.get("anerkennungsdatum", date.today().isoformat())
    try:
        db.execute(
            text(
                "UPDATE domain_agrar.saatgut_partien "
                "SET anerkennungsnr=:anr, anerkennungsdatum=:adt, status='ANERKANNT' "
                "WHERE id=:id AND tenant_id=:tid"
            ),
            {"anr": anerkennungsnr, "adt": anerkennungsdatum, "id": id, "tid": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()
        if id in _store:
            _store[id]["anerkennungsnr"] = anerkennungsnr
            _store[id]["anerkennungsdatum"] = anerkennungsdatum
            _store[id]["status"] = "ANERKANNT"
    return get_partie(id, db, tenant_id)


@router.post("/partien/{id}/etikett", response_model=SaatgutEtikett, summary="Etikett")
def etikett(
    id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Generate label data for a seed lot."""
    partie = get_partie(id, db, tenant_id)
    los_nr = f"{partie.partie_nr}-{date.today().strftime('%y%m')}"
    return SaatgutEtikett(
        partie_nr=partie.partie_nr,
        sorte=partie.sorte_bezeichnung,
        art_code=partie.art_code,
        z_stufe=partie.z_stufe,
        anerkennungsnr=partie.anerkennungsnr,
        netto_kg=partie.saatgutmenge_kg,
        los_nr=los_nr,
        druckdatum=date.today().isoformat(),
    )


@router.get("/partien/{id}/kontrollprotokoll", summary="Kontrollprotokoll",
    response_model=SaatzuchtOut
)
def kontrollprotokoll(
    id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """QC protocol for a seed lot."""
    partie = get_partie(id, db, tenant_id)
    keim = partie.keimfaehigkeit_prozent
    bewertung = "BESTANDEN" if (keim is not None and keim >= 85) else "NICHT BESTANDEN"
    return {
        "partie_nr": partie.partie_nr,
        "keimtest_ergebnis": keim,
        "sortenreinheit": partie.sortenreinheit_prozent,
        "tkg": partie.tkg_gramm,
        "bewertung": bewertung,
        "protokoll_nr": f"QC-{id[:8]}",
    }


@router.get("/statistik", summary="Statistik",
    response_model=SaatzuchtOut
)
def statistik(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Summary statistics — graceful fallback to zeros."""
    try:
        row = db.execute(
            text(
                "SELECT COUNT(*) AS total, "
                "SUM(saatgutmenge_kg) AS total_kg, "
                "SUM(anbauflaeche_ha) AS total_ha "
                "FROM domain_agrar.saatgut_partien WHERE tenant_id=:tid"
            ),
            {"tid": tenant_id},
        ).fetchone()
        z_rows = db.execute(
            text(
                "SELECT z_stufe, COUNT(*) AS n "
                "FROM domain_agrar.saatgut_partien WHERE tenant_id=:tid GROUP BY z_stufe"
            ),
            {"tid": tenant_id},
        ).fetchall()
        return {
            "total_partien": row.total or 0,
            "total_kg": float(row.total_kg or 0),
            "total_ha": float(row.total_ha or 0),
            "nach_z_stufe": {r.z_stufe: r.n for r in z_rows},
        }
    except Exception:
        items = list(_store.values())
        return {
            "total_partien": len(items),
            "total_kg": sum(i.get("saatgutmenge_kg", 0) for i in items),
            "total_ha": sum(i.get("anbauflaeche_ha", 0) for i in items),
            "nach_z_stufe": {},
        }
