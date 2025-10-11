"""
Finanzbuchhaltung Router
Endpoints für Debitoren, Kreditoren, Buchungsjournal, Bilanz, GuV, BWA, etc.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

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

# ========== IN-MEMORY STORES (TODO: Replace with DB) ==========

debitoren_store: List[OffenerPosten] = [
    OffenerPosten(
        id="1",
        rechnungsnr="RE-2025-0123",
        datum=date(2025, 9, 15),
        faelligkeit=date(2025, 10, 15),
        betrag=Decimal("12500.00"),
        offen=Decimal("12500.00"),
        kunde_id="K-10001",
        kunde_name="Agrar Schmidt GmbH",
        mahn_stufe=0,
        zahlbar=True,
    ),
]

kreditoren_store: List[OffenerPosten] = [
    OffenerPosten(
        id="1",
        rechnungsnr="LI-2025-4523",
        datum=date(2025, 10, 5),
        faelligkeit=date(2025, 11, 5),
        betrag=Decimal("18500.00"),
        offen=Decimal("18500.00"),
        lieferant_id="L-20001",
        lieferant_name="Saatgut Nord GmbH",
        skonto_prozent=Decimal("2.0"),
        skonto_bis=date(2025, 10, 15),
        zahlbar=True,
    ),
]

buchungen_store: List[Buchung] = [
    Buchung(
        id="1",
        belegnr="RE-2025-0123",
        datum=date(2025, 10, 11),
        soll_konto="1200",
        haben_konto="8400",
        betrag=Decimal("12500.00"),
        text="Agrar Schmidt GmbH",
        belegart="ER",
    ),
]

konten_store: List[Konto] = [
    Konto(
        id="1",
        kontonummer="1200",
        bezeichnung="Bank",
        kontoart="Umlaufvermögen",
        typ="aktiv",
        saldo=Decimal("285000.00"),
    ),
    Konto(
        id="2",
        kontonummer="8400",
        bezeichnung="Erlöse",
        kontoart="Erträge",
        typ="ertrag",
        saldo=Decimal("680000.00"),
    ),
]

anlagen_store: List[Anlage] = [
    Anlage(
        id="1",
        anlagennr="ANL-001",
        bezeichnung="Mähdrescher Claas Lexion 770",
        anschaffung=date(2022, 4, 15),
        anschaffungswert=Decimal("420000.00"),
        nutzungsdauer=10,
        afa_satz=Decimal("10.0"),
        kumulierte_afa=Decimal("126000.00"),
        buchwert=Decimal("294000.00"),
    ),
]

# ========== ENDPOINTS ==========

# Debitoren
@router.get("/debitoren", response_model=List[OffenerPosten])
async def get_debitoren(
    ueberfaellig: Optional[bool] = Query(None),
    mahn_stufe: Optional[int] = Query(None),
):
    """Offene Posten Kunden abrufen"""
    result = debitoren_store
    if ueberfaellig is not None:
        heute = date.today()
        result = [op for op in result if (op.faelligkeit < heute) == ueberfaellig]
    if mahn_stufe is not None:
        result = [op for op in result if op.mahn_stufe == mahn_stufe]
    return result

@router.post("/debitoren/{id}/mahnen")
async def mahnen(id: str):
    """Mahnung für offenen Posten erstellen"""
    for op in debitoren_store:
        if op.id == id:
            op.mahn_stufe += 1
            return {"success": True, "mahn_stufe": op.mahn_stufe}
    raise HTTPException(status_code=404, detail="Offener Posten nicht gefunden")

# Kreditoren
@router.get("/kreditoren", response_model=List[OffenerPosten])
async def get_kreditoren(zahlbar: Optional[bool] = Query(None)):
    """Offene Posten Lieferanten abrufen"""
    result = kreditoren_store
    if zahlbar is not None:
        result = [op for op in result if op.zahlbar == zahlbar]
    return result

@router.post("/kreditoren/zahlungslauf")
async def zahlungslauf(ids: List[str]):
    """Zahlungslauf für ausgewählte Kreditoren durchführen"""
    gezahlt = []
    for id in ids:
        for op in kreditoren_store:
            if op.id == id and op.zahlbar:
                op.offen = Decimal("0.00")
                gezahlt.append(op.rechnungsnr)
    return {"success": True, "gezahlt": gezahlt, "anzahl": len(gezahlt)}

# Buchungsjournal
@router.get("/buchungen", response_model=List[Buchung])
async def get_buchungen(
    datum_von: Optional[date] = Query(None),
    datum_bis: Optional[date] = Query(None),
    belegart: Optional[str] = Query(None),
):
    """Buchungsjournal abrufen"""
    result = buchungen_store
    if datum_von:
        result = [b for b in result if b.datum >= datum_von]
    if datum_bis:
        result = [b for b in result if b.datum <= datum_bis]
    if belegart:
        result = [b for b in result if b.belegart == belegart]
    return result

@router.post("/buchungen", response_model=Buchung)
async def create_buchung(buchung: Buchung):
    """Neue Buchung erstellen"""
    buchungen_store.append(buchung)
    # Update Kontosalden
    for konto in konten_store:
        if konto.kontonummer == buchung.soll_konto:
            konto.saldo += buchung.betrag
        elif konto.kontonummer == buchung.haben_konto:
            konto.saldo -= buchung.betrag
    return buchung

# Kontenplan
@router.get("/konten", response_model=List[Konto])
async def get_konten(typ: Optional[str] = Query(None)):
    """Kontenplan abrufen"""
    if typ:
        return [k for k in konten_store if k.typ == typ]
    return konten_store

@router.get("/konten/{kontonummer}", response_model=Konto)
async def get_konto(kontonummer: str):
    """Einzelnes Konto abrufen"""
    for konto in konten_store:
        if konto.kontonummer == kontonummer:
            return konto
    raise HTTPException(status_code=404, detail="Konto nicht gefunden")

# Anlagenbuchhaltung
@router.get("/anlagen", response_model=List[Anlage])
async def get_anlagen():
    """Anlagevermögen abrufen"""
    return anlagen_store

@router.post("/anlagen", response_model=Anlage)
async def create_anlage(anlage: Anlage):
    """Neue Anlage erfassen"""
    anlagen_store.append(anlage)
    return anlage

@router.get("/anlagen/{id}/afa")
async def berechne_afa(id: str, jahr: int = Query(default=2025)):
    """AfA für eine Anlage berechnen"""
    for anlage in anlagen_store:
        if anlage.id == id:
            jahres_afa = anlage.anschaffungswert * (anlage.afa_satz / Decimal("100"))
            return {
                "anlage_id": id,
                "jahr": jahr,
                "afa_satz": anlage.afa_satz,
                "jahres_afa": jahres_afa,
                "kumulierte_afa": anlage.kumulierte_afa,
                "buchwert": anlage.buchwert,
            }
    raise HTTPException(status_code=404, detail="Anlage nicht gefunden")

# Bilanz
@router.get("/bilanz")
async def get_bilanz(stichtag: str = Query(default="2024-12-31")):
    """Bilanz abrufen"""
    # Mock-Daten (TODO: Aus Konten berechnen)
    return {
        "stichtag": stichtag,
        "aktiva": {
            "anlagevermoegen": {
                "positionen": [
                    {"name": "Grundstücke & Gebäude", "betrag": 280000},
                    {"name": "Technische Anlagen", "betrag": 120000},
                    {"name": "Fuhrpark", "betrag": 50000},
                ],
                "gesamt": 450000,
            },
            "umlaufvermoegen": {
                "positionen": [
                    {"name": "Vorräte", "betrag": 185000},
                    {"name": "Forderungen", "betrag": 125000},
                    {"name": "Bank", "betrag": 65000},
                    {"name": "Kasse", "betrag": 10000},
                ],
                "gesamt": 385000,
            },
        },
        "passiva": {
            "eigenkapital": {
                "positionen": [
                    {"name": "Gezeichnetes Kapital", "betrag": 250000},
                    {"name": "Gewinnrücklage", "betrag": 180000},
                    {"name": "Jahresüberschuss", "betrag": 55000},
                ],
                "gesamt": 485000,
            },
            "fremdkapital": {
                "positionen": [
                    {"name": "Verbindlichkeiten LuL", "betrag": 125000},
                    {"name": "Bankdarlehen", "betrag": 185000},
                    {"name": "Sonstige Verbindlichkeiten", "betrag": 40000},
                ],
                "gesamt": 350000,
            },
        },
        "bilanzsumme": 835000,
        "eigenkapitalquote": 58.1,
    }

# GuV
@router.get("/guv")
async def get_guv(periode: str = Query(default="2024")):
    """Gewinn- und Verlustrechnung abrufen"""
    return {
        "periode": periode,
        "ertraege": {
            "positionen": [
                {"name": "Umsatzerlöse", "betrag": 1180000},
                {"name": "Sonstige betriebliche Erträge", "betrag": 45000},
                {"name": "Zinserträge", "betrag": 25000},
            ],
            "gesamt": 1250000,
        },
        "aufwendungen": {
            "positionen": [
                {"name": "Materialaufwand", "betrag": 520000},
                {"name": "Personalaufwand", "betrag": 385000},
                {"name": "Abschreibungen", "betrag": 85000},
                {"name": "Sonstige betriebliche Aufwendungen", "betrag": 75000},
                {"name": "Zinsaufwendungen", "betrag": 30000},
            ],
            "gesamt": 1095000,
        },
        "jahresueberschuss": 155000,
        "umsatzrendite": 12.4,
    }

# BWA
@router.get("/bwa")
async def get_bwa(monat: int = Query(default=10), jahr: int = Query(default=2025)):
    """Betriebswirtschaftliche Auswertung abrufen"""
    return {
        "periode": f"{monat}/{jahr}",
        "monat": {
            "umsatz": 125000,
            "wareneingang": 52000,
            "rohertrag": 73000,
            "personalkosten": 38000,
            "raumkosten": 8500,
            "sonstige_kosten": 12000,
            "betriebsergebnis": 14500,
            "zinsen": 2500,
            "ergebnis": 12000,
        },
        "kumuliert": {
            "umsatz": 1050000,
            "wareneingang": 480000,
            "rohertrag": 570000,
            "personalkosten": 350000,
            "raumkosten": 85000,
            "sonstige_kosten": 105000,
            "betriebsergebnis": 30000,
            "zinsen": 25000,
            "ergebnis": 5000,
        },
        "kennzahlen": {
            "rohertrag_quote": 58.4,
            "personalkosten_quote": 30.4,
            "betriebsergebnis_quote": 11.6,
        },
    }

# OP-Verwaltung
@router.get("/op-verwaltung")
async def get_op_verwaltung():
    """Offene Posten Übersicht (Debitoren + Kreditoren)"""
    debitoren_summe = sum(op.offen for op in debitoren_store)
    kreditoren_summe = sum(op.offen for op in kreditoren_store)
    
    return {
        "debitoren": {
            "anzahl": len(debitoren_store),
            "summe": debitoren_summe,
            "ueberfaellig": sum(1 for op in debitoren_store if op.faelligkeit < date.today()),
            "mahnungen": sum(1 for op in debitoren_store if op.mahn_stufe > 0),
        },
        "kreditoren": {
            "anzahl": len(kreditoren_store),
            "summe": kreditoren_summe,
            "zahlbar": sum(1 for op in kreditoren_store if op.zahlbar),
            "skonto_verfuegbar": sum(1 for op in kreditoren_store if op.skonto_bis and op.skonto_bis >= date.today()),
        },
        "liquiditaet": {
            "bank": Decimal("285000.00"),
            "erwartete_eingaenge": debitoren_summe,
            "fallige_ausgaben": sum(op.offen for op in kreditoren_store if op.faelligkeit <= date.today()),
            "prognose": Decimal("285000.00") + debitoren_summe - sum(op.offen for op in kreditoren_store if op.faelligkeit <= date.today()),
        },
    }

# DATEV Export
@router.get("/export/datev")
async def export_datev(
    typ: str = Query(..., description="buchungen, debitoren, kreditoren, anlagen"),
    datum_von: Optional[date] = Query(None),
    datum_bis: Optional[date] = Query(None),
):
    """DATEV-Export (CSV-Format)"""
    if typ == "buchungen":
        data = buchungen_store
        if datum_von:
            data = [b for b in data if b.datum >= datum_von]
        if datum_bis:
            data = [b for b in data if b.datum <= datum_bis]
        
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
async def get_fibu_stats():
    """Fibu-Dashboard Statistiken"""
    return {
        "offene_forderungen": sum(op.offen for op in debitoren_store),
        "offene_verbindlichkeiten": sum(op.offen for op in kreditoren_store),
        "buchungen_heute": len([b for b in buchungen_store if b.datum == date.today()]),
        "konten_gesamt": len(konten_store),
        "anlagen_buchwert": sum(a.buchwert for a in anlagen_store),
    }
