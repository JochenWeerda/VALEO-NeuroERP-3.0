"""Der Zustand einer Buchungsperiode — ein Woerterbuch, eine Pruefung.

Bis zum 01.10.2026 standen drei Vokabulare in derselben Spalte
``public.finance_accounting_periods.status``: Die Verwaltungsmaske prueft
``OPEN|CLOSED|ADJUSTING``, ``close_period`` schrieb ``closed``,
``reopen_period`` schrieb ``offen``. Sieben Buchungswege verglichen jeder fuer
sich ``status != "OPEN"``.

Die Folge war nicht theoretisch: Eine Wiedereroeffnung verlangte einen Grund,
protokollierte ihn — und setzte ``offen``. Die Waechter lasen ``offen != OPEN``
und sperrten weiter. Die dokumentierte Wiedereroeffnung existierte nur auf dem
Papier. Und ``ADJUSTING`` sperrte wie ``CLOSED``, war also bedeutungslos.

**GoBD.** Unveraenderbarkeit (Rz. 107 ff.) verlangt, dass eine abgeschlossene
Periode nicht mehr bebucht werden kann. Nachvollziehbarkeit (Rz. 30 ff.)
verlangt, dass der Zustand einer Periode eindeutig feststellbar ist. Beides
braucht **ein** Woerterbuch und **eine** Stelle, die es anwendet. Diese hier.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import text

#: Die Periode ist offen. Buchen erlaubt.
OFFEN = "OPEN"

#: Die Periode ist abgeschlossen. Buchen gesperrt — das ist die
#: Unveraenderbarkeit, die GoBD verlangt.
GESCHLOSSEN = "CLOSED"

#: Die Periode ist nur noch fuer Abschlussbuchungen offen. Buchen **erlaubt**:
#: Ein Zustand, in den niemand buchen kann, waere gleichbedeutend mit
#: ``CLOSED`` und damit wertlos. Wer die Periode gegen jede Buchung sperren
#: will, schliesst sie.
ABSCHLUSSBUCHUNGEN = "ADJUSTING"

#: Die zulaessigen Zustaende. Die Datenbank haelt diese Menge als
#: Pruefbedingung (``periode_statuswoerterbuch_20261001``).
ZUSTAENDE: tuple[str, ...] = (OFFEN, GESCHLOSSEN, ABSCHLUSSBUCHUNGEN)

#: Zustaende, in denen **nicht** gebucht werden darf.
SPERRT: frozenset[str] = frozenset({GESCHLOSSEN})

TABELLE = "public.finance_accounting_periods"

#: Alte Schreibweisen, die vor dem 01.10.2026 geschrieben wurden. Die Migration
#: normalisiert den Bestand; diese Abbildung faengt zusaetzlich alles ab, was
#: aus einem Altdatenbestand oder einer Fremdschnittstelle nachkommt.
_ALTE_SCHREIBWEISEN = {
    "closed": GESCHLOSSEN,
    "geschlossen": GESCHLOSSEN,
    "gesperrt": GESCHLOSSEN,
    "offen": OFFEN,
    "open": OFFEN,
    "adjusting": ABSCHLUSSBUCHUNGEN,
    "anpassung": ABSCHLUSSBUCHUNGEN,
}


def normalisiere(status: Any) -> Optional[str]:
    """Bildet einen gelesenen Zustand auf das Woerterbuch ab.

    Unbekannte Werte werden **nicht** stillschweigend zu ``OPEN``: Sie kommen
    unveraendert zurueck, damit der Aufrufer sie als Sperre behandeln kann. Ein
    Zustand, den niemand kennt, ist kein Freibrief zum Buchen.
    """
    if status is None:
        return None
    roh = str(status).strip()
    if roh in ZUSTAENDE:
        return roh
    return _ALTE_SCHREIBWEISEN.get(roh.lower(), roh)


def sperrt(status: Any) -> bool:
    """Ob in diesem Zustand gebucht werden darf.

    Unbekannte Zustaende sperren. Lieber eine abgewiesene Buchung als eine
    Buchung in eine Periode, deren Zustand niemand benennen kann.
    """
    zustand = normalisiere(status)
    if zustand is None:
        return False
    return zustand not in (OFFEN, ABSCHLUSSBUCHUNGEN)


def gesperrter_zustand(db: Any, tenant_id: str, period: str) -> Optional[str]:
    """Gibt den sperrenden Zustand der Periode zurueck, sonst ``None``.

    ``None`` heisst: buchen erlaubt. Das gilt auch, wenn es **keine** Zeile zur
    Periode gibt — Perioden werden erst beim ersten Abschluss angelegt, und eine
    nie angelegte Periode ist nicht abgeschlossen. Ein Fehler beim Lesen wird
    **nicht** gefangen: Wer nicht sagen kann, ob eine Periode offen ist, darf
    nicht buchen lassen.
    """
    zeile = db.execute(
        text(
            f"SELECT status FROM {TABELLE} "  # nosec B608  # reviewed-safe: TABELLE ist ein Code-Literal
            "WHERE tenant_id = :tenant_id AND period = :period LIMIT 1"
        ),
        {"tenant_id": tenant_id, "period": period},
    ).fetchone()
    if not zeile:
        return None
    if sperrt(zeile[0]):
        return normalisiere(zeile[0])
    return None


def meldung(period: str, zustand: str) -> str:
    """Der Wortlaut, mit dem eine gesperrte Periode abgewiesen wird."""
    return f"Periode {period} ist {zustand}. Buchung gesperrt."
