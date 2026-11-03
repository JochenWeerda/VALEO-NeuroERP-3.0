"""Spaltenbausteine der Masken-Cluster: eine Schreibweise fuer Text, Betrag, Menge, Datum, Ja/Nein und Status.

Die Darstellung (Waehrung, Einheit, Summenzeile, rechnende Spalten) kommt aus den Feldklassen des Mask Builders;
hier wird nur deklariert, welche Klasse eine Spalte hat.
"""
from __future__ import annotations

from typing import Any


def text(key: str, label: str, prioritaet: str = "secondary", **zusatz: Any) -> dict[str, Any]:
    return {"key": key, "label": label, "sortable": True, "filterable": True, "priority": prioritaet, **zusatz}


def betrag(key: str, label: str, summe: bool = True, prioritaet: str = "primary", **zusatz: Any) -> dict[str, Any]:
    spalte = {"key": key, "label": label, "renderKind": "currency", "numeric": True, "sortable": True,
              "priority": prioritaet, **zusatz}
    return {**spalte, "aggregate": "sum"} if summe else spalte


def menge(key: str, label: str, *, einheit: str | None = None, einheit_feld: str | None = None, summe: bool = False,
          anzeige: str | None = None, prioritaet: str = "primary") -> dict[str, Any]:
    """Menge mit Einheit. ``anzeige`` rechnet Masse/Volumen exakt um (Landhandel: Masse in dt, nicht t); die
    Summenzeile rechnet gemischte Masse/Volumen um und summiert Zaehleinheiten nie mit kg."""
    spalte: dict[str, Any] = {"key": key, "label": label, "renderKind": "quantity", "numeric": True, "sortable": True,
                              "priority": prioritaet}
    if einheit:
        spalte["unit"] = einheit
    if einheit_feld:
        spalte["unitField"] = einheit_feld
    if anzeige:
        spalte["displayUnit"] = anzeige
    return {**spalte, "aggregate": "sum"} if summe else spalte


def zahl(key: str, label: str, prioritaet: str = "secondary") -> dict[str, Any]:
    return {"key": key, "label": label, "renderKind": "number", "numeric": True, "sortable": True, "priority": prioritaet}


def datum(key: str, label: str, prioritaet: str = "secondary") -> dict[str, Any]:
    return {"key": key, "label": label, "renderKind": "date", "sortable": True, "priority": prioritaet}


def janein(key: str, label: str, prioritaet: str = "secondary") -> dict[str, Any]:
    return {"key": key, "label": label, "renderKind": "boolean", "filterable": True, "priority": prioritaet}


def status(key: str = "status", label: str = "Status") -> dict[str, Any]:
    return {**text(key, label, "primary"), "renderKind": "status"}
