"""Compliance API - DB-backed endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import (
    ComplianceEintrag,
    ENNIMeldung,
    QSCheckEintrag,
    ZulassungRegister,
    SachkundeEintrag,
    SaatgutNachbauEintrag,
    VVVOEintrag,
)

router = APIRouter(prefix="/compliance", tags=["Compliance"])


def _dt(v: Optional[datetime]) -> Optional[str]:
    return v.date().isoformat() if v else None


def _seed(db: Session) -> None:
    if db.query(ComplianceEintrag).count() == 0:
        db.add_all([
            ComplianceEintrag(bereich="Gewaesserschutz", anforderung="Gewaesserrandstreifen 5m", erfuellt=True, nachweis="Feldprotokoll", frist=datetime(2026, 12, 31)),
            ComplianceEintrag(bereich="Duengeverordnung", anforderung="Naehrstoffbilanz erstellt", erfuellt=True, nachweis="Bilanz 2025/26", frist=datetime(2026, 3, 31)),
            ComplianceEintrag(bereich="PSM-Dokumentation", anforderung="Anwendungsprotokolle vollstaendig", erfuellt=False, nachweis="", frist=datetime(2026, 3, 15)),
        ])
    if db.query(ENNIMeldung).count() == 0:
        db.add_all([
            ENNIMeldung(typ="DBE", betrieb="Landwirtschaft Mueller", vvvo="03-276-1234", datum=datetime(2026, 1, 15), status="bestaetigt", naehrstoff_n=180, naehrstoff_p=60, naehrstoff_k=120),
            ENNIMeldung(typ="WDE", betrieb="Agrar Schmidt", vvvo="03-276-5678", datum=datetime(2026, 2, 1), status="gesendet", naehrstoff_n=150, naehrstoff_p=45, naehrstoff_k=90),
        ])
    if db.query(QSCheckEintrag).count() == 0:
        db.add_all([
            QSCheckEintrag(bereich="Wareneingangskontrolle", pruefpunkt="Lieferschein-Pruefung", erfuellt=True, bemerkung="Vollstaendig", geprueft_am=datetime(2026, 2, 10)),
            QSCheckEintrag(bereich="Temperaturkontrolle", pruefpunkt="Lagerungstemperatur dokumentiert", erfuellt=True, bemerkung="Im Normbereich", geprueft_am=datetime(2026, 2, 10)),
        ])
    if db.query(ZulassungRegister).count() == 0:
        db.add_all([
            ZulassungRegister(produkt="Roundup PowerFlex", typ="PSM", nummer="024567-00", behoerde="BVL", gueltig_bis=datetime(2026, 12, 31), status="aktiv"),
            ZulassungRegister(produkt="Fungizid X", typ="PSM", nummer="024568-00", behoerde="BVL", gueltig_bis=datetime(2025, 6, 30), status="auslaufend"),
        ])
    if db.query(SachkundeEintrag).count() == 0:
        db.add(
            SachkundeEintrag(
                kunde="Landwirtschaft Mueller",
                kundennr="K-10023",
                nachweis_nr="SK-NDS-2022-4567",
                ausstellungsdatum=datetime(2022, 3, 15),
                gueltig_bis=datetime(2025, 3, 15),
                ausstellende_stelle="LWK Niedersachsen",
                status="ablaufend",
            )
        )
    if db.query(SaatgutNachbauEintrag).count() == 0:
        db.add(
            SaatgutNachbauEintrag(
                betrieb="Landwirtschaft Mueller",
                sorte="Weichweizen Eltan",
                kultur="Weichweizen",
                flaeche=45.5,
                erntejahr=2024,
                gebuehr=682.50,
                status="bezahlt",
            )
        )
    if db.query(VVVOEintrag).count() == 0:
        db.add(
            VVVOEintrag(
                betriebsname="Landwirtschaft Mueller",
                vvvo="03-276-123456",
                bundesland="Niedersachsen",
                tierart="Rind (Milch)",
                status="aktiv",
                letzte_aktualisierung=datetime(2026, 1, 15),
            )
        )
    db.commit()


@router.get("/cross-compliance", response_model=dict)
async def list_cross_compliance(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(ComplianceEintrag).all()
    payload = [
        {
            "id": i.id,
            "bereich": i.bereich,
            "anforderung": i.anforderung,
            "erfuellt": bool(i.erfuellt),
            "nachweis": i.nachweis,
            "frist": _dt(i.frist),
        }
        for i in items
    ]
    return {
        "items": payload,
        "total": len(payload),
        "erfuellt": sum(1 for i in payload if i["erfuellt"]),
        "offen": sum(1 for i in payload if not i["erfuellt"]),
    }


@router.get("/enni-meldungen", response_model=dict)
async def list_enni_meldungen(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(ENNIMeldung).all()
    return {
        "items": [
            {
                "id": i.id,
                "typ": i.typ,
                "betrieb": i.betrieb,
                "vvvo": i.vvvo,
                "datum": _dt(i.datum),
                "status": i.status,
                "naehrstoffe": {"n": i.naehrstoff_n, "p": i.naehrstoff_p, "k": i.naehrstoff_k},
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/qs-checkliste", response_model=dict)
async def list_qs_checkliste(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(QSCheckEintrag).all()
    payload = [
        {
            "id": i.id,
            "bereich": i.bereich,
            "pruefpunkt": i.pruefpunkt,
            "erfuellt": bool(i.erfuellt),
            "bemerkung": i.bemerkung,
            "geprueft_am": _dt(i.geprueft_am),
        }
        for i in items
    ]
    return {
        "items": payload,
        "total": len(payload),
        "erfuellt": sum(1 for i in payload if i["erfuellt"]),
        "offen": sum(1 for i in payload if not i["erfuellt"]),
    }


@router.get("/zulassungen-register", response_model=dict)
async def list_zulassungen(
    typ: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> dict:
    _seed(db)
    q = db.query(ZulassungRegister)
    if typ:
        q = q.filter(ZulassungRegister.typ == typ)
    if status:
        q = q.filter(ZulassungRegister.status == status)
    items = q.all()
    return {
        "items": [
            {
                "id": i.id,
                "produkt": i.produkt,
                "typ": i.typ,
                "nummer": i.nummer,
                "behoerde": i.behoerde,
                "gueltig_bis": _dt(i.gueltig_bis),
                "status": i.status,
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/sachkunde-register", response_model=dict)
async def list_sachkunde(status: Optional[str] = Query(None), db: Session = Depends(get_db)) -> dict:
    _seed(db)
    q = db.query(SachkundeEintrag)
    if status:
        q = q.filter(SachkundeEintrag.status == status)
    items = q.all()
    return {
        "items": [
            {
                "id": i.id,
                "kunde": i.kunde,
                "kundennr": i.kundennr,
                "nachweis_nr": i.nachweis_nr,
                "ausstellungsdatum": _dt(i.ausstellungsdatum),
                "gueltig_bis": _dt(i.gueltig_bis),
                "ausstellende_stelle": i.ausstellende_stelle,
                "status": i.status,
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/saatgut-nachbau", response_model=dict)
async def list_saatgut_nachbau(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(SaatgutNachbauEintrag).all()
    return {
        "items": [
            {
                "id": i.id,
                "betrieb": i.betrieb,
                "sorte": i.sorte,
                "kultur": i.kultur,
                "flaeche": i.flaeche,
                "erntejahr": i.erntejahr,
                "gebuehr": float(i.gebuehr or 0),
                "status": i.status,
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/vvvo-register", response_model=dict)
async def list_vvvo(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(VVVOEintrag).all()
    return {
        "items": [
            {
                "id": i.id,
                "betriebsname": i.betriebsname,
                "vvvo": i.vvvo,
                "bundesland": i.bundesland,
                "tierart": i.tierart,
                "status": i.status,
                "letzte_aktualisierung": _dt(i.letzte_aktualisierung),
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/stats", response_model=dict)
async def get_compliance_stats(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    total_checks = db.query(ComplianceEintrag).count()
    fulfilled = db.query(ComplianceEintrag).filter(ComplianceEintrag.erfuellt == True).count()  # noqa: E712
    enni_total = db.query(ENNIMeldung).count()
    enni_confirmed = db.query(ENNIMeldung).filter(ENNIMeldung.status == "bestaetigt").count()
    avg_n = db.query(ENNIMeldung).with_entities(ENNIMeldung.naehrstoff_n).all()
    avg_n_val = sum(float(x[0] or 0) for x in avg_n) / len(avg_n) if avg_n else 0

    return {
        "cross_compliance": {
            "total": total_checks,
            "erfuellt": fulfilled,
            "offen": total_checks - fulfilled,
            "quote": round((fulfilled / total_checks * 100) if total_checks else 0, 1),
        },
        "enni": {
            "total": enni_total,
            "bestaetigt": enni_confirmed,
            "in_bearbeitung": enni_total - enni_confirmed,
            "durchschnitt_n": round(avg_n_val, 1),
        },
        "generated_at": datetime.utcnow().isoformat(),
    }
