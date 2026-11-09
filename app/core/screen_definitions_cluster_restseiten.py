"""Studio-Listen fuer Seiten, die eine screenId ohne ScreenDefinition renderten (Restseiten, 09.11.2026).

Die Seiten zeigten "Workspace konnte nicht geladen werden"; ihr Leseweg existierte schon mit typisiertem
Response-Model. Spalten folgen diesem Modell. Schichtplan: Mitarbeiterbezuege stehen nicht in der Liste
(datensparsam, die Besetzung pflegt die Schichtmaske).
"""
from __future__ import annotations

from typing import Any

from app.core.cluster_spalten import datum, janein, status, text, zahl
from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_export_action

_EXPORT = stamm_list_export_action()


def _liste(**kwargs: Any) -> dict[str, Any]:
    return build_stamm_list_screen(actions=[_EXPORT], row_actions=[], row_route=None, **kwargs)


def build_nawaro_raps_profile() -> dict[str, Any]:
    return _liste(
        screen_id="nawaro/raps-profil", domain="agrar", bundle="nawaro", title="Raps-Profile",
        subtitle="Rapsprofile je Erntejahr mit Verwendungsanteilen und THG-Wert",
        endpoint="/api/v1/agrar/nawaro/raps-profiles",
        columns=[text("article_name", "Artikel", "primary"), text("article_number", "Artikelnr."),
                 zahl("harvest_year", "Erntejahr", "primary"), zahl("yield_dt_per_ha", "Ertrag (dt/ha)"),
                 text("usage_energy_pct", "Energie %"), text("usage_feed_pct", "Futter %", "tertiary"),
                 text("usage_food_pct", "Lebensmittel %", "tertiary"),
                 text("usage_material_pct", "Stofflich %", "tertiary"),
                 zahl("thg_gco2eq_mj", "THG (g CO2eq/MJ)"), datum("updated_at", "Geändert", "tertiary")],
        purpose="Rapsprofile pruefen: Ertrag, Verwendung und Treibhausgaswert je Erntejahr.",
        prompts=["Welcher THG-Wert gilt fuer Raps der Ernte 2026?", "Wie hoch ist der Energieanteil im Rapsprofil?"],
        no_workflow="Stammdatenliste; Nachweise und Bilanzen im NawaRo-Ablauf.",
    )


def build_schichtplan_liste() -> dict[str, Any]:
    return _liste(
        screen_id="schichtplan/liste", domain="personal", bundle="personal", title="Schichtplan",
        subtitle="Schichten mit Zeit, Standort, Bedarf und Stand",
        endpoint="/api/v1/personal/shifts",
        columns=[datum("datum", "Datum", "primary"), text("name", "Schicht", "primary"),
                 text("startTime", "Beginn"), text("endTime", "Ende"), text("locationCode", "Standort"),
                 text("requiredRole", "Rolle"), zahl("requiredHeadcount", "Bedarf (Köpfe)"), status()],
        purpose="Pruefen, welche Schichten anstehen und wo Besetzung fehlt.",
        prompts=["Welche Schichten sind diese Woche geplant?", "Welche Schichten sind abgesagt?"],
        no_workflow="Planungsliste; Besetzung und Konflikte in der Schichtmaske.",
    )


def build_wissen_wissensbasis() -> dict[str, Any]:
    return _liste(
        screen_id="wissen/wissensbasis", domain="platform", bundle="wissen", title="Wissensbasis",
        subtitle="Wissensartikel mit Typ, Stand, Version und Agentenfreigabe",
        endpoint="/api/v1/knowledge/", fetch_limit=500,
        columns=[text("titel", "Titel", "primary"), text("typ", "Typ", "primary"), status(),
                 text("beschreibung", "Beschreibung", "tertiary"), zahl("versionen_count", "Versionen"),
                 janein("agentenfreigabe", "Für Agenten"), datum("updated_at", "Geändert")],
        purpose="Wissensartikel finden und pruefen, welche fuer Agenten freigegeben sind.",
        prompts=["Welche Artikel sind fuer Agenten freigegeben?", "Gibt es eine Anleitung zur Ernteannahme?"],
        no_workflow="Nachschlageliste; Pflege und Versionen in der Wissensmaske.",
    )


CLUSTER_RESTSEITEN_SCREEN_BUILDERS: dict[str, Any] = {
    "nawaro/raps-profil": build_nawaro_raps_profile,
    "schichtplan/liste": build_schichtplan_liste,
    "wissen/wissensbasis": build_wissen_wissensbasis,
}
