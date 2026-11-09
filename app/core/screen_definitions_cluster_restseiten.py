"""Studio-Listen fuer Seiten, die eine screenId ohne ScreenDefinition renderten (Restseiten, 09.11.2026).

Die Seiten zeigten "Workspace konnte nicht geladen werden"; ihr Leseweg existierte schon mit typisiertem
Response-Model. Spalten folgen diesem Modell. Schichtplan: Mitarbeiterbezuege stehen nicht in der Liste
(datensparsam, die Besetzung pflegt die Schichtmaske).
"""
from __future__ import annotations

from typing import Any

from app.core.cluster_spalten import betrag, datum, janein, status, text, zahl
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


def build_disposition_positionsregeln() -> dict[str, Any]:
    return _liste(
        screen_id="disposition/regeln", domain="agrar", bundle="disposition", title="Positionsregeln",
        subtitle="Spekulationsschutz je Artikel oder Gruppe: Toleranz, Ampelschwellen und Freigabe",
        endpoint="/api/v1/positions/rules",
        columns=[text("scope_type", "Bezug", "primary"), text("scope_id", "Artikel/Gruppe", "primary"),
                 zahl("neg_tolerance_qty", "Negative Toleranz (Artikeleinheit)", "primary"), zahl("max_short_days", "Max. Tage short"),
                 zahl("yellow_threshold", "Gelb ab", "tertiary"),
                 zahl("red_threshold", "Rot ab", "tertiary"),
                 janein("approval_required", "Freigabe nötig"), text("approval_role", "Freigaberolle", "tertiary"),
                 datum("active_from", "Gültig ab"), datum("active_to", "Gültig bis", "tertiary")],
        purpose="Pruefen, welche Toleranz und welche Ampelschwellen fuer offene Positionen gelten.",
        prompts=["Welche Artikel brauchen eine Freigabe bei Unterdeckung?", "Welche Toleranz gilt fuer Weizen?"],
        no_workflow="Regelliste; die Ampel wertet der Deckungsmonitor aus.",
    )


def build_agribusiness_landwirte() -> dict[str, Any]:
    return _liste(
        screen_id="agribusiness/farmers", domain="agrar", bundle="agribusiness", title="Landwirte",
        subtitle="Landwirte mit Nummer, Art, Stand und Portalzugang",
        endpoint="/api/v1/agribusiness/farmers",
        columns=[text("farmerNumber", "Nummer", "primary"), text("lastName", "Name", "primary"),
                 text("firstName", "Vorname", "primary"), text("farmerType", "Art"), status(),
                 janein("portalAccessEnabled", "Portalzugang"), datum("updatedAt", "Geändert", "tertiary")],
        purpose="Landwirte finden und pruefen, wer Zugang zum Portal hat.",
        prompts=["Welche Landwirte haben Portalzugang?", "Welche Landwirte sind inaktiv?"],
        no_workflow="Stammdatenliste; Kontaktdaten stehen in der Partnerakte (datensparsam nicht in der Liste).",
    )


def build_workflows_trigger() -> dict[str, Any]:
    return _liste(
        screen_id="workflows/trigger", domain="platform", bundle="workflow", title="Workflow-Trigger",
        subtitle="Regeln, die einen Workflow ausloesen: Art, Bedingungen und Stand",
        endpoint="/api/v1/process/trigger/regeln",
        columns=[text("trigger_id", "Trigger", "primary"), text("workflow_typ", "Workflow", "primary"),
                 text("trigger_typ", "Art"), zahl("bedingungen_anzahl", "Bedingungen"), status(),
                 text("beschreibung", "Beschreibung")],
        purpose="Pruefen, welche Regeln einen Workflow ausloesen und welche aktiv sind.",
        prompts=["Welche Trigger loesen eine Kontraktfreigabe aus?", "Welche Trigger sind inaktiv?"],
        no_workflow="Regelliste des Prozesskerns; die Bedingungen prueft der Kommandoweg pruefe-bedingungen.",
    )


_PROVISION = "/api/v1/crm/vertreter/provisionen"


def _provision_ansicht(ziel: str, label: str) -> dict[str, Any]:
    return {"key": f"ansicht_{ziel.rsplit('/', 1)[-1]}", "label": label, "kind": "secondary", "dangerLevel": "safe",
            "zone": "header", "navigationRoute": ziel, "localEffect": "navigation",
            "stubReason": f"Wechselt zu {label}."}


def build_crm_vertreterprovisionen() -> dict[str, Any]:
    from app.core.eingabefelder_stamm import PROVISION_GRUPPE_FELDER as GRUPPE_FELDER
    from app.core.eingabefelder_stamm import PROVISION_STAFFEL_FELDER as STAFFEL_FELDER

    return build_stamm_list_screen(
        screen_id="crm/vertreterprovisionen", domain="crm", bundle="crm", title="Vertreterprovisionen",
        subtitle="Provisionsgruppen je Richtung: fester Satz oder Staffel",
        endpoint=f"{_PROVISION}/gruppen", row_route=None,
        columns=[text("gruppe_nr", "Gruppe", "primary"), text("bezeichnung", "Bezeichnung", "primary"),
                 text("richtung", "Richtung"), text("provisionstyp", "Provisionstyp"),
                 zahl("provisionssatz", "Satz %"), datum("created_at", "Angelegt", "tertiary")],
        actions=[{"key": "anlegen", "label": "Provisionsgruppe anlegen", "kind": "primary", "zone": "header",
                  "dangerLevel": "low", "permission": "crm.vertreter.update",
                  "commandEndpoint": f"{_PROVISION}/gruppen/actions/anlegen", "method": "POST",
                  "requiresConfirmation": False, "inputFields": GRUPPE_FELDER},
                 _provision_ansicht("/crm/vertreterprovisionen/staffeln", "Staffelzeilen"), _EXPORT],
        row_actions=[{"key": "staffelzeile_anlegen", "label": "Staffelzeile anlegen", "dangerLevel": "moderate",
                      "permission": "crm.vertreter.update",
                      "commandEndpoint": f"{_PROVISION}/gruppen/{{entity_id}}/actions/staffelzeile_anlegen",
                      "method": "POST", "requiresConfirmation": False, "inputFields": STAFFEL_FELDER,
                      "visibleWhen": {"field": "provisionstyp", "values": ["staffel_optpreis", "staffel_preis_zuab"]}},
                     {"key": "deaktivieren", "label": "Stilllegen", "dangerLevel": "moderate",
                      "permission": "crm.vertreter.update",
                      "commandEndpoint": f"{_PROVISION}/gruppen/{{entity_id}}/actions/deaktivieren", "method": "POST",
                      "requiresConfirmation": True, "auditReasonRequired": True}],
        purpose="Provisionsgruppen pflegen: wie ein Vertreter am Umsatz beteiligt wird.",
        prompts=["Lege die Provisionsgruppe P1 mit 2,5 % an.", "Welche Gruppen rechnen mit Staffel?"],
        no_workflow="Stammdatenliste; die Provisionsabrechnung liest Gruppe und Staffel.",
    )


def build_crm_vertreterprovisionen_staffeln() -> dict[str, Any]:
    return build_stamm_list_screen(
        screen_id="crm/vertreterprovisionen-staffeln", domain="crm", bundle="crm", title="Provisionsstaffeln",
        subtitle="Staffelzeilen je Provisionsgruppe und Vertreterklasse",
        endpoint=f"{_PROVISION}/staffelzeilen", row_route=None,
        columns=[text("gruppe_nr", "Gruppe", "primary"), text("gruppe_bezeichnung", "Bezeichnung"),
                 text("vertreterklasse", "Vertreterklasse", "primary"), zahl("zeile_nr", "Zeile"),
                 betrag("ab_wert", "Ab Wert", summe=False), zahl("provisionssatz", "Satz %", "primary")],
        actions=[_provision_ansicht("/crm/vertreterprovisionen", "Provisionsgruppen"), _EXPORT], row_actions=[],
        purpose="Pruefen, ab welchem Wert welcher Provisionssatz gilt.",
        prompts=["Welcher Satz gilt in Gruppe P2 ab 10.000 EUR?"],
        no_workflow="Nachschlageliste; Zeilen legt die Provisionsgruppe an.",
    )


def build_admin_nummernkreise() -> dict[str, Any]:
    from app.core.eingabefelder_stamm import NUMMERNKREIS_FORMAT_FELDER as AENDERN_FELDER
    from app.core.eingabefelder_stamm import NUMMERNKREIS_KONFIGURIEREN_FELDER as KONFIGURIEREN_FELDER

    weg = "/api/v1/admin/number-ranges"
    return build_stamm_list_screen(
        screen_id="admin/nummernkreise", domain="platform", bundle="admin", title="Nummernkreise",
        subtitle="Debitoren-, Kreditoren- und Partnernummern: Format, Stand und naechste Nummer",
        endpoint=f"{weg}/", row_route=None,
        columns=[text("range_type", "Nummernkreis", "primary"), text("prefix", "Präfix"),
                 zahl("start_number", "Start"), zahl("current_value", "Stand", "primary"),
                 zahl("digit_count", "Stellen"), zahl("reserved_prefix_digits", "Reserviert", "tertiary"),
                 text("next_number", "Nächste Nummer", "primary"), janein("is_active", "Aktiv")],
        actions=[{"key": "konfigurieren", "label": "Nummernkreis konfigurieren", "kind": "primary", "zone": "header",
                  "dangerLevel": "moderate", "permission": "admin.number_range.update",
                  "commandEndpoint": f"{weg}/actions/konfigurieren", "method": "POST",
                  "requiresConfirmation": False, "inputFields": KONFIGURIEREN_FELDER}, _EXPORT],
        row_actions=[{"key": "aendern", "label": "Ändern", "dangerLevel": "moderate",
                      "permission": "admin.number_range.update",
                      "commandEndpoint": f"{weg}/{{entity_id}}/actions/aendern", "method": "POST",
                      "requiresConfirmation": False, "inputFields": AENDERN_FELDER},
                     {"key": "stilllegen", "label": "Stilllegen", "dangerLevel": "moderate",
                      "permission": "admin.number_range.update",
                      "commandEndpoint": f"{weg}/{{entity_id}}/actions/stilllegen", "method": "POST",
                      "requiresConfirmation": True, "auditReasonRequired": True,
                      "visibleWhen": {"field": "is_active", "values": [True]}}],
        purpose="Nummernkreise einrichten und pruefen, welche Nummer als naechste vergeben wird.",
        prompts=["Welche Debitorennummer wird als naechste vergeben?", "Richte den Kreditoren-Nummernkreis ab 70000 ein."],
        no_workflow="Konfigurationsliste; vergeben werden die Nummern beim Anlegen der Partner.",
    )


def build_admin_report_berechtigungen() -> dict[str, Any]:
    from app.core.eingabefelder_stamm import REPORT_BERECHTIGUNG_FELDER

    weg = "/api/v1/admin/report-permissions"
    return build_stamm_list_screen(
        screen_id="admin/report-berechtigungen", domain="platform", bundle="admin", title="Report-Berechtigungen",
        subtitle="Welche Rolle welche Auswertung sehen und exportieren darf",
        endpoint=f"{weg}?active_only=false", row_route=None,
        columns=[text("role_id", "Rolle", "primary"), text("report_key", "Auswertung", "primary"),
                 janein("can_view", "Ansehen"), janein("can_export", "Exportieren"), janein("active", "Aktiv"),
                 datum("updated_at", "Geändert", "tertiary")],
        actions=[{"key": "anlegen", "label": "Berechtigung anlegen", "kind": "primary", "zone": "header",
                  "dangerLevel": "moderate", "permission": "admin.report_permission.update",
                  "commandEndpoint": f"{weg}/actions/anlegen", "method": "POST", "requiresConfirmation": False,
                  "inputFields": REPORT_BERECHTIGUNG_FELDER}, _EXPORT],
        row_actions=[{"key": "aendern", "label": "Ändern", "dangerLevel": "moderate",
                      "permission": "admin.report_permission.update",
                      "commandEndpoint": f"{weg}/{{entity_id}}/actions/aendern", "method": "POST",
                      "requiresConfirmation": False, "inputFields": REPORT_BERECHTIGUNG_FELDER},
                     {"key": "entfernen", "label": "Entfernen", "dangerLevel": "moderate",
                      "permission": "admin.report_permission.update",
                      "commandEndpoint": f"{weg}/{{entity_id}}/actions/entfernen", "method": "POST",
                      "requiresConfirmation": True, "auditReasonRequired": True}],
        purpose="Festlegen, welche Rolle welche Auswertung sehen und exportieren darf.",
        prompts=["Darf der Controller die BWA exportieren?", "Gib der Rolle Vertrieb Leserecht auf die Umsatzstatistik."],
        no_workflow="Berechtigungsliste; wirkt beim Aufruf der Auswertung.",
    )


def _webshop_ansicht(ziel: str, label: str) -> dict[str, Any]:
    return {"key": f"ansicht_{ziel.rsplit('/', 1)[-1]}", "label": label, "kind": "secondary", "dangerLevel": "safe",
            "zone": "header", "navigationRoute": ziel, "localEffect": "navigation", "stubReason": f"Wechselt zu {label}."}


def build_admin_webshop() -> dict[str, Any]:
    from app.core.eingabefelder_stamm import WEBSHOP_ANBINDUNG_FELDER

    weg = "/api/v1/webshop/konfigurationen"
    return build_stamm_list_screen(
        screen_id="admin/webshop", domain="sales", bundle="verkauf", title="Webshop-Anbindungen",
        subtitle="Shops, aus denen Bestellungen kommen; der API-Schluessel wird nur maskiert gespeichert",
        endpoint=weg, row_route=None,
        columns=[text("shop_url", "Shop", "primary"), text("shop_system", "System", "primary"),
                 zahl("sync_interval_minutes", "Intervall (Min.)"), janein("is_active", "Aktiv")],
        actions=[{"key": "anlegen", "label": "Shop anbinden", "kind": "primary", "zone": "header",
                  "dangerLevel": "moderate", "permission": "verkauf.webshop.update",
                  "commandEndpoint": f"{weg}/actions/anlegen", "method": "POST", "requiresConfirmation": False,
                  "inputFields": WEBSHOP_ANBINDUNG_FELDER},
                 _webshop_ansicht("/admin/webshop/bestellungen", "Webshop-Bestellungen"), _EXPORT],
        row_actions=[{"key": "entfernen", "label": "Entfernen", "dangerLevel": "moderate",
                      "permission": "verkauf.webshop.update",
                      "commandEndpoint": f"{weg}/{{entity_id}}/actions/entfernen", "method": "POST",
                      "requiresConfirmation": True, "auditReasonRequired": True}],
        purpose="Webshops anbinden und pruefen, welche Anbindungen aktiv sind.",
        prompts=["Welche Shops sind angebunden?", "Binde den Shopware-Shop https://shop.example an."],
        no_workflow="Konfigurationsliste; Bestellungen laufen ueber die Liste Webshop-Bestellungen.",
    )


def build_admin_webshop_bestellungen() -> dict[str, Any]:
    return build_stamm_list_screen(
        screen_id="admin/webshop-bestellungen", domain="sales", bundle="verkauf", title="Webshop-Bestellungen",
        subtitle="Importierte Shop-Bestellungen mit Stand, Blockern und Auftrag",
        endpoint="/api/v1/webshop/bestellungen/liste", row_route=None,
        columns=[text("externe_bestellnr", "Shop-Bestellung", "primary"), text("kunde_name", "Kunde", "primary"),
                 datum("bestelldatum", "Bestellt am", "primary"), betrag("gesamtbetrag_brutto", "Brutto"),
                 status(), text("blocker", "Blocker"), text("erp_order_number", "Auftrag"),
                 text("shop_system", "System", "tertiary"), datum("imported_at", "Importiert", "tertiary")],
        actions=[_webshop_ansicht("/admin/webshop", "Webshop-Anbindungen"), _EXPORT],
        row_actions=[{"key": "verarbeiten", "label": "Als Auftrag anlegen", "dangerLevel": "moderate",
                      "permission": "verkauf.auftrag.create",
                      "commandEndpoint": "/api/v1/webshop/bestellungen/{entity_id}/actions/verarbeiten",
                      "method": "POST", "requiresConfirmation": True,
                      "visibleWhen": {"field": "status", "values": ["NEU", "FEHLER"]}}],
        purpose="Shop-Bestellungen pruefen und als Auftragsentwurf in die Belegmaske uebernehmen.",
        prompts=["Welche Shop-Bestellungen haben Blocker?", "Lege Shop-Bestellung 10045 als Auftrag an."],
        no_workflow="Eingangsliste; der Auftrag laeuft danach in der Belegmaske weiter.",
    )


def build_agrar_wetterwarnung() -> dict[str, Any]:
    return _liste(
        screen_id="agrar/wetterwarnung", domain="agrar", bundle="agrar", title="Wetterwarnungen",
        subtitle="DWD-Warnungen fuer den Betriebsstandort (Mandanten-Einstellung standort)",
        endpoint="/api/v1/agrar/wetter/warnungen",
        columns=[text("event", "Ereignis", "primary"), status("severity", "Stufe"),
                 text("headline", "Meldung", "primary"), datum("gueltig_von", "Gültig ab", "primary"),
                 datum("gueltig_bis", "Gültig bis"), text("instruction", "Handlungsempfehlung", "tertiary"),
                 text("urgency", "Dringlichkeit", "tertiary")],
        purpose="Pruefen, welche Unwetterwarnungen fuer den Betriebsstandort gelten (Ernte, Duengung, Ausbringung).",
        prompts=["Gibt es heute eine Unwetterwarnung?", "Bis wann gilt die Sturmwarnung?"],
        no_workflow="Hinweisliste des DWD; ohne eigenen Ablauf.",
    )


CLUSTER_RESTSEITEN_SCREEN_BUILDERS: dict[str, Any] = {
    "nawaro/raps-profil": build_nawaro_raps_profile,
    "schichtplan/liste": build_schichtplan_liste,
    "wissen/wissensbasis": build_wissen_wissensbasis,
    "disposition/regeln": build_disposition_positionsregeln,
    "agribusiness/farmers": build_agribusiness_landwirte,
    "workflows/trigger": build_workflows_trigger,
    "crm/vertreterprovisionen": build_crm_vertreterprovisionen,
    "crm/vertreterprovisionen-staffeln": build_crm_vertreterprovisionen_staffeln,
    "admin/nummernkreise": build_admin_nummernkreise,
    "admin/report-berechtigungen": build_admin_report_berechtigungen,
    "admin/webshop": build_admin_webshop,
    "admin/webshop-bestellungen": build_admin_webshop_bestellungen,
    "agrar/wetterwarnung": build_agrar_wetterwarnung,
}
