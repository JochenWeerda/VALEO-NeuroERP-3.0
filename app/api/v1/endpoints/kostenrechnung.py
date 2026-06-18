"""Kostenrechnung: Kostenstellen, Kostenarten, Kostenstellen-Buchungen.

Domain: domain_finance (Alembic: kostenrechnung_stammdaten_20260618)

Fachlicher Hintergrund (Referenz-ERP Domain 09 Kostenrechnung):
  Kostenstellen-Stammdaten [KST], Kostenarten [KOA], Kostenbuchungen,
  Auswertung Ist vs. Budget pro Periode und Kostenstelle.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7


router = APIRouter(prefix="/kostenrechnung", tags=["Kostenrechnung"])

GUELTIGE_ARTEN = {"KOSTENSTELLE", "KOSTENTRAEGER", "PROJEKT", "ABTEILUNG"}
GUELTIGE_BUDGET_PERIODEN = {"MONAT", "QUARTAL", "JAHR"}
GUELTIGE_KOSTENART_GRUPPEN = {"PERSONAL", "MATERIAL", "ABSCHREIBUNG", "FREMDLEISTUNG", "ENERGIE", "SONSTIGE"}


# ── Schemas ───────────────────────────────────────────────────────────────────

class KostenstelleCreate(BaseModel):
    nummer: str = Field(..., max_length=20)
    bezeichnung: str = Field(..., max_length=200)
    kostenstelle_art: str = Field(default="KOSTENSTELLE")
    uebergeordnet: Optional[str] = None
    verantwortlicher: Optional[str] = None
    budget: Optional[Decimal] = Field(None, ge=0)
    budget_periode: Optional[str] = None
    aktiv: bool = True

    def model_post_init(self, __context) -> None:
        if self.kostenstelle_art not in GUELTIGE_ARTEN:
            raise ValueError(f"kostenstelle_art muss einer von {GUELTIGE_ARTEN} sein")
        if self.budget_periode and self.budget_periode not in GUELTIGE_BUDGET_PERIODEN:
            raise ValueError(f"budget_periode muss einer von {GUELTIGE_BUDGET_PERIODEN} sein")


class KostenstelleOut(BaseModel):
    id: str
    tenant_id: str
    nummer: str
    bezeichnung: str
    kostenstelle_art: str
    uebergeordnet: Optional[str]
    verantwortlicher: Optional[str]
    budget: Optional[Decimal]
    budget_periode: Optional[str]
    aktiv: bool
    created_at: datetime
    updated_at: datetime


class KostenartCreate(BaseModel):
    nummer: str = Field(..., max_length=20)
    bezeichnung: str = Field(..., max_length=200)
    kostenart_gruppe: str = Field(default="SONSTIGE")
    konto_nr: Optional[str] = Field(None, max_length=20)
    aktiv: bool = True

    def model_post_init(self, __context) -> None:
        if self.kostenart_gruppe not in GUELTIGE_KOSTENART_GRUPPEN:
            raise ValueError(f"kostenart_gruppe muss einer von {GUELTIGE_KOSTENART_GRUPPEN} sein")


class KostenartOut(BaseModel):
    id: str
    tenant_id: str
    nummer: str
    bezeichnung: str
    kostenart_gruppe: str
    konto_nr: Optional[str]
    aktiv: bool
    created_at: datetime


class BuchungCreate(BaseModel):
    kostenstelle_id: str
    kostenart_id: Optional[str] = None
    buchungsdatum: date
    betrag_eur: Decimal = Field(..., description="Positiv = Kosten, Negativ = Erlöse/Korrekturen")
    buchungstext: Optional[str] = Field(None, max_length=255)
    belegnummer: Optional[str] = Field(None, max_length=50)


class BuchungOut(BaseModel):
    id: str
    tenant_id: str
    kostenstelle_id: str
    kostenart_id: Optional[str]
    buchungsdatum: date
    betrag_eur: Decimal
    buchungstext: Optional[str]
    belegnummer: Optional[str]
    periode: str
    erstellt_von: Optional[str]
    created_at: datetime


class KostenstelleAuswertung(BaseModel):
    kostenstelle_id: str
    nummer: str
    bezeichnung: str
    kostenstelle_art: str
    budget: Decimal
    budget_periode: Optional[str]
    verbraucht: Decimal
    offen: Decimal
    auslastung_prozent: float
    buchungen_anzahl: int


class KostenstellenReport(BaseModel):
    periode_von: date
    periode_bis: date
    gesamt_budget: Decimal
    gesamt_verbraucht: Decimal
    gesamt_offen: Decimal
    auswertungen: list[KostenstelleAuswertung]


# ── Kostenstellen CRUD ────────────────────────────────────────────────────────

@router.get("/kostenstellen", response_model=list[KostenstelleOut])
def list_kostenstellen(
    art: Optional[str] = Query(None),
    aktiv: Optional[bool] = Query(True),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    clauses = ["tenant_id = :tid"]
    params: dict = {"tid": tenant_id}
    if art:
        clauses.append("kostenstelle_art = :art")
        params["art"] = art
    if aktiv is not None:
        clauses.append("aktiv = :aktiv")
        params["aktiv"] = aktiv
    sql = f"SELECT * FROM domain_finance.kostenstellen WHERE {' AND '.join(clauses)} ORDER BY nummer"
    rows = db.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]


@router.get("/kostenstellen/{kst_id}", response_model=KostenstelleOut)
def get_kostenstelle(kst_id: str, db=Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    row = db.execute(
        text("SELECT * FROM domain_finance.kostenstellen WHERE id = :id AND tenant_id = :tid"),
        {"id": kst_id, "tid": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Kostenstelle nicht gefunden")
    return dict(row)


@router.post("/kostenstellen", response_model=KostenstelleOut, status_code=201)
def create_kostenstelle(payload: KostenstelleCreate, db=Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    # Duplikat-Check
    existing = db.execute(
        text("SELECT id FROM domain_finance.kostenstellen WHERE tenant_id = :tid AND nummer = :nr"),
        {"tid": tenant_id, "nr": payload.nummer},
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Kostenstelle {payload.nummer!r} existiert bereits")
    new_id = uuid7()
    now = datetime.now(timezone.utc)
    db.execute(
        text("""
            INSERT INTO domain_finance.kostenstellen
              (id, tenant_id, nummer, bezeichnung, kostenstelle_art, uebergeordnet,
               verantwortlicher, budget, budget_periode, aktiv, created_at, updated_at)
            VALUES
              (:id, :tid, :nummer, :bezeichnung, :art, :uebergeordnet,
               :verantwortlicher, :budget, :budget_periode, :aktiv, :now, :now)
        """),
        {
            "id": new_id,
            "tid": tenant_id,
            "nummer": payload.nummer,
            "bezeichnung": payload.bezeichnung,
            "art": payload.kostenstelle_art,
            "uebergeordnet": payload.uebergeordnet,
            "verantwortlicher": payload.verantwortlicher,
            "budget": payload.budget,
            "budget_periode": payload.budget_periode,
            "aktiv": payload.aktiv,
            "now": now,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_finance.kostenstellen WHERE id = :id"),
        {"id": new_id},
    ).mappings().first()
    return dict(row)


@router.patch("/kostenstellen/{kst_id}", response_model=KostenstelleOut)
def update_kostenstelle(
    kst_id: str,
    payload: KostenstelleCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(
        text("SELECT id FROM domain_finance.kostenstellen WHERE id = :id AND tenant_id = :tid"),
        {"id": kst_id, "tid": tenant_id},
    ).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Kostenstelle nicht gefunden")
    now = datetime.now(timezone.utc)
    db.execute(
        text("""
            UPDATE domain_finance.kostenstellen
            SET bezeichnung = :bezeichnung,
                kostenstelle_art = :art,
                uebergeordnet = :uebergeordnet,
                verantwortlicher = :verantwortlicher,
                budget = :budget,
                budget_periode = :budget_periode,
                aktiv = :aktiv,
                updated_at = :now
            WHERE id = :id AND tenant_id = :tid
        """),
        {
            "bezeichnung": payload.bezeichnung,
            "art": payload.kostenstelle_art,
            "uebergeordnet": payload.uebergeordnet,
            "verantwortlicher": payload.verantwortlicher,
            "budget": payload.budget,
            "budget_periode": payload.budget_periode,
            "aktiv": payload.aktiv,
            "now": now,
            "id": kst_id,
            "tid": tenant_id,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_finance.kostenstellen WHERE id = :id"),
        {"id": kst_id},
    ).mappings().first()
    return dict(row)


@router.delete("/kostenstellen/{kst_id}", response_class=Response, status_code=204)
def delete_kostenstelle(kst_id: str, db=Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    existing = db.execute(
        text("SELECT id FROM domain_finance.kostenstellen WHERE id = :id AND tenant_id = :tid"),
        {"id": kst_id, "tid": tenant_id},
    ).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Kostenstelle nicht gefunden")
    buchungen = db.execute(
        text("SELECT COUNT(*) FROM domain_finance.kostenstellen_buchungen WHERE kostenstelle_id = :id"),
        {"id": kst_id},
    ).scalar()
    if buchungen and buchungen > 0:
        raise HTTPException(status_code=409, detail=f"Kostenstelle hat {buchungen} Buchungen — erst Buchungen löschen")
    db.execute(
        text("DELETE FROM domain_finance.kostenstellen WHERE id = :id AND tenant_id = :tid"),
        {"id": kst_id, "tid": tenant_id},
    )
    db.commit()
    return Response(status_code=204)


# ── Kostenarten CRUD ──────────────────────────────────────────────────────────

@router.get("/kostenarten", response_model=list[KostenartOut])
def list_kostenarten(
    aktiv: Optional[bool] = Query(True),
    gruppe: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    clauses = ["tenant_id = :tid"]
    params: dict = {"tid": tenant_id}
    if aktiv is not None:
        clauses.append("aktiv = :aktiv")
        params["aktiv"] = aktiv
    if gruppe:
        clauses.append("kostenart_gruppe = :gruppe")
        params["gruppe"] = gruppe
    sql = f"SELECT * FROM domain_finance.kostenarten WHERE {' AND '.join(clauses)} ORDER BY nummer"
    return [dict(r) for r in db.execute(text(sql), params).mappings().all()]


@router.post("/kostenarten", response_model=KostenartOut, status_code=201)
def create_kostenart(payload: KostenartCreate, db=Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    existing = db.execute(
        text("SELECT id FROM domain_finance.kostenarten WHERE tenant_id = :tid AND nummer = :nr"),
        {"tid": tenant_id, "nr": payload.nummer},
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Kostenart {payload.nummer!r} existiert bereits")
    new_id = uuid7()
    now = datetime.now(timezone.utc)
    db.execute(
        text("""
            INSERT INTO domain_finance.kostenarten
              (id, tenant_id, nummer, bezeichnung, kostenart_gruppe, konto_nr, aktiv, created_at)
            VALUES (:id, :tid, :nummer, :bezeichnung, :gruppe, :konto_nr, :aktiv, :now)
        """),
        {
            "id": new_id, "tid": tenant_id, "nummer": payload.nummer,
            "bezeichnung": payload.bezeichnung, "gruppe": payload.kostenart_gruppe,
            "konto_nr": payload.konto_nr, "aktiv": payload.aktiv, "now": now,
        },
    )
    db.commit()
    row = db.execute(text("SELECT * FROM domain_finance.kostenarten WHERE id = :id"), {"id": new_id}).mappings().first()
    return dict(row)


@router.delete("/kostenarten/{koa_id}", response_class=Response, status_code=204)
def delete_kostenart(koa_id: str, db=Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    db.execute(
        text("DELETE FROM domain_finance.kostenarten WHERE id = :id AND tenant_id = :tid"),
        {"id": koa_id, "tid": tenant_id},
    )
    db.commit()
    return Response(status_code=204)


# ── Kostenbuchungen ───────────────────────────────────────────────────────────

@router.get("/buchungen", response_model=list[BuchungOut])
def list_buchungen(
    kostenstelle_id: Optional[str] = Query(None),
    periode: Optional[str] = Query(None, description="Format: YYYY-MM"),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    clauses = ["tenant_id = :tid"]
    params: dict = {"tid": tenant_id}
    if kostenstelle_id:
        clauses.append("kostenstelle_id = :kst_id")
        params["kst_id"] = kostenstelle_id
    if periode:
        clauses.append("periode = :periode")
        params["periode"] = periode
    sql = f"SELECT * FROM domain_finance.kostenstellen_buchungen WHERE {' AND '.join(clauses)} ORDER BY buchungsdatum DESC"
    return [dict(r) for r in db.execute(text(sql), params).mappings().all()]


@router.post("/buchungen", response_model=BuchungOut, status_code=201)
def create_buchung(payload: BuchungCreate, db=Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    kst = db.execute(
        text("SELECT id FROM domain_finance.kostenstellen WHERE id = :id AND tenant_id = :tid"),
        {"id": payload.kostenstelle_id, "tid": tenant_id},
    ).first()
    if not kst:
        raise HTTPException(status_code=404, detail="Kostenstelle nicht gefunden")
    new_id = uuid7()
    periode = payload.buchungsdatum.strftime("%Y-%m")
    now = datetime.now(timezone.utc)
    db.execute(
        text("""
            INSERT INTO domain_finance.kostenstellen_buchungen
              (id, tenant_id, kostenstelle_id, kostenart_id, buchungsdatum, betrag_eur,
               buchungstext, belegnummer, periode, created_at)
            VALUES (:id, :tid, :kst_id, :koa_id, :datum, :betrag, :text, :beleg, :periode, :now)
        """),
        {
            "id": new_id, "tid": tenant_id, "kst_id": payload.kostenstelle_id,
            "koa_id": payload.kostenart_id, "datum": payload.buchungsdatum,
            "betrag": payload.betrag_eur, "text": payload.buchungstext,
            "beleg": payload.belegnummer, "periode": periode, "now": now,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_finance.kostenstellen_buchungen WHERE id = :id"),
        {"id": new_id},
    ).mappings().first()
    return dict(row)


@router.delete("/buchungen/{buchung_id}", response_class=Response, status_code=204)
def delete_buchung(buchung_id: str, db=Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    db.execute(
        text("DELETE FROM domain_finance.kostenstellen_buchungen WHERE id = :id AND tenant_id = :tid"),
        {"id": buchung_id, "tid": tenant_id},
    )
    db.commit()
    return Response(status_code=204)


# ── Auswertung ────────────────────────────────────────────────────────────────

@router.get("/report", response_model=KostenstellenReport)
def get_report(
    von: date = Query(..., description="Periode von (YYYY-MM-DD)"),
    bis: date = Query(..., description="Periode bis (YYYY-MM-DD)"),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Kostenstellen-Auswertung: Budget vs. Ist-Kosten für den gewählten Zeitraum."""
    kostenstellen = db.execute(
        text("SELECT * FROM domain_finance.kostenstellen WHERE tenant_id = :tid AND aktiv = true ORDER BY nummer"),
        {"tid": tenant_id},
    ).mappings().all()

    # Aggregiere Buchungen pro Kostenstelle im Zeitraum
    buchungen = db.execute(
        text("""
            SELECT kostenstelle_id, SUM(betrag_eur) AS summe, COUNT(*) AS anzahl
            FROM domain_finance.kostenstellen_buchungen
            WHERE tenant_id = :tid AND buchungsdatum BETWEEN :von AND :bis
            GROUP BY kostenstelle_id
        """),
        {"tid": tenant_id, "von": von, "bis": bis},
    ).mappings().all()

    verbrauch_map = {r["kostenstelle_id"]: (Decimal(str(r["summe"])), int(r["anzahl"])) for r in buchungen}

    auswertungen = []
    gesamt_budget = Decimal("0")
    gesamt_verbraucht = Decimal("0")

    for k in kostenstellen:
        budget = Decimal(str(k["budget"] or 0))
        verbraucht, anzahl = verbrauch_map.get(k["id"], (Decimal("0"), 0))
        offen = budget - verbraucht
        auslastung = float(verbraucht / budget * 100) if budget > 0 else 0.0
        gesamt_budget += budget
        gesamt_verbraucht += verbraucht
        auswertungen.append(KostenstelleAuswertung(
            kostenstelle_id=k["id"],
            nummer=k["nummer"],
            bezeichnung=k["bezeichnung"],
            kostenstelle_art=k["kostenstelle_art"],
            budget=budget,
            budget_periode=k["budget_periode"],
            verbraucht=verbraucht,
            offen=offen,
            auslastung_prozent=round(auslastung, 1),
            buchungen_anzahl=anzahl,
        ))

    return KostenstellenReport(
        periode_von=von,
        periode_bis=bis,
        gesamt_budget=gesamt_budget,
        gesamt_verbraucht=gesamt_verbraucht,
        gesamt_offen=gesamt_budget - gesamt_verbraucht,
        auswertungen=auswertungen,
    )


# ── KORE-BAB-001: Betriebsabrechnungsbogen + Kostenumlagen ───────────────────

class UmlageCreate(BaseModel):
    von_kostenstelle_id: str
    nach_kostenstelle_id: str
    umlage_art: str = Field(..., pattern="^(PROZENT|BETRAG|MENGE)$")
    umlage_wert: Decimal = Field(..., gt=0)
    umlage_basis: Optional[str] = None


class UmlageOut(BaseModel):
    id: str
    periode: str
    von_kostenstelle_id: str
    nach_kostenstelle_id: str
    umlage_art: str
    umlage_wert: Decimal
    umlage_basis: Optional[str]
    umlagebetrag_eur: Optional[Decimal]


class BABZeile(BaseModel):
    kostenstelle_id: str
    nummer: str
    bezeichnung: str
    primaerkosten_eur: Decimal          # direkte Buchungen
    umlage_eingang_eur: Decimal         # empfangene Umlagen
    umlage_ausgang_eur: Decimal         # weitergegebene Umlagen
    gesamtkosten_eur: Decimal           # primär + eingang - ausgang
    budget_eur: Decimal
    abweichung_eur: Decimal             # budget - gesamt
    abweichung_pct: float


class BABReport(BaseModel):
    periode: str
    zeilen: list[BABZeile]
    gesamt_primaer_eur: Decimal
    gesamt_umlage_eur: Decimal
    gesamt_kosten_eur: Decimal


@router.post("/umlagen", summary="Kostenumlage anlegen für Periode")
def create_umlage(
    periode: str = Query(..., example="2026-06"),
    payload: UmlageCreate = ...,
    tenant_id: str = Depends(get_tenant_id),
    db=Depends(get_db),
):
    """Legt eine Kostenumlage von einer Kostenstelle zu einer anderen für eine Periode an."""
    # Bestimme Umlagebetrag je nach Art
    if payload.umlage_art == "BETRAG":
        umlagebetrag = payload.umlage_wert
    elif payload.umlage_art == "PROZENT":
        # Primärkosten der Quell-KST berechnen
        period_start = f"{periode}-01"
        period_end = f"{periode}-31"
        row = db.execute(
            text("""
                SELECT COALESCE(SUM(betrag_eur), 0) AS summe
                FROM domain_finance.kostenstellen_buchungen
                WHERE tenant_id = :tid AND kostenstelle_id = :kst
                  AND buchungsdatum BETWEEN :von AND :bis
            """),
            {"tid": tenant_id, "kst": payload.von_kostenstelle_id,
             "von": period_start, "bis": period_end},
        ).fetchone()
        umlagebetrag = Decimal(str(row[0])) * payload.umlage_wert / Decimal("100")
    else:  # MENGE — Wert ist Kostensatz × Menge; Menge = umlage_wert
        umlagebetrag = payload.umlage_wert  # caller liefert Betrag direkt

    uid = str(uuid7())
    try:
        db.execute(
            text("""
                INSERT INTO domain_finance.kostenstellen_umlagen
                    (id, tenant_id, periode, von_kostenstelle_id, nach_kostenstelle_id,
                     umlage_art, umlage_wert, umlage_basis, umlagebetrag_eur)
                VALUES (:id, :tid, :per, :von, :nach, :art, :wert, :basis, :betrag)
            """),
            {
                "id": uid, "tid": tenant_id, "per": periode,
                "von": payload.von_kostenstelle_id,
                "nach": payload.nach_kostenstelle_id,
                "art": payload.umlage_art, "wert": float(payload.umlage_wert),
                "basis": payload.umlage_basis, "betrag": float(umlagebetrag),
            },
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        if "uq_kostenstellen_umlage" in str(exc):
            raise HTTPException(409, "Umlage für diesen KST-Schlüssel und Periode bereits vorhanden")
        raise HTTPException(500, str(exc))

    return {"id": uid, "umlagebetrag_eur": float(umlagebetrag), "ok": True}


@router.get("/bab", summary="Betriebsabrechnungsbogen (BAB) für eine Periode")
def get_bab(
    periode: str = Query(..., example="2026-06"),
    tenant_id: str = Depends(get_tenant_id),
    db=Depends(get_db),
) -> BABReport:
    """Berechnet den BAB für eine Periode.

    Logik:
      Primärkosten = Summe Kostenstellen-Buchungen im Monat der Periode
      Umlage-Eingang = Summe umlagebetrag_eur wo diese KST = nach_kostenstelle_id
      Umlage-Ausgang = Summe umlagebetrag_eur wo diese KST = von_kostenstelle_id
      Gesamtkosten = Primär + Eingang - Ausgang
    """
    period_start = f"{periode}-01"
    period_end = f"{periode}-31"

    kostenstellen = db.execute(
        text("""
            SELECT id, nummer, bezeichnung, budget, budget_periode
            FROM domain_finance.kostenstellen
            WHERE tenant_id = :tid AND aktiv = true
            ORDER BY nummer
        """),
        {"tid": tenant_id},
    ).mappings().all()

    # Primärkosten
    pk_rows = db.execute(
        text("""
            SELECT kostenstelle_id, SUM(betrag_eur) AS summe
            FROM domain_finance.kostenstellen_buchungen
            WHERE tenant_id = :tid AND buchungsdatum BETWEEN :von AND :bis
            GROUP BY kostenstelle_id
        """),
        {"tid": tenant_id, "von": period_start, "bis": period_end},
    ).mappings().all()
    pk_map = {r["kostenstelle_id"]: Decimal(str(r["summe"])) for r in pk_rows}

    # Umlagen
    umlage_rows = db.execute(
        text("""
            SELECT von_kostenstelle_id, nach_kostenstelle_id, COALESCE(umlagebetrag_eur, 0) AS betrag
            FROM domain_finance.kostenstellen_umlagen
            WHERE tenant_id = :tid AND periode = :per
        """),
        {"tid": tenant_id, "per": periode},
    ).mappings().all()

    umlage_ein: dict[str, Decimal] = {}
    umlage_aus: dict[str, Decimal] = {}
    for u in umlage_rows:
        betrag = Decimal(str(u["betrag"]))
        umlage_ein[u["nach_kostenstelle_id"]] = umlage_ein.get(u["nach_kostenstelle_id"], Decimal("0")) + betrag
        umlage_aus[u["von_kostenstelle_id"]] = umlage_aus.get(u["von_kostenstelle_id"], Decimal("0")) + betrag

    zeilen: list[BABZeile] = []
    gesamt_prim = Decimal("0")
    gesamt_uml = Decimal("0")
    gesamt_ges = Decimal("0")

    for k in kostenstellen:
        kid = str(k["id"])
        prim = pk_map.get(kid, Decimal("0"))
        ein = umlage_ein.get(kid, Decimal("0"))
        aus = umlage_aus.get(kid, Decimal("0"))
        ges = prim + ein - aus
        budget = Decimal(str(k["budget"] or 0))
        abw = budget - ges
        abw_pct = float(abw / budget * 100) if budget > 0 else 0.0

        gesamt_prim += prim
        gesamt_uml += ein
        gesamt_ges += ges

        zeilen.append(BABZeile(
            kostenstelle_id=kid,
            nummer=str(k["nummer"]),
            bezeichnung=str(k["bezeichnung"]),
            primaerkosten_eur=prim,
            umlage_eingang_eur=ein,
            umlage_ausgang_eur=aus,
            gesamtkosten_eur=ges,
            budget_eur=budget,
            abweichung_eur=abw,
            abweichung_pct=round(abw_pct, 1),
        ))

    return BABReport(
        periode=periode,
        zeilen=zeilen,
        gesamt_primaer_eur=gesamt_prim,
        gesamt_umlage_eur=gesamt_uml,
        gesamt_kosten_eur=gesamt_ges,
    )
