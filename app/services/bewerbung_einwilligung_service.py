"""Erteilen und Widerrufen der Aufbewahrungs-Einwilligung.

Der Loeschlauf achtet eine Einwilligung zur laengeren Aufbewahrung (Talentpool,
Art. 6 Abs. 1 lit. a DSGVO). Dieser Dienst ist der Weg dorthin — und zurueck.

Zwei Pflichten bestimmen die Form:

* **Art. 7 Abs. 3 DSGVO:** Der Widerruf muss jederzeit moeglich sein und darf nicht
  schwerer sein als die Erteilung. Deshalb verlangt er **keinen Grund**, keine
  Freigabe und keine Angaben.
* **Art. 7 Abs. 1 DSGVO:** Die Einwilligung muss **nachweisbar** sein. Deshalb ist
  der Widerruf eine **neue Zeile** im Verzeichnis und keine Aenderung der alten: Wer
  die Erteilung ueberschreibt, vernichtet den Nachweis, warum die Daten im
  abgelaufenen Zeitraum ueberhaupt noch da waren.

**Stand und Verzeichnis.** `applications.aufbewahrung_einwilligung_bis/_am` ist der
**operative Stand**, den der Loeschlauf liest; `domain_hr.bewerbung_einwilligungen`
ist der **Nachweis der Vorgaenge**. Das ist keine doppelt gehaltene Ableitung,
sondern Stand und Journal: Geschrieben werden beide nur hier und nur in **einer**
Transaktion, und ein Vertrag prueft, dass der Stand immer der letzten Zeile
entspricht.

Siehe ``docs/quality-assurance/bewerbung-einwilligung-20261006.md``.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

BEWERBUNGEN = "domain_hr.applications"
VERZEICHNIS = "domain_hr.bewerbung_einwilligungen"

#: Die beiden Vorgaenge — deckungsgleich mit ``ck_beweinw_vorgang``.
ERTEILT = "ERTEILT"
WIDERRUFEN = "WIDERRUFEN"
VORGAENGE = (ERTEILT, WIDERRUFEN)

#: Deckungsgleich mit ``ck_beweinw_kanal``.
KANAELE = ("WEB", "E_MAIL", "PAPIER", "MUENDLICH")

#: Eine Erlaubnis ohne Ende ist ein Vorrat, keine Einwilligung. Dieselbe Obergrenze
#: wie bei der Aufbewahrungsfrist — drei Jahre.
MAX_TAGE = 1095

FELDER = (
    "id, tenant_id, bewerbung_id, vorgang, erfolgt_am, gueltig_bis, kanal, "
    "einwilligungstext, erfasst_durch"
)

ZEITFELDER = ("erfolgt_am", "gueltig_bis")


def als_dict(zeile: Any) -> dict:
    d = dict(zeile)
    for schluessel in ZEITFELDER:
        wert = d.get(schluessel)
        if wert is not None and hasattr(wert, "isoformat"):
            d[schluessel] = wert.isoformat()
    return d


def bewerbung_sperren(db: Session, tenant_id: str, bewerbung_id: str) -> dict:
    """Die Bewerbung zum Schreiben holen — oder 404.

    Gesperrt, weil Stand und Verzeichnis zusammen geschrieben werden: Zwei
    gleichzeitige Widerrufe duerfen nicht zwei Staende hinterlassen.
    """
    zeile = db.execute(
        text(
            "SELECT id, status, aufbewahrung_einwilligung_bis, "
            "       aufbewahrung_einwilligung_am "
            f"FROM {BEWERBUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE id = :id AND tenant_id = :tid FOR UPDATE"
        ),
        {"id": bewerbung_id, "tid": tenant_id},
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")
    return dict(zeile)


def verzeichnis(db: Session, tenant_id: str, bewerbung_id: str, limit: int = 200) -> list[dict]:
    """Alle Vorgaenge zu dieser Bewerbung, neueste zuerst."""
    zeilen = db.execute(
        text(
            f"SELECT {FELDER} FROM {VERZEICHNIS} "  # nosec B608  # reviewed-safe: FELDER und Tabellenname sind Code-Literale
            "WHERE tenant_id = :tid AND bewerbung_id = :bid "
            "ORDER BY erfolgt_am DESC, id DESC LIMIT :limit"
        ),
        {"tid": tenant_id, "bid": bewerbung_id, "limit": limit},
    ).mappings().fetchmany(limit)
    return [als_dict(z) for z in zeilen]


def stand(db: Session, tenant_id: str, bewerbung_id: str) -> dict:
    """Stand und Verzeichnis in einer Antwort.

    ``laeuft`` sagt, ob die Erlaubnis **heute** noch gilt — eine abgelaufene
    Einwilligung schuetzt nicht mehr, und ein Feld, das nur ein Datum nennt, laesst
    das offen.
    """
    bewerbung = db.execute(
        text(
            "SELECT aufbewahrung_einwilligung_bis AS gueltig_bis, "
            "       aufbewahrung_einwilligung_am AS erteilt_am, "
            "       (aufbewahrung_einwilligung_bis IS NOT NULL "
            "        AND aufbewahrung_einwilligung_bis >= CURRENT_DATE) AS laeuft "
            f"FROM {BEWERBUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": bewerbung_id, "tid": tenant_id},
    ).mappings().first()
    if not bewerbung:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")
    d = dict(bewerbung)
    for schluessel in ("gueltig_bis", "erteilt_am"):
        if d.get(schluessel) is not None and hasattr(d[schluessel], "isoformat"):
            d[schluessel] = d[schluessel].isoformat()
    return {
        "bewerbung_id": bewerbung_id,
        "gueltig_bis": d["gueltig_bis"],
        "erteilt_am": d["erteilt_am"],
        "laeuft": bool(d["laeuft"]),
        "vorgaenge": verzeichnis(db, tenant_id, bewerbung_id),
    }


def _vorgang_schreiben(
    db: Session,
    tenant_id: str,
    bewerbung_id: str,
    neue_id: str,
    vorgang: str,
    gueltig_bis: Optional[date],
    kanal: Optional[str],
    einwilligungstext: Optional[str],
    erfasst_durch: Optional[str],
) -> dict:
    zeile = db.execute(
        text(
            f"INSERT INTO {VERZEICHNIS} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, bewerbung_id, vorgang, gueltig_bis, kanal, "
            " einwilligungstext, erfasst_durch) "
            "VALUES (:id, :tid, :bid, :vorgang, CAST(:bis AS date), :kanal, :wortlaut, :durch) "
            f"RETURNING {FELDER}"
        ),
        {
            "id": neue_id,
            "tid": tenant_id,
            "bid": bewerbung_id,
            "vorgang": vorgang,
            "bis": gueltig_bis,
            "kanal": kanal,
            "wortlaut": einwilligungstext,
            "durch": erfasst_durch,
        },
    ).mappings().first()
    return als_dict(zeile)


def erteilen(
    db: Session, tenant_id: str, bewerbung_id: str, neue_id: str, payload: Any
) -> dict:
    """Erteilt die Einwilligung: Verzeichniszeile **und** Stand, in einer Transaktion.

    Eine Verzeichniszeile ohne Stand waere ein Nachweis ohne Wirkung — der
    Loeschlauf wuerde die Daten trotzdem mitnehmen.
    """
    bewerbung_sperren(db, tenant_id, bewerbung_id)

    heute = date.today()
    if payload.gueltig_bis <= heute:
        raise HTTPException(
            status_code=422,
            detail=(
                "Die Einwilligung muss in der Zukunft enden. Ein bereits "
                "abgelaufenes Ende erlaubt nichts und verhindert nichts."
            ),
        )
    if (payload.gueltig_bis - heute).days > MAX_TAGE:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Hoechstens {MAX_TAGE} Tage ab heute. Eine Erlaubnis ohne nahes "
                "Ende ist ein Vorrat, keine Einwilligung; sie kann erneuert werden."
            ),
        )

    vorgang = _vorgang_schreiben(
        db,
        tenant_id,
        bewerbung_id,
        neue_id,
        ERTEILT,
        payload.gueltig_bis,
        payload.kanal,
        payload.einwilligungstext,
        payload.erfasst_durch,
    )
    db.execute(
        text(
            f"UPDATE {BEWERBUNGEN} SET "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "    aufbewahrung_einwilligung_bis = CAST(:bis AS date), "
            "    aufbewahrung_einwilligung_am = NOW() "
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {"bis": payload.gueltig_bis, "id": bewerbung_id, "tid": tenant_id},
    )
    return vorgang


def widerrufen(
    db: Session, tenant_id: str, bewerbung_id: str, neue_id: str, erfasst_durch: Optional[str]
) -> dict:
    """Widerruft die Einwilligung — ohne Grund, ohne Rumpf, jederzeit.

    Art. 7 Abs. 3 DSGVO: Der Widerruf darf nicht schwerer sein als die Erteilung.
    Deshalb verlangt dieser Weg **nichts** ausser der Bewerbung.

    Die Erteilung bleibt im Verzeichnis stehen; der Widerruf ist eine neue Zeile.
    """
    bewerbung = bewerbung_sperren(db, tenant_id, bewerbung_id)
    if bewerbung.get("aufbewahrung_einwilligung_bis") is None:
        # Stillzuhalten waere die bequemere Antwort und die schlechtere: Wer
        # widerruft, will wissen, dass etwas da war.
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Fuer diese Bewerbung liegt keine Einwilligung vor.",
                "hinweis": (
                    "Es gibt nichts zu widerrufen. Die Aufbewahrung richtet sich "
                    "allein nach der beschlossenen Frist."
                ),
            },
        )

    # Der Kanal bleibt leer. Ihn zu erfragen waere eine Angabe mehr als bei der
    # Erteilung; ihn zu erfinden ("WEB") waere eine Behauptung ueber einen Vorgang,
    # von dem niemand weiss, wie er einging. Leer heisst "nicht erhoben".
    vorgang = _vorgang_schreiben(
        db, tenant_id, bewerbung_id, neue_id, WIDERRUFEN, None, None, None, erfasst_durch
    )
    db.execute(
        text(
            f"UPDATE {BEWERBUNGEN} SET "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "    aufbewahrung_einwilligung_bis = NULL, "
            "    aufbewahrung_einwilligung_am = NULL "
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": bewerbung_id, "tid": tenant_id},
    )
    logger.info(
        "Einwilligung widerrufen (Bewerbung %s, Mandant %s)", bewerbung_id, tenant_id
    )
    return vorgang
