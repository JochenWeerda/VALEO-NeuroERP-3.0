"""Cockpit ScreenDefinitions — Batch 14 (85 Seiten)."""
from __future__ import annotations

from typing import Any

from app.core.cockpit_overview_parent import (
    build_cockpit_overview_screen,
    cockpit_entity_source,
    cockpit_nav_tile,
    cockpit_refresh_action,
)


def build_auswertungen_umsatzstatistik_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="auswertungen/umsatzstatistik",
        domain="reporting",
        title="Umsatzstatistik",
        subtitle="Vertriebsumsatz nach Zeitraum",
        business_purpose="Umsatzstatistik als Read-Model-Cockpit.",
        example_prompts=["Zeige Umsatzstatistik.", "Was ist der aktuelle Stand?"],
        test_id="auswertungen-umsatzstatistik",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/sales/reports/summary")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/auswertungen/umsatzstatistik")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="reporting.read")],
        context_rail="combined",
    )


def build_auswertungen_vertriebstrichter_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="auswertungen/vertriebstrichter",
        domain="reporting",
        title="Vertriebstrichter",
        subtitle="Pipeline und Conversion",
        business_purpose="Vertriebstrichter als Read-Model-Cockpit.",
        example_prompts=["Zeige Vertriebstrichter.", "Was ist der aktuelle Stand?"],
        test_id="auswertungen-vertriebstrichter",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/sales/reports/pipeline")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/auswertungen/vertriebstrichter")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="reporting.read")],
        context_rail="combined",
    )


def build_auswertungen_warengruppen_analyse_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="auswertungen/warengruppen-analyse",
        domain="reporting",
        title="Warengruppen-Analyse",
        subtitle="Umsatz und Menge je Warengruppe",
        business_purpose="Warengruppen-Analyse als Read-Model-Cockpit.",
        example_prompts=["Zeige Warengruppen-Analyse.", "Was ist der aktuelle Stand?"],
        test_id="auswertungen-warengruppen-analyse",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/warengruppen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/auswertungen/warengruppen-analyse")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="reporting.read")],
        context_rail="combined",
    )


def build_auth_callback_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="auth/callback",
        domain="identity",
        title="OIDC Callback",
        subtitle="Anmeldung abschliessen",
        business_purpose="OIDC Callback als Read-Model-Cockpit.",
        example_prompts=["Zeige OIDC Callback.", "Was ist der aktuelle Stand?"],
        test_id="auth-callback",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/identity/session")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/auth/callback")],
        actions=[cockpit_refresh_action(permission="identity.session.read")],
        context_rail="combined",
    )


def build_auth_login_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="auth/login",
        domain="identity",
        title="Anmeldung",
        subtitle="SSO-Anmeldung",
        business_purpose="Anmeldung als Read-Model-Cockpit.",
        example_prompts=["Zeige Anmeldung.", "Was ist der aktuelle Stand?"],
        test_id="auth-login",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/identity/session")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/auth/login")],
        actions=[cockpit_refresh_action(permission="identity.session.read")],
        context_rail="combined",
    )


def build_banken_konten_stamm_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="banken/konten-stamm",
        domain="finance",
        title="Bankkonten-Stamm",
        subtitle="Hausbanken und Konten",
        business_purpose="Bankkonten-Stamm als Read-Model-Cockpit.",
        example_prompts=["Zeige Bankkonten-Stamm.", "Was ist der aktuelle Stand?"],
        test_id="banken-konten-stamm",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/banken/konten")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/banken/konten-stamm")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="finance.read")],
        context_rail="combined",
    )


def build_banken_lastschriften_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="banken/lastschriften",
        domain="finance",
        title="Lastschriften",
        subtitle="SEPA-Lastschriftlaeufe",
        business_purpose="Lastschriften als Read-Model-Cockpit.",
        example_prompts=["Zeige Lastschriften.", "Was ist der aktuelle Stand?"],
        test_id="banken-lastschriften",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/finance/payment-runs")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/banken/lastschriften")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="finance.read")],
        context_rail="combined",
    )


def build_banken_sepa_export_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="banken/sepa-export",
        domain="finance",
        title="SEPA-Export",
        subtitle="Zahlungsdateien exportieren",
        business_purpose="SEPA-Export als Read-Model-Cockpit.",
        example_prompts=["Zeige SEPA-Export.", "Was ist der aktuelle Stand?"],
        test_id="banken-sepa-export",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/finance/payment-runs")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/banken/sepa-export")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="finance.read")],
        context_rail="combined",
    )


def build_banken_ueberweisungen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="banken/ueberweisungen",
        domain="finance",
        title="Ueberweisungen",
        subtitle="Bankumsaetze und Ueberweisungen",
        business_purpose="Ueberweisungen als Read-Model-Cockpit.",
        example_prompts=["Zeige Ueberweisungen.", "Was ist der aktuelle Stand?"],
        test_id="banken-ueberweisungen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/banken/fints/umsaetze")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/banken/ueberweisungen")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="finance.read")],
        context_rail="combined",
    )


def build_banken_zahlungsavise_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="banken/zahlungsavise",
        domain="finance",
        title="Zahlungsavise",
        subtitle="Avise zu Zahlungslaeufen",
        business_purpose="Zahlungsavise als Read-Model-Cockpit.",
        example_prompts=["Zeige Zahlungsavise.", "Was ist der aktuelle Stand?"],
        test_id="banken-zahlungsavise",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/finance/payment-runs")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/banken/zahlungsavise")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="finance.read")],
        context_rail="combined",
    )


def build_banken_zahlungsvorschlaege_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="banken/zahlungsvorschlaege",
        domain="finance",
        title="Zahlungsvorschlaege",
        subtitle="Vorschlaege aus offenen Posten",
        business_purpose="Zahlungsvorschlaege als Read-Model-Cockpit.",
        example_prompts=["Zeige Zahlungsvorschlaege.", "Was ist der aktuelle Stand?"],
        test_id="banken-zahlungsvorschlaege",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/finance/payment-suggestions")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/banken/zahlungsvorschlaege")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="finance.read")],
        context_rail="combined",
    )


def build_belege_belegfolge_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="belege/belegfolge",
        domain="documents",
        title="Belegfolge",
        subtitle="DocFlow-Kette und Folgebelege",
        business_purpose="Belegfolge als Read-Model-Cockpit.",
        example_prompts=["Zeige Belegfolge.", "Was ist der aktuelle Stand?"],
        test_id="belege-belegfolge",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/docflow/")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/belege/belegfolge")],
        actions=[cockpit_refresh_action(permission="documents.read")],
        context_rail="combined",
    )


def build_betrieb_gefahrstoff_betriebsanweisung_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="betrieb/gefahrstoff-betriebsanweisung",
        domain="operations",
        title="Gefahrstoff-Betriebsanweisung",
        subtitle="Betriebsanweisungen und Export",
        business_purpose="Gefahrstoff-Betriebsanweisung als Read-Model-Cockpit.",
        example_prompts=["Zeige Gefahrstoff-Betriebsanweisung.", "Was ist der aktuelle Stand?"],
        test_id="betrieb-gefahrstoff-betriebsanweisung",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/compliance/exports/gefahrstoffdoku")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/betrieb/gefahrstoff-betriebsanweisung")],
        actions=[cockpit_refresh_action(permission="compliance.read")],
        context_rail="combined",
    )


def build_betrieb_gefahrstoff_kataster_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="betrieb/gefahrstoff-kataster",
        domain="operations",
        title="Gefahrstoff-Kataster",
        subtitle="Gefahrstoffregister",
        business_purpose="Gefahrstoff-Kataster als Read-Model-Cockpit.",
        example_prompts=["Zeige Gefahrstoff-Kataster.", "Was ist der aktuelle Stand?"],
        test_id="betrieb-gefahrstoff-kataster",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/compliance/exports/gefahrstoffdoku")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/betrieb/gefahrstoff-kataster")],
        actions=[cockpit_refresh_action(permission="compliance.read")],
        context_rail="combined",
    )


def build_betrieb_maschinen_stamm_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="betrieb/maschinen-stamm",
        domain="operations",
        title="Maschinen-Stamm",
        subtitle="Maschinenpark",
        business_purpose="Maschinen-Stamm als Read-Model-Cockpit.",
        example_prompts=["Zeige Maschinen-Stamm.", "Was ist der aktuelle Stand?"],
        test_id="betrieb-maschinen-stamm",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/agrar/maschinen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/betrieb/maschinen-stamm")],
        actions=[cockpit_refresh_action(permission="agrar.read")],
        context_rail="combined",
    )


def build_betrieb_prueffristen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="betrieb/prueffristen",
        domain="operations",
        title="Prueffristen",
        subtitle="Anlagen und Prueftermine",
        business_purpose="Prueffristen als Read-Model-Cockpit.",
        example_prompts=["Zeige Prueffristen.", "Was ist der aktuelle Stand?"],
        test_id="betrieb-prueffristen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/wartung/anlagen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/betrieb/prueffristen")],
        actions=[cockpit_refresh_action(permission="operations.read")],
        context_rail="combined",
    )


def build_betrieb_schadensmeldung_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="betrieb/schadensmeldung",
        domain="operations",
        title="Schadensmeldung",
        subtitle="Schaeden und Reklamationen",
        business_purpose="Schadensmeldung als Read-Model-Cockpit.",
        example_prompts=["Zeige Schadensmeldung.", "Was ist der aktuelle Stand?"],
        test_id="betrieb-schadensmeldung",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/qualitaet/reklamationen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/betrieb/schadensmeldung")],
        actions=[cockpit_refresh_action(permission="quality.read")],
        context_rail="combined",
    )


def build_betrieb_standorte_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="betrieb/standorte",
        domain="operations",
        title="Standorte",
        subtitle="Betriebsstaetten",
        business_purpose="Standorte als Read-Model-Cockpit.",
        example_prompts=["Zeige Standorte.", "Was ist der aktuelle Stand?"],
        test_id="betrieb-standorte",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/stammdaten/betriebsstaetten")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/betrieb/standorte")],
        actions=[cockpit_refresh_action(permission="masterdata.read")],
        context_rail="combined",
    )


def build_betrieb_unterweisungen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="betrieb/unterweisungen",
        domain="operations",
        title="Unterweisungen",
        subtitle="Schulungen und Unterweisungen",
        business_purpose="Unterweisungen als Read-Model-Cockpit.",
        example_prompts=["Zeige Unterweisungen.", "Was ist der aktuelle Stand?"],
        test_id="betrieb-unterweisungen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/personal/absences")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/betrieb/unterweisungen")],
        actions=[cockpit_refresh_action(permission="hrm.read")],
        context_rail="combined",
    )


def build_betrieb_wartungsplan_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="betrieb/wartungsplan",
        domain="operations",
        title="Wartungsplan",
        subtitle="Anlagenwartung",
        business_purpose="Wartungsplan als Read-Model-Cockpit.",
        example_prompts=["Zeige Wartungsplan.", "Was ist der aktuelle Stand?"],
        test_id="betrieb-wartungsplan",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/wartung/anlagen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/betrieb/wartungsplan")],
        actions=[cockpit_refresh_action(permission="operations.read")],
        context_rail="combined",
    )


def build_charge_etiketten_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="charge/etiketten",
        domain="inventory",
        title="Etiketten",
        subtitle="Etikettendruck",
        business_purpose="Etiketten als Read-Model-Cockpit.",
        example_prompts=["Zeige Etiketten.", "Was ist der aktuelle Stand?"],
        test_id="charge-etiketten",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/etiketten/drucker")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/charge/etiketten")],
        table_profile="inventory",
        actions=[cockpit_refresh_action(permission="inventory.read")],
        context_rail="combined",
    )


def build_charge_mischung_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="charge/mischung",
        domain="inventory",
        title="Chargen-Mischung",
        subtitle="Mischchargen",
        business_purpose="Chargen-Mischung als Read-Model-Cockpit.",
        example_prompts=["Zeige Chargen-Mischung.", "Was ist der aktuelle Stand?"],
        test_id="charge-mischung",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/chargen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/charge/mischung")],
        table_profile="inventory",
        actions=[cockpit_refresh_action(permission="inventory.read")],
        context_rail="combined",
    )


def build_charge_probenahme_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="charge/probenahme",
        domain="inventory",
        title="Probenahme",
        subtitle="Chargen-Probenahme",
        business_purpose="Probenahme als Read-Model-Cockpit.",
        example_prompts=["Zeige Probenahme.", "Was ist der aktuelle Stand?"],
        test_id="charge-probenahme",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/chargen/stats/summary")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/charge/probenahme")],
        table_profile="inventory",
        actions=[cockpit_refresh_action(permission="inventory.read")],
        context_rail="combined",
    )


def build_charge_sperrlager_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="charge/sperrlager",
        domain="inventory",
        title="Sperrlager",
        subtitle="Gesperrte Bestaende",
        business_purpose="Sperrlager als Read-Model-Cockpit.",
        example_prompts=["Zeige Sperrlager.", "Was ist der aktuelle Stand?"],
        test_id="charge-sperrlager",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/compliance/artikel-sperren")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/charge/sperrlager")],
        table_profile="inventory",
        actions=[cockpit_refresh_action(permission="inventory.read")],
        context_rail="combined",
    )


def build_charge_teilung_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="charge/teilung",
        domain="inventory",
        title="Chargenteilung",
        subtitle="Chargen teilen",
        business_purpose="Chargenteilung als Read-Model-Cockpit.",
        example_prompts=["Zeige Chargenteilung.", "Was ist der aktuelle Stand?"],
        test_id="charge-teilung",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/chargen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/charge/teilung")],
        table_profile="inventory",
        actions=[cockpit_refresh_action(permission="inventory.read")],
        context_rail="combined",
    )


def build_charge_zusammenfuehrung_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="charge/zusammenfuehrung",
        domain="inventory",
        title="Chargenzusammenfuehrung",
        subtitle="Chargen zusammenfuehren",
        business_purpose="Chargenzusammenfuehrung als Read-Model-Cockpit.",
        example_prompts=["Zeige Chargenzusammenfuehrung.", "Was ist der aktuelle Stand?"],
        test_id="charge-zusammenfuehrung",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/chargen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/charge/zusammenfuehrung")],
        table_profile="inventory",
        actions=[cockpit_refresh_action(permission="inventory.read")],
        context_rail="combined",
    )


def build_crm_activities_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/activities",
        domain="crm",
        title="Aktivitaeten",
        subtitle="CRM-Aktivitaetenliste",
        business_purpose="Aktivitaeten als Read-Model-Cockpit.",
        example_prompts=["Zeige Aktivitaeten.", "Was ist der aktuelle Stand?"],
        test_id="crm-activities",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/crm/activities")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/activities")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_activity_detail_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/activity-detail",
        domain="crm",
        title="Aktivitaet",
        subtitle="Aktivitaetsdetail",
        business_purpose="Aktivitaet als Read-Model-Cockpit.",
        example_prompts=["Zeige Aktivitaet.", "Was ist der aktuelle Stand?"],
        test_id="crm-activity-detail",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/crm/activities/{activity_id}")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/activity-detail")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_angebot_erstellen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/angebot-erstellen",
        domain="crm",
        title="Angebot erstellen",
        subtitle="Vertriebsangebot anlegen",
        business_purpose="Angebot erstellen als Read-Model-Cockpit.",
        example_prompts=["Zeige Angebot erstellen.", "Was ist der aktuelle Stand?"],
        test_id="crm-angebot-erstellen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/angebote")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/angebot-erstellen")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_anruf_protokoll_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/anruf-protokoll",
        domain="crm",
        title="Anruf-Protokoll",
        subtitle="Telefonate dokumentieren",
        business_purpose="Anruf-Protokoll als Read-Model-Cockpit.",
        example_prompts=["Zeige Anruf-Protokoll.", "Was ist der aktuelle Stand?"],
        test_id="crm-anruf-protokoll",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/crm/activities")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/anruf-protokoll")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_besuchsberichte_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/besuchsberichte",
        domain="crm",
        title="Besuchsberichte",
        subtitle="Kundenbesuche",
        business_purpose="Besuchsberichte als Read-Model-Cockpit.",
        example_prompts=["Zeige Besuchsberichte.", "Was ist der aktuelle Stand?"],
        test_id="crm-besuchsberichte",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/crm/activities")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/besuchsberichte")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_betreuungsgebiet_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/betreuungsgebiet",
        domain="crm",
        title="Betreuungsgebiet",
        subtitle="Gebiete und Segmente",
        business_purpose="Betreuungsgebiet als Read-Model-Cockpit.",
        example_prompts=["Zeige Betreuungsgebiet.", "Was ist der aktuelle Stand?"],
        test_id="crm-betreuungsgebiet",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/crm/segments")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/betreuungsgebiet")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_bonus_vereinbarungen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/bonus-vereinbarungen",
        domain="crm",
        title="Bonus-Vereinbarungen",
        subtitle="Bonuslaeufe",
        business_purpose="Bonus-Vereinbarungen als Read-Model-Cockpit.",
        example_prompts=["Zeige Bonus-Vereinbarungen.", "Was ist der aktuelle Stand?"],
        test_id="crm-bonus-vereinbarungen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/l3-report-catalog/bonus-runs")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/bonus-vereinbarungen")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_churn_risiko_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/churn-risiko",
        domain="crm",
        title="Churn-Risiko",
        subtitle="Abwanderungsrisiko",
        business_purpose="Churn-Risiko als Read-Model-Cockpit.",
        example_prompts=["Zeige Churn-Risiko.", "Was ist der aktuelle Stand?"],
        test_id="crm-churn-risiko",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/crm/dashboard")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/churn-risiko")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_cross_selling_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/cross-selling",
        domain="crm",
        title="Cross-Selling",
        subtitle="Cross-Sell-Potenziale",
        business_purpose="Cross-Selling als Read-Model-Cockpit.",
        example_prompts=["Zeige Cross-Selling.", "Was ist der aktuelle Stand?"],
        test_id="crm-cross-selling",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/agrar/milchvieh-crosssell/summary")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/cross-selling")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_dokumente_kunden_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/dokumente-kunden",
        domain="crm",
        title="Kundendokumente",
        subtitle="DMS je Kunde",
        business_purpose="Kundendokumente als Read-Model-Cockpit.",
        example_prompts=["Zeige Kundendokumente.", "Was ist der aktuelle Stand?"],
        test_id="crm-dokumente-kunden",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/dokumente")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/dokumente-kunden")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_dubletten_pruefung_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/dubletten-pruefung",
        domain="crm",
        title="Dubletten-Pruefung",
        subtitle="Partner-Dubletten",
        business_purpose="Dubletten-Pruefung als Read-Model-Cockpit.",
        example_prompts=["Zeige Dubletten-Pruefung.", "Was ist der aktuelle Stand?"],
        test_id="crm-dubletten-pruefung",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/crm/duplicates")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/dubletten-pruefung")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_events_messen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/events-messen",
        domain="crm",
        title="Events und Messen",
        subtitle="Marketing-Events",
        business_purpose="Events und Messen als Read-Model-Cockpit.",
        example_prompts=["Zeige Events und Messen.", "Was ist der aktuelle Stand?"],
        test_id="crm-events-messen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/marketing/kampagnen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/events-messen")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_gebietsschutz_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/gebietsschutz",
        domain="crm",
        title="Gebietsschutz",
        subtitle="Ownership und Gebiete",
        business_purpose="Gebietsschutz als Read-Model-Cockpit.",
        example_prompts=["Zeige Gebietsschutz.", "Was ist der aktuelle Stand?"],
        test_id="crm-gebietsschutz",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/crm/ownership/unassigned")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/gebietsschutz")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_geschenke_liste_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/geschenke-liste",
        domain="crm",
        title="Geschenke",
        subtitle="Geschenkregister",
        business_purpose="Geschenke als Read-Model-Cockpit.",
        example_prompts=["Zeige Geschenke.", "Was ist der aktuelle Stand?"],
        test_id="crm-geschenke-liste",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/crm/kim/customers/{kunden_nr}/gifts")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/geschenke-liste")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_interaktions_historie_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/interaktions-historie",
        domain="crm",
        title="Interaktions-Historie",
        subtitle="Kundenhistorie",
        business_purpose="Interaktions-Historie als Read-Model-Cockpit.",
        example_prompts=["Zeige Interaktions-Historie.", "Was ist der aktuelle Stand?"],
        test_id="crm-interaktions-historie",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/crm/customers/{customer_id}/tabs/historie")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/interaktions-historie")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_kampagne_detail_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/kampagne-detail",
        domain="crm",
        title="Kampagne",
        subtitle="Kampagnendetail",
        business_purpose="Kampagne als Read-Model-Cockpit.",
        example_prompts=["Zeige Kampagne.", "Was ist der aktuelle Stand?"],
        test_id="crm-kampagne-detail",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/marketing/kampagnen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/kampagne-detail")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_kampagne_erstellen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/kampagne-erstellen",
        domain="crm",
        title="Kampagne erstellen",
        subtitle="Neue Marketing-Kampagne",
        business_purpose="Kampagne erstellen als Read-Model-Cockpit.",
        example_prompts=["Zeige Kampagne erstellen.", "Was ist der aktuelle Stand?"],
        test_id="crm-kampagne-erstellen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/marketing/kampagnen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/kampagne-erstellen")],
        actions=[cockpit_refresh_action(permission="crm.write")],
        context_rail="combined",
    )


def build_crm_kaufverhalten_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/kaufverhalten",
        domain="crm",
        title="Kaufverhalten",
        subtitle="Kundenkaufverhalten",
        business_purpose="Kaufverhalten als Read-Model-Cockpit.",
        example_prompts=["Zeige Kaufverhalten.", "Was ist der aktuelle Stand?"],
        test_id="crm-kaufverhalten",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/sales/reports/top-customers")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/kaufverhalten")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_kommunikation_center_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/kommunikation-center",
        domain="crm",
        title="Kommunikations-Center",
        subtitle="Kanaele und Vorlagen",
        business_purpose="Kommunikations-Center als Read-Model-Cockpit.",
        example_prompts=["Zeige Kommunikations-Center.", "Was ist der aktuelle Stand?"],
        test_id="crm-kommunikation-center",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/query-center/catalog")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/kommunikation-center")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_wettbewerber_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/wettbewerber",
        domain="crm",
        title="Wettbewerber",
        subtitle="Wettbewerbsbeobachtung",
        business_purpose="Wettbewerber als Read-Model-Cockpit.",
        example_prompts=["Zeige Wettbewerber.", "Was ist der aktuelle Stand?"],
        test_id="crm-wettbewerber",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/crm/dashboard")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/wettbewerber")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_crm_zielgruppen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/zielgruppen",
        domain="crm",
        title="Zielgruppen",
        subtitle="Segmente und Zielgruppen",
        business_purpose="Zielgruppen als Read-Model-Cockpit.",
        example_prompts=["Zeige Zielgruppen.", "Was ist der aktuelle Stand?"],
        test_id="crm-zielgruppen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/crm/segments")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/crm/zielgruppen")],
        actions=[cockpit_refresh_action(permission="crm.read")],
        context_rail="combined",
    )


def build_dashboard_customizable_dashboard_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dashboard/customizable-dashboard",
        domain="platform",
        title="Anpassbares Dashboard",
        subtitle="Widget-Cockpit",
        business_purpose="Anpassbares Dashboard als Read-Model-Cockpit.",
        example_prompts=["Zeige Anpassbares Dashboard.", "Was ist der aktuelle Stand?"],
        test_id="dashboard-customizable-dashboard",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/controlling/dashboards")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/dashboard/customizable-dashboard")],
        actions=[cockpit_refresh_action(permission="controlling.read")],
        context_rail="combined",
    )


def build_dashboard_sales_dashboard_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dashboard/sales-dashboard",
        domain="sales",
        title="Verkaufs-Dashboard",
        subtitle="Vertriebs-KPIs",
        business_purpose="Verkaufs-Dashboard als Read-Model-Cockpit.",
        example_prompts=["Zeige Verkaufs-Dashboard.", "Was ist der aktuelle Stand?"],
        test_id="dashboard-sales-dashboard",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/sales/reports/summary")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/dashboard/sales-dashboard")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="sales.read")],
        context_rail="combined",
    )


def build_disposition_bestell_vorschlag_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="disposition/bestell-vorschlag",
        domain="logistics",
        title="Bestellvorschlag",
        subtitle="Disposition Bestellvorschlaege",
        business_purpose="Bestellvorschlag als Read-Model-Cockpit.",
        example_prompts=["Zeige Bestellvorschlag.", "Was ist der aktuelle Stand?"],
        test_id="disposition-bestell-vorschlag",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/bestellvorschlaege")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/disposition/bestell-vorschlag")],
        table_profile="inventory",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_disposition_engpass_monitor_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="disposition/engpass-monitor",
        domain="logistics",
        title="Engpass-Monitor",
        subtitle="Engpaesse in der Disposition",
        business_purpose="Engpass-Monitor als Read-Model-Cockpit.",
        example_prompts=["Zeige Engpass-Monitor.", "Was ist der aktuelle Stand?"],
        test_id="disposition-engpass-monitor",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/disposition/stats")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/disposition/engpass-monitor")],
        table_profile="inventory",
        actions=[cockpit_refresh_action(permission="logistics.read")],
        context_rail="combined",
    )


def build_disposition_kontrakt_abruf_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="disposition/kontrakt-abruf",
        domain="logistics",
        title="Kontrakt-Abruf",
        subtitle="Kontraktabrufe",
        business_purpose="Kontrakt-Abruf als Read-Model-Cockpit.",
        example_prompts=["Zeige Kontrakt-Abruf.", "Was ist der aktuelle Stand?"],
        test_id="disposition-kontrakt-abruf",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/kontrakte")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/disposition/kontrakt-abruf")],
        table_profile="inventory",
        actions=[cockpit_refresh_action(permission="contracts.read")],
        context_rail="combined",
    )


def build_disposition_lager_reichweite_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="disposition/lager-reichweite",
        domain="logistics",
        title="Lager-Reichweite",
        subtitle="Reichweitenprognose",
        business_purpose="Lager-Reichweite als Read-Model-Cockpit.",
        example_prompts=["Zeige Lager-Reichweite.", "Was ist der aktuelle Stand?"],
        test_id="disposition-lager-reichweite",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/lager/dashboard")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/disposition/lager-reichweite")],
        table_profile="inventory",
        actions=[cockpit_refresh_action(permission="inventory.read")],
        context_rail="combined",
    )


def build_disposition_saison_planung_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="disposition/saison-planung",
        domain="logistics",
        title="Saison-Planung",
        subtitle="Saisonale Planung",
        business_purpose="Saison-Planung als Read-Model-Cockpit.",
        example_prompts=["Zeige Saison-Planung.", "Was ist der aktuelle Stand?"],
        test_id="disposition-saison-planung",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/planung/kalender")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/disposition/saison-planung")],
        table_profile="inventory",
        actions=[cockpit_refresh_action(permission="planung.calendar.read")],
        context_rail="combined",
    )


def build_disposition_strecken_disposition_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="disposition/strecken-disposition",
        domain="logistics",
        title="Strecken-Disposition",
        subtitle="Streckengeschaefte",
        business_purpose="Strecken-Disposition als Read-Model-Cockpit.",
        example_prompts=["Zeige Strecken-Disposition.", "Was ist der aktuelle Stand?"],
        test_id="disposition-strecken-disposition",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/strecke/streckengeschaefte")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/disposition/strecken-disposition")],
        table_profile="inventory",
        actions=[cockpit_refresh_action(permission="logistics.read")],
        context_rail="combined",
    )


def build_disposition_touren_disposition_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="disposition/touren-disposition",
        domain="logistics",
        title="Touren-Disposition",
        subtitle="Tourenplanung",
        business_purpose="Touren-Disposition als Read-Model-Cockpit.",
        example_prompts=["Zeige Touren-Disposition.", "Was ist der aktuelle Stand?"],
        test_id="disposition-touren-disposition",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/logistik/tours")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/disposition/touren-disposition")],
        table_profile="inventory",
        actions=[cockpit_refresh_action(permission="logistics.read")],
        context_rail="combined",
    )


def build_disposition_umlagerungs_vorschlag_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="disposition/umlagerungs-vorschlag",
        domain="logistics",
        title="Umlagerungs-Vorschlag",
        subtitle="Umlagerungsvorschlaege",
        business_purpose="Umlagerungs-Vorschlag als Read-Model-Cockpit.",
        example_prompts=["Zeige Umlagerungs-Vorschlag.", "Was ist der aktuelle Stand?"],
        test_id="disposition-umlagerungs-vorschlag",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/disposition")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/disposition/umlagerungs-vorschlag")],
        table_profile="inventory",
        actions=[cockpit_refresh_action(permission="logistics.read")],
        context_rail="combined",
    )


def build_dms_archiv_suche_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dms/archiv-suche",
        domain="documents",
        title="Archiv-Suche",
        subtitle="DMS-Volltextsuche",
        business_purpose="Archiv-Suche als Read-Model-Cockpit.",
        example_prompts=["Zeige Archiv-Suche.", "Was ist der aktuelle Stand?"],
        test_id="dms-archiv-suche",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/dms/search")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/dms/archiv-suche")],
        actions=[cockpit_refresh_action(permission="documents.read")],
        context_rail="combined",
    )


def build_dms_beleg_erkennung_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dms/beleg-erkennung",
        domain="documents",
        title="Beleg-Erkennung",
        subtitle="OCR-Regeln",
        business_purpose="Beleg-Erkennung als Read-Model-Cockpit.",
        example_prompts=["Zeige Beleg-Erkennung.", "Was ist der aktuelle Stand?"],
        test_id="dms-beleg-erkennung",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/process/dms/erkennungsregeln")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/dms/beleg-erkennung")],
        actions=[cockpit_refresh_action(permission="documents.read")],
        context_rail="combined",
    )


def build_dms_dokument_detail_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dms/dokument-detail",
        domain="documents",
        title="Dokument",
        subtitle="DMS-Dokumentdetail",
        business_purpose="Dokument als Read-Model-Cockpit.",
        example_prompts=["Zeige Dokument.", "Was ist der aktuelle Stand?"],
        test_id="dms-dokument-detail",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/dms/documents")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/dms/dokument-detail")],
        actions=[cockpit_refresh_action(permission="documents.read")],
        context_rail="combined",
    )


def build_dms_dokument_upload_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dms/dokument-upload",
        domain="documents",
        title="Dokument-Upload",
        subtitle="DMS-Upload",
        business_purpose="Dokument-Upload als Read-Model-Cockpit.",
        example_prompts=["Zeige Dokument-Upload.", "Was ist der aktuelle Stand?"],
        test_id="dms-dokument-upload",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/dms/documents")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/dms/dokument-upload")],
        actions=[cockpit_refresh_action(permission="documents.write")],
        context_rail="combined",
    )


def build_dms_freigabe_workflow_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dms/freigabe-workflow",
        domain="documents",
        title="Freigabe-Workflow",
        subtitle="DMS-Freigaben",
        business_purpose="Freigabe-Workflow als Read-Model-Cockpit.",
        example_prompts=["Zeige Freigabe-Workflow.", "Was ist der aktuelle Stand?"],
        test_id="dms-freigabe-workflow",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/docflow/evidence/artifacts")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/dms/freigabe-workflow")],
        actions=[cockpit_refresh_action(permission="documents.approve")],
        context_rail="combined",
    )


def build_dms_posteingang_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dms/posteingang",
        domain="documents",
        title="Posteingang",
        subtitle="DMS-Posteingang",
        business_purpose="Posteingang als Read-Model-Cockpit.",
        example_prompts=["Zeige Posteingang.", "Was ist der aktuelle Stand?"],
        test_id="dms-posteingang",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/dms/inbox")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/dms/posteingang")],
        actions=[cockpit_refresh_action(permission="documents.read")],
        context_rail="combined",
    )


def build_dms_verschlagwortung_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dms/verschlagwortung",
        domain="documents",
        title="Verschlagwortung",
        subtitle="Tags und Metadaten",
        business_purpose="Verschlagwortung als Read-Model-Cockpit.",
        example_prompts=["Zeige Verschlagwortung.", "Was ist der aktuelle Stand?"],
        test_id="dms-verschlagwortung",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/dms/documents")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/dms/verschlagwortung")],
        actions=[cockpit_refresh_action(permission="documents.write")],
        context_rail="combined",
    )


def build_dms_vorlagen_verwaltung_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dms/vorlagen-verwaltung",
        domain="documents",
        title="Vorlagen-Verwaltung",
        subtitle="DMS-Vorlagen",
        business_purpose="Vorlagen-Verwaltung als Read-Model-Cockpit.",
        example_prompts=["Zeige Vorlagen-Verwaltung.", "Was ist der aktuelle Stand?"],
        test_id="dms-vorlagen-verwaltung",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/process/template/vorlagen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/dms/vorlagen-verwaltung")],
        actions=[cockpit_refresh_action(permission="documents.read")],
        context_rail="combined",
    )


def build_dokumente_archiv_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dokumente/archiv",
        domain="documents",
        title="Dokumentarchiv",
        subtitle="Archiv-Eintraege",
        business_purpose="Dokumentarchiv als Read-Model-Cockpit.",
        example_prompts=["Zeige Dokumentarchiv.", "Was ist der aktuelle Stand?"],
        test_id="dokumente-archiv",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/process/archiv/eintraege")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/dokumente/archiv")],
        actions=[cockpit_refresh_action(permission="documents.read")],
        context_rail="combined",
    )


def build_dokumente_eingang_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dokumente/eingang",
        domain="documents",
        title="Dokumenteingang",
        subtitle="Eingangskorb",
        business_purpose="Dokumenteingang als Read-Model-Cockpit.",
        example_prompts=["Zeige Dokumenteingang.", "Was ist der aktuelle Stand?"],
        test_id="dokumente-eingang",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/dms/inbox")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/dokumente/eingang")],
        actions=[cockpit_refresh_action(permission="documents.read")],
        context_rail="combined",
    )


def build_dokumente_suche_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dokumente/suche",
        domain="documents",
        title="Dokumentensuche",
        subtitle="Suche im Archiv",
        business_purpose="Dokumentensuche als Read-Model-Cockpit.",
        example_prompts=["Zeige Dokumentensuche.", "Was ist der aktuelle Stand?"],
        test_id="dokumente-suche",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/dms/search")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/dokumente/suche")],
        actions=[cockpit_refresh_action(permission="documents.read")],
        context_rail="combined",
    )


def build_dokumente_vorlagen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dokumente/vorlagen",
        domain="documents",
        title="Dokumentvorlagen",
        subtitle="Vorlagenkatalog",
        business_purpose="Dokumentvorlagen als Read-Model-Cockpit.",
        example_prompts=["Zeige Dokumentvorlagen.", "Was ist der aktuelle Stand?"],
        test_id="dokumente-vorlagen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/process/template/vorlagen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/dokumente/vorlagen")],
        actions=[cockpit_refresh_action(permission="documents.read")],
        context_rail="combined",
    )


def build_einkauf_anfrage_erstellen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/anfrage-erstellen",
        domain="einkauf",
        title="Anfrage erstellen",
        subtitle="Bedarfsanfrage",
        business_purpose="Anfrage erstellen als Read-Model-Cockpit.",
        example_prompts=["Zeige Anfrage erstellen.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-anfrage-erstellen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/anfragen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/anfrage-erstellen")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_einkauf_angebot_erfassen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/angebot-erfassen",
        domain="einkauf",
        title="Angebot erfassen",
        subtitle="Lieferantenangebot",
        business_purpose="Angebot erfassen als Read-Model-Cockpit.",
        example_prompts=["Zeige Angebot erfassen.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-angebot-erfassen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/angebote")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/angebot-erfassen")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_einkauf_anlieferavis_erfassen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/anlieferavis-erfassen",
        domain="einkauf",
        title="Anlieferavis erfassen",
        subtitle="Lieferavis",
        business_purpose="Anlieferavis erfassen als Read-Model-Cockpit.",
        example_prompts=["Zeige Anlieferavis erfassen.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-anlieferavis-erfassen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/anlieferavis")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/anlieferavis-erfassen")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_einkauf_auftragsbestaetigung_erfassen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/auftragsbestaetigung-erfassen",
        domain="einkauf",
        title="Auftragsbestaetigung",
        subtitle="AB erfassen",
        business_purpose="Auftragsbestaetigung als Read-Model-Cockpit.",
        example_prompts=["Zeige Auftragsbestaetigung.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-auftragsbestaetigung-erfassen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/auftragsbestaetigungen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/auftragsbestaetigung-erfassen")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_einkauf_bestellung_freigabe_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/bestellung-freigabe",
        domain="einkauf",
        title="Bestellfreigabe",
        subtitle="Bestellungen freigeben",
        business_purpose="Bestellfreigabe als Read-Model-Cockpit.",
        example_prompts=["Zeige Bestellfreigabe.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-bestellung-freigabe",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/bestellungen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/bestellung-freigabe")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.approve")],
        context_rail="combined",
    )


def build_einkauf_bestellvorschlag_lager_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/bestellvorschlag-lager",
        domain="einkauf",
        title="Bestellvorschlag Lager",
        subtitle="Lagergetriebene Vorschlaege",
        business_purpose="Bestellvorschlag Lager als Read-Model-Cockpit.",
        example_prompts=["Zeige Bestellvorschlag Lager.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-bestellvorschlag-lager",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/bestellvorschlaege/lager")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/bestellvorschlag-lager")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_einkauf_bestellvorschlag_kontrakt_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/bestellvorschlag-kontrakt",
        domain="einkauf",
        title="Bestellvorschlag Kontrakt",
        subtitle="Kontrakt-Vorschlaege",
        business_purpose="Bestellvorschlag Kontrakt als Read-Model-Cockpit.",
        example_prompts=["Zeige Bestellvorschlag Kontrakt.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-bestellvorschlag-kontrakt",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/bestellvorschlaege/rohware")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/bestellvorschlag-kontrakt")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_einkauf_bestellvorschlag_verbrauch_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/bestellvorschlag-verbrauch",
        domain="einkauf",
        title="Bestellvorschlag Verbrauch",
        subtitle="Verbrauchsvorschlaege",
        business_purpose="Bestellvorschlag Verbrauch als Read-Model-Cockpit.",
        example_prompts=["Zeige Bestellvorschlag Verbrauch.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-bestellvorschlag-verbrauch",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/bestellvorschlaege/bedarf")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/bestellvorschlag-verbrauch")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_einkauf_gutschrift_belastung_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/gutschrift-belastung",
        domain="einkauf",
        title="Gutschrift/Belastung",
        subtitle="Einkaufs-Gutschrift",
        business_purpose="Gutschrift/Belastung als Read-Model-Cockpit.",
        example_prompts=["Zeige Gutschrift/Belastung.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-gutschrift-belastung",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/lieferscheine")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/gutschrift-belastung")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_einkauf_kontrakt_anlage_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/kontrakt-anlage",
        domain="einkauf",
        title="Kontrakt-Anlage",
        subtitle="Einkaufskontrakt",
        business_purpose="Kontrakt-Anlage als Read-Model-Cockpit.",
        example_prompts=["Zeige Kontrakt-Anlage.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-kontrakt-anlage",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/kontrakte")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/kontrakt-anlage")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_einkauf_lieferanten_angebote_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/lieferanten-angebote",
        domain="einkauf",
        title="Lieferanten-Angebote",
        subtitle="Angebotsvergleich",
        business_purpose="Lieferanten-Angebote als Read-Model-Cockpit.",
        example_prompts=["Zeige Lieferanten-Angebote.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-lieferanten-angebote",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/angebote")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/lieferanten-angebote")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_einkauf_lieferanten_dokumente_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/lieferanten-dokumente",
        domain="einkauf",
        title="Lieferanten-Dokumente",
        subtitle="DMS je Lieferant",
        business_purpose="Lieferanten-Dokumente als Read-Model-Cockpit.",
        example_prompts=["Zeige Lieferanten-Dokumente.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-lieferanten-dokumente",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/suppliers/{supplier_id}/documents")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/lieferanten-dokumente")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_einkauf_lieferanten_konditionen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/lieferanten-konditionen",
        domain="einkauf",
        title="Lieferanten-Konditionen",
        subtitle="Einkaufskonditionen",
        business_purpose="Lieferanten-Konditionen als Read-Model-Cockpit.",
        example_prompts=["Zeige Lieferanten-Konditionen.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-lieferanten-konditionen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/preise/konditionen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/lieferanten-konditionen")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_einkauf_lieferanten_reklamationen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/lieferanten-reklamationen",
        domain="einkauf",
        title="Lieferanten-Reklamationen",
        subtitle="Reklamationen",
        business_purpose="Lieferanten-Reklamationen als Read-Model-Cockpit.",
        example_prompts=["Zeige Lieferanten-Reklamationen.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-lieferanten-reklamationen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/qualitaet/reklamationen")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/lieferanten-reklamationen")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_einkauf_lieferschein_erfassen_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/lieferschein-erfassen",
        domain="einkauf",
        title="Lieferschein erfassen",
        subtitle="Einkauf-Lieferschein",
        business_purpose="Lieferschein erfassen als Read-Model-Cockpit.",
        example_prompts=["Zeige Lieferschein erfassen.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-lieferschein-erfassen",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/einkauf/lieferscheine")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/lieferschein-erfassen")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="combined",
    )


def build_einkauf_mahnwesen_lieferanten_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="einkauf/mahnwesen-lieferanten",
        domain="einkauf",
        title="Mahnwesen Lieferanten",
        subtitle="Lieferanten-Mahnwesen",
        business_purpose="Mahnwesen Lieferanten als Read-Model-Cockpit.",
        example_prompts=["Zeige Mahnwesen Lieferanten.", "Was ist der aktuelle Stand?"],
        test_id="einkauf-mahnwesen-lieferanten",
        summary=[
            {"key": "total", "label": "Anzahl", "tone": "neutral"},
            {"key": "open", "label": "Offen", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/finance/followup/mahnwesen/preview")],
        tiles=[cockpit_nav_tile("overview", "Uebersicht", target_route="/einkauf/mahnwesen-lieferanten")],
        table_profile="financial",
        actions=[cockpit_refresh_action(permission="finance.read")],
        context_rail="combined",
    )


BATCH14_BUILDERS: dict[str, Any] = {
    "auswertungen/umsatzstatistik": build_auswertungen_umsatzstatistik_screen_definition,
    "auswertungen/vertriebstrichter": build_auswertungen_vertriebstrichter_screen_definition,
    "auswertungen/warengruppen-analyse": build_auswertungen_warengruppen_analyse_screen_definition,
    "auth/callback": build_auth_callback_screen_definition,
    "auth/login": build_auth_login_screen_definition,
    "banken/konten-stamm": build_banken_konten_stamm_screen_definition,
    "banken/lastschriften": build_banken_lastschriften_screen_definition,
    "banken/sepa-export": build_banken_sepa_export_screen_definition,
    "banken/ueberweisungen": build_banken_ueberweisungen_screen_definition,
    "banken/zahlungsavise": build_banken_zahlungsavise_screen_definition,
    "banken/zahlungsvorschlaege": build_banken_zahlungsvorschlaege_screen_definition,
    "belege/belegfolge": build_belege_belegfolge_screen_definition,
    "betrieb/gefahrstoff-betriebsanweisung": build_betrieb_gefahrstoff_betriebsanweisung_screen_definition,
    "betrieb/gefahrstoff-kataster": build_betrieb_gefahrstoff_kataster_screen_definition,
    "betrieb/maschinen-stamm": build_betrieb_maschinen_stamm_screen_definition,
    "betrieb/prueffristen": build_betrieb_prueffristen_screen_definition,
    "betrieb/schadensmeldung": build_betrieb_schadensmeldung_screen_definition,
    "betrieb/standorte": build_betrieb_standorte_screen_definition,
    "betrieb/unterweisungen": build_betrieb_unterweisungen_screen_definition,
    "betrieb/wartungsplan": build_betrieb_wartungsplan_screen_definition,
    "charge/etiketten": build_charge_etiketten_screen_definition,
    "charge/mischung": build_charge_mischung_screen_definition,
    "charge/probenahme": build_charge_probenahme_screen_definition,
    "charge/sperrlager": build_charge_sperrlager_screen_definition,
    "charge/teilung": build_charge_teilung_screen_definition,
    "charge/zusammenfuehrung": build_charge_zusammenfuehrung_screen_definition,
    "crm/activities": build_crm_activities_screen_definition,
    "crm/activity-detail": build_crm_activity_detail_screen_definition,
    "crm/angebot-erstellen": build_crm_angebot_erstellen_screen_definition,
    "crm/anruf-protokoll": build_crm_anruf_protokoll_screen_definition,
    "crm/besuchsberichte": build_crm_besuchsberichte_screen_definition,
    "crm/betreuungsgebiet": build_crm_betreuungsgebiet_screen_definition,
    "crm/bonus-vereinbarungen": build_crm_bonus_vereinbarungen_screen_definition,
    "crm/churn-risiko": build_crm_churn_risiko_screen_definition,
    "crm/cross-selling": build_crm_cross_selling_screen_definition,
    "crm/dokumente-kunden": build_crm_dokumente_kunden_screen_definition,
    "crm/dubletten-pruefung": build_crm_dubletten_pruefung_screen_definition,
    "crm/events-messen": build_crm_events_messen_screen_definition,
    "crm/gebietsschutz": build_crm_gebietsschutz_screen_definition,
    "crm/geschenke-liste": build_crm_geschenke_liste_screen_definition,
    "crm/interaktions-historie": build_crm_interaktions_historie_screen_definition,
    "crm/kampagne-detail": build_crm_kampagne_detail_screen_definition,
    "crm/kampagne-erstellen": build_crm_kampagne_erstellen_screen_definition,
    "crm/kaufverhalten": build_crm_kaufverhalten_screen_definition,
    "crm/kommunikation-center": build_crm_kommunikation_center_screen_definition,
    "crm/wettbewerber": build_crm_wettbewerber_screen_definition,
    "crm/zielgruppen": build_crm_zielgruppen_screen_definition,
    "dashboard/customizable-dashboard": build_dashboard_customizable_dashboard_screen_definition,
    "dashboard/sales-dashboard": build_dashboard_sales_dashboard_screen_definition,
    "disposition/bestell-vorschlag": build_disposition_bestell_vorschlag_screen_definition,
    "disposition/engpass-monitor": build_disposition_engpass_monitor_screen_definition,
    "disposition/kontrakt-abruf": build_disposition_kontrakt_abruf_screen_definition,
    "disposition/lager-reichweite": build_disposition_lager_reichweite_screen_definition,
    "disposition/saison-planung": build_disposition_saison_planung_screen_definition,
    "disposition/strecken-disposition": build_disposition_strecken_disposition_screen_definition,
    "disposition/touren-disposition": build_disposition_touren_disposition_screen_definition,
    "disposition/umlagerungs-vorschlag": build_disposition_umlagerungs_vorschlag_screen_definition,
    "dms/archiv-suche": build_dms_archiv_suche_screen_definition,
    "dms/beleg-erkennung": build_dms_beleg_erkennung_screen_definition,
    "dms/dokument-detail": build_dms_dokument_detail_screen_definition,
    "dms/dokument-upload": build_dms_dokument_upload_screen_definition,
    "dms/freigabe-workflow": build_dms_freigabe_workflow_screen_definition,
    "dms/posteingang": build_dms_posteingang_screen_definition,
    "dms/verschlagwortung": build_dms_verschlagwortung_screen_definition,
    "dms/vorlagen-verwaltung": build_dms_vorlagen_verwaltung_screen_definition,
    "dokumente/archiv": build_dokumente_archiv_screen_definition,
    "dokumente/eingang": build_dokumente_eingang_screen_definition,
    "dokumente/suche": build_dokumente_suche_screen_definition,
    "dokumente/vorlagen": build_dokumente_vorlagen_screen_definition,
    "einkauf/anfrage-erstellen": build_einkauf_anfrage_erstellen_screen_definition,
    "einkauf/angebot-erfassen": build_einkauf_angebot_erfassen_screen_definition,
    "einkauf/anlieferavis-erfassen": build_einkauf_anlieferavis_erfassen_screen_definition,
    "einkauf/auftragsbestaetigung-erfassen": build_einkauf_auftragsbestaetigung_erfassen_screen_definition,
    "einkauf/bestellung-freigabe": build_einkauf_bestellung_freigabe_screen_definition,
    "einkauf/bestellvorschlag-lager": build_einkauf_bestellvorschlag_lager_screen_definition,
    "einkauf/bestellvorschlag-kontrakt": build_einkauf_bestellvorschlag_kontrakt_screen_definition,
    "einkauf/bestellvorschlag-verbrauch": build_einkauf_bestellvorschlag_verbrauch_screen_definition,
    "einkauf/gutschrift-belastung": build_einkauf_gutschrift_belastung_screen_definition,
    "einkauf/kontrakt-anlage": build_einkauf_kontrakt_anlage_screen_definition,
    "einkauf/lieferanten-angebote": build_einkauf_lieferanten_angebote_screen_definition,
    "einkauf/lieferanten-dokumente": build_einkauf_lieferanten_dokumente_screen_definition,
    "einkauf/lieferanten-konditionen": build_einkauf_lieferanten_konditionen_screen_definition,
    "einkauf/lieferanten-reklamationen": build_einkauf_lieferanten_reklamationen_screen_definition,
    "einkauf/lieferschein-erfassen": build_einkauf_lieferschein_erfassen_screen_definition,
    "einkauf/mahnwesen-lieferanten": build_einkauf_mahnwesen_lieferanten_screen_definition,
}

BATCH14_SCREEN_IDS: tuple[str, ...] = tuple(BATCH14_BUILDERS.keys())
