"""Abruf kontrahierter Mengen — eine Wahrheit uber Freigabe und Menge.

Hier stehen das Zustandswoerterbuch, die erlaubten Uebergaenge und die
Mengenpruefung gegen den Kontrakt. Die Regel stand schon im Modell und wurde nie
gelesen: ``kon_contract.allow_overdelivery`` sagt, ob mehr abgerufen werden darf
als kontrahiert ist.

Siehe ``docs/quality-assurance/kontrakt-disposition-20261005.md``.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

DISPOSITIONEN = "domain_agrar.kontrakt_dispositionen"
KONTRAKTE = "domain_ops.kon_contract"
KONTRAKTZEILEN = "domain_ops.kon_contract_line"
WIEGESCHEINE = "domain_inventory.weighing_tickets"

#: Deckungsgleich mit ``ck_dispo_status``.
ZUSTAENDE = ("OFFEN", "FREIGEGEBEN", "GELIEFERT", "STORNIERT")

#: Zustaende, die eine Kontraktmenge binden. Ein stornierter Abruf bindet nichts.
BINDEND = ("OFFEN", "FREIGEGEBEN", "GELIEFERT")

#: Endgueltige Zustaende. Aus ihnen fuehrt kein Weg heraus.
ENDGUELTIG = ("GELIEFERT", "STORNIERT")

#: Erlaubte Uebergaenge. Geliefert wird nur aus der Freigabe — sonst waere die
#: Freigabe kein Tor, sondern eine Notiz.
UEBERGAENGE = {
    "OFFEN": ("FREIGEGEBEN", "STORNIERT"),
    "FREIGEGEBEN": ("GELIEFERT", "STORNIERT"),
    "GELIEFERT": (),
    "STORNIERT": (),
}

FELDER = (
    "id, tenant_id, kontrakt_id, kontrakt_nr, kontrakt_pos_nr, disposition_nr, "
    "geplantes_lieferdatum, lieferdatum, menge, status, wiegeschein_id, "
    "bemerkung, erfasst_durch, created_at, updated_at"
)

ZEITFELDER = ("geplantes_lieferdatum", "lieferdatum", "created_at", "updated_at")

MIGRATIONS_HINWEIS = {
    "X-Migration-Hint": "Run: alembic upgrade head (kontrakt_disposition_20261005)"
}


def als_dict(row: Any) -> dict:
    """Eine Zeile als Abbildung — mit abgeleiteter Freigabe.

    ``freigabe`` ist keine Spalte mehr: Sie war als Boolean **und** als Zustand
    gespeichert, und der Lieferweg setzte nur einen von beiden.
    """
    d = dict(row)
    for schluessel in ZEITFELDER:
        wert = d.get(schluessel)
        if wert is not None and hasattr(wert, "isoformat"):
            d[schluessel] = wert.isoformat()
    if d.get("menge") is not None:
        d["menge"] = float(d["menge"])
    d["freigabe"] = d.get("status") in ("FREIGEGEBEN", "GELIEFERT")
    return d


def nicht_lesbar(db: Session, fehler: Exception, was: str, tenant_id: str) -> HTTPException:
    """Ein Lesefehler ist keine leere Dispositionsliste.

    Ein Kontrakt ohne sichtbare Abrufe sieht aus wie ein Kontrakt, der noch ganz
    offen ist — und genau danach wuerde disponiert.
    """
    db.rollback()
    logger.exception("%s nicht lesbar (Mandant %s)", was, tenant_id)
    return HTTPException(
        status_code=503,
        detail={"error": str(fehler), "migration_hint": MIGRATIONS_HINWEIS["X-Migration-Hint"]},
        headers=MIGRATIONS_HINWEIS,
    )


def kontraktposition(db: Session, tenant_id: str, kontrakt_id: str, pos_nr: int) -> dict:
    """Kontrakt und Position — oder 404.

    Gelesen wird auch ``allow_overdelivery``: Ob ueber die kontrahierte Menge
    hinaus abgerufen werden darf, ist eine Eigenschaft des Kontrakts und keine
    des Abrufs.
    """
    zeile = db.execute(
        text(
            "SELECT k.contract_id, k.contract_no, k.status AS kontrakt_status, "
            "       COALESCE(k.allow_overdelivery, FALSE) AS ueberlieferung_erlaubt, "
            "       z.line_id, z.position_no, z.qty_contract, z.article_id "
            f"FROM {KONTRAKTE} k "  # nosec B608  # reviewed-safe: Tabellennamen sind Code-Literale
            f"JOIN {KONTRAKTZEILEN} z "
            "     ON z.contract_id = k.contract_id AND z.tenant_id = k.tenant_id "
            "WHERE k.contract_id = :kid AND k.tenant_id = :tid AND z.position_no = :pos"
        ),
        {"kid": kontrakt_id, "tid": tenant_id, "pos": pos_nr},
    ).mappings().first()
    if not zeile:
        raise HTTPException(
            status_code=404,
            detail=f"Kontrakt {kontrakt_id} Position {pos_nr} nicht gefunden",
        )
    return dict(zeile)


def bereits_abgerufen(
    db: Session, tenant_id: str, kontrakt_id: str, pos_nr: int, ausser: Optional[str] = None
) -> Decimal:
    """Die Summe der bindenden Abrufe einer Kontraktposition."""
    summe = db.execute(
        text(
            "SELECT COALESCE(SUM(menge), 0) "
            f"FROM {DISPOSITIONEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE tenant_id = :tid AND kontrakt_id = :kid AND kontrakt_pos_nr = :pos "
            "  AND status = ANY(:bindend) AND (:ausser IS NULL OR id <> :ausser)"
        ),
        {
            "tid": tenant_id,
            "kid": kontrakt_id,
            "pos": pos_nr,
            "bindend": list(BINDEND),
            "ausser": ausser,
        },
    ).scalar()
    return Decimal(str(summe or 0))


def menge_pruefen(position: dict, bereits: Decimal, neu: float) -> None:
    """Mehr abrufen als kontrahiert ist nur erlaubt, wenn der Kontrakt es sagt.

    Die Regel stand schon im Modell (``kon_contract.allow_overdelivery``) und
    wurde nie gelesen. Ohne sie liess sich jede Menge abrufen, und der Kontrakt
    war eine Notiz.
    """
    kontrahiert = position.get("qty_contract")
    if kontrahiert is None:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Kontraktposition {position['position_no']} fuehrt keine "
                "kontrahierte Menge. Ohne sie ist kein Abruf pruefbar."
            ),
        )
    kontrahiert = Decimal(str(kontrahiert))
    gesamt = bereits + Decimal(str(neu))
    if gesamt > kontrahiert and not position["ueberlieferung_erlaubt"]:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Kontrakt {position['contract_no']} Position {position['position_no']} "
                f"ist mit {kontrahiert} kontrahiert, davon sind {bereits} abgerufen. "
                f"Ein Abruf von {neu} wuerde die Kontraktmenge um "
                f"{gesamt - kontrahiert} uebersteigen. Der Kontrakt erlaubt keine "
                "Ueberlieferung (allow_overdelivery)."
            ),
        )


def uebergang_pruefen(von: str, nach: str, dispositions_nr: Any) -> None:
    """Ein verbotener Zustandswechsel ist ein 409 mit der Begruendung.

    Vorher gab es keine Regel: Eine stornierte Disposition liess sich als
    geliefert melden, eine gelieferte stornieren, und geliefert werden konnte
    ohne Freigabe.
    """
    if von not in UEBERGAENGE:
        raise HTTPException(
            status_code=409, detail=f"Unbekannter Zustand {von!r} an Disposition {dispositions_nr}."
        )
    if nach in UEBERGAENGE[von]:
        return
    if von in ENDGUELTIG:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Disposition {dispositions_nr} ist {von} — das ist endgueltig. "
                f"Ein Wechsel nach {nach} wuerde einen abgeschlossenen Vorgang "
                "nachtraeglich veraendern."
            ),
        )
    erlaubt = ", ".join(UEBERGAENGE[von]) or "keiner"
    raise HTTPException(
        status_code=409,
        detail=(
            f"Disposition {dispositions_nr} ist {von}; ein Wechsel nach {nach} ist "
            f"nicht vorgesehen. Erlaubt: {erlaubt}. "
            "Geliefert wird nur aus der Freigabe — sonst waere die Freigabe kein Tor."
        ),
    )


def disposition_sperren(db: Session, tenant_id: str, kontrakt_id: str, disp_id: str) -> dict:
    """Die Disposition holen und die Zeile sperren.

    ``FOR UPDATE``, damit zwei gleichzeitige Zustandswechsel nicht beide vom
    alten Zustand ausgehen.
    """
    zeile = db.execute(
        text(
            f"SELECT {FELDER} FROM {DISPOSITIONEN} "  # nosec B608  # reviewed-safe: FELDER und Tabellenname sind Code-Literale
            "WHERE id = :id AND kontrakt_id = :kid AND tenant_id = :tid FOR UPDATE"
        ),
        {"id": disp_id, "kid": kontrakt_id, "tid": tenant_id},
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail=f"Disposition {disp_id} nicht gefunden")
    return dict(zeile)


def wiegeschein_aufloesen(db: Session, tenant_id: str, nummer: Optional[str]) -> Optional[str]:
    """Die Wiegescheinnummer in die Kennung des kanonischen Scheins uebersetzen.

    Vorher stand hier freier Text. Eine Lieferung, die sich auf einen
    Wiegeschein beruft, den es nicht gibt, ist nicht belegt — und ein Text, den
    niemand nachschlagen kann, ist kein Beleg.
    """
    if not nummer or not nummer.strip():
        return None
    schein_id = db.execute(
        text(
            f"SELECT id FROM {WIEGESCHEINE} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE tenant_id = :tid AND ticket_number = :nr"
        ),
        {"tid": tenant_id, "nr": nummer.strip()},
    ).scalar()
    if not schein_id:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Wiegeschein {nummer!r} ist im Register nicht zu finden. Eine "
                "Lieferung wird gegen einen vorhandenen Wiegeschein gemeldet; "
                "eine Nummer ohne Schein ist kein Beleg."
            ),
        )
    return str(schein_id)


def zustand_setzen(
    db: Session,
    tenant_id: str,
    kontrakt_id: str,
    disp_id: str,
    nach: str,
    *,
    lieferdatum: Any = None,
    wiegeschein_id: Optional[str] = None,
) -> dict:
    """Den Zustand wechseln und die Zeile zurueckgeben."""
    zeile = db.execute(
        text(
            f"UPDATE {DISPOSITIONEN} SET status = :nach, "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            # Die Umwandlung ist ausgeschrieben: Ein ungebundenes NULL im CASE
            # leitet Postgres als ``text`` ab und bricht an der Datumsspalte.
            "    lieferdatum = CASE WHEN :nach = 'GELIEFERT' "
            "                      THEN CAST(:lieferdatum AS date) ELSE NULL END, "
            "    wiegeschein_id = CASE WHEN :nach = 'GELIEFERT' "
            "                        THEN CAST(:schein AS varchar) ELSE NULL END, "
            "    updated_at = NOW() "
            f"WHERE id = :id AND kontrakt_id = :kid AND tenant_id = :tid RETURNING {FELDER}"
        ),
        {
            "nach": nach,
            "lieferdatum": lieferdatum,
            "schein": wiegeschein_id,
            "id": disp_id,
            "kid": kontrakt_id,
            "tid": tenant_id,
        },
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail=f"Disposition {disp_id} nicht gefunden")
    return als_dict(zeile)


def auflisten(db: Session, tenant_id: str, kontrakt_id: str, limit: int) -> list[dict]:
    zeilen = db.execute(
        text(
            f"SELECT {FELDER} FROM {DISPOSITIONEN} "  # nosec B608  # reviewed-safe: FELDER und Tabellenname sind Code-Literale
            "WHERE kontrakt_id = :kid AND tenant_id = :tid "
            "ORDER BY disposition_nr ASC LIMIT :limit"
        ),
        {"kid": kontrakt_id, "tid": tenant_id, "limit": limit},
    ).mappings().fetchmany(limit)
    return [als_dict(z) for z in zeilen]


def anlegen(
    db: Session,
    tenant_id: str,
    disp_id: str,
    kontrakt_id: str,
    position: dict,
    menge: float,
    *,
    geplantes_lieferdatum: Any = None,
    bemerkung: Optional[str] = None,
    erfasst_durch: Optional[str] = None,
) -> dict:
    """Einen Abruf anlegen. Die laufende Nummer ist je Kontrakt fortlaufend."""
    zeile = db.execute(
        text(
            f"INSERT INTO {DISPOSITIONEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, kontrakt_id, kontrakt_nr, kontrakt_pos_nr, disposition_nr, "
            " geplantes_lieferdatum, menge, status, bemerkung, erfasst_durch) "
            "VALUES (:id, :tid, :kid, :knr, :pos, "
            f"        COALESCE((SELECT MAX(disposition_nr) FROM {DISPOSITIONEN} "
            "                  WHERE tenant_id = :tid AND kontrakt_id = :kid), 0) + 1, "
            "        :geplant, :menge, 'OFFEN', :bemerkung, :durch) "
            f"RETURNING {FELDER}"
        ),
        {
            "id": disp_id,
            "tid": tenant_id,
            "kid": kontrakt_id,
            "knr": position["contract_no"],
            "pos": position["position_no"],
            "geplant": geplantes_lieferdatum,
            "menge": Decimal(str(menge)),
            "bemerkung": bemerkung,
            "durch": erfasst_durch,
        },
    ).mappings().first()
    return als_dict(zeile)


def abrufstand(db: Session, tenant_id: str, kontrakt_id: str) -> list[dict]:
    """Kontrahierte, abgerufene und offene Menge je Kontraktposition.

    Die offene Menge ist abgeleitet. Sie irgendwo zu speichern hiesse, eine
    zweite Wahrheit neben den Abrufen zu fuehren.
    """
    zeilen = db.execute(
        text(
            "SELECT k.contract_id, k.contract_no, z.position_no, z.qty_contract, "
            "       COALESCE(k.allow_overdelivery, FALSE) AS ueberlieferung_erlaubt, "
            "       COALESCE(d.abgerufen, 0) AS abgerufen "
            f"FROM {KONTRAKTE} k "  # nosec B608  # reviewed-safe: Tabellennamen sind Code-Literale
            f"JOIN {KONTRAKTZEILEN} z "
            "     ON z.contract_id = k.contract_id AND z.tenant_id = k.tenant_id "
            "LEFT JOIN ("
            "    SELECT kontrakt_id, kontrakt_pos_nr, SUM(menge) AS abgerufen "
            f"    FROM {DISPOSITIONEN} WHERE tenant_id = :tid AND status = ANY(:bindend) "
            "    GROUP BY kontrakt_id, kontrakt_pos_nr"
            ") d ON d.kontrakt_id = k.contract_id AND d.kontrakt_pos_nr = z.position_no "
            "WHERE k.contract_id = :kid AND k.tenant_id = :tid "
            "ORDER BY z.position_no"
        ),
        {"kid": kontrakt_id, "tid": tenant_id, "bindend": list(BINDEND)},
    ).mappings().fetchmany(1000)
    if not zeilen:
        raise HTTPException(status_code=404, detail=f"Kontrakt {kontrakt_id} nicht gefunden")
    stand = []
    for z in zeilen:
        kontrahiert = float(z["qty_contract"] or 0)
        abgerufen = float(z["abgerufen"] or 0)
        stand.append({
            "kontrakt_id": z["contract_id"],
            "kontrakt_nr": z["contract_no"],
            "kontrakt_pos_nr": z["position_no"],
            "menge_kontrahiert": kontrahiert,
            "menge_abgerufen": abgerufen,
            "menge_offen": max(0.0, kontrahiert - abgerufen),
            "ueberlieferung_erlaubt": bool(z["ueberlieferung_erlaubt"]),
        })
    return stand


def zustand_wechseln(
    db: Session,
    tenant_id: str,
    kontrakt_id: str,
    disp_id: str,
    nach: str,
    *,
    wiegeschein_nr: Optional[str] = None,
    lieferdatum: Any = None,
) -> dict:
    """Ein Zustandswechsel, eine Stelle — mit Zeilensperre und Uebergangspruefung."""
    from datetime import date as _date

    try:
        vorher = disposition_sperren(db, tenant_id, kontrakt_id, disp_id)
        uebergang_pruefen(vorher["status"], nach, vorher["disposition_nr"])
        schein_id = None
        if nach == "GELIEFERT":
            schein_id = wiegeschein_aufloesen(db, tenant_id, wiegeschein_nr)
            lieferdatum = lieferdatum or _date.today()
        ergebnis = zustand_setzen(
            db, tenant_id, kontrakt_id, disp_id, nach,
            lieferdatum=lieferdatum, wiegeschein_id=schein_id,
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        logger.exception("Zustandswechsel nach %s fehlgeschlagen (Mandant %s)", nach, tenant_id)
        raise HTTPException(
            status_code=503,
            detail={"error": f"Wechsel nach {nach} nicht moeglich", "grund": str(fehler)},
            headers=MIGRATIONS_HINWEIS,
        ) from fehler
    return ergebnis


def abrufen(db: Session, tenant_id: str, kontrakt_id: str, payload: Any) -> dict:
    """Einen Abruf anlegen: Position holen, Menge pruefen, schreiben, festschreiben."""
    from app.core.uuid7 import uuid7

    try:
        position = kontraktposition(db, tenant_id, kontrakt_id, payload.kontrakt_pos_nr)
        bereits = bereits_abgerufen(db, tenant_id, kontrakt_id, payload.kontrakt_pos_nr)
        menge_pruefen(position, bereits, payload.menge)
        ergebnis = anlegen(
            db, tenant_id, str(uuid7()), kontrakt_id, position, payload.menge,
            geplantes_lieferdatum=payload.geplantes_lieferdatum,
            bemerkung=payload.bemerkung,
            erfasst_durch=payload.erfasst_durch,
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        logger.exception("Abruf nicht anlegbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=503,
            detail={"error": "Abruf nicht angelegt", "grund": str(fehler),
                    "migration_hint": MIGRATIONS_HINWEIS["X-Migration-Hint"]},
            headers=MIGRATIONS_HINWEIS,
        ) from fehler
    return ergebnis
