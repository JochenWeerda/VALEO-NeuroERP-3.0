"""Eingabefelder der Stamm-Kommandos (Vertreterprovisionen, Nummernkreise) - eine Quelle fuer Maske und Fachweg.

Bewusst ohne Abhaengigkeiten: Die ScreenDefinitions lesen diese Felder auch in schlanken Umgebungen (Doku-Bau,
Agenten-Handbuch), in denen das Schema-Paket der API nicht importierbar ist.
"""
from __future__ import annotations

from typing import Any


def _auswahl(werte: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [{"value": w, "label": t} for w, t in werte]


RICHTUNGEN = [("vk", "Verkauf"), ("ek", "Einkauf")]
PROVISIONSTYPEN = [("fix", "Fester Satz"), ("staffel_optpreis", "Staffel nach OPT-Preis"),
                   ("staffel_preis_zuab", "Staffel nach Preis + Zu-/Abschlägen")]
PROVISION_GRUPPE_FELDER: list[dict[str, Any]] = [
    {"key": "gruppe_nr", "label": "Gruppe", "type": "text", "required": True},
    {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
    {"key": "richtung", "label": "Richtung", "type": "select", "required": True, "options": _auswahl(RICHTUNGEN)},
    {"key": "provisionstyp", "label": "Provisionstyp", "type": "select", "required": True,
     "options": _auswahl(PROVISIONSTYPEN)},
    {"key": "provisionssatz", "label": "Provisionssatz %", "type": "number"},
]
PROVISION_STAFFEL_FELDER: list[dict[str, Any]] = [
    {"key": "vertreterklasse", "label": "Vertreterklasse", "type": "text"},
    {"key": "ab_wert", "label": "Ab Wert (EUR)", "type": "number", "required": True},
    {"key": "provisionssatz", "label": "Provisionssatz %", "type": "number", "required": True},
]

KREISARTEN = [("debtor_account", "Debitorenkonto"), ("creditor_account", "Kreditorenkonto"),
              ("partner_number", "Partnernummer")]
NUMMERNKREIS_FORMAT_FELDER: list[dict[str, Any]] = [
    {"key": "prefix", "label": "Präfix", "type": "text"},
    {"key": "start_number", "label": "Startnummer", "type": "number", "required": True},
    {"key": "digit_count", "label": "Stellen", "type": "number", "required": True},
    {"key": "reserved_prefix_digits", "label": "Reservierte Präfixstellen", "type": "number"},
]
NUMMERNKREIS_KONFIGURIEREN_FELDER: list[dict[str, Any]] = [
    {"key": "range_type", "label": "Nummernkreis", "type": "select", "required": True,
     "options": _auswahl(KREISARTEN)},
    *NUMMERNKREIS_FORMAT_FELDER,
]
