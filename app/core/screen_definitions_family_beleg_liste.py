"""Maskenfamilie ``beleg-liste``: eine Belegliste, eine Variante je Belegart (08.11.2026).

Gegenstueck zur Belegmaske (``beleg/*``): Die Liste liest DocFlow, den einzigen Belegspeicher (Nutzerentscheidung
BELEG-052), ueber ``GET /api/v1/belege/{belegart}``. Je Variante wechseln Titel, Quelle, Betragsspalten (nur bei
Belegen mit Preisen), Buchungsdatum (nur bei buchenden Belegen), Zeilenziel und Neuanlage. Freigeben, Umwandeln,
Buchen und Stornieren laufen in der Belegmaske je Beleg, mit dem Stand, den der Server dort liefert.
"""
from __future__ import annotations

from typing import Any

from app.core.belegvertrag import BELEGARTEN
from app.core.cluster_spalten import betrag, datum, status
from app.core.cluster_spalten import text as textspalte  # nicht sqlalchemy.text (Pruefung SQL-f-Strings)
from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_export_action, stamm_list_neu_action

FAMILIE = "beleg-liste"

_MEHRZAHL = {
    "sales_offer": "Angebote", "sales_order": "Aufträge", "sales_delivery": "Lieferscheine",
    "sales_invoice": "Ausgangsrechnungen", "sales_credit_memo": "Gutschriften",
    "purchase_order": "Bestellungen", "goods_receipt": "Wareneingänge", "purchase_invoice": "Eingangsrechnungen",
    "purchase_credit_memo": "Einkaufsgutschriften",
}


def _ansichten(belegart: str) -> list[dict[str, Any]]:
    """Wechsel zu den anderen Belegarten derselben Richtung (Verkauf bzw. Einkauf)."""
    richtung = BELEGARTEN[belegart].richtung
    return [{"key": f"ansicht_{art}", "label": _MEHRZAHL[art], "kind": "secondary", "dangerLevel": "safe",
             "zone": "header", "navigationRoute": f"/belege/{art}", "localEffect": "navigation",
             "stubReason": f"Wechselt zur Belegliste {_MEHRZAHL[art]}."}
            for art, v in BELEGARTEN.items() if v.richtung == richtung and art != belegart]


def _spalten(belegart: str) -> list[dict[str, Any]]:
    variante = BELEGARTEN[belegart]
    partner = "Lieferant" if variante.partnerrolle == "lieferant" else "Kunde"
    spalten = [textspalte("beleg_nr", "Beleg-Nr.", "primary"), datum("belegdatum", "Belegdatum", "primary"),
               textspalte("partner_name", partner, "primary"), textspalte("partner_nummer", f"{partner}-Nr.", "secondary"),
               status()]
    if variante.mit_preisen:
        spalten += [betrag("netto", "Netto", currencyField="waehrung", prioritaet="secondary"),
                    betrag("steuer", "Steuer", currencyField="waehrung", prioritaet="tertiary"),
                    betrag("brutto", "Brutto", currencyField="waehrung")]
    if variante.bucht:
        spalten.append(datum("buchungsdatum", "Buchungsdatum", "tertiary"))
    spalten.append(textspalte("referenz", "Referenz", "tertiary"))
    return spalten


_STATUS = [("draft", "Entwurf"), ("open", "Offen"), ("released", "Freigegeben"), ("posted", "Gebucht"),
           ("reversed", "Storniert (Gegenbuchung)"), ("cancelled", "Storniert")]

_ROLLEN = {
    "verkauf": [("sales", "Vertrieb", ["stand"]), ("inside-sales", "Innendienst", ["stand"]),
                ("order-desk", "Auftragsabwicklung", ["stand"]), ("finance", "Finance", ["leitung"]),
                ("management", "Leitung", ["leitung"])],
    "einkauf": [("purchasing", "Einkauf", ["stand"]), ("warehouse", "Lager", ["stand"]),
                ("finance", "Finance", ["leitung"]), ("management", "Leitung", ["leitung"])],
}

# Druck der sichtbaren Liste (lokale Wirkung, wie bei den abgeloesten Listen).
_DRUCKEN = {"key": "print", "label": "Drucken", "dangerLevel": "safe", "zone": "header", "localEffect": "print"}


def _listenerlebnis(belegart: str, spalten: list[dict[str, Any]]) -> dict[str, Any]:
    """Suche, Statusfilter, Kennzahlen, Export und Rollenfokus wie die abgeloesten Listen, mit DocFlow-Status."""
    variante = BELEGARTEN[belegart]
    mehrzahl = _MEHRZAHL[belegart]
    return {
        "searchFields": ["beleg_nr", "partner_name", "partner_nummer", "referenz"],
        "presets": [{"key": "status", "label": "Belegstatus", "field": "status", "kind": "choice",
                     "options": [{"value": "all", "label": "Alle Status"},
                                 *({"value": wert, "label": text_} for wert, text_ in _STATUS)]}],
        "aggregates": [{"key": "total", "label": mehrzahl, "conditions": []},
                       {"key": "draft", "label": "Entwürfe", "conditions": [{"field": "status", "op": "eq",
                                                                              "value": "draft"}]}],
        "export": {"filenamePrefix": f"{mehrzahl}_", "delimiter": ";",
                   "columns": [{"key": c["key"], "label": c["label"]} for c in spalten]},
        "insightLines": [{"key": "stand", "label": "Stand",
                          "variants": [{"text": f"{{total}} {mehrzahl} in der aktuellen Sicht, davon {{draft}} Entwürfe."}]},
                         {"key": "leitung", "label": "Leitung",
                          "variants": [{"text": f"{{total}} {mehrzahl} in der aktuellen Sicht."}]}],
        "roleFocus": {"defaultKey": "all", "options": [
            {"key": "all", "label": "Alle Rollen"},
            *({"key": k, "label": label, "insightLineKeys": zeilen} for k, label, zeilen in _ROLLEN[variante.richtung])]},
    }


def _variante(belegart: str) -> dict[str, Any]:
    variante = BELEGARTEN[belegart]
    mehrzahl = _MEHRZAHL[belegart]
    profil = "financial" if variante.mit_preisen else "inventory"
    definition = build_stamm_list_screen(
        screen_id=f"{FAMILIE}/{belegart.replace('_', '-')}",
        domain="sales" if variante.richtung == "verkauf" else "einkauf",
        bundle="belege", title=mehrzahl,
        subtitle=f"{mehrzahl} aus DocFlow mit Stand" + (" und Beträgen" if variante.mit_preisen else ""),
        endpoint=f"/api/v1/belege/{belegart}", row_route=f"/belege/{belegart}/{{id}}", columns=_spalten(belegart),
        actions=[stamm_list_neu_action(f"{variante.bezeichnung} anlegen", f"/belege/{belegart}/neu"),
                 stamm_list_export_action(), _DRUCKEN, *_ansichten(belegart)],
        row_actions=[], table_profile=profil, fetch_limit=500,
        purpose=f"{mehrzahl} finden, ihren Stand pruefen und den Beleg oeffnen.",
        prompts=[f"Welche {mehrzahl} sind noch im Entwurf?", f"Zeige die {mehrzahl} von heute."],
        no_workflow="Belegliste; Freigeben, Umwandeln, Buchen und Stornieren laufen in der Belegmaske je Beleg.",
    )
    definition["listExperience"] = _listenerlebnis(belegart, _spalten(belegart))
    definition["variant"] = {"family": FAMILIE, "id": belegart}
    return definition


def beleg_liste_varianten() -> dict[str, dict[str, Any]]:
    return {art: _variante(art) for art in BELEGARTEN}


FAMILIEN_BUILDER = {FAMILIE: beleg_liste_varianten}
