"""Studio-Objektmasken fuer Stammdaten (MASKEN-STUDIO-ROLLOUT, Stammdatenwelle 20.10.2026).

Ersetzt handgebaute Stammdatenseiten durch ScreenDefinitions ueber die Builder-Kette (``UniversalNativeDetailPage``,
Anlage ueber ``creation``). Jede Aenderung laeuft ueber einen Kommandoweg ``.../actions/bearbeiten``
(``app/api/v1/endpoints/stammdaten_bearbeiten.py``), der an den bestehenden Fachweg delegiert.
"""
from __future__ import annotations

from typing import Any

from app.core.stamm_object_page_parent import (
    build_stamm_object_page,
    stamm_entity_source,
    stamm_entity_tab,
    stamm_kopf_tab,
    stamm_lazy_table_tab,
    stamm_tab_source,
)


def _feld(key: str, label: str, typ: str = "text", **mehr: Any) -> dict[str, Any]:
    return {"key": key, "label": label, "type": typ, **mehr}


def _register(key: str, label: str, quelle: str, spalten: list[dict[str, Any]]) -> dict[str, Any]:
    return stamm_lazy_table_tab(
        key=key,
        label=label,
        data_source_key=quelle,
        columns=spalten,
        server_pagination=False,
    )


# Felder des Artikelstamms (``ArticleBase``), gruppiert wie die bisherige Maske.
_ARTIKEL_STAMM = [
    _feld("article_number", "Artikel-Nr.", required=True),
    _feld("name", "Bezeichnung", required=True),
    _feld("short_description", "Kurzbezeichnung"),
    _feld("description", "Beschreibung", "textarea"),
    _feld("suchbegriff", "Suchbegriff"),
    _feld("warengruppe", "Warengruppe"),
    _feld("category", "Kategorie", required=True),
    _feld("subcategory", "Unterkategorie"),
    _feld("unit", "Einheit", required=True, width=80),
    _feld("hersteller", "Hersteller"),
    _feld("herkunftsland", "Herkunftsland (ISO)", width=80),
    _feld("ean_code", "EAN"),
    _feld("lieferantennummer", "Hauptlieferant"),
]
_ARTIKEL_PREISE = [
    _feld("sales_price", "Verkaufspreis", "currency", required=True),
    _feld("purchase_price", "Einkaufspreis", "currency"),
    _feld("currency", "Waehrung", width=70),
    _feld("einheit_preiseinheit", "Preiseinheit"),
    _feld("steuerschluessel_verkauf", "Steuerschluessel Verkauf"),
    _feld("steuerschluessel_einkauf", "Steuerschluessel Einkauf"),
    _feld("rabattfaehig", "Rabattfaehig", "boolean"),
    _feld("skontofaehig", "Skontofaehig", "boolean"),
    _feld("bonus_faehig", "Bonusfaehig", "boolean"),
]
_ARTIKEL_LAGER = [
    _feld("lagerartikel", "Lagerartikel", "boolean"),
    _feld("min_stock", "Mindestbestand", "number"),
    _feld("max_stock", "Hoechstbestand", "number"),
    _feld("chargenpflicht", "Chargenpflicht", "boolean"),
    _feld("mhd_erforderlich", "MHD erforderlich", "boolean"),
    _feld("lager_silo", "Silolagerung", "boolean"),
    _feld("gebinde_groesse", "Gebindegroesse", "number"),
    _feld("gebinde_einheit", "Gebindeeinheit"),
    _feld("weight", "Gewicht je Einheit", "number"),
]
_ARTIKEL_QUALITAET = [
    _feld("qs_pruefung_erforderlich", "QS-Pruefung erforderlich", "boolean"),
    _feld("gmp_plus_relevanz", "GMP+-relevant", "boolean"),
    _feld("bio_kennzeichnung", "Bio", "boolean"),
    _feld("analyse_protein", "Protein %", "number"),
    _feld("analyse_feuchtigkeit", "Feuchte %", "number"),
    _feld("analyse_fremdstoffe", "Fremdstoffe %", "number"),
    _feld("gefahrgutklasse", "Gefahrgutklasse"),
    _feld("gefahrgut_un_nummer", "UN-Nummer"),
    _feld("zolltarifnummer", "Zolltarifnummer"),
]
#: Felder, die die Aktion "Bearbeiten" aendern darf (auch der Kommandoweg nimmt nur diese an).
ARTIKEL_BEARBEITEN_FELDER = tuple(
    f["key"] for f in (*_ARTIKEL_STAMM, *_ARTIKEL_PREISE, *_ARTIKEL_LAGER, *_ARTIKEL_QUALITAET)
)


def _eingabe(felder: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Eingabefelder des Bearbeiten-Dialogs: ohne Pflicht (nur gesetzte Felder aendern), Waehrungen als Zahl."""
    return [{"key": f["key"], "label": f["label"], "type": "number" if f["type"] == "currency" else f["type"]}
            for f in felder]


def build_artikel_stamm() -> dict[str, Any]:
    """Artikelstamm: Stammdaten, Preise/Steuer, Lager, Qualitaet; Register Lieferanten, Preise, Dokumente."""
    return build_stamm_object_page(
        screen_id="artikel/stamm",
        domain="lager",
        title="Artikel",
        subtitle="Artikelstamm",
        identity_field="article_number",
        creation={
            "endpoint": "/api/v1/articles/",
            "permission": "artikel.create",
            "detailRoute": "/artikel/{entity_id}",
            "defaults": {"currency": "EUR", "lagerartikel": True, "rabattfaehig": True, "skontofaehig": True},
        },
        summary=[
            {"key": "article_number", "label": "Artikel-Nr.", "value": None, "kind": "identity"},
            {"key": "available_stock", "label": "Verfuegbar", "value": None, "kind": "kpi"},
            {"key": "sales_price", "label": "Verkaufspreis", "value": None, "kind": "kpi"},
        ],
        data_sources=[
            stamm_entity_source("/api/v1/articles/{entity_id}"),
            stamm_tab_source("lieferanten", "/api/v1/articles/{entity_id}/suppliers"),
            stamm_tab_source("preise", "/api/v1/articles/{entity_id}/prices"),
            stamm_tab_source("dokumente", "/api/v1/articles/{entity_id}/documents"),
        ],
        tabs=[
            stamm_kopf_tab([*_ARTIKEL_STAMM, _feld("is_active", "Aktiv", "boolean", readOnly=True)]),
            stamm_entity_tab(key="preise_steuer", label="Preise und Steuer", fields=_ARTIKEL_PREISE),
            stamm_entity_tab(
                key="lager",
                label="Lager",
                fields=[
                    *_ARTIKEL_LAGER,
                    _feld("current_stock", "Bestand", "number", readOnly=True),
                    _feld("reserved_stock", "Reserviert", "number", readOnly=True),
                    _feld("available_stock", "Verfuegbar", "number", readOnly=True),
                ],
            ),
            stamm_entity_tab(key="qualitaet", label="Qualitaet und Gefahrgut", fields=_ARTIKEL_QUALITAET),
            _register("lieferanten", "Lieferanten", "lieferanten", [
                {"key": "supplier_number", "label": "Lieferant", "width": 140, "sortable": True},
                {"key": "supplier_article_number", "label": "Lieferanten-Art.-Nr.", "width": 160},
                {"key": "purchase_price", "label": "EK-Preis", "numeric": True, "renderKind": "currency"},
                {"key": "lead_time_days", "label": "Lieferzeit (Tage)", "numeric": True},
                {"key": "is_preferred", "label": "Bevorzugt", "renderKind": "boolean", "width": 90},
            ]),
            _register("preise", "Preisvereinbarungen", "preise", [
                {"key": "partner_id", "label": "Partner", "width": 140, "sortable": True},
                {"key": "price_net", "label": "Netto", "numeric": True, "renderKind": "currency", "sortable": True},
                {"key": "price_unit", "label": "Preiseinheit", "width": 100},
                {"key": "valid_from", "label": "Gueltig ab", "renderKind": "date", "sortable": True},
                {"key": "valid_to", "label": "Gueltig bis", "renderKind": "date"},
            ]),
            _register("dokumente", "Dokumente", "dokumente", [
                {"key": "document_name", "label": "Dokument", "width": 220, "sortable": True},
                {"key": "document_type", "label": "Typ", "width": 120, "filterable": True},
                {"key": "document_category", "label": "Kategorie", "width": 120, "filterable": True},
                {"key": "created_at", "label": "Erfasst", "renderKind": "date", "sortable": True},
            ]),
        ],
        edit_permission="artikel.update",
        edit_action_key="bearbeiten",
        edit_action_overrides={
            "commandEndpoint": "/api/v1/articles/{entity_id}/actions/bearbeiten",
            "method": "POST",
            "inputFields": _eingabe([*_ARTIKEL_STAMM, *_ARTIKEL_PREISE, *_ARTIKEL_LAGER, *_ARTIKEL_QUALITAET]),
        },
        no_workflow_reason="Artikelstamm ist ein Verwaltungsobjekt — Ablaeufe liegen in den Belegen, nicht im Stammsatz.",
        business_purpose=(
            "Artikelstamm fuer Verkauf, Einkauf und Lager: Kennungen, Preise und Steuer, "
            "Lagerfuehrung, Qualitaet; Lieferanten, Preisvereinbarungen und Dokumente."
        ),
        example_prompts=[
            "Welchen Verkaufspreis und Steuerschluessel hat Artikel {entity_id}?",
            "Welche Lieferanten liefern Artikel {entity_id} und zu welchem EK-Preis?",
            "Ist Artikel {entity_id} chargen- oder QS-pflichtig?",
        ],
        sensitive_fields=["purchase_price"],
        test_id="artikel-stamm",
        density="expertDense",
        context_rail="combined",
        table_profile="inventory",
        payload_budget_kb=48,
        requires_virtual_tables=True,
        bundle_group="lager",
    )


STAMM_SCREEN_BUILDERS = {
    "artikel/stamm": build_artikel_stamm,
}

STAMM_ROUTEN = {
    "artikel/stamm": "/artikel",
}
