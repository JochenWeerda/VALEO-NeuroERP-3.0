"""Validierung von SQL-Bezeichnern, die als Text in Statements landen.

Parametrisierung (``:name``) deckt nur **Werte** ab. Tabellen-, Schema- und
Spaltennamen muessen als Text in das SQL, weshalb jede Quelle ausserhalb des
Codes — Umgebungsvariablen, Konfigurationsdateien, Deployment-Overrides — vor
der Interpolation geprueft werden muss.

Verwendung an genau den Stellen, an denen der Bezeichner *nicht* aus einer
Modulkonstante oder einer Allowlist stammt::

    SALES_TABLE = qualifizierter_bezeichner(
        os.getenv("SALES_TABLE", "domain_portal.customer_orders"), "SALES_TABLE"
    )
"""
from __future__ import annotations

import re

# Postgres-Bezeichner ohne Quoting: Buchstabe/Unterstrich, dann alphanumerisch.
_BEZEICHNER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_MAX_LAENGE = 63  # NAMEDATALEN - 1


class UngueltigerBezeichnerError(ValueError):
    """Ein als SQL-Bezeichner vorgesehener Wert ist nicht sicher verwendbar."""


def bezeichner(wert: str, quelle: str) -> str:
    """Prueft einen einteiligen Bezeichner (Spalte, Tabelle ohne Schema).

    Args:
        wert: der zu pruefende Bezeichner.
        quelle: Name der Konfiguration/Variablen — erscheint in der Fehlermeldung.

    Raises:
        UngueltigerBezeichnerError: bei leerem, zu langem oder nicht rein
            alphanumerischem Wert.
    """
    if not isinstance(wert, str) or not wert:
        raise UngueltigerBezeichnerError(f"{quelle}: leerer SQL-Bezeichner")
    if len(wert) > _MAX_LAENGE:
        raise UngueltigerBezeichnerError(
            f"{quelle}: SQL-Bezeichner laenger als {_MAX_LAENGE} Zeichen"
        )
    if not _BEZEICHNER.match(wert):
        raise UngueltigerBezeichnerError(
            f"{quelle}: ungueltiger SQL-Bezeichner {wert!r} — erlaubt sind "
            "Buchstaben, Ziffern und Unterstrich, beginnend mit Buchstabe/Unterstrich"
        )
    return wert


def qualifizierter_bezeichner(wert: str, quelle: str) -> str:
    """Prueft ``tabelle`` oder ``schema.tabelle``; gibt den Wert unveraendert zurueck."""
    if not isinstance(wert, str) or not wert:
        raise UngueltigerBezeichnerError(f"{quelle}: leerer SQL-Bezeichner")
    teile = wert.split(".")
    if len(teile) > 2:
        raise UngueltigerBezeichnerError(
            f"{quelle}: {wert!r} hat mehr als zwei Bezeichnerteile"
        )
    for teil in teile:
        bezeichner(teil, quelle)
    return wert
