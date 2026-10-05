"""Mitgliederregister einer eG — eine Wahrheit uber den Anteilsbestand.

Der Bestand steht **nicht** in einer Spalte. Er wird aus den Bewegungen
gerechnet, und die Rechnung steht genau einmal: in :data:`BESTANDSAUSDRUCK`,
erzeugt aus :data:`ZUGANG`. Wer das Vorzeichen aendern will, aendert eine Menge
und nicht zwei Codestellen, die auseinanderlaufen konnen.

Grundlage: § 30 GenG (Mitgliederliste), § 73 GenG (Auseinandersetzung),
§ 337 HGB (Geschaeftsguthaben als Bilanzposition), GoBD Rz. 107 ff.
(Unveraenderbarkeit). Siehe
``docs/quality-assurance/genossenschaft-mitgliederregister-20261005.md``.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

MITGLIEDER = "domain_shared.genossenschaft_mitglieder"
BEWEGUNGEN = "domain_shared.genossenschaft_anteilsbewegungen"

#: Mitgliedsstaende. Deckungsgleich mit ``ck_geno_mitglied_status``.
STAENDE = ("AKTIV", "RUHEND", "AUSGETRETEN")

#: Bewegungen, die Anteile hinzufuegen.
ZUGANG = ("ZEICHNUNG", "ERHOEHUNG", "UEBERTRAGUNG_AN")

#: Bewegungen, die Anteile abziehen.
ABGANG = ("TEILRUECKZAHLUNG", "VOLLRUECKZAHLUNG", "UEBERTRAGUNG_AB")

BEWEGUNGSTYPEN = ZUGANG + ABGANG

#: Typen mit zwei Seiten: Ohne Gegenseite waere nicht nachvollziehbar, wohin die
#: Anteile gegangen sind.
UEBERTRAGUNGEN = ("UEBERTRAGUNG_AB", "UEBERTRAGUNG_AN")

#: Die Gegenbuchung einer Uebertragung — eine Seite erzwingt die andere.
GEGENTYP = {"UEBERTRAGUNG_AB": "UEBERTRAGUNG_AN", "UEBERTRAGUNG_AN": "UEBERTRAGUNG_AB"}

#: Das Vorzeichen je Typ, aus einer Menge erzeugt statt zweimal geschrieben.
VORZEICHEN = {typ: (1 if typ in ZUGANG else -1) for typ in BEWEGUNGSTYPEN}

_ZUGANG_SQL = ", ".join(f"'{typ}'" for typ in ZUGANG)

#: Der abgeleitete Anteilsbestand. Dieselbe Rechnung wie ``VORZEICHEN``, aus
#: derselben Menge erzeugt.
BESTANDSAUSDRUCK = (
    f"SUM(CASE WHEN b.bewegungstyp IN ({_ZUGANG_SQL}) "
    "THEN b.anzahl_anteile ELSE -b.anzahl_anteile END)"
)

MITGLIEDSFELDER = (
    "m.id, m.tenant_id, m.mitglieds_nr, m.name, m.adresse, m.eintrittsdatum, "
    "m.austrittsdatum, m.anteilswert_eur, m.status, m.iban, m.bank_name, m.created_at"
)

#: Mitglied samt abgeleitetem Bestand und Geschaeftsguthaben.
MITGLIEDER_MIT_BESTAND = f"""
    SELECT {MITGLIEDSFELDER},
           COALESCE({BESTANDSAUSDRUCK}, 0) AS genossenschaftsanteile,
           COALESCE({BESTANDSAUSDRUCK}, 0) * m.anteilswert_eur AS geschaeftsguthaben_eur
    FROM {MITGLIEDER} m
    LEFT JOIN {BEWEGUNGEN} b
           ON b.mitglieds_id = m.id AND b.tenant_id = m.tenant_id
    WHERE m.tenant_id = :tid
    GROUP BY m.id, m.tenant_id, m.mitglieds_nr, m.name, m.adresse, m.eintrittsdatum,
             m.austrittsdatum, m.anteilswert_eur, m.status, m.iban, m.bank_name, m.created_at
"""

MIGRATIONS_HINWEIS = {
    "X-Migration-Hint": "Run: alembic upgrade head (genossenschaft_mitgliederregister_20261005)"
}

ZEITFELDER = ("eintrittsdatum", "austrittsdatum", "datum", "created_at")
ZAHLFELDER = ("anteilswert_eur", "geschaeftsguthaben_eur", "wert_eur")


def als_dict(row: Any) -> dict:
    """Eine Datenbankzeile als Abbildung mit ISO-Datumsangaben."""
    d = dict(row)
    for schluessel in ZEITFELDER:
        wert = d.get(schluessel)
        if wert is not None and hasattr(wert, "isoformat"):
            d[schluessel] = wert.isoformat()
    for schluessel in ZAHLFELDER:
        if d.get(schluessel) is not None:
            d[schluessel] = float(d[schluessel])
    return d


def nicht_lesbar(db: Session, fehler: Exception, was: str, tenant_id: str) -> HTTPException:
    """Ein Lesefehler ist keine leere Mitgliederliste und kein Kapital von 0,00 EUR.

    § 30 GenG verpflichtet die eG zur Mitgliederliste, und das
    Geschaeftsguthaben ist eine Bilanzposition (§ 337 HGB). "Nichts gefunden"
    waere hier die Aussage, es gebe keine Mitglieder und kein Kapital.
    """
    db.rollback()
    logger.exception("%s nicht lesbar (Mandant %s)", was, tenant_id)
    return HTTPException(
        status_code=503,
        detail={"error": str(fehler), "migration_hint": MIGRATIONS_HINWEIS["X-Migration-Hint"]},
        headers=MIGRATIONS_HINWEIS,
    )


def naechste_mitglieds_nr(db: Session, tenant_id: str) -> str:
    """Die naechste freie Mitgliedsnummer des Mandanten.

    Gezaehlt wird die hoechste vergebene Nummer, nicht die Anzahl der Zeilen: Ein
    ausgetretenes Mitglied bleibt in der Liste, und eine Nummer wird nach § 30
    GenG nicht wiederverwendet. Ein Lesefehler wird **nicht** zu ``1``
    verschwiegen — das vergaebe eine Nummer, die es schon gibt.
    """
    jahr = db.execute(text("SELECT EXTRACT(YEAR FROM NOW())::int")).scalar()
    hoechste = db.execute(
        text(
            "SELECT MAX(SUBSTRING(mitglieds_nr FROM '[0-9]+$')::int) "
            f"FROM {MITGLIEDER} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE tenant_id = :tid AND mitglieds_nr ~ :muster"
        ),
        {"tid": tenant_id, "muster": f"^M-{jahr}-[0-9]+$"},
    ).scalar()
    return f"M-{jahr}-{(hoechste or 0) + 1:05d}"


def mitglied_sperren(db: Session, tenant_id: str, mitglied_id: str) -> dict:
    """Das Mitglied holen und die Zeile sperren.

    ``FOR UPDATE`` serialisiert gleichzeitige Bewegungen auf demselben Mitglied.
    Ohne die Sperre koennten zwei Rueckzahlungen denselben Bestand sehen und
    gemeinsam mehr abziehen, als da ist.
    """
    zeile = db.execute(
        text(
            "SELECT id, mitglieds_nr, name, status, anteilswert_eur "
            f"FROM {MITGLIEDER} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE id = :id AND tenant_id = :tid FOR UPDATE"
        ),
        {"id": mitglied_id, "tid": tenant_id},
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail="Mitglied nicht gefunden")
    return dict(zeile)


def bestand(db: Session, tenant_id: str, mitglied_id: str) -> int:
    """Der abgeleitete Anteilsbestand eines Mitglieds."""
    wert = db.execute(
        text(
            f"SELECT COALESCE({BESTANDSAUSDRUCK}, 0) "  # nosec B608  # reviewed-safe: BESTANDSAUSDRUCK ist aus Code-Literalen erzeugt, Werte sind gebunden
            f"FROM {BEWEGUNGEN} b WHERE b.mitglieds_id = :id AND b.tenant_id = :tid"
        ),
        {"id": mitglied_id, "tid": tenant_id},
    ).scalar()
    return int(wert or 0)


def bewegungen(db: Session, tenant_id: str, mitglied_id: str, limit: int = 500) -> list[dict]:
    """Die Bewegungen eines Mitglieds, neueste zuerst."""
    zeilen = db.execute(
        text(
            "SELECT id, bewegungstyp, anzahl_anteile, wert_eur, datum, bemerkung, "
            "gegen_mitglieds_id, journal_entry_id, erfasst_durch, created_at "
            f"FROM {BEWEGUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "WHERE mitglieds_id = :id AND tenant_id = :tid "
            "ORDER BY datum DESC, created_at DESC LIMIT :limit"
        ),
        {"id": mitglied_id, "tid": tenant_id, "limit": limit},
    ).mappings().all()
    return [als_dict(z) for z in zeilen]


def abgang_pruefen(typ: str, anzahl: int, verfuegbar: int, mitglieds_nr: str) -> None:
    """Ein Abgang darf den Bestand nicht unterschreiten.

    § 7 GenG kennt keinen negativen Geschaeftsanteil. Und eine
    ``VOLLRUECKZAHLUNG``, die nicht den ganzen Bestand trifft, ist keine — sie
    liesse einen Rest stehen und hiesse trotzdem "voll".
    """
    if typ not in ABGANG:
        return
    if anzahl > verfuegbar:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Mitglied {mitglieds_nr} haelt {verfuegbar} Anteile. "
                f"{anzahl} Anteile abzuziehen wuerde den Bestand unterschreiten."
            ),
        )
    if typ == "VOLLRUECKZAHLUNG" and anzahl != verfuegbar:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Vollrueckzahlung muss den ganzen Bestand treffen: Mitglied "
                f"{mitglieds_nr} haelt {verfuegbar} Anteile, angegeben sind {anzahl}. "
                "Fuer einen Teil ist TEILRUECKZAHLUNG der richtige Typ."
            ),
        )


def bewegung_schreiben(
    db: Session,
    tenant_id: str,
    bewegung_id: str,
    mitglied_id: str,
    typ: str,
    anzahl: int,
    wert_eur: float,
    datum: Any,
    bemerkung: str | None = None,
    gegen_mitglieds_id: str | None = None,
    journal_entry_id: str | None = None,
    erfasst_durch: str | None = None,
) -> None:
    """Eine Anteilsbewegung festschreiben. Der Bestand folgt daraus, nicht umgekehrt."""
    db.execute(
        text(
            f"INSERT INTO {BEWEGUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, mitglieds_id, bewegungstyp, anzahl_anteile, wert_eur, "
            " datum, bemerkung, gegen_mitglieds_id, journal_entry_id, erfasst_durch) "
            "VALUES (:id, :tid, :mid, :typ, :anzahl, :wert, :datum, :bemerkung, "
            "        :gegen, :journal, :durch)"
        ),
        {
            "id": bewegung_id,
            "tid": tenant_id,
            "mid": mitglied_id,
            "typ": typ,
            "anzahl": anzahl,
            "wert": wert_eur,
            "datum": datum,
            "bemerkung": bemerkung,
            "gegen": gegen_mitglieds_id,
            "journal": journal_entry_id,
            "durch": erfasst_durch,
        },
    )
