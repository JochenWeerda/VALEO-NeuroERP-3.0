"""Drucker und Druckauftraege — ein Auftrag, der gespeichert ist.

Bis zum 06.10.2026 antwortete `POST /etiketten/druckauftrag` mit `201`, einer
Auftragsnummer und `status: "erstellt"` — und schrieb nichts und druckte nichts.
Die Druckerliste bestand aus drei Literalen mit IP-Adressen und dem Status
„online".

Der Auftrag wird jetzt gespeichert. Gedruckt wird er nicht: Es ist kein Spooler
angebunden. Deshalb endet er bei :data:`ANGELEGT`, und die Antwort sagt das —
``uebermittlung: "NICHT_ANGEBUNDEN"``. Ein Etikett ist ein
Rueckverfolgbarkeitsbeleg; ein Auftrag, der „fertig" meldet, ohne dass etwas
gedruckt wurde, ist schlimmer als einer, der ehrlich wartet.

Siehe ``docs/quality-assurance/quittung-ohne-vorgang-20261006.md``.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

DRUCKER = "domain_erp.drucker"
AUFTRAEGE = "domain_erp.druckauftraege"

#: Deckungsgleich mit ``ck_drucker_status``.
DRUCKERSTAENDE = ("online", "offline", "fehler", "wartung")

#: Deckungsgleich mit ``ck_druckauftrag_status``.
AUFTRAGSSTAENDE = ("ANGELEGT", "UEBERMITTELT", "GEDRUCKT", "FEHLER", "ABGEBROCHEN")

#: Solange kein Spooler angebunden ist, ist dies die Wahrheit ueber den Versand.
#: Sie steht in der Antwort, damit niemand einen Druck annimmt.
UEBERMITTLUNG_UNVERBUNDEN = "NICHT_ANGEBUNDEN"

FELDER_DRUCKER = (
    "id, tenant_id, name, standort, typ, modell, status, ip, aktiv, created_at"
)

FELDER_AUFTRAG = (
    "id, tenant_id, auftrags_nr, chargen_id, artikel, menge, lieferant, eingang, "
    "anzahl_etiketten, drucker_id, status, uebermittelt_am, gedruckt_am, fehler, "
    "erfasst_durch, created_at"
)

MIGRATIONS_HINWEIS = {
    "X-Migration-Hint": "Run: alembic upgrade head (quittung_ohne_vorgang_20261006)"
}


def nicht_lesbar(db: Session, fehler: Exception, was: str, tenant_id: str) -> HTTPException:
    """Ein Lesefehler ist keine leere Liste — und keine erfundene."""
    db.rollback()
    logger.exception("%s nicht lesbar (Mandant %s)", was, tenant_id)
    return HTTPException(
        status_code=503,
        detail={"error": str(fehler), "migration_hint": MIGRATIONS_HINWEIS["X-Migration-Hint"]},
        headers=MIGRATIONS_HINWEIS,
    )


def _als_dict(row: Any, zeitfelder: tuple[str, ...], zahlfelder: tuple[str, ...]) -> dict:
    d = dict(row)
    for schluessel in zeitfelder:
        wert = d.get(schluessel)
        if wert is not None and hasattr(wert, "isoformat"):
            d[schluessel] = wert.isoformat()
    for schluessel in zahlfelder:
        if d.get(schluessel) is not None:
            d[schluessel] = float(d[schluessel])
    return d


# ── Drucker ─────────────────────────────────────────────────────────────────


def drucker(db: Session, tenant_id: str, limit: int = 200) -> list[dict]:
    zeilen = db.execute(
        text(
            f"SELECT {FELDER_DRUCKER} FROM {DRUCKER} "  # nosec B608  # reviewed-safe: FELDER und Tabellenname sind Code-Literale
            "WHERE tenant_id = :tid AND aktiv ORDER BY name LIMIT :limit"
        ),
        {"tid": tenant_id, "limit": limit},
    ).mappings().fetchmany(limit)
    return [_als_dict(z, ("created_at",), ()) for z in zeilen]


def drucker_holen(db: Session, tenant_id: str, drucker_id: str) -> dict:
    zeile = db.execute(
        text(
            f"SELECT {FELDER_DRUCKER} FROM {DRUCKER} "  # nosec B608  # reviewed-safe: FELDER und Tabellenname sind Code-Literale
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": drucker_id, "tid": tenant_id},
    ).mappings().first()
    if not zeile:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Drucker {drucker_id!r} gehoert nicht zu diesem Mandanten oder "
                "existiert nicht. Vorher stand hier eine Literalliste, und jede "
                "beliebige Kennung ging durch."
            ),
        )
    return dict(zeile)


def drucker_anlegen(db: Session, tenant_id: str, neue_id: str, payload: Any) -> dict:
    zeile = db.execute(
        text(
            f"INSERT INTO {DRUCKER} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, name, standort, typ, modell, status, ip) "
            "VALUES (:id, :tid, :name, :ort, :typ, :modell, :status, :ip) "
            f"RETURNING {FELDER_DRUCKER}"
        ),
        {
            "id": neue_id,
            "tid": tenant_id,
            "name": payload.name,
            "ort": payload.standort,
            "typ": payload.typ,
            "modell": payload.modell,
            "status": payload.status,
            "ip": payload.ip,
        },
    ).mappings().first()
    return _als_dict(zeile, ("created_at",), ())


# ── Druckauftraege ──────────────────────────────────────────────────────────


def naechste_auftragsnummer(db: Session, tenant_id: str) -> str:
    """Fortlaufend je Mandant und Tag — die Nummer steht auf dem Beleg."""
    tag = db.execute(text("SELECT TO_CHAR(NOW(), 'YYYYMMDD')")).scalar()
    hoechste = db.execute(
        text(
            "SELECT MAX(SUBSTRING(auftrags_nr FROM '[0-9]+$')::int) "
            f"FROM {AUFTRAEGE} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE tenant_id = :tid AND auftrags_nr ~ :muster"
        ),
        {"tid": tenant_id, "muster": f"^ETK-{tag}-[0-9]+$"},
    ).scalar()
    return f"ETK-{tag}-{(hoechste or 0) + 1:04d}"


def auftraege(
    db: Session, tenant_id: str, status: Optional[str], limit: int
) -> list[dict]:
    if status is not None and status not in AUFTRAGSSTAENDE:
        raise HTTPException(
            status_code=422,
            detail=f"Unbekannter Stand {status!r}. Erlaubt: {', '.join(AUFTRAGSSTAENDE)}.",
        )
    zeilen = db.execute(
        text(
            f"SELECT a.{FELDER_AUFTRAG.replace(', ', ', a.')}, d.name AS drucker_name "  # nosec B608  # reviewed-safe: FELDER und Tabellennamen sind Code-Literale
            f"FROM {AUFTRAEGE} a "
            f"JOIN {DRUCKER} d ON d.id = a.drucker_id AND d.tenant_id = a.tenant_id "
            "WHERE a.tenant_id = :tid AND (:status IS NULL OR a.status = :status) "
            "ORDER BY a.created_at DESC LIMIT :limit"
        ),
        {"tid": tenant_id, "status": status, "limit": limit},
    ).mappings().fetchmany(limit)
    return [_mit_uebermittlung(z) for z in zeilen]


def _mit_uebermittlung(row: Any) -> dict:
    """Die Antwort nennt den Versandstand — nicht nur den Auftragsstand.

    Ein Auftrag kann angelegt sein, ohne dass ihn jemals ein Drucker gesehen hat.
    Genau diese Unterscheidung fehlte.
    """
    d = _als_dict(
        row, ("eingang", "uebermittelt_am", "gedruckt_am", "created_at"), ("menge",)
    )
    d["uebermittlung"] = (
        UEBERMITTLUNG_UNVERBUNDEN if d.get("uebermittelt_am") is None else "UEBERMITTELT"
    )
    return d


def auftrag_anlegen(
    db: Session, tenant_id: str, neue_id: str, nummer: str, payload: Any, drucker_satz: dict
) -> dict:
    """Legt den Auftrag an — im Stand `ANGELEGT`, nicht „erstellt und gedruckt"."""
    zeile = db.execute(
        text(
            f"INSERT INTO {AUFTRAEGE} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, auftrags_nr, chargen_id, artikel, menge, lieferant, "
            " eingang, anzahl_etiketten, drucker_id, status, erfasst_durch) "
            "VALUES (:id, :tid, :nr, :charge, :artikel, :menge, :lieferant, :eingang, "
            "        :anzahl, :drucker, 'ANGELEGT', :durch) "
            f"RETURNING {FELDER_AUFTRAG}"
        ),
        {
            "id": neue_id,
            "tid": tenant_id,
            "nr": nummer,
            "charge": payload.chargen_id,
            "artikel": payload.artikel,
            "menge": None if payload.menge is None else Decimal(str(payload.menge)),
            "lieferant": payload.lieferant,
            "eingang": payload.eingang,
            "anzahl": payload.anzahl_etiketten,
            "drucker": payload.drucker_id,
            "durch": payload.erfasst_durch,
        },
    ).mappings().first()
    ergebnis = _mit_uebermittlung(zeile)
    ergebnis["drucker_name"] = drucker_satz["name"]
    return ergebnis


def auftrag_abbrechen(db: Session, tenant_id: str, auftrag_id: str, grund: str) -> dict:
    """Bricht einen Auftrag ab. Ein gedruckter Auftrag wird nicht abgebrochen."""
    vorher = db.execute(
        text(
            f"SELECT {FELDER_AUFTRAG} FROM {AUFTRAEGE} "  # nosec B608  # reviewed-safe: FELDER und Tabellenname sind Code-Literale
            "WHERE id = :id AND tenant_id = :tid FOR UPDATE"
        ),
        {"id": auftrag_id, "tid": tenant_id},
    ).mappings().first()
    if not vorher:
        raise HTTPException(status_code=404, detail=f"Druckauftrag {auftrag_id} nicht gefunden")
    if vorher["status"] == "GEDRUCKT":
        raise HTTPException(
            status_code=409,
            detail=(
                f"Druckauftrag {vorher['auftrags_nr']} ist gedruckt. Etiketten, die "
                "im Umlauf sind, macht kein Abbruch rueckgaengig."
            ),
        )
    zeile = db.execute(
        text(
            f"UPDATE {AUFTRAEGE} SET status = 'ABGEBROCHEN', fehler = :grund, "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "    updated_at = NOW() WHERE id = :id AND tenant_id = :tid "
            f"RETURNING {FELDER_AUFTRAG}"
        ),
        {"grund": grund, "id": auftrag_id, "tid": tenant_id},
    ).mappings().first()
    return _mit_uebermittlung(zeile)
