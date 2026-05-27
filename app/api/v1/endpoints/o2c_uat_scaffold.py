"""O2C/P2P UAT scaffold — end-to-end process chain test data and scenario runner.

This is a UAT tooling endpoint (not for production use).
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/uat/o2c", tags=["uat", "o2c", "testing"])

# ── Predefined UAT steps ───────────────────────────────────────────────────────

_STEPS_TEMPLATE = [
    (1, "Rohware-Annahme (harvest_acceptance) anlegen"),
    (2, "Qualitätsprotokoll erfassen"),
    (3, "Silo-Einbuchung"),
    (4, "Settlement-Preview berechnen"),
    (5, "Settlement buchen"),
    (6, "Fibu-Buchung erzeugen"),
    (7, "Partie-Genealogie prüfen"),
]

_READINESS_COVERAGE = [
    {
        "domain": "O2C",
        "covered_paths": [
            "customer_order_context",
            "delivery_and_inventory_trace",
            "invoice_or_settlement_reference",
        ],
        "repo_status": "prepared",
    },
    {
        "domain": "P2P",
        "covered_paths": [
            "supplier_delivery_context",
            "purchase_or_contract_reference",
            "goods_receipt_to_settlement",
        ],
        "repo_status": "prepared",
    },
    {
        "domain": "PARTIE",
        "covered_paths": [
            "harvest_acceptance",
            "quality_protocol",
            "silo_booking",
            "settlement_preview",
            "fibu_posting",
            "genealogy_check",
        ],
        "repo_status": "prepared",
    },
]

# In-memory store for UAT scenarios (UAT data, DB optional)
_store: dict[str, dict] = {}

# ── Schemas ───────────────────────────────────────────────────────────────────

class UATSzenarioCreate(BaseModel):
    szenario_name: str
    rohwarengruppe: str  # GETREIDE/OELFRUECHTE/LEGUMINOSEN/HACKFRUECHTE
    region: str          # NRW/BY/NDS/SH/BB/SONSTIGE
    test_menge_t: float = 50.0
    test_preis_eur_t: float = 200.0
    beschreibung: Optional[str] = None


class UATSchritt(BaseModel):
    schritt_nr: int
    name: str
    status: str = "OFFEN"  # OFFEN/LAUFEND/BESTANDEN/FEHLGESCHLAGEN/UEBERSPRUNGEN
    fehler_details: Optional[str] = None
    dauer_ms: Optional[int] = None


class UATSzenarioOut(BaseModel):
    id: str
    szenario_name: str
    rohwarengruppe: str
    region: str
    test_menge_t: float
    test_preis_eur_t: float
    beschreibung: Optional[str]
    gesamtstatus: str  # OFFEN/LAUFEND/BESTANDEN/FEHLGESCHLAGEN
    schritte: list[UATSchritt]
    erstellt_am: str
    abgeschlossen_am: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_schritte() -> list[dict]:
    return [
        {"schritt_nr": nr, "name": name, "status": "OFFEN", "fehler_details": None, "dauer_ms": None}
        for nr, name in _STEPS_TEMPLATE
    ]


def _calc_gesamtstatus(schritte: list[dict]) -> str:
    statuses = [s["status"] for s in schritte]
    if all(s == "BESTANDEN" for s in statuses):
        return "BESTANDEN"
    if any(s == "FEHLGESCHLAGEN" for s in statuses):
        return "FEHLGESCHLAGEN"
    if any(s in ("LAUFEND", "BESTANDEN") for s in statuses):
        return "LAUFEND"
    return "OFFEN"


def _load_from_db_or_store(id: str, db: Session, tenant_id: str) -> Optional[dict]:
    try:
        row = db.execute(
            text("SELECT * FROM domain_shared.uat_szenarien WHERE id=:id AND tenant_id=:tid"),
            {"id": id, "tid": tenant_id},
        ).fetchone()
        if row:
            import json
            schritte = row.schritte
            if isinstance(schritte, str):
                schritte = json.loads(schritte)
            return {
                "id": str(row.id),
                "szenario_name": row.szenario_name,
                "rohwarengruppe": row.rohwarengruppe,
                "region": row.region,
                "test_menge_t": float(row.test_menge_t),
                "test_preis_eur_t": float(row.test_preis_eur_t),
                "beschreibung": row.beschreibung,
                "gesamtstatus": row.gesamtstatus,
                "schritte": schritte,
                "erstellt_am": str(row.erstellt_am),
                "abgeschlossen_am": str(row.abgeschlossen_am) if row.abgeschlossen_am else None,
            }
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass
    return _store.get(id)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/readiness", summary="Readiness")
def readiness(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Repo-side UAT readiness for the O2C/P2P/Partie chain."""
    return {
        "tenant_id": tenant_id,
        "status": "repo_ready",
        "scenario_steps": len(_STEPS_TEMPLATE),
        "coverage": _READINESS_COVERAGE,
        "required_external_gates": [
            "browser_uat_with_productive_master_data",
            "scale_archive_reconciliation",
            "dms_live_probe",
            "tax_advisor_fibu_signoff",
            "signed_uat_protocol",
        ],
    }


@router.get("/szenarien", response_model=list[UATSzenarioOut], summary="Szenarien auflisten")
def list_szenarien(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        rows = db.execute(
            text(
                "SELECT * FROM domain_shared.uat_szenarien "
                "WHERE tenant_id=:tid ORDER BY erstellt_am DESC LIMIT 100"
            ),
            {"tid": tenant_id},
        ).fetchall()
        import json
        result = []
        for row in rows:
            schritte = row.schritte
            if isinstance(schritte, str):
                schritte = json.loads(schritte)
            result.append(UATSzenarioOut(
                id=str(row.id),
                szenario_name=row.szenario_name,
                rohwarengruppe=row.rohwarengruppe,
                region=row.region,
                test_menge_t=float(row.test_menge_t),
                test_preis_eur_t=float(row.test_preis_eur_t),
                beschreibung=row.beschreibung,
                gesamtstatus=row.gesamtstatus,
                schritte=[UATSchritt(**s) for s in (schritte or [])],
                erstellt_am=str(row.erstellt_am),
                abgeschlossen_am=str(row.abgeschlossen_am) if row.abgeschlossen_am else None,
            ))
        return result
    except Exception:
        return [UATSzenarioOut(**v) for v in _store.values()]


@router.post("/szenarien", response_model=UATSzenarioOut, status_code=201, summary="Szenario anlegen")
def create_szenario(
    payload: UATSzenarioCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    new_id = str(uuid4())
    now = datetime.utcnow().isoformat()
    schritte = _make_schritte()
    record = {
        "id": new_id,
        "szenario_name": payload.szenario_name,
        "rohwarengruppe": payload.rohwarengruppe,
        "region": payload.region,
        "test_menge_t": payload.test_menge_t,
        "test_preis_eur_t": payload.test_preis_eur_t,
        "beschreibung": payload.beschreibung,
        "gesamtstatus": "OFFEN",
        "schritte": schritte,
        "erstellt_am": now,
        "abgeschlossen_am": None,
    }
    import json
    # Always populate in-memory store so fallback reads work
    _store[new_id] = record
    try:
        db.execute(
            text(
                "INSERT INTO domain_shared.uat_szenarien "
                "(id, tenant_id, szenario_name, rohwarengruppe, region, test_menge_t, "
                "test_preis_eur_t, beschreibung, gesamtstatus, schritte, erstellt_am) "
                "VALUES (:id, :tid, :name, :rg, :reg, :menge, :preis, :desc, 'OFFEN', :schritte::jsonb, :now)"
            ),
            {
                "id": new_id, "tid": tenant_id,
                "name": payload.szenario_name,
                "rg": payload.rohwarengruppe,
                "reg": payload.region,
                "menge": payload.test_menge_t,
                "preis": payload.test_preis_eur_t,
                "desc": payload.beschreibung,
                "schritte": json.dumps(schritte),
                "now": now,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        _store[new_id] = record
    return UATSzenarioOut(**record)


@router.post("/szenarien/{id}/schritt/{nr}/ausfuehren", summary="Ausfuehren schritt")
def schritt_ausfuehren(
    id: str,
    nr: int,
    body: dict,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Mark a step as run (BESTANDEN or FEHLGESCHLAGEN)."""
    import json
    rec = _load_from_db_or_store(id, db, tenant_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Szenario nicht gefunden")

    schritte = rec["schritte"]
    step = next((s for s in schritte if s["schritt_nr"] == nr), None)
    if not step:
        raise HTTPException(status_code=404, detail=f"Schritt {nr} nicht gefunden")

    step["status"] = body.get("status", "BESTANDEN")
    step["fehler_details"] = body.get("fehler_details")
    step["dauer_ms"] = body.get("dauer_ms")

    neuer_gesamtstatus = _calc_gesamtstatus(schritte)
    abgeschlossen_am = datetime.utcnow().isoformat() if neuer_gesamtstatus in ("BESTANDEN", "FEHLGESCHLAGEN") else None

    # Always update in-memory store
    if id in _store:
        _store[id]["schritte"] = schritte
        _store[id]["gesamtstatus"] = neuer_gesamtstatus
        _store[id]["abgeschlossen_am"] = abgeschlossen_am
    try:
        db.execute(
            text(
                "UPDATE domain_shared.uat_szenarien "
                "SET schritte=:schritte::jsonb, gesamtstatus=:gs, abgeschlossen_am=:ab "
                "WHERE id=:id AND tenant_id=:tid"
            ),
            {
                "schritte": json.dumps(schritte),
                "gs": neuer_gesamtstatus,
                "ab": abgeschlossen_am,
                "id": id, "tid": tenant_id,
            },
        )
        db.commit()
    except Exception:
        db.rollback()

    return {
        "schritt_nr": nr,
        "status": step["status"],
        "gesamtstatus": neuer_gesamtstatus,
    }


@router.get("/szenarien/{id}/bericht", summary="Bericht")
def bericht(
    id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Full UAT report with summary."""
    rec = _load_from_db_or_store(id, db, tenant_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Szenario nicht gefunden")

    schritte = rec["schritte"]
    total = len(schritte)
    bestanden = sum(1 for s in schritte if s["status"] == "BESTANDEN")
    fehlgeschlagen = sum(1 for s in schritte if s["status"] == "FEHLGESCHLAGEN")
    offen = sum(1 for s in schritte if s["status"] == "OFFEN")
    deckung = round(bestanden / total * 100, 2) if total > 0 else 0.0

    return {
        **rec,
        "zusammenfassung": {
            "bestanden": bestanden,
            "fehlgeschlagen": fehlgeschlagen,
            "offen": offen,
            "deckungsgrad_prozent": deckung,
        },
    }


@router.post("/szenarien/{id}/reset", summary="Szenario zurücksetzen")
def reset_szenario(
    id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Reset all steps to OFFEN, gesamtstatus=OFFEN."""
    import json
    rec = _load_from_db_or_store(id, db, tenant_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Szenario nicht gefunden")

    schritte = rec["schritte"]
    for s in schritte:
        s["status"] = "OFFEN"
        s["fehler_details"] = None
        s["dauer_ms"] = None

    if id in _store:
        _store[id]["schritte"] = schritte
        _store[id]["gesamtstatus"] = "OFFEN"
        _store[id]["abgeschlossen_am"] = None
    try:
        db.execute(
            text(
                "UPDATE domain_shared.uat_szenarien "
                "SET schritte=:schritte::jsonb, gesamtstatus='OFFEN', abgeschlossen_am=NULL "
                "WHERE id=:id AND tenant_id=:tid"
            ),
            {"schritte": json.dumps(schritte), "id": id, "tid": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()

    return {"reset": True, "gesamtstatus": "OFFEN"}
