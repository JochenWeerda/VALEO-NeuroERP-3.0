"""
Einkauf — Bestell-Vorschlag Endpoints

Bestellvorschlag-Engines (3 Typen):
  GET /einkauf/bestellvorschlaege/lager    → aus Lagerbestand
  GET /einkauf/bestellvorschlaege/verkauf  → aus offenen VK-Aufträgen
  GET /einkauf/bestellvorschlaege/rohware  → aus Rohstoff-Bedarf

CRUD Bestellvorschläge:
  GET    /einkauf/bestellvorschlaege        → Liste
  POST   /einkauf/bestellvorschlaege        → Speichern
  GET    /einkauf/bestellvorschlaege/{id}   → Detail
  PUT    /einkauf/bestellvorschlaege/{id}   → Aktualisieren
  DELETE /einkauf/bestellvorschlaege/{id}   → Löschen
  POST   /einkauf/bestellvorschlaege/{id}/zu-bestellung → Freigabe → Bestellungen

CRUD ArtikelLagerParameter:
  GET    /einkauf/artikel-lager-parameter
  POST   /einkauf/artikel-lager-parameter
  PUT    /einkauf/artikel-lager-parameter/{id}
  DELETE /einkauf/artikel-lager-parameter/{id}

CRUD Kontrakte:
  GET    /einkauf/kontrakte
  POST   /einkauf/kontrakte
  GET    /einkauf/kontrakte/{id}
  PUT    /einkauf/kontrakte/{id}
  DELETE /einkauf/kontrakte/{id}

CRUD Lieferanten (domain_einkauf):
  GET    /einkauf/lieferanten
  POST   /einkauf/lieferanten
  GET    /einkauf/lieferanten/{id}
  PUT    /einkauf/lieferanten/{id}

CRUD Bestellungen:
  GET    /einkauf/bestellungen
  POST   /einkauf/bestellungen
  GET    /einkauf/bestellungen/{id}
  PUT    /einkauf/bestellungen/{id}
  POST   /einkauf/bestellungen/{id}/versenden    → E-Mail / Fax / EDI versenden
"""
from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.infrastructure.models.einkauf_models import (
    ArtikelLagerParameter,
    EinkaufBestellvorschlag,
    EinkaufBestellvorschlagPosition,
    EinkaufBestellung,
    EinkaufBestellungPosition,
    EinkaufKontrakt,
    EinkaufKontraktPosition,
    EinkaufLieferant,
    LagerKontenzuordnung,
    PalettenKontoBuchung,
    PfandKontoBuchung,
    FremdwarenEinlagerung,
)
from modules.einkauf.services.bestellvorschlag_service import (
    engine_lager,
    engine_rohware,
    engine_verkauf,
    save_vorschlag,
    vorschlag_zu_bestellungen,
)

router = APIRouter(tags=["einkauf", "bestellvorschlag"])


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────────────────────────────────────

class LieferantCreate(BaseModel):
    lieferantennummer: str
    firmenname: str
    partner_id: Optional[str] = None
    ansprechpartner: Optional[str] = None
    email: Optional[str] = None
    telefon: Optional[str] = None
    fax: Optional[str] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    land: str = "Deutschland"
    steuernummer: Optional[str] = None
    ust_id: Optional[str] = None
    zahlungsbedingungen: Optional[str] = None
    zahlungsziel_tage: Optional[int] = None
    skonto_prozent: Optional[float] = None
    lieferzeit_tage: Optional[int] = None
    mindestbestellwert: Optional[float] = None
    bewertung: Optional[int] = None
    edi_kennung: Optional[str] = None
    edi_format: Optional[str] = None
    email_bestellung: Optional[str] = None
    fax_bestellung: Optional[str] = None
    notiz: Optional[str] = None


class LieferantUpdate(LieferantCreate):
    lieferantennummer: Optional[str] = None  # type: ignore[assignment]
    firmenname: Optional[str] = None          # type: ignore[assignment]


class KontraktCreate(BaseModel):
    kontraktnummer: str
    lieferant_id: str
    bezeichnung: Optional[str] = None
    gueltig_von: Optional[date] = None
    gueltig_bis: Optional[date] = None
    status: str = "aktiv"
    kontrakt_typ: str = "rahmen"
    waehrung: str = "EUR"
    gesamtmenge: Optional[float] = None
    niederlassung_id: Optional[str] = None
    notiz: Optional[str] = None


class KontraktPosCreate(BaseModel):
    pos_nr: int
    article_id: Optional[str] = None
    artikel_bezeichnung: Optional[str] = None
    menge: float
    einheit: Optional[str] = None
    preis: Optional[float] = None
    preis_einheit: str = "100kg"
    preisbindung: str = "fix"
    gueltig_von: Optional[date] = None
    gueltig_bis: Optional[date] = None
    notiz: Optional[str] = None


class ArtikelLagerParamCreate(BaseModel):
    article_id: str
    warehouse_id: Optional[str] = None
    niederlassung_id: Optional[str] = None
    mindestbestand: float = 0.0
    maximalbestand: Optional[float] = None
    meldebestand: float = 0.0
    soll_bestand: Optional[float] = None
    std_lieferant_id: Optional[str] = None
    std_bestellmenge: Optional[float] = None
    std_einheit: Optional[str] = None
    wiederbeschaffungs_tage: int = 3
    durchschnitt_verbrauch_tag: Optional[float] = None
    notiz: Optional[str] = None


class ArtikelLagerParamUpdate(ArtikelLagerParamCreate):
    article_id: Optional[str] = None  # type: ignore[assignment]


class VorschlagSaveRequest(BaseModel):
    vorschlag_typ: str  # lager | verkauf | rohware
    positionen: list[dict[str, Any]]
    parameter: Optional[dict[str, Any]] = None
    niederlassung_id: Optional[str] = None
    bezeichnung: Optional[str] = None


class BestellungCreate(BaseModel):
    lieferant_id: str
    bestelldatum: date
    niederlassung_id: Optional[str] = None
    lieferdatum_wunsch: Optional[date] = None
    versand_art: str = "email"
    kontrakt_id: Optional[str] = None
    unsere_referenz: Optional[str] = None
    ihre_referenz: Optional[str] = None
    freitext_kopf: Optional[str] = None
    freitext_fuss: Optional[str] = None
    notiz: Optional[str] = None
    positionen: list[dict[str, Any]] = []


class LagerKontenzuordnungCreate(BaseModel):
    artikelgruppe: str
    niederlassung_id: Optional[str] = None
    bestandskonto: str
    gegenkonto_zugang: Optional[str] = None
    gegenkonto_abgang: Optional[str] = None
    paletten_konto: Optional[str] = None
    pfand_konto: Optional[str] = None
    fremdwaren_konto: Optional[str] = None
    einlagerung_konto: Optional[str] = None
    chargen_konto: Optional[str] = None
    ust_schluessel: Optional[str] = None
    notiz: Optional[str] = None


class PalettenBuchungCreate(BaseModel):
    partner_id: str
    partner_typ: str
    niederlassung_id: Optional[str] = None
    buchungsdatum: date
    buchungsart: str
    paletten_typ: str = "EUR-Palette"
    menge: int
    referenz_typ: Optional[str] = None
    referenz_id: Optional[str] = None
    referenz_nr: Optional[str] = None
    notiz: Optional[str] = None


class PfandBuchungCreate(BaseModel):
    partner_id: str
    partner_typ: str
    niederlassung_id: Optional[str] = None
    buchungsdatum: date
    buchungsart: str
    gebinde_typ: str
    menge: float
    pfandwert_je_einheit: Optional[float] = None
    referenz_typ: Optional[str] = None
    referenz_id: Optional[str] = None
    referenz_nr: Optional[str] = None
    notiz: Optional[str] = None


class FremdwarenCreate(BaseModel):
    einlagerungs_nr: str
    eigentuemer_id: str
    eigentuemer_name: Optional[str] = None
    niederlassung_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    lagerort: Optional[str] = None
    article_id: Optional[str] = None
    artikel_nr: Optional[str] = None
    artikel_bezeichnung: Optional[str] = None
    charge: Optional[str] = None
    einlagerungstyp: str = "fremdware"
    menge_eingelagert: float
    einheit: Optional[str] = None
    einlagerungsdatum: date
    geplante_auslagerung: Optional[date] = None
    gebuehr_pro_tag: Optional[float] = None
    gebuehr_einheit: str = "t"
    notiz: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Bestell-Vorschlag Engines
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/bestellvorschlaege/lager")
async def vorschlag_lager(
    niederlassung_id: Optional[str] = Query(None),
    artikelgruppe: Optional[str] = Query(None),
    artikel_nr: Optional[str] = Query(None, alias="artikelNr"),
    warehouse_id: Optional[str] = Query(None),
    nur_unter_meldebestand: bool = Query(True),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Engine 1: Bestell-Vorschläge aus Lagerbestand (Meldebestand-Unterschreitung)."""
    return engine_lager(
        db,
        tenant_id=tenant_id,
        niederlassung_id=niederlassung_id,
        artikelgruppe=artikelgruppe,
        artikel_nr=artikel_nr,
        warehouse_id=warehouse_id,
        nur_unter_meldebestand=nur_unter_meldebestand,
    )


@router.get("/einkauf/bestellvorschlaege/verkauf")
async def vorschlag_verkauf(
    niederlassung_id: Optional[str] = Query(None),
    artikelgruppe: Optional[str] = Query(None),
    von_datum: Optional[date] = Query(None, alias="vonDatum"),
    bis_datum: Optional[date] = Query(None, alias="bisDatum"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Engine 2: Bestell-Vorschläge aus offenen VK-Auftrags-Positionen."""
    return engine_verkauf(
        db,
        tenant_id=tenant_id,
        niederlassung_id=niederlassung_id,
        artikelgruppe=artikelgruppe,
        von_datum=von_datum,
        bis_datum=bis_datum,
    )


@router.get("/einkauf/bestellvorschlaege/rohware")
async def vorschlag_rohware(
    stichtag: Optional[date] = Query(None),
    niederlassung_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Engine 3: Bestell-Vorschläge aus Rohstoff-Bedarf."""
    return engine_rohware(
        db,
        tenant_id=tenant_id,
        stichtag=stichtag,
        niederlassung_id=niederlassung_id,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Bestellvorschläge CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/bestellvorschlaege")
async def list_bestellvorschlaege(
    vorschlag_typ: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    von: Optional[date] = Query(None),
    bis: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    q = (
        db.query(EinkaufBestellvorschlag)
        .filter(EinkaufBestellvorschlag.tenant_id == tenant_id)
    )
    if vorschlag_typ:
        q = q.filter(EinkaufBestellvorschlag.vorschlag_typ == vorschlag_typ)
    if status:
        q = q.filter(EinkaufBestellvorschlag.status == status)
    if von:
        q = q.filter(EinkaufBestellvorschlag.datum >= von)
    if bis:
        q = q.filter(EinkaufBestellvorschlag.datum <= bis)

    return [
        {
            "id":              str(v.id),
            "vorschlag_typ":   v.vorschlag_typ,
            "bezeichnung":     v.bezeichnung,
            "datum":           v.datum.isoformat() if v.datum else None,
            "status":          v.status,
            "niederlassung_id": v.niederlassung_id,
            "erstellt_von":    v.erstellt_von,
            "positionen_anz":  len(v.positionen),
            "created_at":      v.created_at.isoformat() if v.created_at else None,
        }
        for v in q.order_by(EinkaufBestellvorschlag.datum.desc()).all()
    ]


@router.post("/einkauf/bestellvorschlaege", status_code=201)
async def create_bestellvorschlag(
    data: VorschlagSaveRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Speichert einen berechneten Vorschlag persistent."""
    vorschlag = save_vorschlag(
        db,
        tenant_id=tenant_id,
        vorschlag_typ=data.vorschlag_typ,
        positionen=data.positionen,
        parameter=data.parameter,
        niederlassung_id=data.niederlassung_id,
    )
    if data.bezeichnung:
        vorschlag.bezeichnung = data.bezeichnung
    db.commit()
    db.refresh(vorschlag)
    return {"id": str(vorschlag.id), "status": vorschlag.status,
            "positionen_anz": len(vorschlag.positionen)}


@router.get("/einkauf/bestellvorschlaege/{vorschlag_id}")
async def get_bestellvorschlag(
    vorschlag_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    v = (
        db.query(EinkaufBestellvorschlag)
        .filter(EinkaufBestellvorschlag.id == vorschlag_id,
                EinkaufBestellvorschlag.tenant_id == tenant_id)
        .first()
    )
    if not v:
        raise HTTPException(404, "Vorschlag nicht gefunden")
    return {
        "id":              str(v.id),
        "vorschlag_typ":   v.vorschlag_typ,
        "bezeichnung":     v.bezeichnung,
        "datum":           v.datum.isoformat() if v.datum else None,
        "status":          v.status,
        "parameter":       v.parameter,
        "niederlassung_id": v.niederlassung_id,
        "erstellt_von":    v.erstellt_von,
        "freigegeben_von": v.freigegeben_von,
        "freigegeben_am":  v.freigegeben_am.isoformat() if v.freigegeben_am else None,
        "positionen": [
            {
                "id":                  str(p.id),
                "pos_nr":              p.pos_nr,
                "article_id":          p.article_id,
                "artikel_nr":          p.artikel_nr,
                "artikel_bezeichnung": p.artikel_bezeichnung,
                "artikel_gruppe":      p.artikel_gruppe,
                "einheit":             p.einheit,
                "ist_bestand":         float(p.ist_bestand or 0),
                "offene_auftraege":    float(p.offene_auftraege or 0),
                "bedarf":              float(p.bedarf or 0),
                "vorschlag_menge":     float(p.vorschlag_menge),
                "bestell_menge":       float(p.bestell_menge or p.vorschlag_menge),
                "lieferant_id":        str(p.lieferant_id) if p.lieferant_id else None,
                "lieferant_name":      p.lieferant_name,
                "letzter_preis":       float(p.letzter_preis) if p.letzter_preis else None,
                "preis_einheit":       p.preis_einheit,
                "status":              p.status,
            }
            for p in v.positionen
        ],
    }


@router.put("/einkauf/bestellvorschlaege/{vorschlag_id}")
async def update_bestellvorschlag(
    vorschlag_id: str,
    data: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Aktualisiert Vorschlag-Positionen (bestell_menge, status, lieferant_id)."""
    v = (
        db.query(EinkaufBestellvorschlag)
        .filter(EinkaufBestellvorschlag.id == vorschlag_id,
                EinkaufBestellvorschlag.tenant_id == tenant_id)
        .first()
    )
    if not v:
        raise HTTPException(404, "Vorschlag nicht gefunden")

    # Kopf-Felder aktualisieren
    for field in ("bezeichnung", "status", "notiz"):
        if field in data:
            setattr(v, field, data[field])

    # Positionen aktualisieren
    if "positionen" in data:
        pos_map = {str(p.id): p for p in v.positionen}
        for pos_data in data["positionen"]:
            pos = pos_map.get(str(pos_data.get("id", "")))
            if pos:
                for f in ("bestell_menge", "lieferant_id", "lieferant_name",
                          "letzter_preis", "status"):
                    if f in pos_data:
                        setattr(pos, f, pos_data[f])

    db.commit()
    return {"id": str(v.id), "status": v.status}


@router.delete("/einkauf/bestellvorschlaege/{vorschlag_id}",
               status_code=204, response_class=Response)
async def delete_bestellvorschlag(
    vorschlag_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    v = (
        db.query(EinkaufBestellvorschlag)
        .filter(EinkaufBestellvorschlag.id == vorschlag_id,
                EinkaufBestellvorschlag.tenant_id == tenant_id)
        .first()
    )
    if not v:
        raise HTTPException(404, "Vorschlag nicht gefunden")
    db.delete(v)
    db.commit()
    return Response(status_code=204)


@router.post("/einkauf/bestellvorschlaege/{vorschlag_id}/zu-bestellung", status_code=201)
async def vorschlag_freigeben(
    vorschlag_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Gibt Vorschlag frei und erzeugt daraus Einkaufs-Bestellungen je Lieferant."""
    try:
        orders = vorschlag_zu_bestellungen(
            db,
            vorschlag_id=vorschlag_id,
            tenant_id=tenant_id,
            freigegeben_von="system",
        )
        db.commit()
        return {"bestellungen": orders, "anzahl": len(orders)}
    except ValueError as e:
        raise HTTPException(404, str(e))


# ─────────────────────────────────────────────────────────────────────────────
# ArtikelLagerParameter CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/artikel-lager-parameter")
async def list_artikel_lager_parameter(
    article_id: Optional[str] = Query(None),
    warehouse_id: Optional[str] = Query(None),
    niederlassung_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    q = (
        db.query(ArtikelLagerParameter)
        .filter(ArtikelLagerParameter.tenant_id == tenant_id)
    )
    if article_id:
        q = q.filter(ArtikelLagerParameter.article_id == article_id)
    if warehouse_id:
        q = q.filter(ArtikelLagerParameter.warehouse_id == warehouse_id)
    if niederlassung_id:
        q = q.filter(ArtikelLagerParameter.niederlassung_id == niederlassung_id)

    return [
        {
            "id":              str(p.id),
            "article_id":      p.article_id,
            "warehouse_id":    p.warehouse_id,
            "niederlassung_id": p.niederlassung_id,
            "mindestbestand":  float(p.mindestbestand or 0),
            "maximalbestand":  float(p.maximalbestand or 0),
            "meldebestand":    float(p.meldebestand or 0),
            "soll_bestand":    float(p.soll_bestand or 0),
            "std_lieferant_id": str(p.std_lieferant_id) if p.std_lieferant_id else None,
            "std_bestellmenge": float(p.std_bestellmenge) if p.std_bestellmenge else None,
            "std_einheit":     p.std_einheit,
            "wiederbeschaffungs_tage": p.wiederbeschaffungs_tage,
            "durchschnitt_verbrauch_tag": float(p.durchschnitt_verbrauch_tag) if p.durchschnitt_verbrauch_tag else None,
            "reichweite_tage": float(p.reichweite_tage) if p.reichweite_tage else None,
            "aktiv":           p.aktiv,
            "notiz":           p.notiz,
        }
        for p in q.all()
    ]


@router.post("/einkauf/artikel-lager-parameter", status_code=201)
async def create_artikel_lager_parameter(
    data: ArtikelLagerParamCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    # Prüfen ob schon vorhanden
    existing = (
        db.query(ArtikelLagerParameter)
        .filter(
            ArtikelLagerParameter.tenant_id == tenant_id,
            ArtikelLagerParameter.article_id == data.article_id,
            ArtikelLagerParameter.warehouse_id == data.warehouse_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(409, "Parameter für diesen Artikel/Lager bereits vorhanden")

    param = ArtikelLagerParameter(
        id=uuid7(),
        tenant_id=tenant_id,
        **data.model_dump(),
    )
    db.add(param)
    db.commit()
    db.refresh(param)
    return {"id": str(param.id), "article_id": param.article_id}


@router.put("/einkauf/artikel-lager-parameter/{param_id}")
async def update_artikel_lager_parameter(
    param_id: str,
    data: ArtikelLagerParamUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    p = (
        db.query(ArtikelLagerParameter)
        .filter(ArtikelLagerParameter.id == param_id,
                ArtikelLagerParameter.tenant_id == tenant_id)
        .first()
    )
    if not p:
        raise HTTPException(404, "Parameter nicht gefunden")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(p, field, value)
    db.commit()
    return {"id": str(p.id)}


@router.delete("/einkauf/artikel-lager-parameter/{param_id}",
               status_code=204, response_class=Response)
async def delete_artikel_lager_parameter(
    param_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    p = (
        db.query(ArtikelLagerParameter)
        .filter(ArtikelLagerParameter.id == param_id,
                ArtikelLagerParameter.tenant_id == tenant_id)
        .first()
    )
    if not p:
        raise HTTPException(404, "Parameter nicht gefunden")
    db.delete(p)
    db.commit()
    return Response(status_code=204)


# ─────────────────────────────────────────────────────────────────────────────
# Lieferanten CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/lieferanten")
async def list_lieferanten(
    suche: Optional[str] = Query(None),
    aktiv: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    q = db.query(EinkaufLieferant).filter(EinkaufLieferant.tenant_id == tenant_id)
    if aktiv is not None:
        q = q.filter(EinkaufLieferant.aktiv == aktiv)
    if suche:
        q = q.filter(EinkaufLieferant.firmenname.ilike(f"%{suche}%"))
    return [
        {
            "id":                 str(lf.id),
            "lieferantennummer":  lf.lieferantennummer,
            "firmenname":         lf.firmenname,
            "ort":                lf.ort,
            "plz":                lf.plz,
            "email":              lf.email,
            "telefon":            lf.telefon,
            "partner_id":         lf.partner_id,
            "zahlungsbedingungen": lf.zahlungsbedingungen,
            "lieferzeit_tage":    lf.lieferzeit_tage,
            "bewertung":          lf.bewertung,
            "aktiv":              lf.aktiv,
        }
        for lf in q.order_by(EinkaufLieferant.firmenname).all()
    ]


@router.post("/einkauf/lieferanten", status_code=201)
async def create_lieferant(
    data: LieferantCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    lf = EinkaufLieferant(id=uuid7(), tenant_id=tenant_id, **data.model_dump())
    db.add(lf)
    db.commit()
    db.refresh(lf)
    return {"id": str(lf.id), "lieferantennummer": lf.lieferantennummer,
            "firmenname": lf.firmenname}


@router.get("/einkauf/lieferanten/{lieferant_id}")
async def get_lieferant(
    lieferant_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    lf = (
        db.query(EinkaufLieferant)
        .filter(EinkaufLieferant.id == lieferant_id,
                EinkaufLieferant.tenant_id == tenant_id)
        .first()
    )
    if not lf:
        raise HTTPException(404, "Lieferant nicht gefunden")
    return {c.name: getattr(lf, c.name) for c in lf.__table__.columns
            if c.name not in ("created_at", "updated_at")}


@router.put("/einkauf/lieferanten/{lieferant_id}")
async def update_lieferant(
    lieferant_id: str,
    data: LieferantUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    lf = (
        db.query(EinkaufLieferant)
        .filter(EinkaufLieferant.id == lieferant_id,
                EinkaufLieferant.tenant_id == tenant_id)
        .first()
    )
    if not lf:
        raise HTTPException(404, "Lieferant nicht gefunden")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(lf, field, value)
    db.commit()
    return {"id": str(lf.id)}


# ─────────────────────────────────────────────────────────────────────────────
# Kontrakte CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/kontrakte")
async def list_kontrakte(
    lieferant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    q = db.query(EinkaufKontrakt).filter(EinkaufKontrakt.tenant_id == tenant_id)
    if lieferant_id:
        q = q.filter(EinkaufKontrakt.lieferant_id == lieferant_id)
    if status:
        q = q.filter(EinkaufKontrakt.status == status)
    return [
        {
            "id":            str(k.id),
            "kontraktnummer": k.kontraktnummer,
            "lieferant_id":  str(k.lieferant_id),
            "bezeichnung":   k.bezeichnung,
            "gueltig_von":   k.gueltig_von.isoformat() if k.gueltig_von else None,
            "gueltig_bis":   k.gueltig_bis.isoformat() if k.gueltig_bis else None,
            "status":        k.status,
            "kontrakt_typ":  k.kontrakt_typ,
            "gesamtmenge":   float(k.gesamtmenge) if k.gesamtmenge else None,
            "offene_menge":  float(k.offene_menge) if k.offene_menge else None,
        }
        for k in q.order_by(EinkaufKontrakt.gueltig_bis.desc()).all()
    ]


@router.post("/einkauf/kontrakte", status_code=201)
async def create_kontrakt(
    data: KontraktCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    k = EinkaufKontrakt(id=uuid7(), tenant_id=tenant_id, **data.model_dump())
    db.add(k)
    db.commit()
    db.refresh(k)
    return {"id": str(k.id), "kontraktnummer": k.kontraktnummer}


@router.get("/einkauf/kontrakte/{kontrakt_id}")
async def get_kontrakt(
    kontrakt_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    k = (
        db.query(EinkaufKontrakt)
        .filter(EinkaufKontrakt.id == kontrakt_id,
                EinkaufKontrakt.tenant_id == tenant_id)
        .first()
    )
    if not k:
        raise HTTPException(404, "Kontrakt nicht gefunden")
    return {
        "id":            str(k.id),
        "kontraktnummer": k.kontraktnummer,
        "lieferant_id":  str(k.lieferant_id),
        "bezeichnung":   k.bezeichnung,
        "gueltig_von":   k.gueltig_von.isoformat() if k.gueltig_von else None,
        "gueltig_bis":   k.gueltig_bis.isoformat() if k.gueltig_bis else None,
        "status":        k.status,
        "kontrakt_typ":  k.kontrakt_typ,
        "gesamtmenge":   float(k.gesamtmenge) if k.gesamtmenge else None,
        "offene_menge":  float(k.offene_menge) if k.offene_menge else None,
        "positionen": [
            {
                "id":       str(p.id),
                "pos_nr":   p.pos_nr,
                "article_id": p.article_id,
                "artikel_bezeichnung": p.artikel_bezeichnung,
                "menge":    float(p.menge),
                "offene_menge": float(p.offene_menge) if p.offene_menge else None,
                "einheit":  p.einheit,
                "preis":    float(p.preis) if p.preis else None,
                "preis_einheit": p.preis_einheit,
                "preisbindung": p.preisbindung,
                "gueltig_von": p.gueltig_von.isoformat() if p.gueltig_von else None,
                "gueltig_bis": p.gueltig_bis.isoformat() if p.gueltig_bis else None,
            }
            for p in k.positionen
        ],
    }


@router.put("/einkauf/kontrakte/{kontrakt_id}")
async def update_kontrakt(
    kontrakt_id: str,
    data: KontraktCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    k = (
        db.query(EinkaufKontrakt)
        .filter(EinkaufKontrakt.id == kontrakt_id,
                EinkaufKontrakt.tenant_id == tenant_id)
        .first()
    )
    if not k:
        raise HTTPException(404, "Kontrakt nicht gefunden")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(k, field, value)
    db.commit()
    return {"id": str(k.id)}


@router.post("/einkauf/kontrakte/{kontrakt_id}/positionen", status_code=201)
async def add_kontrakt_position(
    kontrakt_id: str,
    data: KontraktPosCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    k = (
        db.query(EinkaufKontrakt)
        .filter(EinkaufKontrakt.id == kontrakt_id,
                EinkaufKontrakt.tenant_id == tenant_id)
        .first()
    )
    if not k:
        raise HTTPException(404, "Kontrakt nicht gefunden")
    pos = EinkaufKontraktPosition(id=uuid7(), kontrakt_id=kontrakt_id, **data.model_dump())
    db.add(pos)
    db.commit()
    return {"id": str(pos.id)}


# ─────────────────────────────────────────────────────────────────────────────
# Bestellungen CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/bestellungen")
async def list_bestellungen(
    lieferant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    von: Optional[date] = Query(None),
    bis: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    q = db.query(EinkaufBestellung).filter(EinkaufBestellung.tenant_id == tenant_id)
    if lieferant_id:
        q = q.filter(EinkaufBestellung.lieferant_id == lieferant_id)
    if status:
        q = q.filter(EinkaufBestellung.status == status)
    if von:
        q = q.filter(EinkaufBestellung.bestelldatum >= von)
    if bis:
        q = q.filter(EinkaufBestellung.bestelldatum <= bis)
    return [
        {
            "id":             str(b.id),
            "bestellnummer":  b.bestellnummer,
            "lieferant_id":   str(b.lieferant_id),
            "lieferant_name": b.lieferant.firmenname if b.lieferant else None,
            "bestelldatum":   b.bestelldatum.isoformat() if b.bestelldatum else None,
            "lieferdatum_wunsch": b.lieferdatum_wunsch.isoformat() if b.lieferdatum_wunsch else None,
            "status":         b.status,
            "versand_art":    b.versand_art,
            "versandt_am":    b.versandt_am.isoformat() if b.versandt_am else None,
            "netto_summe":    float(b.netto_summe) if b.netto_summe else None,
            "brutto_summe":   float(b.brutto_summe) if b.brutto_summe else None,
            "positionen_anz": len(b.positionen),
        }
        for b in q.order_by(EinkaufBestellung.bestelldatum.desc()).all()
    ]


@router.post("/einkauf/bestellungen", status_code=201)
async def create_bestellung(
    data: BestellungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    from datetime import datetime
    ts = datetime.now().strftime("%y%m%d%H%M%S")
    bestell_nr = f"EK-{ts}"

    bestellung = EinkaufBestellung(
        id=uuid7(),
        tenant_id=tenant_id,
        bestellnummer=bestell_nr,
        **{k: v for k, v in data.model_dump().items() if k != "positionen"},
    )
    db.add(bestellung)
    db.flush()

    for i, pos_data in enumerate(data.positionen, start=1):
        pos = EinkaufBestellungPosition(
            id=uuid7(),
            bestellung_id=bestellung.id,
            pos_nr=i,
            artikel_nr=pos_data.get("artikel_nr", ""),
            artikel_bezeichnung=pos_data.get("artikel_bezeichnung", ""),
            article_id=pos_data.get("article_id"),
            menge=pos_data.get("menge", 0),
            menge_geliefert=0,
            menge_offen=pos_data.get("menge", 0),
            einheit=pos_data.get("einheit", "t"),
            einzelpreis=pos_data.get("einzelpreis"),
            preis_einheit=pos_data.get("preis_einheit", "100kg"),
        )
        db.add(pos)

    db.commit()
    db.refresh(bestellung)
    return {"id": str(bestellung.id), "bestellnummer": bestellung.bestellnummer}


@router.get("/einkauf/bestellungen/{bestellung_id}")
async def get_bestellung(
    bestellung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    b = (
        db.query(EinkaufBestellung)
        .filter(EinkaufBestellung.id == bestellung_id,
                EinkaufBestellung.tenant_id == tenant_id)
        .first()
    )
    if not b:
        raise HTTPException(404, "Bestellung nicht gefunden")
    return {
        "id":             str(b.id),
        "bestellnummer":  b.bestellnummer,
        "lieferant_id":   str(b.lieferant_id),
        "lieferant_name": b.lieferant.firmenname if b.lieferant else None,
        "bestelldatum":   b.bestelldatum.isoformat() if b.bestelldatum else None,
        "lieferdatum_wunsch": b.lieferdatum_wunsch.isoformat() if b.lieferdatum_wunsch else None,
        "lieferdatum_zugesagt": b.lieferdatum_zugesagt.isoformat() if b.lieferdatum_zugesagt else None,
        "status":         b.status,
        "versand_art":    b.versand_art,
        "netto_summe":    float(b.netto_summe) if b.netto_summe else None,
        "mwst_betrag":    float(b.mwst_betrag) if b.mwst_betrag else None,
        "brutto_summe":   float(b.brutto_summe) if b.brutto_summe else None,
        "unsere_referenz": b.unsere_referenz,
        "ihre_referenz":  b.ihre_referenz,
        "freitext_kopf":  b.freitext_kopf,
        "freitext_fuss":  b.freitext_fuss,
        "notiz":          b.notiz,
        "positionen": [
            {
                "id":                  str(p.id),
                "pos_nr":              p.pos_nr,
                "article_id":          p.article_id,
                "artikel_nr":          p.artikel_nr,
                "artikel_bezeichnung": p.artikel_bezeichnung,
                "lieferanten_artnr":   p.lieferanten_artnr,
                "menge":               float(p.menge),
                "menge_geliefert":     float(p.menge_geliefert or 0),
                "menge_offen":         float(p.menge_offen or p.menge),
                "einheit":             p.einheit,
                "einzelpreis":         float(p.einzelpreis) if p.einzelpreis else None,
                "preis_einheit":       p.preis_einheit,
                "netto_betrag":        float(p.netto_betrag) if p.netto_betrag else None,
                "status":              p.status,
            }
            for p in b.positionen
        ],
    }


@router.put("/einkauf/bestellungen/{bestellung_id}")
async def update_bestellung(
    bestellung_id: str,
    data: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    b = (
        db.query(EinkaufBestellung)
        .filter(EinkaufBestellung.id == bestellung_id,
                EinkaufBestellung.tenant_id == tenant_id)
        .first()
    )
    if not b:
        raise HTTPException(404, "Bestellung nicht gefunden")
    for field in ("status", "lieferdatum_zugesagt", "lieferdatum_wunsch",
                  "notiz", "freitext_kopf", "freitext_fuss",
                  "unsere_referenz", "ihre_referenz"):
        if field in data:
            setattr(b, field, data[field])
    db.commit()
    return {"id": str(b.id), "status": b.status}


@router.post("/einkauf/bestellungen/{bestellung_id}/versenden")
async def bestellung_versenden(
    bestellung_id: str,
    versand_art: str = Query("email"),
    empfaenger: Optional[str] = Query(None, description="Override-Empfänger (E-Mail oder Faxnummer)"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """
    Bestellung versenden: E-Mail (SMTP), Fax (Twilio) oder EDI (EDIFACT/SFTP).
    Setzt Status auf 'versandt' und speichert Versanddatum.
    """
    from modules.einkauf.services.versand_service import versende_bestellung

    b = (
        db.query(EinkaufBestellung)
        .filter(EinkaufBestellung.id == bestellung_id,
                EinkaufBestellung.tenant_id == tenant_id)
        .first()
    )
    if not b:
        raise HTTPException(404, "Bestellung nicht gefunden")

    result = versende_bestellung(
        db, b,
        versand_art=versand_art,
        empfaenger_override=empfaenger,
    )
    db.commit()

    return {
        "bestellung_id": str(b.id),
        "bestellnummer": b.bestellnummer,
        "versand":       result,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Lager-Konten-Zuordnung CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/lager-konten")
async def list_lager_konten(
    artikelgruppe: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    q = db.query(LagerKontenzuordnung).filter(LagerKontenzuordnung.tenant_id == tenant_id)
    if artikelgruppe:
        q = q.filter(LagerKontenzuordnung.artikelgruppe == artikelgruppe)
    return [
        {c.name: getattr(lk, c.name) for c in lk.__table__.columns
         if c.name not in ("created_at", "updated_at")}
        for lk in q.order_by(LagerKontenzuordnung.artikelgruppe).all()
    ]


@router.post("/einkauf/lager-konten", status_code=201)
async def create_lager_konto(
    data: LagerKontenzuordnungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    lk = LagerKontenzuordnung(id=uuid7(), tenant_id=tenant_id, **data.model_dump())
    db.add(lk)
    db.commit()
    db.refresh(lk)
    return {"id": str(lk.id), "artikelgruppe": lk.artikelgruppe,
            "bestandskonto": lk.bestandskonto}


@router.put("/einkauf/lager-konten/{konto_id}")
async def update_lager_konto(
    konto_id: str,
    data: LagerKontenzuordnungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    lk = (
        db.query(LagerKontenzuordnung)
        .filter(LagerKontenzuordnung.id == konto_id,
                LagerKontenzuordnung.tenant_id == tenant_id)
        .first()
    )
    if not lk:
        raise HTTPException(404, "Konten-Zuordnung nicht gefunden")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(lk, field, value)
    db.commit()
    return {"id": str(lk.id)}


# ─────────────────────────────────────────────────────────────────────────────
# Paletten-Konto
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/paletten-konto/{partner_id}")
async def get_paletten_saldo(
    partner_id: str,
    paletten_typ: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Gibt den aktuellen Paletten-Saldo für einen Partner zurück."""
    q = (
        db.query(PalettenKontoBuchung)
        .filter(
            PalettenKontoBuchung.tenant_id == tenant_id,
            PalettenKontoBuchung.partner_id == partner_id,
        )
        .order_by(PalettenKontoBuchung.buchungsdatum.desc())
    )
    if paletten_typ:
        q = q.filter(PalettenKontoBuchung.paletten_typ == paletten_typ)

    buchungen = q.all()
    letzter_saldo = buchungen[0].saldo_nachher if buchungen else 0

    return {
        "partner_id":    partner_id,
        "paletten_typ":  paletten_typ or "alle",
        "saldo":         letzter_saldo,
        "buchungen_anz": len(buchungen),
        "letzte_buchung": buchungen[0].buchungsdatum.isoformat() if buchungen else None,
    }


@router.post("/einkauf/paletten-konto", status_code=201)
async def create_paletten_buchung(
    data: PalettenBuchungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    # Letzten Saldo ermitteln
    last = (
        db.query(PalettenKontoBuchung)
        .filter(
            PalettenKontoBuchung.tenant_id == tenant_id,
            PalettenKontoBuchung.partner_id == data.partner_id,
            PalettenKontoBuchung.paletten_typ == data.paletten_typ,
        )
        .order_by(PalettenKontoBuchung.buchungsdatum.desc())
        .first()
    )
    saldo_vorher = last.saldo_nachher if last else 0

    # Saldo berechnen
    if data.buchungsart in ("ausgabe",):
        saldo_neu = saldo_vorher - data.menge
    elif data.buchungsart in ("ruecknahme",):
        saldo_neu = saldo_vorher + data.menge
    elif data.buchungsart == "kauf":
        saldo_neu = saldo_vorher + data.menge
    elif data.buchungsart == "verkauf":
        saldo_neu = saldo_vorher - data.menge
    else:
        saldo_neu = saldo_vorher  # differenz bleibt neutral

    buchung = PalettenKontoBuchung(
        id=uuid7(),
        tenant_id=tenant_id,
        saldo_vorher=saldo_vorher,
        saldo_nachher=saldo_neu,
        **data.model_dump(),
    )
    db.add(buchung)
    db.commit()
    return {"id": str(buchung.id), "saldo_nachher": saldo_neu}


# ─────────────────────────────────────────────────────────────────────────────
# Pfand-Konto
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/pfand-konto/{partner_id}")
async def get_pfand_saldo(
    partner_id: str,
    gebinde_typ: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Gibt Pfand-Salden je Gebinde-Typ für einen Partner zurück."""
    from sqlalchemy import func as sqlfunc
    q = (
        db.query(
            PfandKontoBuchung.gebinde_typ,
            sqlfunc.max(PfandKontoBuchung.saldo_menge).label("saldo_menge"),
            sqlfunc.max(PfandKontoBuchung.saldo_wert).label("saldo_wert"),
            sqlfunc.max(PfandKontoBuchung.buchungsdatum).label("letzte_buchung"),
        )
        .filter(
            PfandKontoBuchung.tenant_id == tenant_id,
            PfandKontoBuchung.partner_id == partner_id,
        )
        .group_by(PfandKontoBuchung.gebinde_typ)
    )
    if gebinde_typ:
        q = q.filter(PfandKontoBuchung.gebinde_typ == gebinde_typ)

    return [
        {
            "gebinde_typ":   r[0],
            "saldo_menge":   float(r[1] or 0),
            "saldo_wert":    float(r[2] or 0),
            "letzte_buchung": r[3].isoformat() if r[3] else None,
        }
        for r in q.all()
    ]


@router.post("/einkauf/pfand-konto", status_code=201)
async def create_pfand_buchung(
    data: PfandBuchungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    # Letzten Saldo ermitteln
    last = (
        db.query(PfandKontoBuchung)
        .filter(
            PfandKontoBuchung.tenant_id == tenant_id,
            PfandKontoBuchung.partner_id == data.partner_id,
            PfandKontoBuchung.gebinde_typ == data.gebinde_typ,
        )
        .order_by(PfandKontoBuchung.buchungsdatum.desc())
        .first()
    )
    saldo_menge_vorher = float(last.saldo_menge or 0) if last else 0.0
    saldo_wert_vorher  = float(last.saldo_wert  or 0) if last else 0.0

    delta = float(data.menge)
    pfandwert = float(data.pfandwert_je_einheit or 0) * delta

    if data.buchungsart in ("ausgabe",):
        saldo_menge_neu = saldo_menge_vorher - delta
        saldo_wert_neu  = saldo_wert_vorher  - pfandwert
    elif data.buchungsart in ("ruecknahme",):
        saldo_menge_neu = saldo_menge_vorher + delta
        saldo_wert_neu  = saldo_wert_vorher  + pfandwert
    else:
        saldo_menge_neu = saldo_menge_vorher
        saldo_wert_neu  = saldo_wert_vorher

    buchung = PfandKontoBuchung(
        id=uuid7(),
        tenant_id=tenant_id,
        gesamtpfandwert=pfandwert,
        saldo_menge=saldo_menge_neu,
        saldo_wert=saldo_wert_neu,
        **data.model_dump(),
    )
    db.add(buchung)
    db.commit()
    return {"id": str(buchung.id),
            "saldo_menge": saldo_menge_neu,
            "saldo_wert": saldo_wert_neu}


# ─────────────────────────────────────────────────────────────────────────────
# Fremdwaren-Einlagerung
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/einkauf/fremdwaren-einlagerung")
async def list_fremdwaren(
    eigentuemer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    warehouse_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    q = db.query(FremdwarenEinlagerung).filter(FremdwarenEinlagerung.tenant_id == tenant_id)
    if eigentuemer_id:
        q = q.filter(FremdwarenEinlagerung.eigentuemer_id == eigentuemer_id)
    if status:
        q = q.filter(FremdwarenEinlagerung.status == status)
    if warehouse_id:
        q = q.filter(FremdwarenEinlagerung.warehouse_id == warehouse_id)
    return [
        {
            "id":               str(fw.id),
            "einlagerungs_nr":  fw.einlagerungs_nr,
            "eigentuemer_id":   fw.eigentuemer_id,
            "eigentuemer_name": fw.eigentuemer_name,
            "artikel_bezeichnung": fw.artikel_bezeichnung,
            "charge":           fw.charge,
            "einlagerungstyp":  fw.einlagerungstyp,
            "menge_eingelagert": float(fw.menge_eingelagert),
            "menge_aktuell":    float(fw.menge_aktuell),
            "einheit":          fw.einheit,
            "einlagerungsdatum": fw.einlagerungsdatum.isoformat() if fw.einlagerungsdatum else None,
            "geplante_auslagerung": fw.geplante_auslagerung.isoformat() if fw.geplante_auslagerung else None,
            "gebuehr_pro_tag":  float(fw.gebuehr_pro_tag) if fw.gebuehr_pro_tag else None,
            "status":           fw.status,
        }
        for fw in q.order_by(FremdwarenEinlagerung.einlagerungsdatum.desc()).all()
    ]


@router.post("/einkauf/fremdwaren-einlagerung", status_code=201)
async def create_fremdwaren_einlagerung(
    data: FremdwarenCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    fw = FremdwarenEinlagerung(
        id=uuid7(),
        tenant_id=tenant_id,
        menge_aktuell=data.menge_eingelagert,  # initial = eingelegert
        **data.model_dump(),
    )
    db.add(fw)
    db.commit()
    db.refresh(fw)
    return {"id": str(fw.id), "einlagerungs_nr": fw.einlagerungs_nr}


@router.put("/einkauf/fremdwaren-einlagerung/{einlagerung_id}")
async def update_fremdwaren_einlagerung(
    einlagerung_id: str,
    data: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    fw = (
        db.query(FremdwarenEinlagerung)
        .filter(FremdwarenEinlagerung.id == einlagerung_id,
                FremdwarenEinlagerung.tenant_id == tenant_id)
        .first()
    )
    if not fw:
        raise HTTPException(404, "Einlagerung nicht gefunden")
    for field in ("menge_aktuell", "status", "auslagerungsdatum",
                  "geplante_auslagerung", "notiz", "lagerort"):
        if field in data:
            setattr(fw, field, data[field])
    db.commit()
    return {"id": str(fw.id), "status": fw.status}
