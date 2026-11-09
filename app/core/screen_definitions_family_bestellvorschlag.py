"""Maskenfamilie ``bestellvorschlag`` (09.11.2026): eine Liste, je Rechenweg eine Variante, dazu die gespeicherten.

Lager (Meldebestand), Verkauf (Abverkauf), Rohware (Kontrakte), Bedarf (Bestand gegen tatsaechlichen Abverkauf,
mit Lager- und Frachtkosten) und Gespeichert. Die Rechenwege teilen ihre Spalten; je Variante wechseln Quelle,
Zusatzspalten und Aktion. "Als Vorschlag speichern" rechnet auf dem Server neu; "Zu Bestellung" legt je
Lieferant einen DocFlow-Bestellentwurf an. Ersetzt die Seiten bestellvorschlag-rohware/-verkauf (ohne Maske) und
die Cockpit-Platzhalter bestellvorschlag-kontrakt/-lager/-verbrauch sowie die Platzhalterliste bestellvorschlaege-liste.
"""
from __future__ import annotations

from typing import Any

from app.core.cluster_spalten import betrag, datum, menge, status, zahl
from app.core.cluster_spalten import text as textspalte  # nicht sqlalchemy.text (Pruefung SQL-f-Strings)
from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_export_action

FAMILIE = "bestellvorschlag"
_WEG = "/api/v1/einkauf/bestellvorschlaege"

_TITEL = {"lager": "Bestellvorschlag Lager", "verkauf": "Bestellvorschlag Verkauf",
          "rohware": "Bestellvorschlag Rohware", "bedarf": "Bestellvorschlag Bedarf",
          "gespeichert": "Gespeicherte Bestellvorschläge"}
_UNTERTITEL = {"lager": "Artikel unter Meldebestand mit Vorschlagsmenge",
               "verkauf": "Vorschlag aus dem Abverkauf des Zeitraums",
               "rohware": "Rohware aus offenen Kontrakten",
               "bedarf": "Bestand gegen tatsächlichen Abverkauf, mit Lager- und Frachtkosten",
               "gespeichert": "Gespeicherte Vorschläge und ihr Stand"}


def _m(key: str, label: str, prioritaet: str = "primary", summe: bool = False) -> dict[str, Any]:
    return menge(key, label, einheit_feld="einheit", prioritaet=prioritaet, summe=summe)


_GRUND = [textspalte("artikel_nr", "Artikel", "primary"), textspalte("artikel_bezeichnung", "Bezeichnung", "primary"),
          textspalte("artikel_gruppe", "Gruppe", "tertiary"), _m("ist_bestand", "Bestand"),
          _m("offene_auftraege", "Offene Aufträge", "secondary"), _m("bedarf", "Bedarf", "secondary"),
          _m("vorschlag_menge", "Vorschlag", summe=True), zahl("reichweite_tage", "Reichweite (Tage)"),
          textspalte("lieferant_name", "Lieferant", "secondary"),
          betrag("letzter_preis", "Letzter Preis", summe=False, prioritaet="secondary"),
          textspalte("preis_einheit", "je", "tertiary"), zahl("wiederbeschaffungs_tage", "WBZ (Tage)", "tertiary")]

_ZUSATZ = {
    "lager": [_m("meldebestand", "Meldebestand", "secondary"), _m("mindestbestand", "Mindestbestand", "tertiary")],
    "verkauf": [_m("mindestbestand", "Mindestbestand", "tertiary")],
    "rohware": [_m("mindestbestand", "Mindestbestand", "tertiary")],
    "bedarf": [_m("abverkauf_menge", "Abverkauf", "secondary"), zahl("abverkauf_pro_tag", "je Tag", "tertiary"),
               betrag("lagerkosten", "Lagerkosten", summe=True, prioritaet="tertiary"),
               betrag("frachtkosten", "Frachtkosten", summe=True, prioritaet="tertiary"),
               textspalte("begruendung", "Begründung", "secondary")],
}


def _ansichten(aktuell: str) -> list[dict[str, Any]]:
    return [{"key": f"ansicht_{v}", "label": titel, "kind": "secondary", "dangerLevel": "safe", "zone": "header",
             "navigationRoute": f"/einkauf/bestellvorschlaege/ansicht/{v}", "localEffect": "navigation",
             "stubReason": f"Wechselt zur Variante {titel}."}
            for v, titel in _TITEL.items() if v != aktuell]


def _variante(art: str) -> dict[str, Any]:
    if art == "gespeichert":
        endpoint, row_route = _WEG, None
        spalten = [textspalte("bezeichnung", "Bezeichnung", "primary"), status("vorschlag_typ", "Art"),
                   datum("datum", "Datum", "primary"), status(), zahl("positionen_anz", "Positionen"),
                   textspalte("erstellt_von", "Erstellt von", "tertiary")]
        aktionen = [stamm_list_export_action()]
        zeilen = [{"key": "zu_bestellung", "label": "Zu Bestellung", "dangerLevel": "moderate",
                   "permission": "einkauf.bestellung.create", "commandEndpoint": _WEG + "/{entity_id}/actions/zu_bestellung",
                   "method": "POST", "requiresConfirmation": True,
                   "visibleWhen": {"field": "status", "values": ["entwurf", "offen", "neu", "draft"]}}]
    else:
        endpoint, row_route = f"{_WEG}/{art}", None
        spalten = [*_GRUND, *_ZUSATZ[art]]
        aktionen = [{"key": "speichern", "label": "Als Vorschlag speichern", "kind": "primary", "zone": "header",
                     "dangerLevel": "low", "permission": "einkauf.bestellvorschlag.create",
                     "commandEndpoint": f"{_WEG}/berechnung/{art}/actions/speichern", "method": "POST",
                     "requiresConfirmation": False,
                     "inputFields": [{"key": "bezeichnung", "label": "Bezeichnung", "type": "text"}]},
                    stamm_list_export_action()]
        zeilen = []
    definition = build_stamm_list_screen(
        screen_id=f"{FAMILIE}/{art}", domain="einkauf", bundle="einkauf", title=_TITEL[art],
        subtitle=_UNTERTITEL[art], endpoint=endpoint, row_route=row_route, columns=spalten,
        actions=[*aktionen, *_ansichten(art)], row_actions=zeilen, table_profile="inventory", fetch_limit=500,
        purpose=f"{_TITEL[art]}: pruefen, was zu bestellen ist, und den Vorschlag in eine Bestellung ueberfuehren.",
        prompts=["Welche Artikel liegen unter Meldebestand?", "Speichere den Bestellvorschlag Lager."],
        no_workflow="Vorschlagsliste; die Bestellung entsteht als DocFlow-Entwurf und laeuft in der Belegmaske weiter.")
    definition["variant"] = {"family": FAMILIE, "id": art}
    return definition


def bestellvorschlag_varianten() -> dict[str, dict[str, Any]]:
    return {art: _variante(art) for art in _TITEL}


FAMILIEN_BUILDER = {FAMILIE: bestellvorschlag_varianten}
