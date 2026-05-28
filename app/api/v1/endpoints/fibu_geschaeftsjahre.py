"""Geschäftsjahre, FiBu-Perioden und Periodische Buchungen.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 03 FIBU):
  Geschäftsjahre [JAHR]: Definieren das Wirtschaftsjahr mit Beginn/Ende,
  Datumsgrenzen für Buchungen, Warndatumsbereich und Perioden (12 Ware + 12 FiBu
  plus Eröffnung/Abschluss). Journal-Nummernkreis je Geschäftsjahr.

  Perioden: 1–12 = Normalperioden, 0 = Eröffnungsperiode, 13 = Abschlussperiode.
  Gesperrte Perioden akzeptieren keine weiteren Buchungen.

  Periodische Buchungen [FIWIEBU]: Wiederkehrende FIBU-Buchungen (Miete, Versicherung,
  Abschreibung etc.) mit Intervall (monatlich/quartalsweise/halbjaehrlich/jaehrlich).
  Parameter "alle Belege erzeugen" ermöglicht, alle ausstehenden Buchungen bis zum
  Abgrenzungsdatum in einem Lauf zu erstellen.
"""
import calendar
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut
from app.api.v1.schemas.fibu_geschaeftsjahre_schemas import FibuGeschaeftsjahreOut


router = APIRouter(prefix="/fibu/geschaeftsjahre",
                   tags=["FIBU - Geschäftsjahre & Periodische Buchungen"])

INTERVALLE = ("monatlich", "quartalsweise", "halbjaehrlich", "jaehrlich")


# ── Schemas ───────────────────────────────────────────────────────────────────

class GeschaeftsjahreCreate(BaseModel):
    jahr_nr: int = Field(..., ge=1990, le=2100)
    bezeichnung: str
    datum_beginn: date
    datum_ende: date
    kleinstes_datum: Optional[date] = None
    groesstes_datum: Optional[date] = None
    warndatum_von: Optional[date] = None
    warndatum_bis: Optional[date] = None
    anzahl_perioden_ware: int = Field(default=12, ge=1, le=14)
    anzahl_perioden_fibu: int = Field(default=12, ge=1, le=14)
    journal_nummernkreis: Optional[str] = None

    @model_validator(mode="after")
    def validate_datum(self) -> "GeschaeftsjahreCreate":
        if self.datum_ende <= self.datum_beginn:
            raise ValueError("datum_ende muss nach datum_beginn liegen.")
        return self


class GeschaeftsjahreOut(BaseModel):
    id: str
    jahr_nr: int
    bezeichnung: str
    datum_beginn: date
    datum_ende: date
    kleinstes_datum: Optional[date]
    groesstes_datum: Optional[date]
    warndatum_von: Optional[date]
    warndatum_bis: Optional[date]
    anzahl_perioden_ware: int
    anzahl_perioden_fibu: int
    journal_nummernkreis: Optional[str]
    status: str
    created_at: datetime


class FibuPeriodeOut(BaseModel):
    id: str
    jahr_nr: int
    periode_nr: int
    bezeichnung: Optional[str]
    datum_von: date
    datum_bis: date
    typ: str
    gesperrt: bool
    created_at: datetime


class PeriodischeBuchungCreate(BaseModel):
    bezeichnung: str
    soll_konto: str = Field(..., max_length=20)
    haben_konto: str = Field(..., max_length=20)
    betrag_eur: Decimal = Field(..., gt=0)
    buchungstext: Optional[str] = None
    intervall: str = Field(..., description="monatlich, quartalsweise, halbjaehrlich, jaehrlich")
    naechste_buchung: Optional[date] = None
    buchung_bis: Optional[date] = None
    alle_belege_erzeugen: bool = False

    def model_post_init(self, __context):
        if self.intervall not in INTERVALLE:
            raise ValueError(f"intervall muss eines von {INTERVALLE} sein.")


class PeriodischeBuchungOut(BaseModel):
    id: str
    bezeichnung: str
    soll_konto: str
    haben_konto: str
    betrag_eur: Decimal
    buchungstext: Optional[str]
    intervall: str
    naechste_buchung: Optional[date]
    buchung_bis: Optional[date]
    alle_belege_erzeugen: bool
    anzahl_erzeugte_belege: int
    letzter_beleg_datum: Optional[date]
    aktiv: bool
    created_at: datetime


# ── Geschäftsjahre ────────────────────────────────────────────────────────────

@router.get("", response_model=list[GeschaeftsjahreOut], summary="Geschaeftsjahre auflisten")
def list_geschaeftsjahre(
    status: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.fibu_geschaeftsjahre WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if status:
        sql += " AND status = :status"
        params["status"] = status
    sql += " ORDER BY jahr_nr DESC"
    rows = db.execute(text(sql), params).fetchall()
    return [GeschaeftsjahreOut(**dict(r._mapping)) for r in rows]


@router.post("", response_model=GeschaeftsjahreOut, status_code=201, summary="Geschaeftsjahr anlegen")
def create_geschaeftsjahr(
    payload: GeschaeftsjahreCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.fibu_geschaeftsjahre
        WHERE tenant_id = :tid AND jahr_nr = :jr
    """), {"tid": tenant_id, "jr": payload.jahr_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Geschäftsjahr {payload.jahr_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.fibu_geschaeftsjahre
            (id, tenant_id, jahr_nr, bezeichnung, datum_beginn, datum_ende,
             kleinstes_datum, groesstes_datum, warndatum_von, warndatum_bis,
             anzahl_perioden_ware, anzahl_perioden_fibu,
             journal_nummernkreis, status)
        VALUES (:id, :tid, :jr, :bez, :dbeg, :dend, :kdatum, :gdatum,
                :wvon, :wbis, :pware, :pfibu, :jnk, 'offen')
    """), {
        "id": new_id, "tid": tenant_id, "jr": payload.jahr_nr,
        "bez": payload.bezeichnung, "dbeg": payload.datum_beginn,
        "dend": payload.datum_ende, "kdatum": payload.kleinstes_datum,
        "gdatum": payload.groesstes_datum, "wvon": payload.warndatum_von,
        "wbis": payload.warndatum_bis, "pware": payload.anzahl_perioden_ware,
        "pfibu": payload.anzahl_perioden_fibu,
        "jnk": payload.journal_nummernkreis,
    })
    # Automatisch 12 Monatsperioden anlegen
    for monat in range(1, payload.anzahl_perioden_ware + 1):
        _, letzter_tag = calendar.monthrange(payload.jahr_nr, monat)
        p_id = uuid7()
        db.execute(text("""
            INSERT INTO domain_shared.fibu_perioden
                (id, tenant_id, jahr_nr, periode_nr, bezeichnung,
                 datum_von, datum_bis, typ, gesperrt)
            VALUES (:id, :tid, :jr, :pnr, :bez, :von, :bis, 'normal', false)
        """), {
            "id": p_id, "tid": tenant_id, "jr": payload.jahr_nr,
            "pnr": monat,
            "bez": f"{payload.jahr_nr}/{monat:02d}",
            "von": date(payload.jahr_nr, monat, 1),
            "bis": date(payload.jahr_nr, monat, letzter_tag),
        })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.fibu_geschaeftsjahre WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return GeschaeftsjahreOut(**dict(row._mapping))


@router.get("/{jahr_nr}/perioden", response_model=list[FibuPeriodeOut], summary="Perioden auflisten")
def list_perioden(
    jahr_nr: int,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.fibu_perioden
        WHERE tenant_id = :tid AND jahr_nr = :jr
        ORDER BY periode_nr
    """), {"tid": tenant_id, "jr": jahr_nr}).fetchall()
    return [FibuPeriodeOut(**dict(r._mapping)) for r in rows]


@router.patch("/{jahr_nr}/perioden/{periode_nr}/sperren", summary="Sperren periode",
    response_model=FibuGeschaeftsjahreOut
)
def periode_sperren(
    jahr_nr: int,
    periode_nr: int,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Fibu-Periode sperren — keine weiteren Buchungen möglich."""
    db.execute(text("""
        UPDATE domain_shared.fibu_perioden
        SET gesperrt = true
        WHERE tenant_id = :tid AND jahr_nr = :jr AND periode_nr = :pnr
    """), {"tid": tenant_id, "jr": jahr_nr, "pnr": periode_nr})
    db.commit()
    return {"jahr_nr": jahr_nr, "periode_nr": periode_nr, "gesperrt": True}


# ── Periodische Buchungen ─────────────────────────────────────────────────────

@router.get("/periodisch", response_model=list[PeriodischeBuchungOut], summary="Periodische buchungen auflisten")
def list_periodische_buchungen(
    nur_aktive: bool = Query(True),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.fibu_periodische_buchungen WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if nur_aktive:
        sql += " AND aktiv = true"
    sql += " ORDER BY bezeichnung"
    rows = db.execute(text(sql), params).fetchall()
    return [PeriodischeBuchungOut(**dict(r._mapping)) for r in rows]


@router.post("/periodisch", response_model=PeriodischeBuchungOut, status_code=201, summary="Periodische buchung anlegen")
def create_periodische_buchung(
    payload: PeriodischeBuchungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.fibu_periodische_buchungen
            (id, tenant_id, bezeichnung, soll_konto, haben_konto, betrag_eur,
             buchungstext, intervall, naechste_buchung, buchung_bis,
             alle_belege_erzeugen, anzahl_erzeugte_belege, aktiv)
        VALUES (:id, :tid, :bez, :sk, :hk, :betrag, :btext, :iv,
                :nbuch, :bbis, :alle, 0, true)
    """), {
        "id": new_id, "tid": tenant_id, "bez": payload.bezeichnung,
        "sk": payload.soll_konto, "hk": payload.haben_konto,
        "betrag": payload.betrag_eur, "btext": payload.buchungstext,
        "iv": payload.intervall, "nbuch": payload.naechste_buchung,
        "bbis": payload.buchung_bis, "alle": payload.alle_belege_erzeugen,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.fibu_periodische_buchungen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return PeriodischeBuchungOut(**dict(row._mapping))


@router.post("/periodisch/{buchung_id}/ausfuehren", summary="Buchung ausfuehren periodische",
    response_model=FibuGeschaeftsjahreOut
)
def periodische_buchung_ausfuehren(
    buchung_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Periodische Buchung ausführen — erzeugt Buchungsbeleg(e) bis heute/Abgrenzungsdatum.

    Bei alle_belege_erzeugen=True werden alle ausstehenden Perioden auf einmal erzeugt.
    """
    row = db.execute(text("""
        SELECT * FROM domain_shared.fibu_periodische_buchungen
        WHERE id = :id AND tenant_id = :tid AND aktiv = true
    """), {"id": buchung_id, "tid": tenant_id}).fetchone()
    if not row:
        raise HTTPException(404, "Periodische Buchung nicht gefunden oder inaktiv.")

    b = dict(row._mapping)
    heute = date.today()
    abgrenzung = b.get("buchung_bis") or heute
    naechste = b.get("naechste_buchung") or heute

    if naechste > min(heute, abgrenzung):
        return {"erzeugte_belege": 0, "hinweis": "Keine ausstehenden Buchungen."}

    # Berechne wie viele Buchungen ausgeführt werden
    erzeugte = 0
    current_datum = naechste
    belege_daten = []

    while current_datum <= min(heute, abgrenzung):
        belege_daten.append(current_datum)
        erzeugte += 1
        # Nächstes Buchungsdatum berechnen
        if b["intervall"] == "monatlich":
            monat = current_datum.month + 1
            jahr = current_datum.year + (monat - 1) // 12
            monat = ((monat - 1) % 12) + 1
            current_datum = current_datum.replace(year=jahr, month=monat)
        elif b["intervall"] == "quartalsweise":
            monat = current_datum.month + 3
            jahr = current_datum.year + (monat - 1) // 12
            monat = ((monat - 1) % 12) + 1
            current_datum = current_datum.replace(year=jahr, month=monat)
        elif b["intervall"] == "halbjaehrlich":
            monat = current_datum.month + 6
            jahr = current_datum.year + (monat - 1) // 12
            monat = ((monat - 1) % 12) + 1
            current_datum = current_datum.replace(year=jahr, month=monat)
        else:  # jaehrlich
            current_datum = current_datum.replace(year=current_datum.year + 1)

        if not b.get("alle_belege_erzeugen"):
            break  # Nur einen Beleg auf einmal

    db.execute(text("""
        UPDATE domain_shared.fibu_periodische_buchungen
        SET anzahl_erzeugte_belege = anzahl_erzeugte_belege + :anz,
            letzter_beleg_datum = :letzter,
            naechste_buchung = :naechste
        WHERE id = :id
    """), {
        "id": buchung_id,
        "anz": erzeugte,
        "letzter": belege_daten[-1] if belege_daten else None,
        "naechste": current_datum,
    })
    db.commit()
    return {
        "erzeugte_belege": erzeugte,
        "buchungsdaten": [str(d) for d in belege_daten],
        "naechste_buchung": str(current_datum),
        "betrag_eur": float(b["betrag_eur"]),
        "soll_konto": b["soll_konto"],
        "haben_konto": b["haben_konto"],
    }


@router.delete("/periodisch/{buchung_id}", summary="Periodische buchung löschen",
    response_model=None
)
def delete_periodische_buchung(
    buchung_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.fibu_periodische_buchungen SET aktiv = false
        WHERE id = :id AND tenant_id = :tid
    """), {"id": buchung_id, "tid": tenant_id})
    db.commit()
    return Response(status_code=204)
