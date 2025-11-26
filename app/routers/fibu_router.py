"""
Finanzbuchhaltung Router
Endpoints für Debitoren, Kreditoren, Buchungsjournal, Bilanz, GuV, BWA, etc.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.core.dependency_container import container
from app.finance.repositories import OffenerPostenRepository, BuchungRepository, KontoRepository, AnlageRepository

router = APIRouter(prefix="/api/fibu", tags=["fibu"])

# ========== MODELS ==========

class OffenerPosten(BaseModel):
    id: str
    rechnungsnr: str
    datum: date
    faelligkeit: date
    betrag: Decimal
    offen: Decimal
    kunde_id: Optional[str] = None
    kunde_name: Optional[str] = None
    lieferant_id: Optional[str] = None
    lieferant_name: Optional[str] = None
    skonto_prozent: Optional[Decimal] = None
    skonto_bis: Optional[date] = None
    mahn_stufe: int = 0
    zahlbar: bool = True

class Buchung(BaseModel):
    id: str
    belegnr: str
    datum: date
    soll_konto: str
    haben_konto: str
    betrag: Decimal
    text: str
    belegart: str  # ER=Erlös, EB=Eingangsrechnung, ZE=Zahlungseingang, etc.

class Konto(BaseModel):
    id: str
    kontonummer: str
    bezeichnung: str
    kontoart: str
    typ: str  # aktiv, passiv, aufwand, ertrag
    saldo: Decimal

class Anlage(BaseModel):
    id: str
    anlagennr: str
    bezeichnung: str
    anschaffung: date
    anschaffungswert: Decimal
    nutzungsdauer: int  # Jahre
    afa_satz: Decimal
    kumulierte_afa: Decimal
    buchwert: Decimal

class BilanzPosition(BaseModel):
    name: str
    betrag: Decimal

class BilanzSeite(BaseModel):
    positionen: List[BilanzPosition]
    gesamt: Decimal

class BilanzData(BaseModel):
    periode: str
    aktiva_anlagevermoegen: BilanzSeite
    aktiva_umlaufvermoegen: BilanzSeite
    passiva_eigenkapital: BilanzSeite
    passiva_fremdkapital: BilanzSeite

class GuVData(BaseModel):
    periode: str
    ertraege: BilanzSeite
    aufwendungen: BilanzSeite
    jahresueberschuss: Decimal

# ========== DATABASE INTEGRATION ==========

# ========== ENDPOINTS ==========

# Debitoren
@router.get("/debitoren", response_model=List[OffenerPosten])
async def get_debitoren(
    ueberfaellig: Optional[bool] = Query(None),
    mahn_stufe: Optional[int] = Query(None),
    tenant_id: str = Query("system", description="Tenant ID"),
):
    """Offene Posten Kunden abrufen"""
    op_repo = container.resolve(OffenerPostenRepository)
    return op_repo.get_debitoren(tenant_id, ueberfaellig, mahn_stufe)

@router.post("/debitoren/{id}/mahnen")
async def mahnen(id: str, tenant_id: str = Query("system", description="Tenant ID")):
    """Mahnung für offenen Posten erstellen"""
    op_repo = container.resolve(OffenerPostenRepository)
    new_stufe = op_repo.get_by_id(id, tenant_id).mahn_stufe + 1 if op_repo.get_by_id(id, tenant_id) else 0
    if op_repo.update_mahn_stufe(id, tenant_id, new_stufe):
        return {"success": True, "mahn_stufe": new_stufe}
    raise HTTPException(status_code=404, detail="Offener Posten nicht gefunden")

# Kreditoren
@router.get("/kreditoren", response_model=List[OffenerPosten])
async def get_kreditoren(zahlbar: Optional[bool] = Query(None), tenant_id: str = Query("system", description="Tenant ID")):
    """Offene Posten Lieferanten abrufen"""
    op_repo = container.resolve(OffenerPostenRepository)
    return op_repo.get_kreditoren(tenant_id, zahlbar)

@router.post("/kreditoren/zahlungslauf")
async def zahlungslauf(ids: List[str], tenant_id: str = Query("system", description="Tenant ID")):
    """Zahlungslauf für ausgewählte Kreditoren durchführen"""
    op_repo = container.resolve(OffenerPostenRepository)
    gezahlt = []
    for id in ids:
        op = op_repo.get_by_id(id, tenant_id)
        if op and op.zahlbar:
            op_repo.update_zahlung(id, tenant_id, op.offen)  # Pay the full remaining amount
            gezahlt.append(op.rechnungsnr)
    return {"success": True, "gezahlt": gezahlt, "anzahl": len(gezahlt)}

# Buchungsjournal
@router.get("/buchungen", response_model=List[Buchung])
async def get_buchungen(
    datum_von: Optional[date] = Query(None),
    datum_bis: Optional[date] = Query(None),
    belegart: Optional[str] = Query(None),
    tenant_id: str = Query("system", description="Tenant ID"),
):
    """Buchungsjournal abrufen"""
    buchung_repo = container.resolve(BuchungRepository)
    return buchung_repo.get_by_filters(tenant_id, datum_von, datum_bis, belegart)

@router.post("/buchungen", response_model=Buchung)
async def create_buchung(buchung: Buchung, tenant_id: str = Query("system", description="Tenant ID")):
    """Neue Buchung erstellen"""
    buchung_repo = container.resolve(BuchungRepository)
    created_buchung = buchung_repo.create(buchung.model_dump(), tenant_id)
    # Update Kontosalden
    buchung_repo.update_konten_saldi(tenant_id, buchung.soll_konto, buchung.haben_konto, buchung.betrag)
    return created_buchung

# Kontenplan
@router.get("/konten", response_model=List[Konto])
async def get_konten(typ: Optional[str] = Query(None), tenant_id: str = Query("system", description="Tenant ID")):
    """Kontenplan abrufen"""
    konto_repo = container.resolve(KontoRepository)
    return konto_repo.get_all(tenant_id, typ)

@router.get("/konten/{kontonummer}", response_model=Konto)
async def get_konto(kontonummer: str, tenant_id: str = Query("system", description="Tenant ID")):
    """Einzelnes Konto abrufen"""
    konto_repo = container.resolve(KontoRepository)
    konto = konto_repo.get_by_nummer(kontonummer, tenant_id)
    if not konto:
        raise HTTPException(status_code=404, detail="Konto nicht gefunden")
    return konto

# Anlagenbuchhaltung
@router.get("/anlagen", response_model=List[Anlage])
async def get_anlagen(tenant_id: str = Query("system", description="Tenant ID")):
    """Anlagevermögen abrufen"""
    anlage_repo = container.resolve(AnlageRepository)
    return anlage_repo.get_all(tenant_id)

@router.post("/anlagen", response_model=Anlage)
async def create_anlage(anlage: Anlage, tenant_id: str = Query("system", description="Tenant ID")):
    """Neue Anlage erfassen"""
    anlage_repo = container.resolve(AnlageRepository)
    return anlage_repo.create(anlage.model_dump(), tenant_id)

@router.get("/anlagen/{id}/afa")
async def berechne_afa(id: str, jahr: int = Query(default=2025), tenant_id: str = Query("system", description="Tenant ID")):
    """AfA für eine Anlage berechnen"""
    anlage_repo = container.resolve(AnlageRepository)
    result = anlage_repo.berechne_afa(id, tenant_id, jahr)
    if not result:
        raise HTTPException(status_code=404, detail="Anlage nicht gefunden")
    return result

# Bilanz
@router.get("/bilanz")
async def get_bilanz(stichtag: str = Query(default="2024-12-31"), tenant_id: str = Query("system", description="Tenant ID")):
    """Bilanz abrufen"""
    konto_repo = container.resolve(KontoRepository)
    konten = konto_repo.get_all(tenant_id)

    # Calculate from real account balances
    anlagevermoegen = sum(k.saldo for k in konten if k.kontoart == "Anlagevermögen" and k.typ == "aktiv")
    umlaufvermoegen = sum(k.saldo for k in konten if k.kontoart == "Umlaufvermögen" and k.typ == "aktiv")
    eigenkapital = sum(k.saldo for k in konten if k.typ == "passiv" and "kapital" in k.bezeichnung.lower())
    fremdkapital = sum(k.saldo for k in konten if k.typ == "passiv" and "kapital" not in k.bezeichnung.lower())

    bilanzsumme = anlagevermoegen + umlaufvermoegen
    eigenkapitalquote = (eigenkapital / bilanzsumme * 100) if bilanzsumme > 0 else 0

    return {
        "stichtag": stichtag,
        "aktiva": {
            "anlagevermoegen": {
                "positionen": [{"name": "Anlagevermögen", "betrag": float(anlagevermoegen)}],
                "gesamt": float(anlagevermoegen),
            },
            "umlaufvermoegen": {
                "positionen": [{"name": "Umlaufvermögen", "betrag": float(umlaufvermoegen)}],
                "gesamt": float(umlaufvermoegen),
            },
        },
        "passiva": {
            "eigenkapital": {
                "positionen": [{"name": "Eigenkapital", "betrag": float(eigenkapital)}],
                "gesamt": float(eigenkapital),
            },
            "fremdkapital": {
                "positionen": [{"name": "Fremdkapital", "betrag": float(fremdkapital)}],
                "gesamt": float(fremdkapital),
            },
        },
        "bilanzsumme": float(bilanzsumme),
        "eigenkapitalquote": round(eigenkapitalquote, 1),
    }

# GuV
@router.get("/guv")
async def get_guv(periode: str = Query(default="2024"), tenant_id: str = Query("system", description="Tenant ID")):
    """Gewinn- und Verlustrechnung abrufen"""
    # TODO: Calculate from real booking data - requires complex P&L logic
    # For now, return placeholder indicating real calculation needed
    return {
        "periode": periode,
        "status": "placeholder",
        "message": "GuV calculation from real booking data not yet implemented",
        "ertraege": {"positionen": [], "gesamt": 0},
        "aufwendungen": {"positionen": [], "gesamt": 0},
        "jahresueberschuss": 0,
        "umsatzrendite": 0,
    }

# BWA
@router.get("/bwa")
async def get_bwa(monat: int = Query(default=10), jahr: int = Query(default=2025), tenant_id: str = Query("system", description="Tenant ID")):
    """Betriebswirtschaftliche Auswertung abrufen"""
    buchung_repo = container.resolve(BuchungRepository)

    # Calculate date ranges
    from datetime import date
    period_start = date(jahr, monat, 1)
    period_end = date(jahr, monat, 28)  # Safe end date for any month

    # Get bookings for the period
    period_bookings = buchung_repo.get_by_filters(tenant_id, period_start, period_end)

    # Get year-to-date bookings (January to current month)
    ytd_start = date(jahr, 1, 1)
    ytd_bookings = buchung_repo.get_by_filters(tenant_id, ytd_start, period_end)

    # Calculate monthly figures (simplified - in reality would need account categorization)
    umsatz = sum(b.betrag for b in period_bookings if b.belegart in ['ER', 'RE'])  # Revenue bookings
    waren_eingang = sum(b.betrag for b in period_bookings if b.belegart in ['WE', 'EB'])  # Material costs
    rohertrag = umsatz - waren_eingang if umsatz > 0 else 0

    # Simplified personnel costs (would need proper account mapping)
    personal_kosten = sum(b.betrag for b in period_bookings if 'personal' in b.text.lower() or 'gehalt' in b.text.lower())

    # Calculate year-to-date figures
    umsatz_ytd = sum(b.betrag for b in ytd_bookings if b.belegart in ['ER', 'RE'])
    waren_eingang_ytd = sum(b.betrag for b in ytd_bookings if b.belegart in ['WE', 'EB'])
    rohertrag_ytd = umsatz_ytd - waren_eingang_ytd if umsatz_ytd > 0 else 0
    personal_kosten_ytd = sum(b.betrag for b in ytd_bookings if 'personal' in b.text.lower() or 'gehalt' in b.text.lower())

    # Calculate KPIs
    rohertrag_quote = (rohertrag / umsatz * 100) if umsatz > 0 else 0
    personal_kosten_quote = (personal_kosten / umsatz * 100) if umsatz > 0 else 0

    return {
        "periode": f"{monat}/{jahr}",
        "monat": {
            "umsatz": float(umsatz),
            "wareneingang": float(waren_eingang),
            "rohertrag": float(rohertrag),
            "personalkosten": float(personal_kosten),
            "raumkosten": 0.0,  # Would need account mapping
            "sonstige_kosten": 0.0,  # Would need account mapping
            "betriebsergebnis": float(rohertrag - personal_kosten),
            "zinsen": 0.0,  # Would need account mapping
            "ergebnis": float(rohertrag - personal_kosten),
        },
        "kumuliert": {
            "umsatz": float(umsatz_ytd),
            "wareneingang": float(waren_eingang_ytd),
            "rohertrag": float(rohertrag_ytd),
            "personalkosten": float(personal_kosten_ytd),
            "raumkosten": 0.0,
            "sonstige_kosten": 0.0,
            "betriebsergebnis": float(rohertrag_ytd - personal_kosten_ytd),
            "zinsen": 0.0,
            "ergebnis": float(rohertrag_ytd - personal_kosten_ytd),
        },
        "kennzahlen": {
            "rohertrag_quote": round(rohertrag_quote, 1),
            "personalkosten_quote": round(personal_kosten_quote, 1),
            "betriebsergebnis_quote": round(((rohertrag - personal_kosten) / umsatz * 100) if umsatz > 0 else 0, 1),
        },
    }

# OP-Verwaltung
@router.get("/op-verwaltung")
async def get_op_verwaltung(tenant_id: str = Query("system", description="Tenant ID")):
    """Offene Posten Übersicht (Debitoren + Kreditoren)"""
    op_repo = container.resolve(OffenerPostenRepository)
    konto_repo = container.resolve(KontoRepository)

    debitoren = op_repo.get_debitoren(tenant_id)
    kreditoren = op_repo.get_kreditoren(tenant_id)

    debitoren_summe = sum(op.offen for op in debitoren)
    kreditoren_summe = sum(op.offen for op in kreditoren)

    # Get bank balance from accounts
    bank_konten = [k for k in konto_repo.get_all(tenant_id) if "bank" in k.bezeichnung.lower()]
    bank_balance = sum(k.saldo for k in bank_konten) if bank_konten else Decimal("0.00")

    return {
        "debitoren": {
            "anzahl": len(debitoren),
            "summe": float(debitoren_summe),
            "ueberfaellig": sum(1 for op in debitoren if op.faelligkeit < date.today()),
            "mahnungen": sum(1 for op in debitoren if op.mahn_stufe > 0),
        },
        "kreditoren": {
            "anzahl": len(kreditoren),
            "summe": float(kreditoren_summe),
            "zahlbar": sum(1 for op in kreditoren if op.zahlbar),
            "skonto_verfuegbar": sum(1 for op in kreditoren if op.skonto_bis and op.skonto_bis >= date.today()),
        },
        "liquiditaet": {
            "bank": float(bank_balance),
            "erwartete_eingaenge": float(debitoren_summe),
            "fallige_ausgaben": float(sum(op.offen for op in kreditoren if op.faelligkeit <= date.today())),
            "prognose": float(bank_balance + debitoren_summe - sum(op.offen for op in kreditoren if op.faelligkeit <= date.today())),
        },
    }

# DATEV Export
@router.get("/export/datev")
async def export_datev(
    typ: str = Query(..., description="buchungen, debitoren, kreditoren, anlagen"),
    datum_von: Optional[date] = Query(None),
    datum_bis: Optional[date] = Query(None),
    tenant_id: str = Query("system", description="Tenant ID"),
):
    """DATEV-Export (CSV-Format)"""
    if typ == "buchungen":
        buchung_repo = container.resolve(BuchungRepository)
        data = buchung_repo.get_by_filters(tenant_id, datum_von, datum_bis)

        # CSV-Header
        csv = "Datum;Beleg;Soll;Haben;Betrag;Text\n"
        for b in data:
            csv += f"{b.datum.isoformat()};{b.belegnr};{b.soll_konto};{b.haben_konto};{b.betrag};{b.text}\n"

        return {
            "format": "DATEV-ASCII",
            "typ": typ,
            "anzahl": len(data),
            "csv": csv,
        }

    return {"error": "Typ nicht unterstützt"}

# Dashboard/Statistik
@router.get("/stats")
async def get_fibu_stats(tenant_id: str = Query("system", description="Tenant ID")):
    """Fibu-Dashboard Statistiken"""
    op_repo = container.resolve(OffenerPostenRepository)
    buchung_repo = container.resolve(BuchungRepository)
    konto_repo = container.resolve(KontoRepository)
    anlage_repo = container.resolve(AnlageRepository)

    debitoren = op_repo.get_debitoren(tenant_id)
    kreditoren = op_repo.get_kreditoren(tenant_id)
    konten = konto_repo.get_all(tenant_id)
    anlagen = anlage_repo.get_all(tenant_id)

    # Get today's bookings
    heute = date.today()
    buchungen_heute = len(buchung_repo.get_by_filters(tenant_id, heute, heute))

    return {
        "offene_forderungen": float(sum(op.offen for op in debitoren)),
        "offene_verbindlichkeiten": float(sum(op.offen for op in kreditoren)),
        "buchungen_heute": buchungen_heute,
        "konten_gesamt": len(konten),
        "anlagen_buchwert": float(sum(a.buchwert for a in anlagen)),
    }
