"""EUDR-Sorgfaltserklaerungen — das Register.

Verordnung (EU) 2023/1115. Die Erklaerung entsteht als **Entwurf**, bekommt eine
**Risikobewertung** (Art. 10/11) und wird erst dann **eingereicht** (Art. 33),
wenn hoechstens ein vernachlaessigbares Risiko festgestellt, beide Nachweise
vorliegen und die Erklaerung unterzeichnet ist (Art. 3/4). Die Datenbank haelt
dieselbe Bedingung — ein Weg, der sie umgeht, kann es nicht geben.

Der Feldsatz folgt Anhang II und Art. 9; die fachjuristische Abnahme gehoert dem
Compliance-Owner. Siehe
``docs/quality-assurance/eudr-sorgfaltserklaerung-20261001.md``.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.eudr_register_schemas import (
    EinreichungIn,
    EudrRegisterStatusOut,
    GeolokationIn,
    GeolokationOut,
    POLYGONGRENZE_HA,
    RISIKOSTUFEN,
    ROHSTOFFE,
    RisikobewertungIn,
    SorgfaltserklaerungDetailOut,
    SorgfaltserklaerungIn,
    SorgfaltserklaerungOut,
    VorgelagerteErklaerungIn,
    VorgelagerteErklaerungOut,
)

router = APIRouter(prefix="/eudr/sorgfaltserklaerungen", tags=["EUDR", "Compliance"])
logger = logging.getLogger(__name__)

ERKLAERUNGEN = "domain_compliance.eudr_due_diligence"
GEOLOKATIONEN = "domain_compliance.eudr_geolokationen"
VORGELAGERT = "domain_compliance.eudr_vorgelagerte_erklaerungen"

MIGRATIONS_HINWEIS = {
    "X-Migration-Hint": "Run: alembic upgrade head (eudr_sorgfaltserklaerung_20261001)"
}

_FELDER = (
    "id, tenant_id, status, betreiber_name, betreiber_adresse, eori_nummer, "
    "rohstoff, hs_code, warenbeschreibung, menge_netto_kg, menge_volumen_m3, "
    "ergaenzende_einheit, produktionsland, produktion_von, produktion_bis, "
    "lieferant_name, lieferant_adresse, lieferant_email, "
    "nachweis_abholzungsfrei, nachweis_abholzungsfrei_quelle, "
    "nachweis_rechtskonform, nachweis_rechtskonform_quelle, "
    "risikostufe, risikobewertung_am, risikobewertung_durch, minderungsmassnahmen, "
    "erklaerung_abgegeben_am, erklaerung_durch_name, erklaerung_durch_funktion, "
    "referenznummer, verifizierungsnummer, eingereicht_am, created_at"
)

_ZEITFELDER = (
    "produktion_von",
    "produktion_bis",
    "risikobewertung_am",
    "erklaerung_abgegeben_am",
    "eingereicht_am",
    "created_at",
)


def _zeile(row: Any) -> dict:
    d = dict(row)
    for schluessel in _ZEITFELDER:
        wert = d.get(schluessel)
        if wert is not None and hasattr(wert, "isoformat"):
            d[schluessel] = wert.isoformat()
    for schluessel in ("menge_netto_kg", "menge_volumen_m3"):
        if d.get(schluessel) is not None:
            d[schluessel] = float(d[schluessel])
    return d


def _nicht_lesbar(db: Session, fehler: Exception, was: str, tenant_id: str) -> HTTPException:
    """Ein Lesefehler ist keine leere Lage.

    Ein EUDR-Register, das bei einer Stoerung "nichts gefunden" antwortet, sagt
    einem Haus, es habe keine Nachweise zu fuehren. Nach Art. 3/4 ist das
    Inverkehrbringen ohne Sorgfaltserklaerung verboten.
    """
    db.rollback()
    logger.exception("%s nicht lesbar (Mandant %s)", was, tenant_id)
    return HTTPException(
        status_code=503,
        detail={"error": str(fehler), "migration_hint": MIGRATIONS_HINWEIS["X-Migration-Hint"]},
        headers=MIGRATIONS_HINWEIS,
    )


def _erklaerung_holen(db: Session, tenant_id: str, erklaerung_id: str) -> dict:
    zeile = db.execute(
        text(f"SELECT {_FELDER} FROM {ERKLAERUNGEN} WHERE id = :id AND tenant_id = :tid"),  # nosec B608  # reviewed-safe: _FELDER und Tabellenname sind Code-Literale
        {"id": erklaerung_id, "tid": tenant_id},
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail="Sorgfaltserklaerung nicht gefunden")
    return _zeile(zeile)


def _geolokation_pruefen(ort: GeolokationIn) -> None:
    """Art. 9: Ab vier Hektar ist die Geolokation als Polygon anzugeben."""
    if ort.flaeche_ha is not None and ort.flaeche_ha > POLYGONGRENZE_HA and not ort.polygon:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Flurstueck mit {ort.flaeche_ha} ha: Ab {POLYGONGRENZE_HA} ha verlangt "
                "Art. 9 der Verordnung (EU) 2023/1115 ein Polygon, kein Punkt."
            ),
        )


def _geolokation_schreiben(
    db: Session, tenant_id: str, erklaerung_id: str, ort: GeolokationIn
) -> str:
    import json

    neue_id = str(uuid7())
    db.execute(
        text(
            f"INSERT INTO {GEOLOKATIONEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, erklaerung_id, flurstueck_kennung, breitengrad, "
            " laengengrad, flaeche_ha, polygon) "
            "VALUES (:id, :tid, :eid, :kennung, :breite, :laenge, :flaeche, "
            "        CAST(:polygon AS jsonb))"
        ),
        {
            "id": neue_id,
            "tid": tenant_id,
            "eid": erklaerung_id,
            "kennung": ort.flurstueck_kennung,
            "breite": ort.breitengrad,
            "laenge": ort.laengengrad,
            "flaeche": ort.flaeche_ha,
            "polygon": json.dumps(ort.polygon) if ort.polygon else None,
        },
    )
    return neue_id


# ── Anlegen und Lesen ───────────────────────────────────────────────────────


@router.post(
    "",
    response_model=SorgfaltserklaerungDetailOut,
    status_code=http_status.HTTP_201_CREATED,
    summary="Sorgfaltserklärung anlegen (Entwurf)",
)
def anlegen(
    payload: SorgfaltserklaerungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Legt eine Erklaerung als **Entwurf** an.

    Eingereicht wird sie erst ueber ``/einreichen`` — und nur, wenn die
    Risikobewertung vernachlaessigbares Risiko ergeben hat.
    """
    if payload.rohstoff not in ROHSTOFFE:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannter Rohstoff '{payload.rohstoff}'. Anhang I: {', '.join(ROHSTOFFE)}",
        )
    if payload.produktion_bis < payload.produktion_von:
        raise HTTPException(
            status_code=422, detail="Produktionszeitraum endet vor seinem Beginn"
        )
    for ort in payload.geolokationen:
        _geolokation_pruefen(ort)

    neue_id = str(uuid7())
    try:
        db.execute(
            text(
                f"INSERT INTO {ERKLAERUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
                "(id, tenant_id, betreiber_name, betreiber_adresse, eori_nummer, "
                " rohstoff, hs_code, warenbeschreibung, menge_netto_kg, menge_volumen_m3, "
                " ergaenzende_einheit, produktionsland, produktion_von, produktion_bis, "
                " lieferant_name, lieferant_adresse, lieferant_email, "
                " nachweis_abholzungsfrei, nachweis_abholzungsfrei_quelle, "
                " nachweis_rechtskonform, nachweis_rechtskonform_quelle, status) "
                "VALUES (:id, :tid, :betreiber_name, :betreiber_adresse, :eori, "
                "        :rohstoff, :hs_code, :beschreibung, :netto, :volumen, "
                "        :einheit, :land, :von, :bis, "
                "        :lieferant_name, :lieferant_adresse, :lieferant_email, "
                "        :nw_abholzung, :nw_abholzung_quelle, "
                "        :nw_recht, :nw_recht_quelle, 'ENTWURF')"
            ),
            {
                "id": neue_id,
                "tid": tenant_id,
                "betreiber_name": payload.betreiber_name,
                "betreiber_adresse": payload.betreiber_adresse,
                "eori": payload.eori_nummer,
                "rohstoff": payload.rohstoff,
                "hs_code": payload.hs_code,
                "beschreibung": payload.warenbeschreibung,
                "netto": payload.menge_netto_kg,
                "volumen": payload.menge_volumen_m3,
                "einheit": payload.ergaenzende_einheit,
                "land": payload.produktionsland.upper(),
                "von": payload.produktion_von,
                "bis": payload.produktion_bis,
                "lieferant_name": payload.lieferant_name,
                "lieferant_adresse": payload.lieferant_adresse,
                "lieferant_email": payload.lieferant_email,
                "nw_abholzung": payload.nachweis_abholzungsfrei,
                "nw_abholzung_quelle": payload.nachweis_abholzungsfrei_quelle,
                "nw_recht": payload.nachweis_rechtskonform,
                "nw_recht_quelle": payload.nachweis_rechtskonform_quelle,
            },
        )
        for ort in payload.geolokationen:
            _geolokation_schreiben(db, tenant_id, neue_id, ort)
        for vorgelagert in payload.vorgelagerte_erklaerungen:
            db.execute(
                text(
                    f"INSERT INTO {VORGELAGERT} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
                    "(id, tenant_id, erklaerung_id, referenznummer, "
                    " verifizierungsnummer, lieferant_name) "
                    "VALUES (:id, :tid, :eid, :ref, :verif, :lieferant)"
                ),
                {
                    "id": str(uuid7()),
                    "tid": tenant_id,
                    "eid": neue_id,
                    "ref": vorgelagert.referenznummer,
                    "verif": vorgelagert.verifizierungsnummer,
                    "lieferant": vorgelagert.lieferant_name,
                },
            )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail={"error": str(fehler), "migration_hint": MIGRATIONS_HINWEIS["X-Migration-Hint"]},
            headers=MIGRATIONS_HINWEIS,
        ) from fehler

    return abrufen(neue_id, tenant_id=tenant_id, db=db)


@router.get("", response_model=list[SorgfaltserklaerungOut], summary="Sorgfaltserklärungen auflisten")
def auflisten(
    status_filter: Optional[str] = Query(None, alias="status"),
    rohstoff: Optional[str] = Query(None),
    produktionsland: Optional[str] = Query(None, min_length=2, max_length=2),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Die Erklaerungen des eigenen Hauses."""
    bedingungen = ["tenant_id = :tid"]
    werte: dict[str, Any] = {"tid": tenant_id, "skip": skip, "limit": limit}
    if status_filter:
        bedingungen.append("status = :status")
        werte["status"] = status_filter
    if rohstoff:
        bedingungen.append("rohstoff = :rohstoff")
        werte["rohstoff"] = rohstoff
    if produktionsland:
        bedingungen.append("produktionsland = :land")
        werte["land"] = produktionsland.upper()

    try:
        zeilen = db.execute(
            text(
                f"SELECT {_FELDER} FROM {ERKLAERUNGEN} "  # nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden
                f"WHERE {' AND '.join(bedingungen)} "
                "ORDER BY created_at DESC OFFSET :skip LIMIT :limit"
            ),
            werte,
        ).mappings().all()
    except Exception as fehler:  # noqa: BLE001
        raise _nicht_lesbar(db, fehler, "EUDR-Erklaerungen", tenant_id) from fehler
    return [_zeile(z) for z in zeilen]


@router.get("/status", response_model=EudrRegisterStatusOut, summary="EUDR-Registerstand")
def registerstand(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Der Stand des Registers — ohne gruene Behauptung.

    ``KONFORM`` nur, wenn jede Erklaerung eingereicht ist und
    vernachlaessigbares Risiko traegt. Ein leeres Register ist
    ``OHNE_ERKLAERUNG``, nicht ``KONFORM``: Nach Art. 3/4 ist das
    Inverkehrbringen ohne Sorgfaltserklaerung verboten, und "nichts erfasst" ist
    kein Nachweis.
    """
    try:
        zahlen = db.execute(
            text(
                "SELECT COUNT(*) AS gesamt, "
                "       COUNT(*) FILTER (WHERE status = 'EINGEREICHT') AS eingereicht, "
                "       COUNT(*) FILTER (WHERE status = 'ENTWURF') AS entwurf, "
                "       COUNT(*) FILTER (WHERE risikostufe = 'NICHT_VERNACHLAESSIGBAR') AS riskant, "
                "       COUNT(*) FILTER (WHERE risikostufe IS NULL) AS unbewertet, "
                "       ARRAY_AGG(DISTINCT produktionsland) AS laender, "
                "       ARRAY_AGG(DISTINCT rohstoff) AS rohstoffe "
                f"FROM {ERKLAERUNGEN} WHERE tenant_id = :tid"  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            ),
            {"tid": tenant_id},
        ).mappings().one()
    except Exception as fehler:  # noqa: BLE001
        raise _nicht_lesbar(db, fehler, "EUDR-Registerstand", tenant_id) from fehler

    gesamt = int(zahlen["gesamt"] or 0)
    eingereicht = int(zahlen["eingereicht"] or 0)
    riskant = int(zahlen["riskant"] or 0)
    unbewertet = int(zahlen["unbewertet"] or 0)

    if gesamt == 0:
        stand = "OHNE_ERKLAERUNG"
    elif riskant > 0:
        stand = "KRITISCH"
    elif eingereicht < gesamt:
        stand = "UNVOLLSTAENDIG"
    else:
        stand = "KONFORM"

    return {
        "status": stand,
        "erklaerungen_gesamt": gesamt,
        "erklaerungen_eingereicht": eingereicht,
        "erklaerungen_entwurf": int(zahlen["entwurf"] or 0),
        "risiko_nicht_vernachlaessigbar": riskant,
        "ohne_risikobewertung": unbewertet,
        "produktionslaender": sorted(x for x in (zahlen["laender"] or []) if x),
        "rohstoffe": sorted(x for x in (zahlen["rohstoffe"] or []) if x),
        "stand_am": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/{erklaerung_id}", response_model=SorgfaltserklaerungDetailOut, summary="Sorgfaltserklärung abrufen")
def abrufen(
    erklaerung_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Eine Erklaerung mit ihren Flurstuecken und vorgelagerten Erklaerungen."""
    try:
        kopf = _erklaerung_holen(db, tenant_id, erklaerung_id)
        orte = db.execute(
            text(
                "SELECT id, flurstueck_kennung, breitengrad, laengengrad, flaeche_ha, polygon "
                f"FROM {GEOLOKATIONEN} WHERE erklaerung_id = :eid AND tenant_id = :tid "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
                "ORDER BY erfasst_am LIMIT 5000"
            ),
            {"eid": erklaerung_id, "tid": tenant_id},
        ).mappings().all()
        vorgelagert = db.execute(
            text(
                "SELECT id, referenznummer, verifizierungsnummer, lieferant_name "
                f"FROM {VORGELAGERT} WHERE erklaerung_id = :eid AND tenant_id = :tid "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
                "ORDER BY erfasst_am LIMIT 5000"
            ),
            {"eid": erklaerung_id, "tid": tenant_id},
        ).mappings().all()
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise _nicht_lesbar(db, fehler, "EUDR-Erklaerung", tenant_id) from fehler

    kopf["geolokationen"] = [
        {
            "id": o["id"],
            "flurstueck_kennung": o["flurstueck_kennung"],
            "breitengrad": float(o["breitengrad"]),
            "laengengrad": float(o["laengengrad"]),
            "flaeche_ha": float(o["flaeche_ha"]) if o["flaeche_ha"] is not None else None,
            "polygon": o["polygon"],
        }
        for o in orte
    ]
    kopf["vorgelagerte_erklaerungen"] = [dict(v) for v in vorgelagert]
    return kopf


# ── Flurstücke nachtragen ───────────────────────────────────────────────────


@router.post(
    "/{erklaerung_id}/geolokationen",
    response_model=GeolokationOut,
    status_code=http_status.HTTP_201_CREATED,
    summary="Flurstück nachtragen",
)
def geolokation_nachtragen(
    erklaerung_id: str,
    payload: GeolokationIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Art. 9: Die Geolokation **aller** Flurstuecke gehoert zur Erklaerung."""
    kopf = _erklaerung_holen(db, tenant_id, erklaerung_id)
    if kopf["status"] != "ENTWURF":
        raise HTTPException(
            status_code=409,
            detail=(
                f"Erklaerung ist {kopf['status']}. Flurstuecke werden am Entwurf "
                "erfasst; eine eingereichte Erklaerung wird nicht nachtraeglich "
                "veraendert."
            ),
        )
    _geolokation_pruefen(payload)
    try:
        neue_id = _geolokation_schreiben(db, tenant_id, erklaerung_id, payload)
        db.commit()
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        raise HTTPException(status_code=503, detail=str(fehler)) from fehler
    return {
        "id": neue_id,
        "flurstueck_kennung": payload.flurstueck_kennung,
        "breitengrad": payload.breitengrad,
        "laengengrad": payload.laengengrad,
        "flaeche_ha": payload.flaeche_ha,
        "polygon": payload.polygon,
    }


# ── Risikobewertung und Einreichung ─────────────────────────────────────────


@router.post(
    "/{erklaerung_id}/risikobewertung",
    response_model=SorgfaltserklaerungOut,
    summary="Risikobewertung festhalten (Art. 10/11)",
)
def risiko_bewerten(
    erklaerung_id: str,
    payload: RisikobewertungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Haelt die Feststellung nach Art. 10 fest.

    Bei mehr als vernachlaessigbarem Risiko verlangt Art. 11
    Minderungsmassnahmen — ohne sie wird die Bewertung nicht angenommen.
    """
    if payload.risikostufe not in RISIKOSTUFEN:
        raise HTTPException(
            status_code=422,
            detail=f"Risikostufe muss eine von {', '.join(RISIKOSTUFEN)} sein",
        )
    if payload.risikostufe == "NICHT_VERNACHLAESSIGBAR" and not (
        payload.minderungsmassnahmen or ""
    ).strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "Bei nicht vernachlaessigbarem Risiko verlangt Art. 11 der "
                "Verordnung (EU) 2023/1115 Minderungsmassnahmen."
            ),
        )

    kopf = _erklaerung_holen(db, tenant_id, erklaerung_id)
    if kopf["status"] == "EINGEREICHT":
        raise HTTPException(
            status_code=409,
            detail="Erklaerung ist eingereicht; die Bewertung wird nicht nachtraeglich geaendert.",
        )
    try:
        db.execute(
            text(
                f"UPDATE {ERKLAERUNGEN} SET risikostufe = :stufe, "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
                "    risikobewertung_am = NOW(), risikobewertung_durch = :durch, "
                "    minderungsmassnahmen = :massnahmen, updated_at = NOW() "
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {
                "stufe": payload.risikostufe,
                "durch": payload.bewertet_durch,
                "massnahmen": payload.minderungsmassnahmen,
                "id": erklaerung_id,
                "tid": tenant_id,
            },
        )
        db.commit()
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        raise HTTPException(status_code=503, detail=str(fehler)) from fehler
    return _erklaerung_holen(db, tenant_id, erklaerung_id)


@router.post(
    "/{erklaerung_id}/einreichen",
    response_model=SorgfaltserklaerungOut,
    summary="Sorgfaltserklärung einreichen (Art. 33)",
)
def einreichen(
    erklaerung_id: str,
    payload: EinreichungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Haelt Referenz- und Verifizierungsnummer des EU-Systems fest.

    Eingereicht wird nur, was die Verordnung erlaubt: vernachlaessigbares
    Risiko, beide Nachweise, Unterzeichnung mit Name und Funktion (Art. 3/4,
    Anhang II Nr. 6). Dieselbe Bedingung haelt die Datenbank.
    """
    kopf = _erklaerung_holen(db, tenant_id, erklaerung_id)
    if kopf["status"] == "EINGEREICHT":
        raise HTTPException(status_code=409, detail="Erklaerung ist bereits eingereicht.")

    fehlt: list[str] = []
    if kopf.get("risikostufe") != "VERNACHLAESSIGBAR":
        fehlt.append(
            "Risikobewertung mit vernachlaessigbarem Risiko (Art. 10; bei hoeherem "
            "Risiko verlangt Art. 11 zuerst Minderungsmassnahmen)"
        )
    if not kopf.get("nachweis_abholzungsfrei"):
        fehlt.append("Nachweis, dass das Erzeugnis abholzungsfrei ist (Art. 9)")
    if not kopf.get("nachweis_rechtskonform"):
        fehlt.append(
            "Nachweis der Herstellung nach dem Recht des Erzeugerlandes (Art. 9)"
        )
    if fehlt:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Einreichung nach Art. 3/4 nicht zulaessig",
                "fehlt": fehlt,
            },
        )

    try:
        db.execute(
            text(
                f"UPDATE {ERKLAERUNGEN} SET status = 'EINGEREICHT', "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
                "    referenznummer = :ref, verifizierungsnummer = :verif, "
                "    eingereicht_am = NOW(), erklaerung_abgegeben_am = NOW(), "
                "    erklaerung_durch_name = :name, erklaerung_durch_funktion = :funktion, "
                "    updated_at = NOW() "
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {
                "ref": payload.referenznummer,
                "verif": payload.verifizierungsnummer,
                "name": payload.erklaerung_durch_name,
                "funktion": payload.erklaerung_durch_funktion,
                "id": erklaerung_id,
                "tid": tenant_id,
            },
        )
        db.commit()
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        # Die Pruefbedingung der Datenbank haelt dieselbe Regel. Wird sie hier
        # verletzt, ist die Einreichung fachlich unzulaessig — nicht der Dienst
        # gestoert.
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Einreichung abgewiesen",
                "grund": str(fehler),
            },
        ) from fehler
    return _erklaerung_holen(db, tenant_id, erklaerung_id)
