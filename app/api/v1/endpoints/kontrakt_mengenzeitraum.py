"""Kontraktmengenzeitraum — Ratierliche Lieferpläne für Rohwarenkontrakte.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 01):
  Im Kontraktstamm können Mengenzeiträume hinterlegt werden, die festlegen,
  in welchem Monat/Quartal wie viel Rohware geliefert werden soll.
  Standardvariante 'Monatlich linear': die Kontraktmenge wird gleichmäßig
  auf die Monate verteilt. Andere Varianten erlauben individuelle Verteilung.

  Zudem werden individuelle Zu-/Abschläge auf Kontraktebene verwaltet
  (SPA 1160). Pro Kontrakt kann eine Zu-/Abschlagsgruppe hinterlegt werden,
  die beim Erzeugen von Vorgängen gezogen wird.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.kontrakt_mengenzeitraum_schemas import KontraktMengenzeitraumOut


router = APIRouter(prefix="/kontrakte", tags=["Kontrakt - Mengenzeitraum & Zu-/Abschläge"])


# ── Schemas Mengenzeitraum ────────────────────────────────────────────────────

# ── Schemas Zu-/Abschläge ─────────────────────────────────────────────────────

# ── Mengenzeitraum Endpoints ──────────────────────────────────────────────────

@router.get("/{kontrakt_nr}/mengenzeitraeume", response_model=list[MengenzeitraumOut], summary="Mengenzeitraeume auflisten")
def list_mengenzeitraeume(
    kontrakt_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Alle Mengenzeiträume eines Kontrakts."""
    rows = db.execute(text("""
        SELECT * FROM domain_shared.kontrakt_mengenzeitraeume
        WHERE tenant_id = :tid AND kontrakt_nr = :ktr_nr
        ORDER BY zeitraum_von
    """), {"tid": tenant_id, "ktr_nr": kontrakt_nr}).fetchall()
    return [MengenzeitraumOut(**dict(r._mapping)) for r in rows]


@router.post("/{kontrakt_nr}/mengenzeitraeume",
             response_model=MengenzeitraumOut, status_code=201, summary="Mengenzeitraum anlegen")
def create_mengenzeitraum(
    kontrakt_nr: str,
    payload: MengenzeitraumCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Mengenzeitraum anlegen."""
    if payload.zeitraum_bis < payload.zeitraum_von:
        raise HTTPException(422, "zeitraum_bis muss nach zeitraum_von liegen.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.kontrakt_mengenzeitraeume
            (id, tenant_id, kontrakt_nr, zeitraum_von, zeitraum_bis,
             menge_t, menge_bereits_geliefert_t, menge_restmenge_t,
             variante, status, bemerkung)
        VALUES (:id, :tid, :ktr_nr, :von, :bis,
                :menge, 0, :menge, :variante, 'offen', :bem)
    """), {
        "id": new_id, "tid": tenant_id, "ktr_nr": kontrakt_nr,
        "von": payload.zeitraum_von, "bis": payload.zeitraum_bis,
        "menge": payload.menge_t, "variante": payload.variante,
        "bem": payload.bemerkung,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.kontrakt_mengenzeitraeume WHERE id = :id
    """), {"id": new_id}).fetchone()
    return MengenzeitraumOut(**dict(row._mapping))


@router.patch("/{kontrakt_nr}/mengenzeitraeume/{zeitraum_id}",
              response_model=MengenzeitraumOut, summary="Mengenzeitraum aktualisieren")
def update_mengenzeitraum(
    kontrakt_nr: str,
    zeitraum_id: str,
    payload: MengenzeitraumUpdate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Mengenzeitraum aktualisieren (z.B. Lieferbuchung)."""
    row = db.execute(text("""
        SELECT * FROM domain_shared.kontrakt_mengenzeitraeume
        WHERE id = :id AND tenant_id = :tid AND kontrakt_nr = :ktr_nr
    """), {"id": zeitraum_id, "tid": tenant_id, "ktr_nr": kontrakt_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Mengenzeitraum nicht gefunden.")

    updates = []
    params: dict = {"id": zeitraum_id}
    if payload.menge_t is not None:
        updates.append("menge_t = :menge_t")
        params["menge_t"] = payload.menge_t
    if payload.menge_bereits_geliefert_t is not None:
        updates.append("menge_bereits_geliefert_t = :geliefert")
        updates.append("menge_restmenge_t = menge_t - :geliefert")
        params["geliefert"] = payload.menge_bereits_geliefert_t
    if payload.status:
        updates.append("status = :status")
        params["status"] = payload.status
    if payload.bemerkung is not None:
        updates.append("bemerkung = :bem")
        params["bem"] = payload.bemerkung

    if updates:
        updates.append("updated_at = now()")
        # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        db.execute(text(f"""
            UPDATE domain_shared.kontrakt_mengenzeitraeume
            SET {', '.join(updates)} WHERE id = :id
        """), params)
        db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.kontrakt_mengenzeitraeume WHERE id = :id
    """), {"id": zeitraum_id}).fetchone()
    return MengenzeitraumOut(**dict(row._mapping))


@router.delete("/{kontrakt_nr}/mengenzeitraeume/{zeitraum_id}", summary="Mengenzeitraum löschen",
    response_model=None
)
def delete_mengenzeitraum(
    kontrakt_nr: str,
    zeitraum_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT status FROM domain_shared.kontrakt_mengenzeitraeume
        WHERE id = :id AND tenant_id = :tid
    """), {"id": zeitraum_id, "tid": tenant_id}).fetchone()
    if not row:
        raise HTTPException(404)
    if row.status == "erfuellt":
        raise HTTPException(409, "Erfüllte Mengenzeiträume können nicht gelöscht werden.")
    db.execute(text("""
        DELETE FROM domain_shared.kontrakt_mengenzeitraeume WHERE id = :id
    """), {"id": zeitraum_id})
    db.commit()
    return Response(status_code=204)


@router.post("/{kontrakt_nr}/mengenzeitraeume/generieren", summary="Mengenzeitraeume generiere",
    response_model=None
)
def generiere_mengenzeitraeume(
    kontrakt_nr: str,
    von_datum: date,
    bis_datum: date,
    gesamt_menge_t: Decimal,
    variante: str = "monatl. lin. Abnahme",
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Mengenzeiträume automatisch generieren (z.B. monatlich linear).

    Fachlich: Bei der Variante 'monatlich linear' wird die Gesamtmenge
    gleichmäßig auf die Monate des Kontraktzeitraums verteilt.
    """
    from calendar import monthrange
    from datetime import timedelta

    # Monate berechnen
    monate = []
    current = von_datum.replace(day=1)
    end_month = bis_datum.replace(day=1)
    while current <= end_month:
        days_in_month = monthrange(current.year, current.month)[1]
        m_start = current
        m_end = current.replace(day=days_in_month)
        if m_start < von_datum:
            m_start = von_datum
        if m_end > bis_datum:
            m_end = bis_datum
        monate.append((m_start, m_end))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    if not monate:
        raise HTTPException(422, "Kein gültiger Zeitraum.")

    menge_pro_monat = (gesamt_menge_t / len(monate)).quantize(Decimal("0.001"))
    created_ids = []
    for m_start, m_end in monate:
        new_id = uuid7()
        db.execute(text("""
            INSERT INTO domain_shared.kontrakt_mengenzeitraeume
                (id, tenant_id, kontrakt_nr, zeitraum_von, zeitraum_bis,
                 menge_t, menge_bereits_geliefert_t, menge_restmenge_t,
                 variante, status)
            VALUES (:id, :tid, :ktr_nr, :von, :bis,
                    :menge, 0, :menge, :variante, 'offen')
        """), {
            "id": new_id, "tid": tenant_id, "ktr_nr": kontrakt_nr,
            "von": m_start, "bis": m_end, "menge": menge_pro_monat,
            "variante": variante,
        })
        created_ids.append(new_id)
    db.commit()
    return {
        "kontrakt_nr": kontrakt_nr,
        "variante": variante,
        "anzahl_zeitraeume": len(created_ids),
        "menge_pro_monat_t": float(menge_pro_monat),
        "gesamt_menge_t": float(gesamt_menge_t),
        "zeitraum_ids": created_ids,
    }


# ── Zu-/Abschläge Endpoints ──────────────────────────────────────────────────

@router.get("/zuabschlagsgruppen", summary="Zuabschlagsgruppen auflisten",
    response_model=list[KontraktMengenzeitraumOut]
)
def list_zuabschlagsgruppen(
    typ: Optional[str] = Query(None, description="zuschlag oder abschlag"),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.kontrakt_zuabschlagsgruppen
        WHERE tenant_id = :tid AND aktiv = true
    """
    params: dict = {"tid": tenant_id}
    if typ:
        sql += " AND typ = :typ"
        params["typ"] = typ
    sql += " ORDER BY gruppe_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [dict(r._mapping) for r in rows]


@router.post("/zuabschlagsgruppen", status_code=201, summary="Zuabschlagsgruppe anlegen",
    response_model=KontraktMengenzeitraumOut
)
def create_zuabschlagsgruppe(
    payload: ZuAbschlagsGruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if payload.typ not in ("zuschlag", "abschlag"):
        raise HTTPException(422, "typ muss 'zuschlag' oder 'abschlag' sein.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.kontrakt_zuabschlagsgruppen
            (id, tenant_id, gruppe_nr, bezeichnung, typ, aktiv)
        VALUES (:id, :tid, :nr, :bez, :typ, true)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr,
        "bez": payload.bezeichnung, "typ": payload.typ,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.kontrakt_zuabschlagsgruppen WHERE id = :id
    """), {"id": new_id}).fetchone()
    return dict(row._mapping)


@router.get("/zuabschlagsgruppen/{gruppe_id}/positionen",
            response_model=list[ZuAbschlagOut], summary="Zuabschlaege auflisten")
def list_zuabschlaege(
    gruppe_id: str,
    kontrakt_nr: Optional[str] = Query(None),
    stichtag: Optional[date] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Zu-/Abschläge einer Gruppe, optional gefiltert nach Kontrakt und Stichtag."""
    check_date = stichtag or date.today()
    sql = """
        SELECT * FROM domain_shared.kontrakt_zuabschlaege
        WHERE gruppe_id = :gruppe_id AND aktiv = true AND tenant_id = :tid
          AND (gueltig_ab IS NULL OR gueltig_ab <= :stichtag)
          AND (gueltig_bis IS NULL OR gueltig_bis >= :stichtag)
    """
    params: dict = {"gruppe_id": gruppe_id, "tid": tenant_id, "stichtag": check_date}
    if kontrakt_nr:
        sql += " AND (kontrakt_nr = :ktr_nr OR kontrakt_nr IS NULL)"
        params["ktr_nr"] = kontrakt_nr
    sql += " ORDER BY bezeichnung"
    rows = db.execute(text(sql), params).fetchall()
    return [ZuAbschlagOut(**dict(r._mapping)) for r in rows]


@router.post("/zuabschlagsgruppen/{gruppe_id}/positionen",
             response_model=ZuAbschlagOut, status_code=201, summary="Zuabschlag anlegen")
def create_zuabschlag(
    gruppe_id: str,
    payload: ZuAbschlagCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if not payload.betrag_eur and not payload.prozent:
        raise HTTPException(422, "Entweder betrag_eur oder prozent muss angegeben werden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.kontrakt_zuabschlaege
            (id, tenant_id, gruppe_id, kontrakt_nr, bezeichnung,
             betrag_eur, prozent, einheit, gueltig_ab, gueltig_bis, aktiv)
        VALUES (:id, :tid, :gruppe_id, :ktr_nr, :bez,
                :betrag, :proz, :einheit, :von, :bis, true)
    """), {
        "id": new_id, "tid": tenant_id, "gruppe_id": gruppe_id,
        "ktr_nr": payload.kontrakt_nr, "bez": payload.bezeichnung,
        "betrag": payload.betrag_eur, "proz": payload.prozent,
        "einheit": payload.einheit, "von": payload.gueltig_ab, "bis": payload.gueltig_bis,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.kontrakt_zuabschlaege WHERE id = :id
    """), {"id": new_id}).fetchone()
    return ZuAbschlagOut(**dict(row._mapping))
