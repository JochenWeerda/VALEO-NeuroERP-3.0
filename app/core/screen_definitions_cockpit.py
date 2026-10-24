"""Native cockpit ScreenDefinitions (CockpitOverviewParent, Batch 10)."""

from __future__ import annotations

from typing import Any

from app.core.screen_definitions_cockpit_batch14 import BATCH14_BUILDERS
from app.core.cockpit_overview_parent import (
    build_cockpit_overview_screen,
    cockpit_entity_source,
    cockpit_list_source,
    cockpit_nav_tile,
    cockpit_refresh_action,
    cockpit_summary_table,
)

_READ = "read"
_CTRL_READ = "controlling.read"
_FIN_READ = "finance.read"
_CRM_READ = "crm.read"
_WF_READ = "workflow.cockpit.read"


def _std_cols(*pairs: tuple[str, str]) -> list[dict[str, Any]]:
    return [
        {"key": k, "label": label, "sortable": True, "filterable": True, "width": 160}
        for k, label in pairs
    ]


def build_controlling_benchmark_cockpit_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="controlling/benchmark-cockpit",
        domain="controlling",
        title="Benchmark-Cockpit",
        subtitle="KPIs, Branchenvergleich und Read-Model",
        business_purpose="Eigene KPIs gegen Branchenbenchmark und Read-Model spiegeln.",
        example_prompts=["Wie stehen unsere KPIs zum Branchendurchschnitt?", "Zeige das Benchmark-Read-Model."],
        test_id="controlling-benchmark-cockpit",
        summary=[
            {"key": "revenue", "label": "Umsatz", "tone": "neutral"},
            {"key": "orders", "label": "Auftraege", "tone": "neutral"},
            {"key": "deviation", "label": "Abweichung", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/benchmark/read-model")],
        tiles=[
            cockpit_nav_tile("katalog", "Kennzahlen-Katalog", target_route="/controlling/kpi-verwaltung"),
            cockpit_nav_tile("plan_ist", "Plan-Ist-Abweichung", target_route="/controlling/plan-ist"),
            cockpit_nav_tile("process_mining", "Process Mining", target_route="/workflow/process-mining-analytics"),
        ],
        actions=[cockpit_refresh_action(permission=_CTRL_READ)],
        context_rail="workflow",
        table_profile="financial",
    )


def build_controlling_dashboard_verwaltung_screen_definition() -> dict[str, Any]:
    cols = _std_cols(("dashboard_code", "Code"), ("name", "Name"), ("is_active", "Aktiv"))
    return build_cockpit_overview_screen(
        screen_id="controlling/dashboard-verwaltung",
        domain="controlling",
        title="Dashboard-Verwaltung",
        subtitle="Cockpit-Layouts und Widget-Zuordnung",
        business_purpose="Controlling-Dashboards mandantensicher verwalten.",
        example_prompts=["Welche Dashboards sind aktiv?", "Zeige alle Cockpit-Layouts."],
        test_id="controlling-dashboard-verwaltung",
        data_sources=[
            cockpit_entity_source("/api/v1/controlling/dashboards"),
            cockpit_list_source("dashboards", "/api/v1/controlling/dashboards"),
        ],
        tables=[cockpit_summary_table(table_key="dashboards", label="Dashboards", columns=cols)],
        actions=[cockpit_refresh_action(permission=_CTRL_READ)],
        context_rail="audit",
        table_profile="financial",
    )


def build_controlling_kpi_verwaltung_screen_definition() -> dict[str, Any]:
    cols = _std_cols(("kpi_code", "KPI-Code"), ("name", "Bezeichnung"), ("is_active", "Aktiv"))
    return build_cockpit_overview_screen(
        screen_id="controlling/kpi-verwaltung",
        domain="controlling",
        title="KPI-Verwaltung",
        subtitle="Kennzahlen, Formeln und Zielwerte",
        business_purpose="KPI-Stamm fuer Controlling-Cockpits pflegen.",
        example_prompts=["Welche KPIs sind aktiv?", "Zeige KPI-Definitionen mit Zielwerten."],
        test_id="controlling-kpi-verwaltung",
        data_sources=[
            cockpit_entity_source("/api/v1/controlling/kpis"),
            cockpit_list_source("kpis", "/api/v1/controlling/kpis"),
        ],
        tables=[cockpit_summary_table(table_key="kpis", label="KPIs", columns=cols)],
        actions=[cockpit_refresh_action(permission=_CTRL_READ)],
        table_profile="financial",
    )


def build_controlling_massnahmen_screen_definition() -> dict[str, Any]:
    cols = _std_cols(("title", "Massnahme"), ("status", "Status"), ("owner", "Verantwortlich"))
    return build_cockpit_overview_screen(
        screen_id="controlling/massnahmen",
        domain="controlling",
        title="Controlling-Massnahmen",
        subtitle="Abweichungen und Massnahmenverfolgung",
        business_purpose="Massnahmen aus Plan-Ist-Abweichungen nachverfolgen.",
        example_prompts=["Welche Massnahmen sind offen?", "Zeige ueberfaellige Massnahmen."],
        test_id="controlling-massnahmen",
        data_sources=[
            cockpit_entity_source("/api/v1/controlling/actions"),
            cockpit_list_source("actions", "/api/v1/controlling/actions"),
        ],
        tables=[cockpit_summary_table(table_key="actions", label="Massnahmen", columns=cols)],
        actions=[cockpit_refresh_action(permission=_CTRL_READ)],
        table_profile="financial",
    )


def build_controlling_plan_ist_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="controlling/plan-ist",
        domain="controlling",
        title="Plan-Ist-Controlling",
        subtitle="Budgets, Ist-Werte und Abweichungen",
        business_purpose="Plan-Ist-Abweichungen fuer Kostenstellen und KPIs sichtbar machen.",
        example_prompts=["Wo weichen Ist-Werte vom Plan ab?", "Zeige die groessten Abweichungen."],
        test_id="controlling-plan-ist",
        summary=[
            {"key": "plan", "label": "Plan", "tone": "neutral"},
            {"key": "ist", "label": "Ist", "tone": "neutral"},
            {"key": "abweichung", "label": "Abweichung", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/controlling/abweichung")],
        tiles=[
            cockpit_nav_tile("budgets", "Budgets", target_route="/controlling/dashboard-verwaltung"),
            cockpit_nav_tile("ist", "Ist-Werte", target_route="/controlling/timeseries-erfassung"),
            cockpit_nav_tile("massnahmen", "Massnahmen", target_route="/controlling/massnahmen"),
        ],
        actions=[cockpit_refresh_action(permission=_CTRL_READ)],
        table_profile="financial",
    )


def build_controlling_timeseries_erfassung_screen_definition() -> dict[str, Any]:
    cols = _std_cols(("kpi_code", "KPI"), ("period", "Periode"), ("value", "Wert"))
    return build_cockpit_overview_screen(
        screen_id="controlling/timeseries-erfassung",
        domain="controlling",
        title="Zeitreihen-Erfassung",
        subtitle="Ist-Werte und Zeitreihen fuer KPIs",
        business_purpose="Zeitreihen fuer Controlling-KPIs erfassen und pruefen.",
        example_prompts=["Welche Zeitreihen fehlen?", "Zeige Ist-Werte der letzten Periode."],
        test_id="controlling-timeseries-erfassung",
        data_sources=[
            cockpit_entity_source("/api/v1/controlling/timeseries"),
            cockpit_list_source("timeseries", "/api/v1/controlling/timeseries"),
        ],
        tables=[cockpit_summary_table(table_key="timeseries", label="Zeitreihen", columns=cols)],
        actions=[cockpit_refresh_action(permission=_CTRL_READ)],
        table_profile="financial",
    )


def build_controlling_widget_verwaltung_screen_definition() -> dict[str, Any]:
    cols = _std_cols(("widget_code", "Widget"), ("dashboard_id", "Dashboard"), ("is_active", "Aktiv"))
    return build_cockpit_overview_screen(
        screen_id="controlling/widget-verwaltung",
        domain="controlling",
        title="Widget-Verwaltung",
        subtitle="Cockpit-Widgets zuordnen und aktivieren",
        business_purpose="Widgets den Controlling-Dashboards zuordnen.",
        example_prompts=["Welche Widgets sind aktiv?", "Zeige Widget-Zuordnungen."],
        test_id="controlling-widget-verwaltung",
        data_sources=[
            cockpit_entity_source("/api/v1/controlling/dashboards"),
            cockpit_list_source("widgets", "/api/v1/controlling/dashboards"),
        ],
        tables=[cockpit_summary_table(table_key="widgets", label="Widgets", columns=cols)],
        actions=[cockpit_refresh_action(permission=_CTRL_READ)],
        table_profile="financial",
    )


def build_crm_crm_dashboard_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/crm-dashboard",
        domain="crm",
        title="CRM-Dashboard",
        subtitle="Pipeline, Aktivitaeten und Kundenlage",
        business_purpose="CRM-KPIs und naechste Aktionen auf einen Blick.",
        example_prompts=["Wie steht die Pipeline?", "Welche Kunden brauchen Aufmerksamkeit?"],
        test_id="crm-crm-dashboard",
        data_sources=[cockpit_entity_source("/api/v1/crm/dashboard")],
        summary=[
            {"key": "pipeline", "label": "Pipeline", "tone": "neutral"},
            {"key": "activities", "label": "Aktivitaeten", "tone": "neutral"},
            {"key": "leads", "label": "Leads", "tone": "warning"},
        ],
        tiles=[
            cockpit_nav_tile("kunden", "Kundenliste", target_screen_id="crm/customer-360", target_route="/crm/kunden-liste"),
            cockpit_nav_tile("leads", "Leads", target_screen_id="crm/lead", target_route="/crm/leads"),
            cockpit_nav_tile("opportunities", "Chancen", target_screen_id="crm/opportunity", target_route="/crm/opportunities"),
        ],
        actions=[cockpit_refresh_action(permission=_CRM_READ)],
        context_rail="copilot",
    )


def build_crm_bedarfsdeckung_cockpit_screen_definition() -> dict[str, Any]:
    cols = _std_cols(("kunden_nr", "Kunde"), ("bedarf", "Bedarf"), ("deckung", "Deckung"))
    return build_cockpit_overview_screen(
        screen_id="crm/bedarfsdeckung-cockpit",
        domain="crm",
        title="Bedarfsdeckung",
        subtitle="Pipeline und Mengenbedarf je Kunde",
        business_purpose="Bedarfsdeckung und Pipeline je Kunde fuer Vertrieb und Agrar.",
        example_prompts=["Welche Kunden haben ungedeckten Bedarf?", "Zeige die Bedarfsdeckungs-Pipeline."],
        test_id="crm-bedarfsdeckung-cockpit",
        data_sources=[
            cockpit_entity_source("/api/v1/crm/bedarfsdeckung/pipeline"),
            cockpit_list_source("pipeline", "/api/v1/crm/bedarfsdeckung/pipeline"),
        ],
        tables=[cockpit_summary_table(table_key="pipeline", label="Pipeline", columns=cols)],
        actions=[cockpit_refresh_action(permission=_CRM_READ)],
        context_rail="combined",
    )


def build_crm_campaign_performance_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/campaign-performance",
        domain="crm",
        title="Kampagnen-Performance",
        subtitle="Kampagnen-KPIs und Conversion",
        business_purpose="Marketing-Kampagnenleistung gegen Ziele auswerten.",
        example_prompts=["Welche Kampagne performt am besten?", "Zeige Conversion je Kampagne."],
        test_id="crm-campaign-performance",
        data_sources=[cockpit_entity_source("/api/v1/crm/dashboard")],
        summary=[
            {"key": "active_campaigns", "label": "Aktive Kampagnen", "tone": "neutral"},
            {"key": "conversion", "label": "Conversion", "tone": "success"},
            {"key": "budget", "label": "Budget", "tone": "warning"},
        ],
        tiles=[cockpit_nav_tile("campaigns", "Kampagnen", target_route="/crm/campaigns")],
        actions=[cockpit_refresh_action(permission=_CRM_READ)],
    )


def build_crm_kunden_cockpit_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="crm/kunden-cockpit",
        domain="crm",
        title="Kunden-Cockpit",
        subtitle="360-Grad-Einstieg und Worklists",
        business_purpose="Vom Kunden-Cockpit in Akte, Offene Posten und Kontrakte springen.",
        example_prompts=["Oeffne die Kundenakte.", "Zeige offene CRM-Aufgaben."],
        test_id="crm-kunden-cockpit",
        tiles=[
            cockpit_nav_tile("akte", "Kundenakte", target_screen_id="crm/customer-360", target_route="/crm/kunden-stamm"),
            cockpit_nav_tile("bedarf", "Bedarfsdeckung", target_route="/crm/bedarfsdeckung-cockpit"),
            cockpit_nav_tile("dashboard", "CRM-Dashboard", target_route="/crm/crm-dashboard"),
        ],
        data_sources=[cockpit_entity_source("/api/v1/crm/dashboard")],
        actions=[cockpit_refresh_action(permission=_CRM_READ)],
        context_rail="copilot",
    )


def build_dashboard_einkauf_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dashboard/einkauf",
        domain="einkauf",
        title="Einkaufs-Dashboard",
        subtitle="Bestellungen, Lieferanten und offene Avis",
        business_purpose="Einkaufslage mit KPIs und Sprung in Bestell- und Avis-Masken.",
        example_prompts=["Wie viele offene Bestellungen gibt es?", "Zeige ueberfaellige Lieferungen."],
        test_id="dashboard-einkauf",
        data_sources=[cockpit_entity_source("/api/v1/purchase-orders/statistics")],
        summary=[
            {"key": "open_orders", "label": "Offene Bestellungen", "tone": "warning"},
            {"key": "volume", "label": "Einkaufsvolumen", "tone": "neutral"},
            {"key": "suppliers", "label": "Aktive Lieferanten", "tone": "neutral"},
        ],
        tiles=[
            cockpit_nav_tile("bestellungen", "Bestellungen", target_screen_id="einkauf/purchase-order"),
            cockpit_nav_tile("avis", "Anlieferavis", target_screen_id="einkauf/anlieferavis"),
            cockpit_nav_tile("workspace", "Einkauf-Cockpit", target_screen_id="workspace/einkauf"),
        ],
        actions=[cockpit_refresh_action(permission="procurement.read")],
    )


def build_dashboard_verkauf_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dashboard/verkauf",
        domain="sales",
        title="Verkaufs-Dashboard",
        subtitle="Umsatz, Auftraege und Top-Kunden",
        business_purpose="Vertriebs-KPIs mit Sprung in Auftrags- und Rechnungsmasken.",
        example_prompts=["Wie ist der Umsatz im Zeitraum?", "Zeige Top-Kunden."],
        test_id="dashboard-verkauf",
        data_sources=[cockpit_entity_source("/api/v1/sales/reports/summary")],
        summary=[
            {"key": "revenue", "label": "Umsatz", "tone": "neutral"},
            {"key": "orders", "label": "Auftraege", "tone": "neutral"},
            {"key": "avg_order", "label": "Durchschn. Auftrag", "tone": "neutral"},
        ],
        tiles=[
            cockpit_nav_tile("auftraege", "Auftraege", target_screen_id="sales/sales-order"),
            cockpit_nav_tile("rechnungen", "Rechnungen", target_screen_id="sales/invoices"),
            cockpit_nav_tile("workspace", "Verkauf-Cockpit", target_screen_id="workspace/verkauf"),
        ],
        actions=[cockpit_refresh_action(permission="sales.read")],
    )


def build_dashboard_customizable_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dashboard/customizable",
        domain="platform",
        title="Anpassbares Dashboard",
        subtitle="Widgets und Rollenfokus",
        business_purpose="Persoenliches Dashboard aus freigegebenen Widgets zusammenstellen.",
        example_prompts=["Zeige mein Dashboard.", "Welche Widgets sind verfuegbar?"],
        test_id="dashboard-customizable",
        tiles=[
            cockpit_nav_tile("controlling", "Controlling", target_route="/controlling/benchmark-cockpit"),
            cockpit_nav_tile("executive", "Geschaeftsfuehrung", target_route="/management/executive-dashboard"),
            cockpit_nav_tile("start", "Start", target_route="/start-dashboard"),
        ],
        data_sources=[cockpit_entity_source("/api/v1/analytics/kpis")],
        actions=[cockpit_refresh_action(permission=_READ)],
    )


def build_dashboards_geschaeftsfuehrung_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="dashboards/geschaeftsfuehrung",
        domain="management",
        title="Geschaeftsfuehrung",
        subtitle="Management-KPIs und Entscheidungslage",
        business_purpose="Geschaeftsfuehrungs-Cockpit mit KPIs und Alerts.",
        example_prompts=["Wie ist die Gesamtperformance?", "Wo gibt es Handlungsbedarf?"],
        test_id="dashboards-geschaeftsfuehrung",
        data_sources=[cockpit_entity_source("/api/v1/management/dashboard")],
        summary=[
            {"key": "revenue", "label": "Umsatz", "tone": "neutral"},
            {"key": "margin", "label": "Marge", "tone": "neutral"},
            {"key": "alerts", "label": "Alerts", "tone": "danger"},
        ],
        tiles=[
            cockpit_nav_tile("executive", "Executive Dashboard", target_route="/management/executive-dashboard"),
            cockpit_nav_tile("benchmark", "Benchmark", target_route="/controlling/benchmark-cockpit"),
            cockpit_nav_tile("leitung", "Leitung-Cockpit", target_screen_id="workspace/leitung"),
        ],
        actions=[cockpit_refresh_action(permission="management.read")],
        context_rail="workflow",
    )


def build_admin_compliance_dashboard_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="admin/compliance-dashboard",
        domain="compliance",
        title="Compliance-Dashboard",
        subtitle="Cross-Compliance, ENNI und Meldepflichten",
        business_purpose="Compliance-Quote und offene Meldungen mandantensicher ueberblicken.",
        example_prompts=["Wie ist die Compliance-Quote?", "Welche ENNI-Meldungen sind offen?"],
        test_id="admin-compliance-dashboard",
        data_sources=[cockpit_entity_source("/api/v1/compliance/stats")],
        summary=[
            {"key": "cross_compliance", "label": "Cross-Compliance", "tone": "neutral"},
            {"key": "enni", "label": "ENNI", "tone": "warning"},
            {"key": "open", "label": "Offen", "tone": "danger"},
        ],
        tiles=[
            cockpit_nav_tile("dsgvo", "DSGVO", target_route="/compliance/dsgvo"),
            cockpit_nav_tile("eudr", "EUDR", target_route="/compliance/eudr"),
        ],
        actions=[cockpit_refresh_action(permission="compliance.read")],
        context_rail="audit",
        table_profile="audit",
    )


def build_admin_qualitaets_cockpit_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="admin/qualitaets-cockpit",
        domain="qualitaet",
        title="Qualitaets-Cockpit",
        subtitle="Labor, Reklamationen und QS-KPIs",
        business_purpose="QS-Lage und Laborauftraege als Admin-Cockpit.",
        example_prompts=["Wie viele Reklamationen sind offen?", "Zeige QS-Statistik."],
        test_id="admin-qualitaets-cockpit",
        data_sources=[cockpit_entity_source("/api/v1/qualitaet/stats")],
        summary=[
            {"key": "reklamationen", "label": "Reklamationen", "tone": "warning"},
            {"key": "labor", "label": "Labor", "tone": "neutral"},
            {"key": "freigaben", "label": "Freigaben", "tone": "success"},
        ],
        tiles=[
            cockpit_nav_tile("qs_leitstand", "QS-Leitstand", target_route="/lager/qs-leitstand"),
            cockpit_nav_tile("labor", "Laborliste", target_route="/qualitaet/labor-liste"),
        ],
        actions=[cockpit_refresh_action(permission="qualitaet.read")],
        table_profile="audit",
    )


def build_fibu_abschluss_cockpit_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="fibu/abschluss-cockpit",
        domain="finance",
        title="Abschluss-Cockpit",
        subtitle="Closing-Checklisten und Periodenfortschritt",
        business_purpose="Monats- und Jahresabschluss-Checklisten mit Fortschritt.",
        example_prompts=["Wie weit ist der Monatsabschluss?", "Welche Closing-Tasks fehlen?"],
        test_id="fibu-abschluss-cockpit",
        data_sources=[cockpit_entity_source("/api/v1/finance/closing-checklists/cockpit/summary")],
        summary=[
            {"key": "progress", "label": "Fortschritt", "tone": "neutral"},
            {"key": "open_tasks", "label": "Offene Tasks", "tone": "warning"},
            {"key": "period", "label": "Periode", "tone": "neutral"},
        ],
        tiles=[
            cockpit_nav_tile("periods", "Perioden", target_route="/finance/perioden"),
            cockpit_nav_tile("fibu_ws", "FiBu-Workspace", target_screen_id="workspace/fibu"),
        ],
        actions=[cockpit_refresh_action(permission=_FIN_READ)],
        table_profile="financial",
    )


def build_finance_offene_posten_cockpit_screen_definition() -> dict[str, Any]:
    cols = _std_cols(("partner_name", "Partner"), ("amount", "Betrag"), ("bucket", "Aging"))
    return build_cockpit_overview_screen(
        screen_id="finance/offene-posten-cockpit",
        domain="finance",
        title="Offene-Posten-Cockpit",
        subtitle="Aging, Mahnstufe und Skonto",
        business_purpose="Offene Posten mandantensicher mit Aging-Buckets auswerten.",
        example_prompts=["Wie hoch sind ueberfaellige Debitoren?", "Zeige OP-Aging."],
        test_id="finance-offene-posten-cockpit",
        data_sources=[
            cockpit_entity_source("/api/v1/finance/offene-posten"),
            cockpit_list_source("open_items", "/api/v1/finance/open-items"),
        ],
        summary=[
            {"key": "summe_offen", "label": "Summe offen", "tone": "neutral"},
            {"key": "ueberfaellig", "label": "Ueberfaellig", "tone": "warning"},
            {"key": "skonto", "label": "Skonto aktiv", "tone": "success"},
        ],
        tables=[cockpit_summary_table(table_key="open_items", label="Offene Posten", columns=cols)],
        actions=[cockpit_refresh_action(permission=_FIN_READ)],
        table_profile="financial",
    )


def build_fuhrpark_auswertung_kosten_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="fuhrpark/auswertung-kosten",
        domain="logistics",
        title="Fuhrpark-Kostenauswertung",
        subtitle="Kosten je Fahrzeug",
        business_purpose="Fuhrpark-Kosten je Fahrzeug auswerten und in Stammdaten springen.",
        example_prompts=["Welches Fahrzeug verursacht die hoechsten Kosten?"],
        test_id="fuhrpark-auswertung-kosten",
        data_sources=[cockpit_entity_source("/api/v1/fuhrpark/fahrzeuge")],
        tiles=[
            cockpit_nav_tile("fahrzeuge", "Fahrzeuge", target_screen_id="fuhrpark/fahrzeuge"),
            cockpit_nav_tile("rechnungen", "Rechnungen", target_screen_id="fuhrpark/rechnungen"),
            cockpit_nav_tile("uebersicht", "Fuhrpark-Uebersicht", target_screen_id="fuhrpark/uebersicht"),
        ],
        actions=[cockpit_refresh_action(permission="logistics.read")],
        table_profile="inventory",
    )


def build_fuhrpark_auswertungen_menu_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="fuhrpark/auswertungen-menu",
        domain="logistics",
        title="Fuhrpark-Auswertungen",
        subtitle="Kosten, Belege und Termine",
        business_purpose="Einstieg in Fuhrpark-Auswertungen und Reports.",
        example_prompts=["Oeffne Fuhrpark-Auswertungen."],
        test_id="fuhrpark-auswertungen-menu",
        tiles=[
            cockpit_nav_tile("kosten", "Kosten pro Fahrzeug", target_route="/fuhrpark/fuhrpark-auswertung-kosten-pro-fahrzeug"),
            cockpit_nav_tile("rechnungen", "Rechnungen", target_screen_id="fuhrpark/rechnungen"),
            cockpit_nav_tile("termine", "Terminarten", target_screen_id="fuhrpark/terminarten"),
        ],
        data_sources=[cockpit_entity_source("/api/v1/fuhrpark/fahrzeuge")],
        actions=[cockpit_refresh_action(permission="logistics.read")],
    )


def build_lager_inventory_dashboard_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="lager/inventory-dashboard",
        domain="lager",
        title="Lager-Dashboard",
        subtitle="Bestand, Bewegungen und Warnungen",
        business_purpose="Lager-KPIs und Sprung in Bestandsmasken.",
        example_prompts=["Welche Artikel sind unter Mindestbestand?", "Zeige Lager-KPIs."],
        test_id="lager-inventory-dashboard",
        data_sources=[cockpit_entity_source("/api/v1/lager/dashboard")],
        summary=[
            {"key": "bestand", "label": "Bestandswert", "tone": "neutral"},
            {"key": "bewegungen", "label": "Bewegungen heute", "tone": "neutral"},
            {"key": "warnungen", "label": "Warnungen", "tone": "warning"},
        ],
        tiles=[
            cockpit_nav_tile("bestand", "Artikelbestand", target_screen_id="lager/article-stock"),
            cockpit_nav_tile("bewegungen", "Lagerbewegungen", target_screen_id="lager/stock-movement"),
            cockpit_nav_tile("leitstand", "Lager-Leitstand", target_screen_id="lager/leitstand"),
        ],
        actions=[cockpit_refresh_action(permission="inventory.read")],
        table_profile="inventory",
    )


def build_lager_qs_leitstand_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="lager/qs-leitstand",
        domain="qualitaet",
        title="QS-Leitstand",
        subtitle="Freigaben, Sperren und Labor",
        business_purpose="QS-Sperren und Laborlage im Lager-Leitstand.",
        example_prompts=["Welche Chargen sind gesperrt?", "Zeige offene Laborauftraege."],
        test_id="lager-qs-leitstand",
        data_sources=[cockpit_entity_source("/api/v1/qualitaet/stats")],
        summary=[
            {"key": "sperren", "label": "Sperren", "tone": "danger"},
            {"key": "labor", "label": "Labor offen", "tone": "warning"},
            {"key": "freigaben", "label": "Freigaben", "tone": "success"},
        ],
        tiles=[
            cockpit_nav_tile("reklamation", "Reklamationen", target_screen_id="qualitaet/reklamation"),
            cockpit_nav_tile("lager_ws", "Lager-Cockpit", target_screen_id="workspace/lager"),
        ],
        actions=[cockpit_refresh_action(permission="qualitaet.read")],
        table_profile="audit",
    )


def build_management_executive_dashboard_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="management/executive-dashboard",
        domain="management",
        title="Executive Dashboard",
        subtitle="Management-KPIs, Trends und Alerts",
        business_purpose="Geschaeftsleitung: KPIs, Trends und Handlungsbedarf.",
        example_prompts=["Wie ist der Umsatz-Trend?", "Welche Alerts sind aktiv?"],
        test_id="management-executive-dashboard",
        data_sources=[cockpit_entity_source("/api/v1/management/dashboard")],
        summary=[
            {"key": "revenue", "label": "Umsatz", "tone": "neutral"},
            {"key": "orders", "label": "Auftraege", "tone": "neutral"},
            {"key": "customers", "label": "Kunden", "tone": "neutral"},
        ],
        tiles=[
            cockpit_nav_tile("benchmark", "Benchmark-Cockpit", target_route="/controlling/benchmark-cockpit"),
            cockpit_nav_tile("gf", "Geschaeftsfuehrung", target_route="/dashboards/geschaeftsfuehrung"),
            cockpit_nav_tile("leitung", "Leitung", target_screen_id="workspace/leitung"),
        ],
        actions=[cockpit_refresh_action(permission="management.read")],
        context_rail="workflow",
    )


def build_portal_feldbuch_auswertungen_screen_definition() -> dict[str, Any]:
    cols = _std_cols(("massnahme_id", "Massnahme"), ("kultur", "Kultur"), ("status", "Status"))
    return build_cockpit_overview_screen(
        screen_id="portal/feldbuch-auswertungen",
        domain="agrar",
        title="Feldbuch-Auswertungen",
        subtitle="Massnahmen und Flaechenauswertung",
        business_purpose="Feldbuch-Massnahmen fuer Auswertung und Nachweis.",
        example_prompts=["Welche Feldbuch-Massnahmen wurden erfasst?"],
        test_id="portal-feldbuch-auswertungen",
        data_sources=[
            cockpit_entity_source("/api/v1/agrar/feldbuch/massnahmen"),
            cockpit_list_source("massnahmen", "/api/v1/agrar/feldbuch/massnahmen"),
        ],
        tables=[cockpit_summary_table(table_key="massnahmen", label="Massnahmen", columns=cols)],
        actions=[cockpit_refresh_action(permission="agrar.read")],
        table_profile="inventory",
    )


def build_platform_analytics_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="platform/analytics",
        domain="platform",
        title="Analytics",
        subtitle="KPIs, Trends und Benchmark",
        business_purpose="Zentrale Analytics-KPIs und Trenduebersicht.",
        example_prompts=["Zeige Analytics-KPIs.", "Wie entwickeln sich die Trends?"],
        test_id="platform-analytics",
        data_sources=[cockpit_entity_source("/api/v1/analytics/kpis")],
        summary=[
            {"key": "kpis", "label": "KPIs", "tone": "neutral"},
            {"key": "trends", "label": "Trends", "tone": "neutral"},
        ],
        tiles=[
            cockpit_nav_tile("benchmark", "Branchenbenchmark", target_route="/controlling/benchmark-cockpit"),
            cockpit_nav_tile("trends", "Trends", target_route="/analytics"),
        ],
        actions=[cockpit_refresh_action(permission=_READ)],
    )


def build_subventionen_dashboard_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="subventionen/dashboard",
        domain="foerderung",
        title="Foerder-Dashboard",
        subtitle="Antraege und Foerderstatistik",
        business_purpose="Foerderantraege und Bewilligungslage ueberblicken.",
        example_prompts=["Wie viele Antraege sind offen?", "Zeige Foerderstatistik."],
        test_id="subventionen-dashboard",
        data_sources=[cockpit_entity_source("/api/v1/foerderung/stats")],
        summary=[
            {"key": "antraege", "label": "Antraege", "tone": "neutral"},
            {"key": "bewilligt", "label": "Bewilligt", "tone": "success"},
            {"key": "offen", "label": "Offen", "tone": "warning"},
        ],
        tiles=[cockpit_nav_tile("antraege", "Antraege", target_route="/foerderung/antraege")],
        actions=[cockpit_refresh_action(permission="foerderung.read")],
    )


def build_workflow_leitstand_screen_definition() -> dict[str, Any]:
    cols = _std_cols(
        ("process_instance_id", "Instanz"),
        ("process_key", "Prozess"),
        ("status", "Status"),
    )
    return build_cockpit_overview_screen(
        screen_id="workflow/leitstand",
        domain="workflow",
        title="Workflow-Leitstand",
        subtitle="Prozessinstanzen, Blocker und Replay",
        business_purpose="Workflow-Instanzen mandantensicher ueberwachen und eingreifen.",
        example_prompts=["Welche Prozesse sind blockiert?", "Zeige fehlgeschlagene Instanzen."],
        test_id="workflow-leitstand",
        data_sources=[
            cockpit_entity_source("/api/v1/workflow/cockpit/summary"),
            cockpit_list_source("processes", "/api/v1/workflow/cockpit/processes"),
        ],
        summary=[
            {"key": "running", "label": "Laufend", "tone": "info"},
            {"key": "failed", "label": "Fehlgeschlagen", "tone": "danger"},
            {"key": "blocked", "label": "Blockiert", "tone": "warning"},
        ],
        tables=[cockpit_summary_table(table_key="processes", label="Prozessinstanzen", columns=cols)],
        workflow={"processKey": "workflow-cockpit", "status": "monitoring", "auditRequired": True},
        no_workflow_reason=None,
        actions=[cockpit_refresh_action(permission=_WF_READ)],
        context_rail="audit",
        table_profile="audit",
        payload_budget_kb=48,
    )


def build_workflow_process_mining_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="workflow/process-mining",
        domain="workflow",
        title="Process Mining",
        subtitle="Finance-Prozessbottlenecks und Top-Prozesse",
        business_purpose="Process-Mining-Report fuer Finance-Prozesse auswerten.",
        example_prompts=["Wo sind Finance-Bottlenecks?", "Zeige Top-Prozesse."],
        test_id="workflow-process-mining",
        data_sources=[cockpit_entity_source("/api/v1/process-mining/finance/report")],
        summary=[
            {"key": "bottlenecks", "label": "Bottlenecks", "tone": "warning"},
            {"key": "top_processes", "label": "Top-Prozesse", "tone": "neutral"},
        ],
        tiles=[
            cockpit_nav_tile("leitstand", "Workflow-Leitstand", target_route="/workflow/leitstand"),
            cockpit_nav_tile("benchmark", "Benchmark Process Mining", target_route="/controlling/benchmark-cockpit"),
        ],
        actions=[cockpit_refresh_action(permission=_WF_READ)],
    )


def build_workspace_start_dashboard_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="workspace/start-dashboard",
        domain="workspace",
        title="Start-Dashboard",
        subtitle="Rollenuebergreifender Einstieg",
        business_purpose="Startseite mit Sprung in rollenbasierte Workspaces.",
        example_prompts=["Was steht heute an?", "Oeffne mein Einkaufs-Cockpit."],
        test_id="start-dashboard",
        tiles=[
            cockpit_nav_tile("einkauf", "Einkauf", target_screen_id="workspace/einkauf"),
            cockpit_nav_tile("verkauf", "Verkauf", target_screen_id="workspace/verkauf"),
            cockpit_nav_tile("lager", "Lager", target_screen_id="workspace/lager"),
            cockpit_nav_tile("fibu", "FiBu", target_screen_id="workspace/fibu"),
            cockpit_nav_tile("leitung", "Leitung", target_screen_id="workspace/leitung"),
        ],
        summary=[
            {"key": "tasks", "label": "Aufgaben", "tone": "neutral"},
            {"key": "alerts", "label": "Alerts", "tone": "warning"},
        ],
        data_sources=[cockpit_entity_source("/api/v1/analytics/kpis")],
        actions=[cockpit_refresh_action(permission=_READ)],
        context_rail="copilot",
    )


def build_workspace_einkauf_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="workspace/einkauf",
        domain="einkauf",
        title="Einkauf-Cockpit",
        subtitle="Startseite Einkauf",
        business_purpose="Rollen-Startseite Einkauf — offene Bestellungen, Avis und Preisabweichungen.",
        example_prompts=["Was steht heute im Einkauf an?", "Zeige offene Bestellungen."],
        test_id="workspace-einkauf",
        summary=[
            {"key": "offene_bestellungen", "label": "Offene Bestellungen", "tone": "neutral"},
            {"key": "avis_heute", "label": "Avis heute", "tone": "neutral"},
            {"key": "preisabweichung", "label": "Preisabweichungen", "tone": "warning"},
        ],
        tiles=[
            cockpit_nav_tile("rechnungspruefung", "Rechnungspruefung", target_screen_id="finance/ap-invoice", tone="warning"),
            cockpit_nav_tile("offene_avis", "Offene Avis", target_screen_id="einkauf/anlieferavis"),
            cockpit_nav_tile("rfq", "RFQ / Anfragen", target_screen_id="einkauf/anfrage"),
        ],
        data_sources=[cockpit_entity_source("/api/v1/purchase-orders/statistics")],
        actions=[cockpit_refresh_action(permission="procurement.read")],
        context_rail="copilot",
    )


def build_workspace_verkauf_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="workspace/verkauf",
        domain="sales",
        title="Verkauf-Cockpit",
        subtitle="Startseite Verkauf",
        business_purpose="Rollen-Startseite Verkauf — Auftragsbestand und Kreditlimit-Warnungen.",
        example_prompts=["Welche Auftraege sind ueberfaellig?", "Zeige Kreditlimit-Warnungen."],
        test_id="workspace-verkauf",
        summary=[
            {"key": "auftragsbestand", "label": "Auftragsbestand", "tone": "neutral"},
            {"key": "ueberfaellig", "label": "Ueberfaellig", "tone": "warning"},
            {"key": "kreditlimit", "label": "Kreditlimit", "tone": "danger"},
        ],
        tiles=[
            cockpit_nav_tile("offene_auftraege", "Offene Auftraege", target_screen_id="sales/sales-order"),
            cockpit_nav_tile("lieferscheine", "Lieferscheine", target_screen_id="sales/delivery-note"),
            cockpit_nav_tile("wiedervorlagen", "Wiedervorlagen", target_screen_id="crm/lead", tone="warning"),
        ],
        data_sources=[cockpit_entity_source("/api/v1/sales/reports/summary")],
        actions=[cockpit_refresh_action(permission="sales.read")],
        context_rail="copilot",
    )


def build_workspace_lager_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="workspace/lager",
        domain="lager",
        title="Lager-Cockpit",
        subtitle="Startseite Lager & Annahme",
        business_purpose="Rollen-Startseite Lager — Annahmen, Wartezeiten und Trockner.",
        example_prompts=["Wie viele Annahmen stehen heute an?", "Zeige QS-Warnungen."],
        test_id="workspace-lager",
        summary=[
            {"key": "annahmen_heute", "label": "Annahmen heute", "tone": "neutral"},
            {"key": "wartezeit", "label": "Wartezeit", "tone": "neutral"},
            {"key": "trockner", "label": "Trockner", "tone": "warning"},
        ],
        tiles=[
            cockpit_nav_tile("qualitaet", "Qualitaet", target_screen_id="qualitaet/reklamation", tone="warning"),
            cockpit_nav_tile("bewegungen", "Lagerbewegungen", target_screen_id="lager/stock-movement"),
            cockpit_nav_tile("bestand", "Bestand", target_screen_id="lager/article-stock"),
        ],
        data_sources=[cockpit_entity_source("/api/v1/lager/dashboard")],
        actions=[cockpit_refresh_action(permission="inventory.read")],
        context_rail="copilot",
        table_profile="inventory",
    )


def build_workspace_fibu_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="workspace/fibu",
        domain="finance",
        title="FiBu-Cockpit",
        subtitle="Startseite Finanzbuchhaltung",
        business_purpose="Rollen-Startseite FiBu — OP, Zahlungslauf und Abschluss.",
        example_prompts=["Wie hoch sind offene Posten?", "Was steht im Abschluss an?"],
        test_id="workspace-fibu",
        summary=[
            {"key": "op_debitoren", "label": "OP Debitoren", "tone": "warning"},
            {"key": "op_kreditoren", "label": "OP Kreditoren", "tone": "warning"},
            {"key": "zahlungslauf", "label": "Zahlungslauf", "tone": "neutral"},
        ],
        tiles=[
            cockpit_nav_tile("op", "Offene Posten", target_route="/finance/offene-posten-cockpit"),
            cockpit_nav_tile("zahlungslauf", "Zahlungslauf", target_screen_id="finance/payment-run"),
            cockpit_nav_tile("abschluss", "Abschluss", target_route="/fibu/abschluss-cockpit"),
        ],
        data_sources=[cockpit_entity_source("/api/v1/finance/offene-posten")],
        actions=[cockpit_refresh_action(permission=_FIN_READ)],
        context_rail="copilot",
        table_profile="financial",
    )


def build_workspace_leitung_screen_definition() -> dict[str, Any]:
    return build_cockpit_overview_screen(
        screen_id="workspace/leitung",
        domain="management",
        title="Leitung-Cockpit",
        subtitle="Startseite Geschaeftsleitung",
        business_purpose="Leitungssicht — KPIs, Alerts und Workspaces.",
        example_prompts=["Was braucht heute Entscheidung?", "Zeige kritische Alerts."],
        test_id="workspace-leitung",
        summary=[
            {"key": "umsatz", "label": "Umsatz", "tone": "neutral"},
            {"key": "marge", "label": "Marge", "tone": "neutral"},
            {"key": "alerts", "label": "Alerts", "tone": "danger"},
        ],
        tiles=[
            cockpit_nav_tile("executive", "Executive Dashboard", target_route="/management/executive-dashboard"),
            cockpit_nav_tile("benchmark", "Benchmark", target_route="/controlling/benchmark-cockpit"),
            cockpit_nav_tile("workflow", "Workflow-Leitstand", target_route="/workflow/leitstand"),
        ],
        data_sources=[cockpit_entity_source("/api/v1/management/dashboard")],
        actions=[cockpit_refresh_action(permission="management.read")],
        context_rail="workflow",
    )


COCKPIT_SCREEN_BUILDERS: dict[str, Any] = {
    "controlling/benchmark-cockpit": build_controlling_benchmark_cockpit_screen_definition,
    "controlling/dashboard-verwaltung": build_controlling_dashboard_verwaltung_screen_definition,
    "controlling/kpi-verwaltung": build_controlling_kpi_verwaltung_screen_definition,
    "controlling/massnahmen": build_controlling_massnahmen_screen_definition,
    "controlling/plan-ist": build_controlling_plan_ist_screen_definition,
    "controlling/timeseries-erfassung": build_controlling_timeseries_erfassung_screen_definition,
    "controlling/widget-verwaltung": build_controlling_widget_verwaltung_screen_definition,
    "crm/crm-dashboard": build_crm_crm_dashboard_screen_definition,
    "crm/bedarfsdeckung-cockpit": build_crm_bedarfsdeckung_cockpit_screen_definition,
    "crm/campaign-performance": build_crm_campaign_performance_screen_definition,
    "crm/kunden-cockpit": build_crm_kunden_cockpit_screen_definition,
    "dashboard/einkauf": build_dashboard_einkauf_screen_definition,
    "dashboard/verkauf": build_dashboard_verkauf_screen_definition,
    "dashboard/customizable": build_dashboard_customizable_screen_definition,
    "dashboards/geschaeftsfuehrung": build_dashboards_geschaeftsfuehrung_screen_definition,
    "admin/compliance-dashboard": build_admin_compliance_dashboard_screen_definition,
    "admin/qualitaets-cockpit": build_admin_qualitaets_cockpit_screen_definition,
    "fibu/abschluss-cockpit": build_fibu_abschluss_cockpit_screen_definition,
    "finance/offene-posten-cockpit": build_finance_offene_posten_cockpit_screen_definition,
    "fuhrpark/auswertung-kosten": build_fuhrpark_auswertung_kosten_screen_definition,
    "fuhrpark/auswertungen-menu": build_fuhrpark_auswertungen_menu_screen_definition,
    "lager/inventory-dashboard": build_lager_inventory_dashboard_screen_definition,
    "lager/qs-leitstand": build_lager_qs_leitstand_screen_definition,
    "management/executive-dashboard": build_management_executive_dashboard_screen_definition,
    "portal/feldbuch-auswertungen": build_portal_feldbuch_auswertungen_screen_definition,
    "platform/analytics": build_platform_analytics_screen_definition,
    "subventionen/dashboard": build_subventionen_dashboard_screen_definition,
    "workflow/leitstand": build_workflow_leitstand_screen_definition,
    "workflow/process-mining": build_workflow_process_mining_screen_definition,
    "workspace/start-dashboard": build_workspace_start_dashboard_screen_definition,
    "workspace/einkauf": build_workspace_einkauf_screen_definition,
    "workspace/verkauf": build_workspace_verkauf_screen_definition,
    "workspace/lager": build_workspace_lager_screen_definition,
    "workspace/fibu": build_workspace_fibu_screen_definition,
    "workspace/leitung": build_workspace_leitung_screen_definition,
    **BATCH14_BUILDERS,
}

COCKPIT_SCREEN_IDS: tuple[str, ...] = tuple(COCKPIT_SCREEN_BUILDERS.keys())
