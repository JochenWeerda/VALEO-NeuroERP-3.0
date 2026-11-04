"""Studio-Listen Futtermittel/Produktion aus vorhandenen Lesewegen (Masken-Cluster Batch 3, 03.11.2026).

Vorher batch15-Platzhalter auf ``/futtermittel/qs/haccp-plaene`` bzw. ``/futter/chargen`` mit
id/name/status/updated_at. Mengen liefert das Backend in t (``verfuegbar_t``, ``menge_t``); angezeigt wird in dt,
der Handelsgroesse des Landhandels (agrar_units).
"""
from __future__ import annotations

from typing import Any

from app.core.cluster_spalten import betrag, datum, janein, menge, status, text, zahl
from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_export_action, stamm_list_neu_action

_EXPORT = stamm_list_export_action()


def build_futter_einzel_liste() -> dict[str, Any]:
    return build_stamm_list_screen(
        screen_id="futter/einzel/liste", domain="futtermittel", bundle="futtermittel", table_profile="inventory",
        title="Einzelfuttermittel", subtitle="Einzelfuttermittel mit Naehrstoffen, Zertifikaten und Bestand",
        endpoint="/api/v1/futter/einzelfuttermittel", row_route="/futter/einzel/{id}",
        columns=[text("artikel_nummer", "Artikelnr.", "primary"), text("name", "Bezeichnung", "primary"),
                 text("art", "Art"), text("lieferant", "Lieferant"),
                 zahl("protein", "Rohprotein %"), zahl("energie", "Energie"), zahl("trockensubstanz", "TS %", "tertiary"),
                 janein("qs_milch", "QS-Milch"), janein("gmp_plus", "GMP+"), janein("bio_zertifiziert", "Bio"),
                 menge("verfuegbar_t", "Verfügbar", einheit="t", anzeige="dt", summe=True),
                 betrag("preis_pro_t", "Preis je dt", summe=False, prioritaet="secondary", je="t", anzeige_je="dt"), janein("aktiv", "Aktiv")],
        actions=[stamm_list_neu_action("Neues Einzelfuttermittel", "/futter/einzel/neu"), _EXPORT], row_actions=[],
        purpose="Einzelfuttermittel nach Naehrstoff, Zertifikat und verfuegbarer Menge finden.",
        prompts=["Welche Einzelfuttermittel sind GMP+-zertifiziert?", "Wie viel Sojaschrot ist verfuegbar?"],
        no_workflow="Stammdatenliste ohne eigenen Ablauf; Pflege in der Objektmaske.",
    )


def build_produktion_mischfutter_produktion() -> dict[str, Any]:
    return build_stamm_list_screen(
        screen_id="produktion/mischfutter-produktion", domain="futtermittel", bundle="produktion",
        table_profile="inventory",
        title="Mischfutter-Produktion", subtitle="Produktionsauftraege mit Rezept, Menge, Charge und Bestandsabzug",
        endpoint="/api/v1/produktion/mischfutter/auftraege", row_route=None,
        columns=[text("rezept_name", "Rezept", "primary"), menge("menge_t", "Menge", einheit="t", anzeige="dt", summe=True),
                 status(), text("charge_id", "Charge"), janein("bestands_abzug_erfolgt", "Bestand abgebucht"),
                 text("fibu_journal_ref", "FiBu-Buchung", "tertiary"), datum("created_at", "Angelegt")],
        actions=[_EXPORT], row_actions=[],
        purpose="Produktionsauftraege verfolgen: Was ist produziert, abgebucht und gebucht?",
        prompts=["Welche Auftraege sind noch nicht vom Bestand abgebucht?", "Wie viel Milchviehfutter lief diese Woche?"],
        no_workflow="Auswertungsliste; Freigabe und Abschluss im Produktionsleitstand.",
    )


CLUSTER_FUTTER_SCREEN_BUILDERS: dict[str, Any] = {
    "futter/einzel/liste": build_futter_einzel_liste,
    "produktion/mischfutter-produktion": build_produktion_mischfutter_produktion,
}
