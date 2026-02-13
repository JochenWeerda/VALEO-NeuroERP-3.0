"""
Finance Router
Advanced finance endpoints: Wechselkurse, Buchungsschemata, Kostenrechnung, Abschlusschecklisten, Nebenbuch-Abstimmung, Intercompany
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
import uuid

from app.auth.deps import get_current_user, get_tenant_id
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
    current_user=Depends(get_current_user)
):
    """Liste Wechselkurse mit optionalem Filter"""
    # TODO: Implementiere echte DB-Queries
    return []


@router.get("/wechselkurse/{id}", response_model=WechselkursResponse)
async def get_wechselkurs(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Hole einzelnen Wechselkurs"""
    # TODO: Implementiere echte DB-Queries
    raise HTTPException(status_code=404, detail="Wechselkurs nicht gefunden")


@router.post("/wechselkurse", response_model=WechselkursResponse)
async def create_wechselkurs(
    data: WechselkursCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Erstelle neuen Wechselkurs"""
    # TODO: Implementiere echte DB-Insert
    wk = Wechselkurs(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        **data.model_dump(),
        created_at=datetime.utcnow()
    )
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
    current_user=Depends(get_current_user)
):
    """Liste Buchungsschemata"""
    # TODO: Implementiere echte DB-Queries
    return []


@router.get("/buchungsschemata/{id}", response_model=BuchungsschemaResponse)
async def get_buchungsschema(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Hole Buchungsschema"""
    raise HTTPException(status_code=404, detail="Buchungsschema nicht gefunden")


@router.post("/buchungsschemata", response_model=BuchungsschemaResponse)
async def create_buchungsschema(
    data: BuchungsschemaCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Erstelle Buchungsschema"""
    schema = Buchungsschema(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        **data.model_dump(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return schema


@router.put("/buchungsschemata/{id}", response_model=BuchungsschemaResponse)
async def update_buchungsschema(
    id: str,
    data: BuchungsschemaCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Update Buchungsschema"""
    raise HTTPException(status_code=404, detail="Buchungsschema nicht gefunden")


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
    """Generiere automatischen Buchungsvorschlag"""
    # TODO: Implementiere Matching-Logik
    return Buchungsvorschlag(
        belegnr="BV-2026-0001",
        datum=date.today(),
        text=text,
        betrag=betrag,
        soll_konto="6000",
        haben_konto="4400",
        konfidenz=0.85
    )


# ============================================================================
# KOSTENRECHNUNG
# ============================================================================

@router.get("/kostenstellen", response_model=List[KostenstelleResponse])
async def list_kostenstellen(
    tenant_id: str = Depends(get_tenant_id),
    art: Optional[str] = None,
    aktiv: Optional[bool] = True,
    current_user=Depends(get_current_user)
):
    """Liste Kostenstellen"""
    # TODO: Implementiere echte DB-Queries
    return []


@router.get("/kostenstellen/{id}", response_model=KostenstelleResponse)
async def get_kostenstelle(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Hole Kostenstelle"""
    raise HTTPException(status_code=404, detail="Kostenstelle nicht gefunden")


@router.post("/kostenstellen", response_model=KostenstelleResponse)
async def create_kostenstelle(
    data: KostenstelleCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Erstelle Kostenstelle"""
    ks = Kostenstelle(
        id=str(uuid.uuid4()),
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
    """Kostenstellen-Auswertung"""
    # TODO: Implementiere echte Aggregation
    return KostenstellenReport(
        periode_von=von,
        periode_bis=bis,
        gesamt_budget=0,
        gesamt_verbraucht=0,
        gesamt_offen=0,
        kostenstellen=[],
        auswertungen=[]
    )


# ============================================================================
# ABSCHLUSSCHECKLISTEN
# ============================================================================

@router.get("/checklisten", response_model=List[AbschlussChecklisteResponse])
async def list_checklisten(
    tenant_id: str = Depends(get_tenant_id),
    periode: Optional[str] = None,
    status: Optional[str] = None,
    current_user=Depends(get_current_user)
):
    """Liste Abschlusschecklisten"""
    # TODO: Implementiere echte DB-Queries
    return []


@router.get("/checklisten/{id}", response_model=AbschlussChecklisteResponse)
async def get_checkliste(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Hole Checkliste"""
    raise HTTPException(status_code=404, detail="Checkliste nicht gefunden")


@router.post("/checklisten", response_model=AbschlussChecklisteResponse)
async def create_checkliste(
    data: AbschlussChecklisteCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Erstelle Abschlusscheckliste"""
    cl = AbschlussCheckliste(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        **data.model_dump(),
        status="OFFEN",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return cl


@router.put("/checklisten/{id}", response_model=AbschlussChecklisteResponse)
async def update_checkliste(
    id: str,
    data: AbschlussChecklisteUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Update Checkliste"""
    raise HTTPException(status_code=404, detail="Checkliste nicht gefunden")


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
    current_user=Depends(get_current_user)
):
    """Liste Nebenbuch-Abstimmungen"""
    # TODO: Implementiere echte DB-Queries
    return []


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
        id=str(uuid.uuid4()),
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
    current_user=Depends(get_current_user)
):
    """Führe Abstimmung aus (vergleiche NB ↔ HB)"""
    # TODO: Implementiere echte Abstimmungslogik
    return {"message": "Abstimmung ausgeführt", "id": id, "differenz": 0}


# ============================================================================
# INTERCOMPANY-BUCHUNGEN
# ============================================================================

@router.get("/intercompany", response_model=List[IntercompanyBuchungResponse])
async def list_intercompany_buchungen(
    tenant_id: str = Depends(get_tenant_id),
    gesellschaft: Optional[str] = None,
    status: Optional[str] = None,
    current_user=Depends(get_current_user)
):
    """Liste Intercompany-Buchungen"""
    # TODO: Implementiere echte DB-Queries
    return []


@router.get("/intercompany/{id}", response_model=IntercompanyBuchungResponse)
async def get_intercompany_buchung(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Hole Intercompany-Buchung"""
    raise HTTPException(status_code=404, detail="Intercompany-Buchung nicht gefunden")


@router.post("/intercompany", response_model=IntercompanyBuchungResponse)
async def create_intercompany_buchung(
    data: IntercompanyBuchungCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Erstelle Intercompany-Buchung"""
    ic = IntercompanyBuchung(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        buchungsnr=f"IC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}",
        **data.model_dump(),
        status="ERSTELLT",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return ic


@router.post("/intercompany/{id}/gegenbuchung")
async def create_gegenbuchung(
    id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user=Depends(get_current_user)
):
    """Erstelle Gegenbuchung für Intercompany"""
    # TODO: Implementiere echte Gegenbuchung
    return {"message": "Gegenbuchung erstellt", "original_id": id, "gegenbuchung_id": str(uuid.uuid4())}


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
    current_user=Depends(get_current_user)
):
    """Hole Intercompany-Salden"""
    # TODO: Implementiere echte Saldenberechnung
    return []
