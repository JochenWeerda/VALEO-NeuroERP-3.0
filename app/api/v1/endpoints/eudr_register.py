"""EUDR-Sorgfaltserklaerungen — das Register.

Die Erklaerung entsteht als **Entwurf**, bekommt eine **Risikobewertung**
(Art. 10/11) und wird erst dann **eingereicht** (Art. 33), wenn hoechstens ein
vernachlaessigbares Risiko festgestellt, beide Nachweise vorliegen und die
Erklaerung unterzeichnet ist (Art. 3/4). Die Datenbank haelt dieselbe
Bedingung — ein Weg, der sie umgeht, kann es nicht geben.

Grundlage: Verordnung (EU) 2023/1115. Entscheidung und Beweislage:
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
from app.services import eudr_register_service as dienst

from app.api.v1.schemas.eudr_register_schemas import (
    EinreichungIn,
    EudrRegisterStatusOut,
    GeolokationIn,
    GeolokationOut,
    RISIKOSTUFEN,
    ROHSTOFFE,
    RisikobewertungIn,
    SorgfaltserklaerungDetailOut,
    SorgfaltserklaerungIn,
    SorgfaltserklaerungOut,
    VorgelagerteErklaerungIn,
    VorgelagerteErklaerungOut,
)

#: Obergrenze fuer die Kindlisten einer Erklaerung. Wird sie erreicht, ist die
#: Antwort ein 503 und keine stillschweigend gekuerzte Liste.
GRENZE_KINDLISTE = 5000

router = APIRouter(prefix="/eudr/sorgfaltserklaerungen", tags=["EUDR", "Compliance"])
logger = logging.getLogger(__name__)


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
        dienst.geolokation_pruefen(ort)

    neue_id = str(uuid7())
    try:
        db.execute(
            text(
                f"INSERT INTO {dienst.ERKLAERUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
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
            dienst.geolokation_schreiben(db, tenant_id, neue_id, ort)
        for vorgelagert in payload.vorgelagerte_erklaerungen:
            db.execute(
                text(
                    f"INSERT INTO {dienst.VORGELAGERT} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
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
            detail={"error": str(fehler), "migration_hint": dienst.MIGRATIONS_HINWEIS["X-Migration-Hint"]},
            headers=dienst.MIGRATIONS_HINWEIS,
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
                f"SELECT {dienst.FELDER} FROM {dienst.ERKLAERUNGEN} "  # nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden
                f"WHERE {' AND '.join(bedingungen)} "
                "ORDER BY created_at DESC OFFSET :skip LIMIT :limit"
            ),
            werte,
        ).mappings().fetchmany(limit)
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "EUDR-Erklaerungen", tenant_id) from fehler
    return [dienst.als_dict(z) for z in zeilen]


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
                # Nur eine Uebermittlung in die Produktion zaehlt als Abgabe.
                # Ein eingerichteter Testzugang darf nicht wie Erfuellung
                # aussehen.
                "       COUNT(*) FILTER (WHERE status = 'EINGEREICHT' "
                "                        AND NOT (uebermittlung_status = 'UEBERMITTELT' "
                "                                 AND uebermittlung_umgebung = 'PRODUKTION')) "
                "         AS nicht_uebermittelt, "
                "       COUNT(*) FILTER (WHERE uebermittlung_status = 'UEBERMITTELT' "
                "                        AND uebermittlung_umgebung = 'ANNAHMETEST') "
                "         AS nur_annahmetest, "
                "       COUNT(*) FILTER (WHERE uebermittlung_status = 'ABGEWIESEN') "
                "         AS abgewiesen, "
                "       ARRAY_AGG(DISTINCT rohstoff) AS rohstoffe "
                f"FROM {dienst.ERKLAERUNGEN} WHERE tenant_id = :tid"  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            ),
            {"tid": tenant_id},
        ).mappings().one()
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "EUDR-Registerstand", tenant_id) from fehler

    gesamt = int(zahlen["gesamt"] or 0)
    eingereicht = int(zahlen["eingereicht"] or 0)
    riskant = int(zahlen["riskant"] or 0)
    unbewertet = int(zahlen["unbewertet"] or 0)

    # Art. 4/5, herein: zugekaufte Referenznummern ohne Pruefung. Eine
    # abgeschriebene Nummer ist kein Nachweis.
    try:
        vorgelagert = db.execute(
            text(
                "SELECT COUNT(*) AS gesamt, "
                "       COUNT(*) FILTER (WHERE pruefung_status <> 'BESTAETIGT') AS ungeprueft "
                f"FROM {dienst.VORGELAGERT} WHERE tenant_id = :tid"  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            ),
            {"tid": tenant_id},
        ).mappings().one()
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "Vorgelagerte EUDR-Erklaerungen", tenant_id) from fehler

    # Art. 4: Eine relevante Charge ohne Nachweis darf nicht in Verkehr. Das
    # ist die Zahl, die ein Haus wirklich braucht.
    try:
        chargen = db.execute(
            text(
                "SELECT COUNT(*) FILTER (WHERE eudr_relevant) AS relevant, "
                "       COUNT(*) FILTER (WHERE kennzeichnung = 'NACHGEWIESEN') AS nachgewiesen, "
                "       COUNT(*) FILTER (WHERE kennzeichnung = 'OFFEN') AS offen, "
                "       COALESCE(SUM(menge_kg - gedeckte_menge_kg) "
                "                FILTER (WHERE kennzeichnung = 'OFFEN'), 0) AS offene_menge "
                f"FROM ({dienst.KENNZEICHNUNG}) k"  # nosec B608  # reviewed-safe: dienst.KENNZEICHNUNG ist ein Code-Literal, Werte sind gebunden
            ),
            {"tid": tenant_id},
        ).mappings().one()
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "EUDR-Chargenkennzeichnung", tenant_id) from fehler

    offene_chargen = int(chargen["offen"] or 0)
    if gesamt == 0:
        stand = "OHNE_ERKLAERUNG"
    elif riskant > 0:
        stand = "KRITISCH"
    elif eingereicht < gesamt or offene_chargen > 0:
        # Eine relevante Charge ohne Nachweis macht den Stand unvollstaendig,
        # auch wenn jede erfasste Erklaerung eingereicht ist: Nach Art. 4 darf
        # diese Charge nicht in Verkehr gebracht werden.
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
        "chargen_relevant": int(chargen["relevant"] or 0),
        "chargen_nachgewiesen": int(chargen["nachgewiesen"] or 0),
        "chargen_offen": int(chargen["offen"] or 0),
        "offene_menge_kg": float(chargen["offene_menge"] or 0),
        "erklaerungen_nicht_uebermittelt": int(zahlen["nicht_uebermittelt"] or 0),
        "erklaerungen_abgewiesen": int(zahlen["abgewiesen"] or 0),
        "erklaerungen_nur_annahmetest": int(zahlen["nur_annahmetest"] or 0),
        "vorgelagerte_gesamt": int(vorgelagert["gesamt"] or 0),
        "vorgelagerte_ungeprueft": int(vorgelagert["ungeprueft"] or 0),
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
        kopf = dienst.erklaerung_holen(db, tenant_id, erklaerung_id)
        orte = db.execute(
            text(
                "SELECT id, flurstueck_kennung, breitengrad, laengengrad, flaeche_ha, polygon "
                f"FROM {dienst.GEOLOKATIONEN} WHERE erklaerung_id = :eid AND tenant_id = :tid "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
                f"ORDER BY erfasst_am LIMIT {GRENZE_KINDLISTE}"
            ),
            {"eid": erklaerung_id, "tid": tenant_id},
        ).mappings().fetchmany(GRENZE_KINDLISTE)
        vorgelagert = db.execute(
            text(
                "SELECT id, referenznummer, verifizierungsnummer, lieferant_name, "
                "       pruefung_status, geprueft_am, pruefung_quelle "
                f"FROM {dienst.VORGELAGERT} WHERE erklaerung_id = :eid AND tenant_id = :tid "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
                f"ORDER BY erfasst_am LIMIT {GRENZE_KINDLISTE}"
            ),
            {"eid": erklaerung_id, "tid": tenant_id},
        ).mappings().fetchmany(GRENZE_KINDLISTE)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "EUDR-Erklaerung", tenant_id) from fehler

    # Eine abgeschnittene Liste darf nicht wie eine vollstaendige aussehen:
    # Art. 9 verlangt **alle** Flurstuecke, und eine Erklaerung, die nur die
    # ersten zeigt, waere ein unvollstaendiger Nachweis, der vollstaendig wirkt.
    for was, zeilen in (("Flurstuecke", orte), ("vorgelagerte Erklaerungen", vorgelagert)):
        if len(zeilen) >= GRENZE_KINDLISTE:
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Die Erklaerung fuehrt mindestens {GRENZE_KINDLISTE} {was}. "
                    "Diese Ansicht kann sie nicht vollstaendig zeigen, und eine "
                    "unvollstaendige Sorgfaltserklaerung ist kein Nachweis "
                    "(Art. 9 Verordnung (EU) 2023/1115)."
                ),
            )

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
    kopf["vorgelagerte_erklaerungen"] = [
        {
            **dict(v),
            "geprueft_am": v["geprueft_am"].isoformat() if v["geprueft_am"] else None,
        }
        for v in vorgelagert
    ]
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
    kopf = dienst.erklaerung_holen(db, tenant_id, erklaerung_id)
    if kopf["status"] != "ENTWURF":
        raise HTTPException(
            status_code=409,
            detail=(
                f"Erklaerung ist {kopf['status']}. Flurstuecke werden am Entwurf "
                "erfasst; eine eingereichte Erklaerung wird nicht nachtraeglich "
                "veraendert."
            ),
        )
    dienst.geolokation_pruefen(payload)
    try:
        neue_id = dienst.geolokation_schreiben(db, tenant_id, erklaerung_id, payload)
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

    kopf = dienst.erklaerung_holen(db, tenant_id, erklaerung_id)
    if kopf["status"] == "EINGEREICHT":
        raise HTTPException(
            status_code=409,
            detail="Erklaerung ist eingereicht; die Bewertung wird nicht nachtraeglich geaendert.",
        )
    try:
        db.execute(
            text(
                f"UPDATE {dienst.ERKLAERUNGEN} SET risikostufe = :stufe, "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
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
    return dienst.erklaerung_holen(db, tenant_id, erklaerung_id)


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
    kopf = dienst.erklaerung_holen(db, tenant_id, erklaerung_id)
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
                f"UPDATE {dienst.ERKLAERUNGEN} SET status = 'EINGEREICHT', "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
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
    return dienst.erklaerung_holen(db, tenant_id, erklaerung_id)

