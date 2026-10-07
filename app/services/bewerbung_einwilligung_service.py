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

**Die Erklaerung in Fassungen.** Erteilt wird gegen eine **Fassung** der
Einwilligungserklaerung (`domain_hr.bewerbung_einwilligungserklaerungen`), nicht
gegen freien Text: Nachweisbar ist eine Einwilligung erst, wenn feststeht, welchem
Wortlaut zugestimmt wurde und dass er sich seitdem nicht geaendert hat. Fassungen
sind je Mandant fortlaufend, derselbe Wortlaut ist eine Fassung, und die Datenbank
haelt sie unveraenderlich.

Siehe ``docs/quality-assurance/bewerbung-einwilligung-20261006.md`` und
``docs/quality-assurance/bewerbung-erklaerung-fassung-20261006.md``.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.business_time import business_today

logger = logging.getLogger(__name__)

BEWERBUNGEN = "domain_hr.applications"
VERZEICHNIS = "domain_hr.bewerbung_einwilligungen"
ERKLAERUNGEN = "domain_hr.bewerbung_einwilligungserklaerungen"

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
    "erfasst_durch"
)

#: Ein Vorgang mit seiner Fassung. Der Wortlaut heisst in der Antwort weiter
#: ``einwilligungstext`` — er steht aber nur noch an einer Stelle, in der Fassung.
VORGANG_MIT_FASSUNG = (
    "v.id, v.tenant_id, v.bewerbung_id, v.vorgang, v.erfolgt_am, v.gueltig_bis, "
    "v.kanal, v.erfasst_durch, e.fassung, e.wortlaut AS einwilligungstext"
)

ERKLAERUNG_FELDER = "id, tenant_id, fassung, wortlaut, erstellt_am, erstellt_durch"

ZEITFELDER = ("erfolgt_am", "gueltig_bis", "erstellt_am")

#: Randleerzeichen machen keinen anderen Text — deckungsgleich mit
#: ``ck_beweinwerk_wortlaut``.
LEERRAUM = " \t\r\n"


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
            f"SELECT {VORGANG_MIT_FASSUNG} FROM {VERZEICHNIS} v "  # nosec B608  # reviewed-safe: Felder und Tabellennamen sind Code-Literale
            f"LEFT JOIN {ERKLAERUNGEN} e "
            "  ON e.id = v.erklaerung_id AND e.tenant_id = v.tenant_id "
            "WHERE v.tenant_id = :tid AND v.bewerbung_id = :bid "
            "ORDER BY v.erfolgt_am DESC, v.id DESC LIMIT :limit"
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
            "        AND aufbewahrung_einwilligung_bis >= CAST(:heute AS date)) AS laeuft "
            f"FROM {BEWERBUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": bewerbung_id, "tid": tenant_id, "heute": business_today()},
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


# ── Die Erklaerung in Fassungen ─────────────────────────────────────────────


def erklaerungen_auflisten(db: Session, tenant_id: str, limit: int = 200) -> list[dict]:
    """Die Fassungen des Mandanten, neueste zuerst."""
    zeilen = db.execute(
        text(
            f"SELECT {ERKLAERUNG_FELDER} FROM {ERKLAERUNGEN} "  # nosec B608  # reviewed-safe: Felder und Tabellenname sind Code-Literale
            "WHERE tenant_id = :tid ORDER BY fassung DESC LIMIT :limit"
        ),
        {"tid": tenant_id, "limit": limit},
    ).mappings().fetchmany(limit)
    return [als_dict(z) for z in zeilen]


def _erklaerung_holen(db: Session, tenant_id: str, fassung: int) -> Optional[dict]:
    zeile = db.execute(
        text(
            f"SELECT {ERKLAERUNG_FELDER} FROM {ERKLAERUNGEN} "  # nosec B608  # reviewed-safe: Felder und Tabellenname sind Code-Literale
            "WHERE tenant_id = :tid AND fassung = :fassung"
        ),
        {"tid": tenant_id, "fassung": fassung},
    ).mappings().first()
    return als_dict(zeile) if zeile else None


def erklaerung_lesen(db: Session, tenant_id: str, fassung: int) -> dict:
    erklaerung = _erklaerung_holen(db, tenant_id, fassung)
    if not erklaerung:
        raise HTTPException(
            status_code=404, detail=f"Fassung {fassung} der Einwilligungserklaerung nicht gefunden"
        )
    return erklaerung


def erklaerung_anlegen(
    db: Session,
    tenant_id: str,
    neue_id: str,
    wortlaut: str,
    erstellt_durch: Optional[str],
) -> dict:
    """Legt die naechste Fassung an — oder sagt, welche diesen Wortlaut schon traegt.

    Die Nummer vergibt das System, je Mandant lueckenlos. Zwei gleichzeitige Anlagen
    werden ueber eine Transaktionssperre je Mandant nacheinander gelegt; die
    Eindeutigkeit in der Datenbank bleibt die letzte Instanz.
    """
    wortlaut = wortlaut.strip(LEERRAUM)
    if not wortlaut:
        raise HTTPException(
            status_code=422,
            detail="Eine Fassung ohne Wortlaut belegt nichts; ohne Text kein Zweck.",
        )
    db.execute(
        text("SELECT pg_advisory_xact_lock(hashtextextended(:schluessel, 0))"),
        {"schluessel": f"bewerbung_einwilligungserklaerung:{tenant_id}"},
    )
    vorhanden = db.execute(
        text(
            f"SELECT fassung FROM {ERKLAERUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE tenant_id = :tid AND md5(wortlaut) = md5(:wortlaut) AND wortlaut = :wortlaut"
        ),
        {"tid": tenant_id, "wortlaut": wortlaut},
    ).scalar()
    if vorhanden is not None:
        # Eine zweite Nummer fuer denselben Text liesse zwei Formulare gleich
        # aussehen und verschieden heissen.
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Dieser Wortlaut ist bereits eine Fassung.",
                "fassung": vorhanden,
            },
        )
    zeile = db.execute(
        text(
            f"INSERT INTO {ERKLAERUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, fassung, wortlaut, erstellt_durch) "
            "SELECT :id, :tid, COALESCE(MAX(fassung), 0) + 1, :wortlaut, :durch "
            f"FROM {ERKLAERUNGEN} WHERE tenant_id = :tid "
            f"RETURNING {ERKLAERUNG_FELDER}"
        ),
        {"id": neue_id, "tid": tenant_id, "wortlaut": wortlaut, "durch": erstellt_durch},
    ).mappings().first()
    return als_dict(zeile)


# ── Vorgaenge ───────────────────────────────────────────────────────────────


def _vorgang_schreiben(
    db: Session,
    tenant_id: str,
    bewerbung_id: str,
    neue_id: str,
    vorgang: str,
    gueltig_bis: Optional[date],
    kanal: Optional[str],
    erklaerung: Optional[dict],
    erfasst_durch: Optional[str],
) -> dict:
    zeile = db.execute(
        text(
            f"INSERT INTO {VERZEICHNIS} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, bewerbung_id, vorgang, gueltig_bis, kanal, "
            " erklaerung_id, erfasst_durch) "
            "VALUES (:id, :tid, :bid, :vorgang, CAST(:bis AS date), :kanal, :erklaerung, :durch) "
            f"RETURNING {FELDER}"
        ),
        {
            "id": neue_id,
            "tid": tenant_id,
            "bid": bewerbung_id,
            "vorgang": vorgang,
            "bis": gueltig_bis,
            "kanal": kanal,
            "erklaerung": erklaerung["id"] if erklaerung else None,
            "durch": erfasst_durch,
        },
    ).mappings().first()
    ergebnis = als_dict(zeile)
    ergebnis["fassung"] = erklaerung["fassung"] if erklaerung else None
    ergebnis["einwilligungstext"] = erklaerung["wortlaut"] if erklaerung else None
    return ergebnis


def erteilen(
    db: Session, tenant_id: str, bewerbung_id: str, neue_id: str, payload: Any
) -> dict:
    """Erteilt die Einwilligung: Verzeichniszeile **und** Stand, in einer Transaktion.

    Eine Verzeichniszeile ohne Stand waere ein Nachweis ohne Wirkung — der
    Loeschlauf wuerde die Daten trotzdem mitnehmen.
    """
    bewerbung_sperren(db, tenant_id, bewerbung_id)

    # Nur eine Fassung des **eigenen** Mandanten. Eine aeltere ist zulaessig: Wer ein
    # frueher gedrucktes Formular unterschrieben hat, hat diesem Text zugestimmt.
    erklaerung = _erklaerung_holen(db, tenant_id, payload.fassung)
    if not erklaerung:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Fassung {payload.fassung} der Einwilligungserklaerung gibt es fuer "
                "diesen Mandanten nicht. Ohne Fassung ist nicht nachweisbar, wozu "
                "eingewilligt wurde."
            ),
        )

    heute = business_today()
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
        erklaerung,
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
