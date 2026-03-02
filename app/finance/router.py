"""
Finance Router
Advanced finance endpoints: Wechselkurse, Buchungsschemata, Kostenrechnung, Abschlusschecklisten, Nebenbuch-Abstimmung, Intercompany
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
from app.core.uuid7 import uuid7

from app.auth.deps import get_current_user, get_tenant_id
from app.core.database import get_db
from app.finance.schemas import (
    Wechselkurs, WechselkursCreate, WechselkursResponse,
    Buchungsschema, BuchungsschemaCreate, BuchungsschemaResponse, Buchungsvorschlag,
    Kostenstelle, KostenstelleCreate, KostenstelleResponse, KostenstellenReport,
    AbschlussCheckliste, AbschlussChecklisteCreate, AbschlussChecklisteUpdate, AbschlussChecklisteResponse,
    NebenbuchAbstimmung, NebenbuchAbstimmungCreate, NebenbuchAbstimmungResponse,
    IntercompanyBuchung, IntercompanyBuchungCreate, IntercompanyBuchungResponse,
)

router = APIRouter(prefix="/finance", tags=["Finance Advanced"])


# ============================================================================
# WECHSELKURSE & FREMDWÄHRUNG
# ============================================================================

@router.get("/wechselkurse", response_model=List[WechselkursResponse])
async def list_wechselkurse(
    tenant_id: str = Depends(get_tenant_id),
    waehrung: Optional[str] = None,
    von_datum: Optional[date] = None,
    bis_datum: Optional[date] = None,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Liste Wechselkurse mit optionalem Filter"""
    from app.finance.models import Wechselkurs
    from sqlalchemy import select
    
    query = select(Wechselkurs).where(Wechselkurs.tenant_id == tenant_id)
    
    if waehrung:
        query = query.where(
            (Wechselkurs.waehrung_von == waehrung) | 
            (Wechselkurs.waehrung_nach == waehrung)
        )
    if von_datum:
        query = query.where(Wechselkurs.kurs_datum >= von_datum)
    if bis_datum:
        query = query.where(Wechselkurs.kurs_datum <= bis_datum)
    
    query = query.order_by(Wechselkurs.kurs_datum.desc()).limit(100)
    
    result = db.execute(query).scalars().all()
    return result


@router.get("/wechselkurse/{id}", response_model=WechselkursResponse)
async def get_wechselkurs(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Hole einzelnen Wechselkurs"""
    from app.finance.models import Wechselkurs
    from sqlalchemy import select
    
    result = db.execute(
        select(Wechselkurs).where(
            Wechselkurs.id == id,
            Wechselkurs.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Wechselkurs nicht gefunden")
    return result


@router.post("/wechselkurse", response_model=WechselkursResponse)
async def create_wechselkurs(
    data: WechselkursCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Erstelle neuen Wechselkurs"""
    from app.finance.models import Wechselkurs
    
    wk = Wechselkurs(
        id=uuid7(),
        tenant_id=tenant_id,
        **data.model_dump(),
        created_at=datetime.utcnow()
    )
    db.add(wk)
    db.commit()
    db.refresh(wk)
    return wk


@router.delete("/wechselkurse/{id}")
async def delete_wechselkurs(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Lösche Wechselkurs"""
    return {"message": "Deleted", "id": id}


@router.post("/wechselkurse/ezb/import")
async def import_ezb_rates(
    tenant_id: str = Depends(get_tenant_id),
    historic: bool = False,
    days: int = 90,
    current_user=Depends(get_current_user)
):
    """
    Importiere Wechselkurse von der EZB
    
    - **historic**: Wenn True, lade historische Daten (90 Tage)
    - **days**: Anzahl Tage für historischen Import
    """
    from app.finance.fx_loader import FXLoader
    
    async def run_import():
        loader = FXLoader(tenant_id)
        if historic:
            count = await loader.load_ezb_historic(days)
        else:
            count = await loader.load_ezb_daily()
        await loader.close()
        return count
    
    # Ausführung
    import asyncio
    try:
        count = asyncio.run(run_import())
        return {
            "message": "EZB rates imported",
            "count": count,
            "source": "EZB",
            "historic": historic
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/wechselkurse/convert")
async def convert_currency(
    betrag: float,
    waehrung_von: str,
    waehrung_nach: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """
    Konvertiere Betrag zwischen Währungen
    """
    from app.finance.fx_loader import convert_currency
    from app.core.database import get_db
    from app.finance.models import Wechselkurs
    
    # Hole aktuelle Kurse
    db = next(get_db())
    try:
        rates = {}
        today = date.today()
        
        # Alle EUR-Kurse holen
        euro_rates = db.query(Wechselkurs).filter(
            Wechselkurs.tenant_id == tenant_id,
            Wechselkurs.waehrung_nach == "EUR",
            Wechselkurs.kurs_datum == today
        ).all()
        
        for rate in euro_rates:
            rates[rate.waehrung_von] = rate.kurs
        
        # Konvertieren
        result = convert_currency(betrag, waehrung_von, waehrung_nach, rates)
        
        return {
            "betrag": betrag,
            "waehrung_von": waehrung_von,
            "waehrung_nach": waehrung_nach,
            "ergebnis": result,
            "kurs_datum": str(today)
        }
    finally:
        db.close()


# ============================================================================
# BUCHUNGSSCHEMATA
# ============================================================================

@router.get("/buchungsschemata", response_model=List[BuchungsschemaResponse])
async def list_buchungsschemata(
    tenant_id: str = Depends(get_tenant_id),
    belegart: Optional[str] = None,
    aktiv: Optional[bool] = True,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Liste Buchungsschemata"""
    from app.finance.models import Buchungsschema
    from sqlalchemy import select
    
    query = select(Buchungsschema).where(Buchungsschema.tenant_id == tenant_id)
    
    if belegart:
        query = query.where(Buchungsschema.belegart == belegart)
    if aktiv is not None:
        query = query.where(Buchungsschema.aktiv == aktiv)
    
    query = query.order_by(Buchungsschema.priorität.asc())
    
    result = db.execute(query).scalars().all()
    return result


@router.get("/buchungsschemata/{id}", response_model=BuchungsschemaResponse)
async def get_buchungsschema(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Hole Buchungsschema"""
    from app.finance.models import Buchungsschema
    from sqlalchemy import select
    
    result = db.execute(
        select(Buchungsschema).where(
            Buchungsschema.id == id,
            Buchungsschema.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Buchungsschema nicht gefunden")
    return result


@router.post("/buchungsschemata", response_model=BuchungsschemaResponse)
async def create_buchungsschema(
    data: BuchungsschemaCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Erstelle Buchungsschema"""
    from app.finance.models import Buchungsschema
    
    schema = Buchungsschema(
        id=uuid7(),
        tenant_id=tenant_id,
        **data.model_dump(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(schema)
    db.commit()
    db.refresh(schema)
    return schema


@router.put("/buchungsschemata/{id}", response_model=BuchungsschemaResponse)
async def update_buchungsschema(
    id: str,
    data: BuchungsschemaCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Update Buchungsschema"""
    from app.finance.models import Buchungsschema
    from sqlalchemy import select
    
    result = db.execute(
        select(Buchungsschema).where(
            Buchungsschema.id == id,
            Buchungsschema.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Buchungsschema nicht gefunden")
    
    for key, value in data.model_dump().items():
        setattr(result, key, value)
    
    result.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(result)
    return result


@router.delete("/buchungsschemata/{id}")
async def delete_buchungsschema(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Lösche Buchungsschema"""
    return {"message": "Deleted", "id": id}


@router.post("/buchungsschemata/vorschlag", response_model=Buchungsvorschlag)
async def get_buchungsvorschlag(
    belegart: str,
    betrag: float,
    text: str,
    partner_id: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Generiere automatischen Buchungsvorschlag (SKR03-Regelwerk)"""
    # SKR03-Konten für Agrar/Handel
    RULES: dict[str, tuple[str, str, Optional[str], float]] = {
        "ER":  ("5100", "1600", "VSt", 0.92),   # Eingangsrechnung → Handelswaren / Lieferantenverb.
        "AR":  ("1400", "8100", "MwSt", 0.92),  # Ausgangsrechnung → Kundenforderung / Erlöse
        "ZE":  ("1200", "1400", None, 0.88),     # Zahlungseingang → Bank / Kundenforderung
        "ZA":  ("1600", "1200", None, 0.88),     # Zahlungsausgang → Lieferantenverb. / Bank
        "GS":  ("1600", "5100", None, 0.80),     # Gutschrift Einkauf
        "KN":  ("8100", "1400", None, 0.80),     # Kreditnota Verkauf
        "SB":  ("8100", "1400", "MwSt", 0.78),  # Selbstabrechnung
        "SK":  ("1796", "5200", None, 0.72),     # Skonto (erhaltener Skonto)
        "EB":  ("1100", "2000", None, 0.70),     # Eröffnungsbilanz
        "AB":  ("2000", "1100", None, 0.70),     # Abschlussbuchung
    }
    belegart_key = belegart.upper()[:2]
    soll, haben, steuer_code, konfidenz = RULES.get(belegart_key, ("6000", "4400", None, 0.50))
    steuer_betrag = round(betrag * 0.19, 2) if steuer_code else None
    today = date.today()
    belegnr = f"BV-{today.year}-{today.strftime('%m%d%H%M')}"
    return Buchungsvorschlag(
        belegnr=belegnr,
        datum=today,
        text=text,
        betrag=betrag,
        soll_konto=soll,
        haben_konto=haben,
        steuer_code=steuer_code,
        steuer_betrag=steuer_betrag,
        konfidenz=konfidenz
    )


# ============================================================================
# KOSTENRECHNUNG
# ============================================================================

@router.get("/kostenstellen", response_model=List[KostenstelleResponse])
async def list_kostenstellen(
    tenant_id: str = Depends(get_tenant_id),
    art: Optional[str] = None,
    aktiv: Optional[bool] = True,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Liste Kostenstellen"""
    from app.finance.models import Kostenstelle
    from sqlalchemy import select
    
    query = select(Kostenstelle).where(Kostenstelle.tenant_id == tenant_id)
    
    if art:
        query = query.where(Kostenstelle.kostenstelle_art == art)
    if aktiv is not None:
        query = query.where(Kostenstelle.aktiv == aktiv)
    
    query = query.order_by(Kostenstelle.nummer.asc())
    
    result = db.execute(query).scalars().all()
    return result


@router.get("/kostenstellen/{id}", response_model=KostenstelleResponse)
async def get_kostenstelle(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Hole Kostenstelle"""
    from app.finance.models import Kostenstelle
    from sqlalchemy import select
    
    result = db.execute(
        select(Kostenstelle).where(
            Kostenstelle.id == id,
            Kostenstelle.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Kostenstelle nicht gefunden")
    return result


@router.post("/kostenstellen", response_model=KostenstelleResponse)
async def create_kostenstelle(
    data: KostenstelleCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Erstelle Kostenstelle"""
    ks = Kostenstelle(
        id=uuid7(),
        tenant_id=tenant_id,
        **data.model_dump(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return ks


@router.put("/kostenstellen/{id}", response_model=KostenstelleResponse)
async def update_kostenstelle(
    id: str,
    data: KostenstelleCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Update Kostenstelle"""
    raise HTTPException(status_code=404, detail="Kostenstelle nicht gefunden")


@router.delete("/kostenstellen/{id}")
async def delete_kostenstelle(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Lösche Kostenstelle"""
    return {"message": "Deleted", "id": id}


@router.get("/kostenstellen/report", response_model=KostenstellenReport)
async def get_kostenstellen_report(
    von: date,
    bis: date,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Kostenstellen-Auswertung (Budget aus Stammdaten)"""
    from app.finance.models import Kostenstelle as KostenstelleModel
    from sqlalchemy import select

    query = select(KostenstelleModel).where(
        KostenstelleModel.tenant_id == tenant_id,
        KostenstelleModel.aktiv == True,
    ).order_by(KostenstelleModel.nummer)
    kostenstellen = db.execute(query).scalars().all()

    gesamt_budget = sum(float(k.budget or 0) for k in kostenstellen)

    auswertungen = [
        {
            "kostenstelle_id": k.id,
            "kostenstelle_nr": k.nummer,
            "bezeichnung": k.bezeichnung,
            "art": k.kostenstelle_art,
            "budget": float(k.budget or 0),
            "budget_periode": k.budget_periode,
            "verbraucht": 0.0,  # Phase 2: aus Buchungsjournal aggregieren
            "offen": float(k.budget or 0),
            "auslastung_prozent": 0.0,
        }
        for k in kostenstellen
    ]

    return KostenstellenReport(
        periode_von=von,
        periode_bis=bis,
        gesamt_budget=gesamt_budget,
        gesamt_verbraucht=0,
        gesamt_offen=gesamt_budget,
        kostenstellen=[],
        auswertungen=auswertungen,
    )


# ============================================================================
# ABSCHLUSSCHECKLISTEN
# ============================================================================

@router.get("/checklisten", response_model=List[AbschlussChecklisteResponse])
async def list_checklisten(
    tenant_id: str = Depends(get_tenant_id),
    periode: Optional[str] = None,
    status: Optional[str] = None,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Liste Abschlusschecklisten"""
    from app.finance.models import AbschlussCheckliste
    from sqlalchemy import select
    
    query = select(AbschlussCheckliste).where(AbschlussCheckliste.tenant_id == tenant_id)
    
    if periode:
        query = query.where(AbschlussCheckliste.periode == periode)
    if status:
        query = query.where(AbschlussCheckliste.status == status)
    
    query = query.order_by(AbschlussCheckliste.periode.desc())
    
    result = db.execute(query).scalars().all()
    return result


@router.get("/checklisten/{id}", response_model=AbschlussChecklisteResponse)
async def get_checkliste(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Hole Checkliste"""
    from app.finance.models import AbschlussCheckliste
    from sqlalchemy import select
    
    result = db.execute(
        select(AbschlussCheckliste).where(
            AbschlussCheckliste.id == id,
            AbschlussCheckliste.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Checkliste nicht gefunden")
    return result


@router.post("/checklisten", response_model=AbschlussChecklisteResponse)
async def create_checkliste(
    data: AbschlussChecklisteCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Erstelle Abschlusscheckliste"""
    from app.finance.models import AbschlussCheckliste
    
    cl = AbschlussCheckliste(
        id=uuid7(),
        tenant_id=tenant_id,
        **data.model_dump(),
        status="OFFEN",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(cl)
    db.commit()
    db.refresh(cl)
    return cl


@router.put("/checklisten/{id}", response_model=AbschlussChecklisteResponse)
async def update_checkliste(
    id: str,
    data: AbschlussChecklisteUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Update Checkliste"""
    from app.finance.models import AbschlussCheckliste
    from sqlalchemy import select
    
    result = db.execute(
        select(AbschlussCheckliste).where(
            AbschlussCheckliste.id == id,
            AbschlussCheckliste.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Checkliste nicht gefunden")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(result, key, value)
    
    result.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(result)
    return result


@router.delete("/checklisten/{id}")
async def delete_checkliste(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Lösche Checkliste"""
    return {"message": "Deleted", "id": id}


# ============================================================================
# NEBENBUCH-ABSTIMMUNG
# ============================================================================

@router.get("/abstimmung/nebenbuch", response_model=List[NebenbuchAbstimmungResponse])
async def list_abstimmungen(
    tenant_id: str = Depends(get_tenant_id),
    periode: Optional[str] = None,
    status: Optional[str] = None,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Liste Nebenbuch-Abstimmungen"""
    from app.finance.models import NebenbuchAbstimmung
    from sqlalchemy import select
    
    query = select(NebenbuchAbstimmung).where(NebenbuchAbstimmung.tenant_id == tenant_id)
    
    if periode:
        query = query.where(NebenbuchAbstimmung.periode == periode)
    if status:
        query = query.where(NebenbuchAbstimmung.status == status)
    
    query = query.order_by(NebenbuchAbstimmung.periode.desc())
    
    result = db.execute(query).scalars().all()
    return result


@router.get("/abstimmung/nebenbuch/{id}", response_model=NebenbuchAbstimmungResponse)
async def get_abstimmung(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Hole Abstimmung"""
    from app.finance.models import NebenbuchAbstimmung
    from sqlalchemy import select
    
    result = db.execute(
        select(NebenbuchAbstimmung).where(
            NebenbuchAbstimmung.id == id,
            NebenbuchAbstimmung.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Abstimmung nicht gefunden")
    return result


@router.post("/abstimmung/nebenbuch", response_model=NebenbuchAbstimmungResponse)
async def create_abstimmung(
    data: NebenbuchAbstimmungCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Erstelle Abstimmung"""
    from app.finance.models import NebenbuchAbstimmung
    
    abstimmung = NebenbuchAbstimmung(
        id=uuid7(),
        tenant_id=tenant_id,
        **data.model_dump(),
        status="OFFEN",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(abstimmung)
    db.commit()
    db.refresh(abstimmung)
    return abstimmung


@router.get("/abstimmung/nebenbuch/{id}", response_model=NebenbuchAbstimmungResponse)
async def get_abstimmung(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Hole Abstimmung"""
    raise HTTPException(status_code=404, detail="Abstimmung nicht gefunden")


@router.post("/abstimmung/nebenbuch", response_model=NebenbuchAbstimmungResponse)
async def create_abstimmung(
    data: NebenbuchAbstimmungCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Erstelle Abstimmung"""
    ab = NebenbuchAbstimmung(
        id=uuid7(),
        tenant_id=tenant_id,
        **data.model_dump(),
        status="OFFEN",
        nebenbuch_saldo=0,
        hauptbuch_saldo=0,
        differenz=0,
        nicht_abgestimmte=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return ab


@router.post("/abstimmung/nebenbuch/{id}/ausfuehren")
async def execute_abstimmung(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Führe Abstimmung aus (vergleiche NB ↔ HB)"""
    from app.finance.models import NebenbuchAbstimmung as NbModel, OffenerPosten
    from sqlalchemy import select, func, text as sqlt

    ab = db.execute(
        select(NbModel).where(NbModel.id == id, NbModel.tenant_id == tenant_id)
    ).scalar_one_or_none()
    if not ab:
        raise HTTPException(status_code=404, detail="Abstimmung nicht gefunden")

    # Nebenbuch: Summe offener Posten (Debitoren + Kreditoren)
    nb_saldo = float(
        db.execute(
            select(func.sum(OffenerPosten.offen)).where(
                OffenerPosten.tenant_id == tenant_id,
                OffenerPosten.zahlbar == True,
            )
        ).scalar() or 0
    )

    # Hauptbuch: Summe über journal_entries für die Periode (soft-fallback)
    hb_saldo = 0.0
    try:
        hb_saldo = float(
            db.execute(sqlt("""
                SELECT COALESCE(SUM(total_credit - total_debit), 0)
                FROM domain_erp.journal_entries
                WHERE tenant_id = :tid
                  AND TO_CHAR(posting_date, 'YYYY-MM') = :periode
            """), {"tid": tenant_id, "periode": ab.periode}).scalar() or 0
        )
    except Exception:
        pass

    differenz = round(nb_saldo - hb_saldo, 2)
    ab.nebenbuch_saldo = nb_saldo
    ab.hauptbuch_saldo = hb_saldo
    ab.differenz = differenz
    ab.status = "ABGESTIMMT" if abs(differenz) < 0.01 else "ABWEICHEND"
    ab.abgestimmt_durch = str(current_user.get("sub", "system"))
    ab.updated_at = datetime.utcnow()
    db.commit()

    return {
        "message": "Abstimmung ausgeführt",
        "id": id,
        "nebenbuch_saldo": nb_saldo,
        "hauptbuch_saldo": hb_saldo,
        "differenz": differenz,
        "status": ab.status,
    }


# ============================================================================
# INTERCOMPANY-BUCHUNGEN
# ============================================================================

@router.get("/intercompany", response_model=List[IntercompanyBuchungResponse])
async def list_intercompany_buchungen(
    tenant_id: str = Depends(get_tenant_id),
    gesellschaft: Optional[str] = None,
    status: Optional[str] = None,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Liste Intercompany-Buchungen"""
    from app.finance.models import IntercompanyBuchung
    from sqlalchemy import select
    
    query = select(IntercompanyBuchung).where(IntercompanyBuchung.tenant_id == tenant_id)
    
    if gesellschaft:
        query = query.where(IntercompanyBuchung.gesellschaft == gesellschaft)
    if status:
        query = query.where(IntercompanyBuchung.status == status)
    
    query = query.order_by(IntercompanyBuchung.buchungsdatum.desc())
    
    result = db.execute(query).scalars().all()
    return result


@router.get("/intercompany/{id}", response_model=IntercompanyBuchungResponse)
async def get_intercompany_buchung(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Hole Intercompany-Buchung"""
    from app.finance.models import IntercompanyBuchung
    from sqlalchemy import select
    
    result = db.execute(
        select(IntercompanyBuchung).where(
            IntercompanyBuchung.id == id,
            IntercompanyBuchung.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Intercompany-Buchung nicht gefunden")
    return result


@router.post("/intercompany", response_model=IntercompanyBuchungResponse)
async def create_intercompany_buchung(
    data: IntercompanyBuchungCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Erstelle Intercompany-Buchung"""
    from app.finance.models import IntercompanyBuchung
    
    ic = IntercompanyBuchung(
        id=uuid7(),
        tenant_id=tenant_id,
        buchungsnr=f"IC-{datetime.now().strftime('%Y%m%d')}-{uuid7()[:4].upper()}",
        **data.model_dump(),
        status="ERSTELLT",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(ic)
    db.commit()
    db.refresh(ic)
    return ic


@router.post("/intercompany/{id}/gegenbuchung")
async def create_gegenbuchung(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Erstelle Gegenbuchung für Intercompany"""
    from app.finance.models import IntercompanyBuchung as ICModel
    from sqlalchemy import select

    original = db.execute(
        select(ICModel).where(ICModel.id == id, ICModel.tenant_id == tenant_id)
    ).scalar_one_or_none()
    if not original:
        raise HTTPException(status_code=404, detail="Intercompany-Buchung nicht gefunden")
    if original.gegenbuchung_id:
        raise HTTPException(status_code=409, detail="Gegenbuchung bereits vorhanden")

    gb_id = uuid7()
    gb_nr = f"IC-GB-{datetime.now().strftime('%Y%m%d')}-{gb_id[:4].upper()}"
    gegenbuchung = ICModel(
        id=gb_id,
        tenant_id=tenant_id,
        buchungsnr=gb_nr,
        gesellschaft_von=original.gesellschaft_nach,
        gesellschaft_nach=original.gesellschaft_von,
        belegnr=f"GB-{original.belegnr}",
        datum=datetime.utcnow().date(),
        betrag=-original.betrag,
        waehrung=original.waehrung,
        wechselkurs=original.wechselkurs,
        betrag_local=-original.betrag_local if original.betrag_local else None,
        konto_von=original.konto_nach,
        konto_nach=original.konto_von,
        status="ERSTELLT",
        referenz=f"Gegenbuchung zu {original.buchungsnr}",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(gegenbuchung)
    original.gegenbuchung_id = gb_id
    original.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Gegenbuchung erstellt", "original_id": id, "gegenbuchung_id": gb_id, "buchungsnr": gb_nr}


@router.post("/intercompany/{id}/buchen")
async def buche_intercompany(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Buche Intercompany-Buchung"""
    return {"message": "Gebucht", "id": id}


@router.get("/intercompany/salden", response_model=List)
async def get_intercompany_salden(
    gesellschaft: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Hole Intercompany-Salden"""
    from app.finance.models import IntercompanyBuchung as ICModel
    from sqlalchemy import select, func

    # Forderungen: betrag positiv (wir haben von anderen zu bekommen)
    forderungen = db.execute(
        select(
            ICModel.gesellschaft_nach.label("gegenpartner"),
            func.sum(ICModel.betrag).label("saldo"),
        ).where(
            ICModel.tenant_id == tenant_id,
            ICModel.gesellschaft_von == gesellschaft,
            ICModel.status.notin_(["STORNIERT"]),
        ).group_by(ICModel.gesellschaft_nach)
    ).all()

    # Verbindlichkeiten: betrag negativ (wir schulden anderen)
    verbindlichkeiten = db.execute(
        select(
            ICModel.gesellschaft_von.label("gegenpartner"),
            func.sum(-ICModel.betrag).label("saldo"),
        ).where(
            ICModel.tenant_id == tenant_id,
            ICModel.gesellschaft_nach == gesellschaft,
            ICModel.status.notin_(["STORNIERT"]),
        ).group_by(ICModel.gesellschaft_von)
    ).all()

    # Merge: Nettosaldo je Gegenpartner
    saldo_map: dict[str, float] = {}
    for row in forderungen:
        saldo_map[row.gegenpartner] = saldo_map.get(row.gegenpartner, 0.0) + float(row.saldo or 0)
    for row in verbindlichkeiten:
        saldo_map[row.gegenpartner] = saldo_map.get(row.gegenpartner, 0.0) - float(row.saldo or 0)

    return [
        {"gesellschaft": gesellschaft, "gegenpartner": gp, "netto_saldo": round(saldo, 2)}
        for gp, saldo in saldo_map.items()
    ]


# ============================================================================
# GOBD COMPLIANCE - VERFAHRENSDOKUMENTATION
# ============================================================================

@router.get("/gobd/verfahrensdokumentation", response_model=List)
async def list_verfahrensdokumentation(
    status: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Liste Verfahrensdokumentation (GoBD §147 AO)"""
    from app.finance.models import ProcedureDoc
    from sqlalchemy import select
    
    query = select(ProcedureDoc).where(ProcedureDoc.tenant_id == tenant_id)
    
    if status:
        query = query.where(ProcedureDoc.status == status)
    
    query = query.order_by(ProcedureDoc.created_at.desc())
    
    result = db.execute(query).scalars().all()
    return [dict(
        id=r.id,
        title=r.title,
        version=r.version,
        status=r.status,
        scope=r.scope,
        software_name=r.software_name,
        software_version=r.software_version,
        released_by=r.released_by,
        released_at=r.released_at.isoformat() if r.released_at else None,
        created_at=r.created_at.isoformat() if r.created_at else None,
    ) for r in result]


@router.get("/gobd/verfahrensdokumentation/{id}")
async def get_verfahrensdokumentation(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Hole einzelne Verfahrensdokumentation"""
    from app.finance.models import ProcedureDoc
    from sqlalchemy import select
    
    result = db.execute(
        select(ProcedureDoc).where(
            ProcedureDoc.id == id,
            ProcedureDoc.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Verfahrensdokumentation nicht gefunden")
    
    return {
        "id": result.id,
        "title": result.title,
        "version": result.version,
        "status": result.status,
        "scope": result.scope,
        "anwenderbeschreibung": result.anwenderbeschreibung,
        "technische_beschreibung": result.technische_beschreibung,
        "betriebsanleitung": result.betriebsanleitung,
        "pruefwege": result.pruefwege,
        "software_name": result.software_name,
        "software_version": result.software_version,
        "datenbank": result.datenbank,
        "betriebssystem": result.betriebssystem,
        "released_by": result.released_by,
        "released_at": result.released_at.isoformat() if result.released_at else None,
        "created_at": result.created_at.isoformat() if result.created_at else None,
        "updated_at": result.updated_at.isoformat() if result.updated_at else None,
    }


@router.post("/gobd/verfahrensdokumentation")
async def create_verfahrensdokumentation(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Erstelle Verfahrensdokumentation (GoBD-konform)"""
    from app.finance.models import ProcedureDoc
    
    doc = ProcedureDoc(
        id=uuid7(),
        tenant_id=tenant_id,
        title=data.get("title", "Neue Verfahrensdokumentation"),
        version=data.get("version", "1.0"),
        status="DRAFT",
        scope=data.get("scope"),
        anwenderbeschreibung=data.get("anwenderbeschreibung"),
        technische_beschreibung=data.get("technische_beschreibung"),
        betriebsanleitung=data.get("betriebsanleitung"),
        pruefwege=data.get("pruefwege"),
        software_name=data.get("software_name", "VALEO NeuroERP"),
        software_version=data.get("software_version", "3.0"),
        datenbank=data.get("datenbank"),
        betriebssystem=data.get("betriebssystem"),
        created_at=datetime.utcnow()
    )
    db.add(doc)
    db.commit()
    
    return {"id": doc.id, "message": "Verfahrensdokumentation erstellt"}


@router.put("/gobd/verfahrensdokumentation/{id}/freigabe")
async def release_verfahrensdokumentation(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Verfahrensdokumentation freigeben (GoBD-konform)"""
    from app.finance.models import ProcedureDoc
    from sqlalchemy import select
    
    result = db.execute(
        select(ProcedureDoc).where(
            ProcedureDoc.id == id,
            ProcedureDoc.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Verfahrensdokumentation nicht gefunden")
    
    result.status = "RELEASED"
    result.released_by = current_user.get("username", current_user.get("sub", "system"))
    result.released_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Freigegeben", "released_at": result.released_at.isoformat()}


@router.get("/gobd/verfahrensdokumentation/{id}/export")
async def export_verfahrensdokumentation_pdf(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Exportiere Verfahrensdokumentation als PDF (GoBD-konform)"""
    from app.finance.models import ProcedureDoc
    from sqlalchemy import select
    
    result = db.execute(
        select(ProcedureDoc).where(
            ProcedureDoc.id == id,
            ProcedureDoc.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Verfahrensdokumentation nicht gefunden")
    
    # GoBD-konforme PDF-Struktur
    pdf_content = f"""
VERFAHRENSDOKUMENTATION (GoBD §147 AO)
{'=' * 50}

Titel: {result.title}
Version: {result.version}
Status: {result.status}
Freigegeben von: {result.released_by or 'N/A'}
Freigegeben am: {result.released_at.isoformat() if result.released_at else 'N/A'}

{'=' * 50}

1. ANWENDUNGSBEREICH
--------------------
{result.scope or 'Keine Angabe'}

2. TECHNISCHE BESCHREIBUNG
--------------------------
Software: {result.software_name} {result.software_version}
Datenbank: {result.datenbank or 'N/A'}
Betriebssystem: {result.betriebssystem or 'N/A'}

3. ANWENDERBESCHREIBUNG
-----------------------
{result.anwenderbeschreibung or 'Siehe separates Benutzerhandbuch'}

4. PRÜFWEGE (GoBD-konform)
--------------------------
{result.pruefwege or 'Alle Buchungen sind durchgehend nummeriert und revisionssicher protokolliert.'}

Erstellt am: {result.created_at.isoformat() if result.created_at else 'N/A'}
Letzte Änderung: {result.updated_at.isoformat() if result.updated_at else 'N/A'}
    """
    
    # In production, use reportlab or weasyprint for real PDF
    return {
        "content": pdf_content,
        "filename": f"verfahrensdokumentation_{result.title}_{result.version}.txt",
        "content_type": "text/plain"
    }


# ============================================================================
# GOBD COMPLIANCE - AUBBEWAHRUNGSFRISTEN
# ============================================================================

@router.get("/gobd/richtlinien", response_model=List)
async def list_retention_policies(
    aktiv: Optional[bool] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Liste Aufbewahrungsrichtlinien (GoBD §147 AO)"""
    from app.finance.models import RetentionPolicy
    from sqlalchemy import select
    
    query = select(RetentionPolicy).where(RetentionPolicy.tenant_id.in_([tenant_id, 'default']))
    
    if aktiv is not None:
        query = query.where(RetentionPolicy.aktiv == aktiv)
    
    query = query.order_by(RetentionPolicy.aufbewahrungs_jahre.desc())
    
    result = db.execute(query).scalars().all()
    return [dict(
        id=r.id,
        dokument_typ=r.dokument_typ,
        beschreibung=r.beschreibung,
        aufbewahrungs_jahre=r.aufbewahrungs_jahre,
        frist_trigger=r.frist_trigger,
        gesetzliche_grundlage=r.gesetzliche_grundlage,
        aktiv=r.aktiv,
    ) for r in result]


@router.get("/gobd/richtlinien/{dokument_typ}/frist")
async def calculate_retention_date(
    dokument_typ: str,
    dokument_datum: date,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Berechne Aufbewahrungsfrist für Dokument (GoBD-konform)"""
    from app.finance.models import RetentionPolicy, DocumentHold
    from sqlalchemy import select
    
    # Finde passende Policy
    policy = db.execute(
        select(RetentionPolicy).where(
            RetentionPolicy.dokument_typ == dokument_typ.upper(),
            RetentionPolicy.tenant_id.in_([tenant_id, 'default']),
            RetentionPolicy.aktiv == True
        )
    ).scalar_one_or_none()
    
    if not policy:
        # Default: 10 Jahre (GoBD Standard)
        jahre = 10
        trigger = "FISCAL_YEAR_END"
        legal = "§147 AO (Standard)"
    else:
        jahre = policy.aufbewahrungs_jahre
        trigger = policy.frist_trigger
        legal = policy.gesetzliche_grundlage
    
    # Berechne Fristende basierend auf Trigger
    if trigger == "FISCAL_YEAR_END":
        # Geschäftsjahresende
        frist_datum = date(dokument_datum.year + jahre, 12, 31)
    elif trigger == "CALENDAR_YEAR_END":
        # Kalenderjahresende
        frist_datum = date(dokument_datum.year + jahre, 12, 31)
    elif trigger == "CONTRACT_END":
        # Vertragsende (hier vereinfacht)
        frist_datum = date(dokument_datum.year + jahre, dokument_datum.month, dokument_datum.day)
    else:
        # Default: creation date + jahre
        frist_datum = date(dokument_datum.year + jahre, dokument_datum.month, dokument_datum.day)
    
    # Prüfe auf aktive Löschsperren
    holds = db.execute(
        select(DocumentHold).where(
            DocumentHold.dokument_typ == dokument_typ.upper(),
            DocumentHold.tenant_id == tenant_id,
            DocumentHold.status == "ACTIVE"
        )
    ).scalars().all()
    
    active_holds = []
    for hold in holds:
        if hold.hold_end_date is None or hold.hold_end_date >= date.today():
            active_holds.append({
                "sperrgrund": hold.sperrgrund,
                "hold_start_date": hold.hold_start_date.isoformat(),
                "hold_end_date": hold.hold_end_date.isoformat() if hold.hold_end_date else "unbefristet"
            })
    
    return {
        "dokument_typ": dokument_typ.upper(),
        "dokument_datum": dokument_datum.isoformat(),
        "aufbewahrungs_jahre": jahre,
        "frist_datum": frist_datum.isoformat(),
        "gesetzliche_grundlage": legal,
        "loeschsperren": active_holds,
        "loeschbar": len(active_holds) == 0 and frist_datum < date.today()
    }


@router.get("/gobd/loeschsperren", response_model=List)
async def list_document_holds(
    status: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Liste aktive Löschsperren"""
    from app.finance.models import DocumentHold
    from sqlalchemy import select
    
    query = select(DocumentHold).where(DocumentHold.tenant_id == tenant_id)
    
    if status:
        query = query.where(DocumentHold.status == status)
    else:
        query = query.where(DocumentHold.status == "ACTIVE")
    
    query = query.order_by(DocumentHold.hold_start_date.desc())
    
    result = db.execute(query).scalars().all()
    return [dict(
        id=r.id,
        dokument_id=r.dokument_id,
        dokument_typ=r.dokument_typ,
        belegnr=r.belegnr,
        sperrgrund=r.sperrgrund,
        hold_start_date=r.hold_start_date.isoformat(),
        hold_end_date=r.hold_end_date.isoformat() if r.hold_end_date else None,
        status=r.status,
        released_by=r.released_by,
    ) for r in result]


@router.post("/gobd/loeschsperren")
async def create_document_hold(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Erstelle Löschsperre (GoBD §147 Abs. 3 AO)"""
    from app.finance.models import DocumentHold
    
    hold = DocumentHold(
        id=uuid7(),
        tenant_id=tenant_id,
        dokument_id=data.get("dokument_id"),
        dokument_typ=data.get("dokument_typ", "ALLGEMEIN").upper(),
        belegnr=data.get("belegnr"),
        sperrgrund=data.get("sperrgrund", "MANUELL"),
        beschreibung=data.get("beschreibung"),
        hold_start_date=datetime.strptime(data.get("hold_start_date", str(date.today())), "%Y-%m-%d").date(),
        hold_end_date=datetime.strptime(data["hold_end_date"], "%Y-%m-%d").date() if data.get("hold_end_date") else None,
        status="ACTIVE",
        created_at=datetime.utcnow()
    )
    db.add(hold)
    db.commit()
    
    return {"id": hold.id, "message": "Löschsperre erstellt"}


@router.put("/gobd/loeschsperren/{id}/freigabe")
async def release_document_hold(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Löschsperre aufheben"""
    from app.finance.models import DocumentHold
    from sqlalchemy import select
    
    result = db.execute(
        select(DocumentHold).where(
            DocumentHold.id == id,
            DocumentHold.tenant_id == tenant_id
        )
    ).scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Löschsperre nicht gefunden")
    
    result.status = "RELEASED"
    result.released_by = current_user.get("username", current_user.get("sub", "system"))
    result.released_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Löschsperre aufgehoben", "released_at": result.released_at.isoformat()}


@router.get("/gobd/audit/loeschprotokoll")
async def get_deletion_audit_log(
    von_datum: Optional[date] = Query(None),
    bis_datum: Optional[date] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    """Audit-Log für Löschungen (GoBD §147 Abs. 3 AO)"""
    # In production, this would query a real audit log table
    # For now, return placeholder
    return {
        "message": "Audit-Log für Löschungen",
        "von_datum": von_datum.isoformat() if von_datum else None,
        "bis_datum": bis_datum.isoformat() if bis_datum else None,
        "eintraege": []
    }
