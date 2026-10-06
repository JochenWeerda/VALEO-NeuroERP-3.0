"""ScreenDefinitions fuer klassische Erfassungen.

Streckengeschaeft und Versand-Avis hatten nur handgeschriebene Seiten.
Der Builder zeichnet sie, sobald die Definition in der Registry steht.
"""

from __future__ import annotations

from typing import Any


def build_strecke_streckengeschaeft_screen_definition() -> dict[str, Any]:
    """Erfassung und Bestand der Streckengeschaefte."""
    return {
        "schemaVersion": 1,
        "id": "strecke/streckengeschaeft",
        "domain": "logistics",
        "mode": "list",
        "title": "Streckengeschäft",
        "subtitle": "Einkauf / Verkauf / Spedition",
        "adapter": {"type": "native", "sourceId": "strecke/streckengeschaeft", "temporary": False},
        "dataSources": [
            {"key": "list", "endpoint": "/api/v1/strecke/streckengeschaefte", "pageSize": 200},
        ],
        "fields": [
            {"key": "strecke_nr", "label": "Strecke-Nr.", "type": "text"},
            {"key": "datum", "label": "Datum", "type": "date"},
            {"key": "niederlassung", "label": "Niederlassung", "type": "text"},
            {"key": "partie_nr", "label": "Partie-Nr.", "type": "text"},
            {"key": "bediener", "label": "Bediener", "type": "text"},
            {"key": "erledigt", "label": "Erledigt", "type": "boolean"},
            {"key": "kostenstelle", "label": "Kostenstelle", "type": "text"},
            {"key": "lagerhalle", "label": "Lagerhalle", "type": "text"},
            {"key": "nls_nr", "label": "NLS-Nr.", "type": "text"},
            {"key": "lieferant_nr", "label": "Lieferant-Nr.", "type": "text"},
            {"key": "lieferant_name", "label": "Lieferant", "type": "text"},
            {"key": "kontrakt_nr", "label": "Kontrakt-Nr.", "type": "text"},
            {"key": "artikel", "label": "Artikel", "type": "text"},
        ],
        "tables": [
            {
                "key": "list",
                "label": "Streckengeschäft",
                "dataSourceKey": "list",
                "serverPagination": False,
                "pageSize": 200,
                "virtualized": True,
                "rowHeight": 36,
                "columns": [
                    {"key": "strecke_nr", "label": "Strecke-Nr.", "sortable": True, "filterable": True, "width": 120},
                    {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "width": 110},
                    {"key": "niederlassung", "label": "Niederlassung", "width": 160},
                    {"key": "lieferant_name", "label": "Lieferant", "sortable": True, "width": 180},
                    {"key": "artikel", "label": "Artikel", "width": 180},
                    {"key": "brutto", "label": "Brutto", "numeric": True, "renderKind": "currency", "width": 120},
                    {"key": "erledigt", "label": "Erledigt", "renderKind": "boolean", "width": 90},
                ],
            },
        ],
        "noWorkflowReason": "Die Erfassung legt ein Streckengeschaeft an; eine Belegkette haengt nicht an dieser Liste.",
        "agentContract": {
            "businessPurpose": "Streckengeschaeft erfassen und den Bestand nach Nummer, Lieferant und Artikel suchen.",
            "examplePrompts": [
                "Welche Streckengeschaefte sind noch nicht erledigt?",
                "Zeige die Strecke mit der Partie von heute.",
            ],
            "sensitiveFields": [],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-strecke/streckengeschaeft']",
            },
        },
        "layout": {
            "floorplan": "worklist",
            "density": "expertDense",
            "contextRail": "none",
            "tableProfile": "standard",
            "columnNavigation": "listDetail",
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
        },
        "performance": {
            "initialPayloadBudgetKb": 40,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_versand_avis_screen_definition() -> dict[str, Any]:
    """Versand-Avis. Die Zeilen kommen aus den Lieferavisen."""
    return {
        "schemaVersion": 1,
        "id": "versand/versand-avis",
        "domain": "logistics",
        "mode": "list",
        "title": "Versand-Avis",
        "subtitle": "Versand",
        "adapter": {"type": "native", "sourceId": "versand/versand-avis", "temporary": False},
        "dataSources": [
            {"key": "list", "endpoint": "/api/v1/logistik/versand/avise", "pageSize": 200},
        ],
        "fields": [
            {"key": "telefax", "label": "Telefax", "type": "text"},
            {"key": "email", "label": "E-Mail", "type": "text"},
        ],
        "tables": [
            {
                "key": "list",
                "label": "Versand-Avis",
                "dataSourceKey": "list",
                "serverPagination": False,
                "pageSize": 50,
                "virtualized": True,
                "rowHeight": 36,
                "columns": [
                    {"key": "avis_nr", "label": "Avis-Nr.", "sortable": True, "filterable": True, "width": 120},
                    {"key": "kunden_nr", "label": "Kunden-Nr.", "width": 120},
                    {"key": "lieferant_nr", "label": "Lieferant-Nr.", "width": 120},
                    {"key": "lieferschein_nr", "label": "Lieferschein-Nr.", "width": 140},
                    {"key": "avis_datum", "label": "Avis-Datum", "renderKind": "date", "sortable": True, "width": 120},
                    {"key": "lieferdatum_erwartet", "label": "Lieferdatum", "renderKind": "date", "width": 120},
                    {"key": "artikel_nr", "label": "Artikel", "width": 120},
                    {"key": "menge", "label": "Menge", "numeric": True, "width": 90},
                    {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "width": 120},
                ],
            },
        ],
        "noWorkflowReason": "Das Versand-Avis ist eine Druckliste, kein Beleg mit eigenem Status.",
        "agentContract": {
            "businessPurpose": "Versand-Avise zur Auswahl stellen und den Empfaenger fuer den Versand nennen.",
            "examplePrompts": [
                "Welche Avise stehen zum Drucken an?",
            ],
            "sensitiveFields": [],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-versand/versand-avis']",
            },
        },
        "layout": {
            "floorplan": "worklist",
            "density": "expertDense",
            "contextRail": "none",
            "tableProfile": "standard",
            "columnNavigation": "listDetail",
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
        },
        "performance": {
            "initialPayloadBudgetKb": 24,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def _capture_worklist_layout() -> dict[str, Any]:
    return {
        "floorplan": "worklist",
        "density": "expertDense",
        "contextRail": "none",
        "tableProfile": "standard",
        "columnNavigation": "listDetail",
        "preferredMode": "desktopDense",
        "mobileMode": "mobileStack",
        "touchTargetPx": 44,
    }


def build_strecke_vorlaeufig_screen_definition() -> dict[str, Any]:
    """Touren, die noch nicht unterwegs sind. Die Liste filtert der Dienst nach Status nicht;
    die Spalte Status zeigt, welche Tour vorlaeufig ist."""
    return {
        "schemaVersion": 1,
        "id": "strecke/vorlaeufig",
        "domain": "logistics",
        "mode": "list",
        "title": "Vorläufige Streckengeschäfte",
        "subtitle": "Touren",
        "adapter": {"type": "native", "sourceId": "strecke/vorlaeufig", "temporary": False},
        "dataSources": [
            {"key": "list", "endpoint": "/api/v1/tours", "pageSize": 100},
        ],
        "tables": [
            {
                "key": "list",
                "label": "Vorläufige Streckengeschäfte",
                "dataSourceKey": "list",
                "serverPagination": False,
                "pageSize": 100,
                "virtualized": True,
                "rowHeight": 36,
                "columns": [
                    {"key": "tour_no", "label": "Strecke-Nr.", "sortable": True, "filterable": True, "width": 140},
                    {"key": "date", "label": "Datum", "renderKind": "date", "sortable": True, "width": 120},
                    {"key": "week", "label": "KW", "width": 90},
                    {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "width": 120},
                    {"key": "type", "label": "Typ", "width": 120},
                    {"key": "notes", "label": "Notiz"},
                ],
            },
        ],
        "noWorkflowReason": "Die Liste zeigt Touren. Der Status haengt an der Tour, nicht an einem eigenen Beleg.",
        "agentContract": {
            "businessPurpose": "Vorlaeufige Streckengeschaefte als Touren nach Nummer, Datum und Status suchen.",
            "examplePrompts": ["Welche Touren sind noch geplant?"],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='screen-strecke/vorlaeufig']"},
        },
        "layout": _capture_worklist_layout(),
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_strecke_disposition_screen_definition() -> dict[str, Any]:
    """Strecken anlegen, loeschen und in der Tourenliste sehen."""
    return {
        "schemaVersion": 1,
        "id": "strecke/disposition",
        "domain": "logistics",
        "mode": "list",
        "title": "Strecken-Disposition",
        "subtitle": "Touren",
        "adapter": {"type": "native", "sourceId": "strecke/disposition", "temporary": False},
        "dataSources": [
            {"key": "list", "endpoint": "/api/v1/tours", "pageSize": 100},
        ],
        "tables": [
            {
                "key": "list",
                "label": "Strecken-Disposition",
                "dataSourceKey": "list",
                "serverPagination": False,
                "pageSize": 100,
                "virtualized": True,
                "rowHeight": 36,
                "columns": [
                    {"key": "tour_no", "label": "Strecke-Nr.", "sortable": True, "filterable": True, "width": 140},
                    {"key": "date", "label": "Datum", "renderKind": "date", "sortable": True, "width": 120},
                    {"key": "week", "label": "KW", "width": 90},
                    {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "width": 120},
                    {"key": "notes", "label": "Notiz"},
                ],
                "rowActions": [
                    {"key": "loeschen", "label": "Löschen", "dangerLevel": "moderate"},
                ],
            },
        ],
        "actions": [
            {
                "key": "neu",
                "label": "Neue Strecke",
                "kind": "primary",
                "dangerLevel": "safe",
                "permission": "logistics.strecke.schreiben",
                "zone": "header",
            },
        ],
        "noWorkflowReason": "Die Disposition plant Touren. Eine Belegkette haengt nicht an dieser Liste.",
        "agentContract": {
            "businessPurpose": "Strecken disponieren: eine Tour fuer heute anlegen, bestehende Touren sehen und loeschen.",
            "examplePrompts": ["Lege eine neue Strecke fuer heute an."],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='screen-strecke/disposition']", "primaryAction": "[data-testid='action-neu']"},
        },
        "layout": _capture_worklist_layout(),
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_verkauf_betriebsauftrag_screen_definition() -> dict[str, Any]:
    """Druckauswahl der Betriebsauftraege aus den Verkaufsauftraegen."""
    return {
        "schemaVersion": 1,
        "id": "verkauf/betriebsauftrag",
        "domain": "sales",
        "mode": "list",
        "title": "Betriebsauftrag drucken",
        "subtitle": "Verkaufsaufträge",
        "adapter": {"type": "native", "sourceId": "verkauf/betriebsauftrag", "temporary": False},
        "dataSources": [
            {"key": "list", "endpoint": "/api/v1/sales/orders/", "pageSize": 50},
        ],
        "fields": [
            {"key": "auftrag_nr_von", "label": "Auftrag-Nr. von", "type": "text"},
            {"key": "auftrag_nr_bis", "label": "Auftrag-Nr. bis", "type": "text"},
            {"key": "nur_geplantes_lieferdatum", "label": "Nur mit geplantem Lieferdatum", "type": "boolean"},
            {"key": "formular", "label": "Formular", "type": "text"},
        ],
        "tables": [
            {
                "key": "list",
                "label": "Betriebsauftrag drucken",
                "dataSourceKey": "list",
                "serverPagination": False,
                "pageSize": 50,
                "virtualized": True,
                "rowHeight": 36,
                "columns": [
                    {"key": "order_number", "label": "Auftrag-Nr.", "sortable": True, "filterable": True, "width": 140},
                    {"key": "subject", "label": "Betreff", "width": 200},
                    {"key": "delivery_date", "label": "gepl. Lieferdatum", "renderKind": "date", "sortable": True, "width": 150},
                    {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "width": 120},
                    {"key": "total_amount", "label": "Betrag", "numeric": True, "renderKind": "currency", "width": 120},
                ],
            },
        ],
        "noWorkflowReason": "Die Maske waehlt Auftraege zum Druck. Der Belegstatus haengt am Verkaufsauftrag.",
        "agentContract": {
            "businessPurpose": "Betriebsauftraege zum Drucken aus den Verkaufsauftraegen heraussuchen.",
            "examplePrompts": ["Welche Auftraege haben ein Lieferdatum?"],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='screen-verkauf/betriebsauftrag']"},
        },
        "layout": {
            **_capture_worklist_layout(),
            "tableProfile": "financial",
        },
        "performance": {
            "initialPayloadBudgetKb": 40,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "sales",
        },
    }


def build_strecke_nawaro_lieferungen_screen_definition() -> dict[str, Any]:
    """NaWaRo-Lieferungen sind die Touren, unter der Streckennummer."""
    return {
        "schemaVersion": 1,
        "id": "strecke/nawaro-lieferungen",
        "domain": "agrar",
        "mode": "list",
        "title": "NaWaRo-Lieferungen",
        "subtitle": "Touren",
        "adapter": {"type": "native", "sourceId": "strecke/nawaro-lieferungen", "temporary": False},
        "dataSources": [
            {"key": "list", "endpoint": "/api/v1/tours", "pageSize": 100},
        ],
        "tables": [
            {
                "key": "list",
                "label": "NaWaRo-Lieferungen",
                "dataSourceKey": "list",
                "serverPagination": False,
                "pageSize": 100,
                "virtualized": True,
                "rowHeight": 36,
                "columns": [
                    {"key": "tour_no", "label": "Strecke-Nr.", "sortable": True, "filterable": True, "width": 140},
                    {"key": "date", "label": "Datum", "renderKind": "date", "sortable": True, "width": 120},
                    {"key": "type", "label": "Typ", "width": 120},
                    {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "width": 120},
                    {"key": "notes", "label": "Notiz"},
                ],
            },
        ],
        "noWorkflowReason": "Die Liste zeigt Lieferungen als Touren. Ein eigener NaWaRo-Belegstatus haengt nicht daran.",
        "agentContract": {
            "businessPurpose": "NaWaRo-Lieferungen nach Streckennummer, Datum, Typ und Status suchen.",
            "examplePrompts": ["Welche NaWaRo-Lieferungen sind noch geplant?"],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='screen-strecke/nawaro-lieferungen']"},
        },
        "layout": _capture_worklist_layout(),
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "agrar",
        },
    }


def build_strecke_qualitaets_abweichung_screen_definition() -> dict[str, Any]:
    """Qualitaetsabweichungen aus den Reklamationen."""
    return {
        "schemaVersion": 1,
        "id": "strecke/qualitaets-abweichung",
        "domain": "qualitaet",
        "mode": "list",
        "title": "Qualitätsabweichung",
        "subtitle": "Reklamationen",
        "adapter": {"type": "native", "sourceId": "strecke/qualitaets-abweichung", "temporary": False},
        "dataSources": [
            {"key": "list", "endpoint": "/api/v1/qualitaet/reklamationen", "pageSize": 200},
        ],
        "tables": [
            {
                "key": "list",
                "label": "Qualitätsabweichung",
                "dataSourceKey": "list",
                "serverPagination": False,
                "pageSize": 200,
                "virtualized": True,
                "rowHeight": 36,
                "columns": [
                    {"key": "nummer", "label": "Nummer", "sortable": True, "filterable": True, "width": 140},
                    {"key": "kunde", "label": "Kunde", "sortable": True, "width": 180},
                    {"key": "artikel", "label": "Artikel", "width": 160},
                    {"key": "grund", "label": "Grund", "width": 140},
                    {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "width": 120},
                    {"key": "prioritaet", "label": "Priorität", "width": 110},
                    {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "width": 140},
                ],
            },
        ],
        "noWorkflowReason": "Die Liste zeigt Reklamationen. Abschluss und Massnahmen haengen am Reklamationsbeleg.",
        "agentContract": {
            "businessPurpose": "Qualitaetsabweichungen nach Nummer, Kunde, Artikel und Status sichten.",
            "examplePrompts": ["Welche Reklamationen sind noch neu?"],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='screen-strecke/qualitaets-abweichung']"},
        },
        "layout": _capture_worklist_layout(),
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "qualitaet",
        },
    }


def _capture_cockpit_layout() -> dict[str, Any]:
    return {
        "floorplan": "cockpit",
        "density": "expertDense",
        "contextRail": "workflow",
        "columnNavigation": "single",
        "preferredMode": "desktopDense",
        "mobileMode": "mobileStack",
        "touchTargetPx": 44,
    }


def _nav_tile(key: str, label: str, route: str) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "targetScreenId": key,
        "targetRoute": route,
        "tone": "neutral",
    }


def _capture_cockpit(
    *,
    screen_id: str,
    domain: str,
    title: str,
    subtitle: str,
    purpose: str,
    tiles: list[dict[str, Any]],
    reason: str,
) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "id": screen_id,
        "domain": domain,
        "mode": "cockpit",
        "title": title,
        "subtitle": subtitle,
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "tiles": tiles,
        "noWorkflowReason": reason,
        "agentContract": {
            "businessPurpose": purpose,
            "examplePrompts": [f"Oeffne {title}."],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": f"[data-testid='screen-{screen_id}']"},
        },
        "layout": _capture_cockpit_layout(),
    }


def build_fuhrpark_uebersicht_screen_definition() -> dict[str, Any]:
    return _capture_cockpit(
        screen_id="fuhrpark/uebersicht",
        domain="logistics",
        title="Fuhrpark",
        subtitle="Einstieg",
        purpose="Vom Fuhrpark in Stammdaten, Rechnungen, Kosten und Belege springen.",
        reason="Die Uebersicht hat keinen eigenen Belegstatus. Jede Kachel oeffnet die bestehende Maske.",
        tiles=[
            _nav_tile("klassisch", "Fuhrpark (klassisch)", "/fuhrpark/fuhrpark-klassisch"),
            _nav_tile("stammdaten", "Stammdaten", "/fuhrpark/fuhrpark-stammdaten"),
            _nav_tile("rechnungen", "Rechnungen", "/fuhrpark/fuhrpark-rechnungen"),
            _nav_tile("auswertung", "Auswertungen", "/fuhrpark/fuhrpark-auswertung-kosten-pro-fahrzeug"),
            _nav_tile("belege", "Ausgehende Belege und Dokumente", "/fuhrpark/ausgehende-belege-dokumente"),
        ],
    )


def build_strecke_dokumente_drucken_screen_definition() -> dict[str, Any]:
    return _capture_cockpit(
        screen_id="strecke/dokumente-drucken",
        domain="logistics",
        title="Strecken-Dokumente drucken",
        subtitle="Druckauswahl",
        purpose="Fracht, Paket, Versand-Avis und Produktion zum Druck oeffnen.",
        reason="Die Auswahl druckt nicht selbst. Jede Kachel oeffnet die bestehende Druckmaske.",
        tiles=[
            _nav_tile("fracht", "Frachtdokumente", "/versand/frachtdokumente"),
            _nav_tile("paket", "Paket-Etiketten", "/versand/paket-etikett"),
            _nav_tile("avis", "Versand-Avis", "/versand/versand-avis"),
            _nav_tile("produktion", "Produktions-Dokumente", "/produktion/produktions-dokumente-drucken"),
        ],
    )


def build_nawaro_ernterklaerung_drucken_screen_definition() -> dict[str, Any]:
    return _capture_cockpit(
        screen_id="strecke/nawaro-ernterklaerung-drucken",
        domain="agrar",
        title="NaWaRo-Ernterklärung drucken",
        subtitle="Mitteilungsdruck",
        purpose="Die Ernterklaerung ueber den NaWaRo-Mitteilungsdruck ausgeben.",
        reason="Der Druck haengt an der Mitteilung. Diese Maske oeffnet nur den bestehenden Druck.",
        tiles=[
            _nav_tile("mitteilung", "NaWaRo-Mitteilung drucken", "/nawaro/mitteilung-drucken"),
        ],
    )


def build_fuhrpark_fahrzeuge_screen_definition() -> dict[str, Any]:
    """Fahrzeugbestand. Anlegen und Oeffnen bleiben an der bestehenden Erfassung."""
    return {
        "schemaVersion": 1,
        "id": "fuhrpark/fahrzeuge",
        "domain": "logistics",
        "mode": "list",
        "title": "Fahrzeuge",
        "subtitle": "Fahrzeuge suchen und öffnen",
        "adapter": {"type": "native", "sourceId": "fuhrpark/fahrzeuge", "temporary": False},
        "dataSources": [
            {"key": "list", "endpoint": "/api/v1/fuhrpark/fahrzeuge", "pageSize": 200},
        ],
        "actions": [
            {
                "key": "neu",
                "label": "Neues Fahrzeug",
                "command": "vehicle.create",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Oeffnet die bestehende Fahrzeug-Erfassung.",
            },
        ],
        "tables": [
            {
                "key": "list",
                "label": "Fahrzeuge",
                "dataSourceKey": "list",
                "serverPagination": False,
                "pageSize": 200,
                "virtualized": True,
                "rowHeight": 36,
                "rowRouteTemplate": "/fuhrpark/fahrzeug/{id}",
                "columns": [
                    {"key": "kennzeichen", "label": "Kennzeichen", "sortable": True, "filterable": True, "priority": "primary"},
                    {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
                    {"key": "typ", "label": "Typ", "filterable": True, "priority": "secondary"},
                    {"key": "kilometerstand", "label": "km-Stand", "numeric": True, "sortable": True, "priority": "secondary"},
                    {"key": "ro_nummer", "label": "RO-Nr.", "sortable": True, "priority": "tertiary"},
                    {"key": "naechste_inspektion", "label": "Inspektion", "renderKind": "date", "sortable": True, "priority": "tertiary"},
                ],
            },
        ],
        "noWorkflowReason": "Status und Fristen haengen am Fahrzeug. Diese Liste sucht und oeffnet es.",
        "agentContract": {
            "businessPurpose": "Fahrzeuge nach Kennzeichen, Typ und Status suchen und in die Erfassung oeffnen.",
            "examplePrompts": ["Welche Fahrzeuge sind verfuegbar?"],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='screen-fuhrpark/fahrzeuge']", "primaryAction": "[data-testid='action-neu']"},
        },
        "layout": _capture_worklist_layout(),
        "performance": {
            "initialPayloadBudgetKb": 40,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_logistik_frachtbrief_screen_definition() -> dict[str, Any]:
    """Transportbeleg-Liste. Anlegen geschieht über die Verladung, nicht hier."""
    return {
        "schemaVersion": 1,
        "id": "logistik/frachtbrief",
        "domain": "logistics",
        "mode": "list",
        "title": "Frachtbriefe",
        "subtitle": "Transportbeleg. Der Lieferschein bleibt der Warenbeleg.",
        "adapter": {"type": "native", "sourceId": "logistik/frachtbrief", "temporary": False},
        "dataSources": [
            {"key": "list", "endpoint": "/api/v1/logistik/frachtbriefe", "pageSize": 100},
        ],
        "actions": [
            {
                "key": "verladung",
                "label": "Zur Verladung",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Oeffnet die Verladung. Dort entsteht der Frachtbrief.",
            },
        ],
        "tables": [
            {
                "key": "list",
                "label": "Frachtbriefe",
                "dataSourceKey": "list",
                "serverPagination": False,
                "pageSize": 100,
                "virtualized": True,
                "rowHeight": 36,
                "columns": [
                    {"key": "nummer", "label": "Frachtbrief-Nr.", "sortable": True, "filterable": True, "width": 150},
                    {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "width": 110},
                    {"key": "absender", "label": "Absender", "width": 160},
                    {"key": "empfaenger", "label": "Empfänger", "sortable": True, "width": 160},
                    {"key": "kennzeichen", "label": "LKW", "filterable": True, "width": 120},
                    {"key": "artikel", "label": "Ware", "width": 160},
                    {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "width": 100},
                    {"key": "lieferschein_ref", "label": "Lieferschein", "width": 140},
                    {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "width": 120},
                ],
            },
        ],
        "noWorkflowReason": "Der Frachtbrief ist der Transportbeleg der Sendung. Statuswechsel haengen an Versand und Zustellung.",
        "agentContract": {
            "businessPurpose": "Transportbelege nach Nummer, Empfaenger und Kennzeichen sichten. Der Lieferschein bleibt der Warenbeleg.",
            "examplePrompts": ["Welche Frachtbriefe sind noch erstellt?"],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='screen-logistik/frachtbrief']", "primaryAction": "[data-testid='action-verladung']"},
        },
        "layout": _capture_worklist_layout(),
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_logistik_verladung_screen_definition() -> dict[str, Any]:
    """Verladung führt die Beförderungsdaten, aus denen der Frachtbrief entsteht."""
    return {
        "schemaVersion": 1,
        "id": "logistik/verladung",
        "domain": "logistics",
        "mode": "list",
        "title": "Verladung",
        "subtitle": "Fahrzeug, Ware, Menge und Orte. Der Frachtbrief entsteht beim Abschluss.",
        "adapter": {"type": "native", "sourceId": "logistik/verladung", "temporary": False},
        "dataSources": [
            {"key": "list", "endpoint": "/api/v1/verladung", "pageSize": 100},
        ],
        "actions": [
            {
                "key": "neu",
                "label": "Neue Beladung",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Oeffnet die bestehende LKW-Beladung.",
            },
        ],
        "tables": [
            {
                "key": "list",
                "label": "Verladung",
                "dataSourceKey": "list",
                "serverPagination": False,
                "pageSize": 100,
                "virtualized": True,
                "rowHeight": 36,
                "columns": [
                    {"key": "kennzeichen", "label": "LKW", "sortable": True, "filterable": True, "width": 120},
                    {"key": "fahrer", "label": "Fahrer", "width": 140},
                    {"key": "artikel", "label": "Ware", "width": 160},
                    {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "width": 90},
                    {"key": "einheit", "label": "Einheit", "width": 70},
                    {"key": "ladeort", "label": "Ladeort", "width": 140},
                    {"key": "zielort", "label": "Ablieferstelle", "width": 140},
                    {"key": "kunde", "label": "Empfänger", "width": 140},
                    {"key": "lieferschein_nr", "label": "Lieferschein", "filterable": True, "width": 140},
                    {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "width": 110},
                    {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "width": 120},
                ],
            },
        ],
        "noWorkflowReason": "Die Verladung ist die Ausführung. Der Frachtbrief wird erzeugt, sobald sie verladen ist.",
        "agentContract": {
            "businessPurpose": "Beladungen nach Kennzeichen, Ware und Lieferschein sichten und eine neue Beladung öffnen.",
            "examplePrompts": ["Welche Verladungen sind noch geplant?"],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='screen-logistik/verladung']", "primaryAction": "[data-testid='action-neu']"},
        },
        "layout": _capture_worklist_layout(),
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_logistik_tourenplanung_screen_definition() -> dict[str, Any]:
    """Ein Dispositionsvorgang. Die Seite liefert Touren, Fahrzeuge und Fahrer."""
    return {
        "schemaVersion": 1,
        "id": "logistik/tourenplanung",
        "domain": "logistics",
        "mode": "cockpit",
        "title": "Tourenplanung",
        "subtitle": "Lieferschein, Fahrzeug und Fahrer, danach die Ampel",
        "adapter": {"type": "native", "sourceId": "logistik/tourenplanung", "temporary": False},
        "dataSources": [
            {"key": "touren", "endpoint": "/api/v1/logistik/tours", "pageSize": 200},
            {"key": "fahrzeuge", "endpoint": "/api/v1/fuhrpark/fahrzeuge", "pageSize": 200},
            {"key": "fahrer", "endpoint": "/api/v1/transporte/fahrer", "pageSize": 200},
        ],
        "fields": [
            {"key": "datum", "label": "Datum", "type": "date", "readOnly": True},
            {"key": "tour_id", "label": "Tour", "type": "text", "readOnly": True},
            {"key": "tour_status", "label": "Status", "type": "text", "readOnly": True},
            {"key": "ziel", "label": "Ziel", "type": "text", "readOnly": True},
            {"key": "lieferschein", "label": "Lieferschein", "type": "text", "placeholder": "Lieferscheinnummer"},
            {"key": "fahrzeug_id", "label": "Fahrzeug", "type": "select", "dataSourceKey": "fahrzeuge"},
            {"key": "fahrer_id", "label": "Fahrer", "type": "select", "dataSourceKey": "fahrer"},
        ],
        "summary": [
            {"key": "heute", "label": "Touren heute", "value": "0"},
            {"key": "geplant", "label": "Geplant", "value": "0"},
            {"key": "unterwegs", "label": "Unterwegs", "value": "0"},
            {"key": "abgeschlossen", "label": "Abgeschlossen", "value": "0"},
        ],
        "workflow": {"processKey": "logistik.tourenplanung"},
        "actions": [
            {
                "key": "dispo",
                "label": "Dispo-Arbeitsraum",
                "command": "tour.openWorkspace",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Oeffnet den bestehenden Dispo-Arbeitsraum.",
            },
            {
                "key": "aufloesen",
                "label": "Auflösen",
                "command": "tour.resolveDeliveryNote",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Liest den Lieferschein und setzt das Ziel.",
            },
            {
                "key": "anlegen",
                "label": "Tour anlegen",
                "command": "tour.create",
                "enabledWhen": "tour.canCreate",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Legt die Tour aus dem aufgeloesten Lieferschein an.",
            },
        ],
        "tables": [
            {
                "key": "touren",
                "label": "Touren",
                "dataSourceKey": "touren",
                "serverPagination": False,
                "pageSize": 50,
                "virtualized": True,
                "rowHeight": 44,
                "rowDetail": False,
                "rowActions": [
                    {"key": "beladung", "label": "Beladung", "command": "tour.openLoading", "dangerLevel": "safe"},
                    {"key": "hinweise", "label": "Hinweise", "command": "tour.showHints", "dangerLevel": "safe"},
                    {
                        "key": "storno",
                        "label": "Stornieren",
                        "command": "tour.cancel",
                        "dangerLevel": "moderate",
                        "requiresConfirmation": True,
                        "visibleWhen": {"field": "status", "values": ["geplant"]},
                    },
                ],
                "columns": [
                    {"key": "ziel", "label": "Ziel", "priority": "primary"},
                    {"key": "kennzeichen", "label": "Fahrzeug", "priority": "primary"},
                    {"key": "fahrer_name", "label": "Fahrer", "priority": "primary"},
                    {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
                    {"key": "stopps", "label": "Stopps", "numeric": True, "priority": "secondary"},
                    {"key": "strecke", "label": "Strecke", "priority": "secondary"},
                    {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "tertiary"},
                ],
            },
        ],
        "agentContract": {
            "businessPurpose": "Eine Tour aus Lieferschein, Fahrzeug und Fahrer disponieren. Die Ampel folgt der Besetzung.",
            "examplePrompts": ["Welche Touren haben heute noch keinen Fahrer?"],
            "sensitiveFields": [],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-logistik/tourenplanung']",
                "primaryAction": "[data-testid='action-anlegen']",
            },
        },
        "layout": {
            "floorplan": "cockpit",
            "density": "compact",
            "contextRail": "workflow",
            "tableProfile": "standard",
            "columnNavigation": "single",
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
            "summaryPlacement": "footer",
            "statusPlacement": "afterFields",
        },
        "performance": {
            "initialPayloadBudgetKb": 48,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_transporte_fahrer_screen_definition() -> dict[str, Any]:
    """Fahrerstamm. Touren heute zaehlt die Seite aus den Touren."""
    return {
        "schemaVersion": 1,
        "id": "transporte/fahrer",
        "domain": "logistics",
        "mode": "list",
        "title": "Fahrer",
        "subtitle": "Fahrer suchen und öffnen",
        "adapter": {"type": "native", "sourceId": "transporte/fahrer", "temporary": False},
        "dataSources": [
            {"key": "list", "endpoint": "/api/v1/transporte/fahrer", "pageSize": 200},
            {"key": "touren", "endpoint": "/api/v1/logistik/tours", "pageSize": 200},
        ],
        "summary": [
            {"key": "gesamt", "label": "Fahrer gesamt", "value": "0"},
            {"key": "verfuegbar", "label": "Verfügbar", "value": "0"},
            {"key": "unterwegs", "label": "Unterwegs", "value": "0"},
            {"key": "touren_heute", "label": "Touren heute", "value": "0"},
        ],
        "actions": [
            {
                "key": "neu",
                "label": "Neuer Fahrer",
                "command": "driver.create",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Oeffnet das bestehende Fahrerformular.",
            },
            {
                "key": "verfuegbar",
                "label": "Verfügbaren Fahrer öffnen",
                "command": "driver.openAvailable",
                "enabledWhen": "driver.hasAvailable",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Oeffnet den ersten verfuegbaren Fahrer.",
            },
            {
                "key": "touren",
                "label": "Tourenplanung",
                "command": "driver.openTours",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Wechselt in die Tourenplanung.",
            },
            {
                "key": "dokumente",
                "label": "Dokumente",
                "command": "driver.openDocuments",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Oeffnet die Dokumentenablage.",
            },
            {
                "key": "export",
                "label": "Export",
                "command": "driver.export",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Exportiert die sichtbare Fahrerliste.",
            },
        ],
        "tables": [
            {
                "key": "list",
                "label": "Fahrer",
                "dataSourceKey": "list",
                "serverPagination": False,
                "pageSize": 200,
                "virtualized": True,
                "rowHeight": 44,
                "rowRouteTemplate": "/transporte/fahrer/{id}",
                "columns": [
                    {"key": "name", "label": "Name", "sortable": True, "filterable": True, "priority": "primary"},
                    {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
                    {"key": "fahrzeug", "label": "Fahrzeug", "filterable": True, "priority": "secondary"},
                    {"key": "fuehrerschein", "label": "Führerschein", "priority": "secondary"},
                    {"key": "touren_heute", "label": "Touren heute", "numeric": True, "sortable": True, "priority": "primary"},
                ],
            },
        ],
        "noWorkflowReason": "Der Status haengt am Fahrer. Touren heute wird aus den Touren gezaehlt.",
        "agentContract": {
            "businessPurpose": "Fahrer nach Name und Status suchen. Touren heute ist die Zahl der heutigen Touren.",
            "examplePrompts": ["Welche Fahrer sind heute unterwegs?"],
            "sensitiveFields": [],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-transporte/fahrer']",
                "primaryAction": "[data-testid='action-neu']",
            },
        },
        "layout": _capture_worklist_layout(),
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_logistik_tour_fracht_arbeitsraum_screen_definition() -> dict[str, Any]:
    """Kombinierte Sicht. Die Ampel folgt Touren, Frachtbriefen und Chargensperren."""
    return {
        "schemaVersion": 1,
        "id": "logistik/tour-fracht-arbeitsraum",
        "domain": "logistics",
        "mode": "cockpit",
        "title": "Tour & Fracht",
        "subtitle": "Disposition, Frachtbriefe und Tarife",
        "adapter": {"type": "native", "sourceId": "logistik/tour-fracht-arbeitsraum", "temporary": False},
        "dataSources": [
            {"key": "touren", "endpoint": "/api/v1/logistik/tours", "pageSize": 50},
            {"key": "fracht", "endpoint": "/api/v1/logistik/frachtbriefe", "pageSize": 50},
            {"key": "tarife", "endpoint": "/api/v1/logistik/freight-tariffs", "pageSize": 50},
        ],
        "summary": [
            {"key": "heute", "label": "Touren heute", "value": "0"},
            {"key": "geplant", "label": "Geplant", "value": "0"},
            {"key": "fracht", "label": "Frachtbriefe", "value": "0"},
            {"key": "tarife", "label": "Aktive Tarife", "value": "0"},
            {"key": "probe", "label": "Probe", "value": "—"},
        ],
        "workflow": {"processKey": "logistik.tour-fracht-arbeitsraum"},
        "actions": [
            {
                "key": "touren",
                "label": "Zur Tourenplanung",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Wechselt in die Tourenplanung.",
            },
            {
                "key": "fracht",
                "label": "Zu Frachtbriefen",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Wechselt zu den Frachtbriefen.",
            },
            {
                "key": "tabellen",
                "label": "Frachttabellen",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Oeffnet die Frachttabellen.",
            },
            {
                "key": "probe",
                "label": "Probe berechnen",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Simuliert die Frachtkosten des ersten aktiven Tarifs.",
            },
        ],
        "tables": [
            {
                "key": "touren",
                "label": "Touren",
                "dataSourceKey": "touren",
                "serverPagination": False,
                "pageSize": 20,
                "virtualized": True,
                "rowHeight": 44,
                "rowDetail": False,
                "columns": [
                    {"key": "ziel", "label": "Ziel", "priority": "primary"},
                    {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
                    {"key": "fahrzeug", "label": "Fahrzeug", "priority": "secondary"},
                    {"key": "stopps", "label": "Stopps", "numeric": True, "priority": "tertiary"},
                ],
            },
            {
                "key": "fracht",
                "label": "Frachtbriefe",
                "dataSourceKey": "fracht",
                "serverPagination": False,
                "pageSize": 20,
                "virtualized": True,
                "rowHeight": 44,
                "rowDetail": False,
                "columns": [
                    {"key": "nummer", "label": "Nummer", "priority": "primary"},
                    {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
                    {"key": "kennzeichen", "label": "Fahrzeug", "priority": "secondary"},
                    {"key": "empfaenger", "label": "Empfänger", "priority": "tertiary"},
                ],
            },
            {
                "key": "tarife",
                "label": "Tarife",
                "dataSourceKey": "tarife",
                "serverPagination": False,
                "pageSize": 20,
                "virtualized": True,
                "rowHeight": 44,
                "rowDetail": False,
                "rowActions": [
                    {
                        "key": "storno",
                        "label": "Stornieren",
                        "dangerLevel": "moderate",
                        "visibleWhen": {"field": "stornierbar", "values": [True]},
                    },
                ],
                "columns": [
                    {"key": "carrier", "label": "Spediteur", "filterable": True, "priority": "primary"},
                    {"key": "status", "label": "Status", "renderKind": "status", "priority": "primary"},
                    {"key": "preis", "label": "Preis je 100 kg", "numeric": True, "priority": "secondary"},
                ],
            },
        ],
        "agentContract": {
            "businessPurpose": "Touren, Frachtbriefe und Tarife gemeinsam sichten. Die Ampel folgt Bestand und Chargensperre.",
            "examplePrompts": ["Welche Frachtbriefe sind noch nicht versendet?"],
            "sensitiveFields": [],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-logistik/tour-fracht-arbeitsraum']",
                "primaryAction": "[data-testid='action-probe']",
            },
        },
        "layout": {
            "floorplan": "cockpit",
            "density": "compact",
            "contextRail": "workflow",
            "tableProfile": "standard",
            "columnNavigation": "single",
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
            "summaryPlacement": "footer",
            "statusPlacement": "afterFields",
        },
        "performance": {
            "initialPayloadBudgetKb": 48,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_logistik_frachttabellen_screen_definition() -> dict[str, Any]:
    """Frachtstaffeln. Die Seite legt Tabellen und Positionen an."""
    return {
        "schemaVersion": 1,
        "id": "logistik/frachttabellen",
        "domain": "logistics",
        "mode": "list",
        "title": "Frachttabellen",
        "subtitle": "Frachtkosten-Staffeln nach Menge und Einheit",
        "adapter": {"type": "native", "sourceId": "logistik/frachttabellen", "temporary": False},
        "dataSources": [
            {"key": "tabellen", "endpoint": "/api/v1/logistik/frachttabellen", "pageSize": 100},
        ],
        "fields": [
            {"key": "tabelle_nr", "label": "Tabelle-Nr", "type": "text", "placeholder": "Nummer"},
            {"key": "bezeichnung", "label": "Bezeichnung", "type": "text"},
            {"key": "einheit", "label": "Einheit", "type": "text", "placeholder": "z. B. t"},
            {"key": "waehrung", "label": "Währung", "type": "text"},
            {"key": "staffel", "label": "Staffel", "type": "text", "readOnly": True},
            {"key": "ab_menge", "label": "Ab-Menge", "type": "number"},
            {"key": "frachtsatz_eur", "label": "Frachtsatz EUR", "type": "number"},
            {"key": "mindestfracht_eur", "label": "Mindestfracht EUR", "type": "number"},
        ],
        "summary": [
            {"key": "tabellen", "label": "Tabellen", "value": "0"},
            {"key": "positionen", "label": "Positionen", "value": "0"},
        ],
        "workflow": {"processKey": "logistik.frachttabellen"},
        "actions": [
            {
                "key": "anlegen",
                "label": "Tabelle speichern",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Legt die Frachttabelle an.",
            },
            {
                "key": "position",
                "label": "Position anlegen",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Haengt eine Staffelposition an die gewaehlte Tabelle.",
            },
        ],
        "tables": [
            {
                "key": "tabellen",
                "label": "Frachttabellen",
                "dataSourceKey": "tabellen",
                "serverPagination": False,
                "pageSize": 100,
                "virtualized": True,
                "rowHeight": 44,
                "rowDetail": False,
                "rowActions": [
                    {
                        "key": "loeschen",
                        "label": "Löschen",
                        "dangerLevel": "destructive",
                        "disabledWhen": {"field": "gesperrt", "values": [True]},
                    },
                ],
                "columns": [
                    {"key": "tabelle_nr", "label": "Nummer", "sortable": True, "filterable": True, "priority": "primary"},
                    {"key": "bezeichnung", "label": "Bezeichnung", "filterable": True, "priority": "primary"},
                    {"key": "einheit", "label": "Einheit", "priority": "secondary"},
                    {"key": "waehrung", "label": "Währung", "priority": "tertiary"},
                ],
            },
            {
                "key": "positionen",
                "label": "Staffel",
                "dataSourceKey": "tabellen",
                "serverPagination": False,
                "pageSize": 50,
                "virtualized": True,
                "rowHeight": 44,
                "rowDetail": False,
                "columns": [
                    {"key": "ab_menge", "label": "Ab-Menge", "numeric": True, "sortable": True, "priority": "primary"},
                    {"key": "frachtsatz_eur", "label": "Frachtsatz EUR", "numeric": True, "priority": "primary"},
                    {"key": "mindestfracht_eur", "label": "Mindestfracht EUR", "numeric": True, "priority": "secondary"},
                ],
            },
        ],
        "noWorkflowReason": "Die Staffel haengt an der Tabelle. Der Stand folgt den Positionen.",
        "agentContract": {
            "businessPurpose": "Frachttabellen und ihre Mengenstaffel anlegen. Der Stand folgt den Positionen.",
            "examplePrompts": ["Welche Frachttabelle hat noch keine Staffel?"],
            "sensitiveFields": [],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-logistik/frachttabellen']",
                "primaryAction": "[data-testid='action-anlegen']",
            },
        },
        "layout": {
            "floorplan": "worklist",
            "density": "compact",
            "contextRail": "none",
            "tableProfile": "standard",
            "columnNavigation": "single",
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
            "summaryPlacement": "footer",
            "statusPlacement": "afterFields",
        },
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_logistik_versandprofile_screen_definition() -> dict[str, Any]:
    """Versandprofile und Lieferavise. Die Seite speichert, der Builder zeichnet die Register."""
    versandarten = [
        {"value": "email", "label": "E-Mail"},
        {"value": "fax", "label": "Fax"},
        {"value": "edi", "label": "EDI"},
        {"value": "post", "label": "Post"},
        {"value": "api", "label": "API"},
    ]
    return {
        "schemaVersion": 1,
        "id": "logistik/versandprofile",
        "domain": "logistics",
        "mode": "list",
        "title": "Versandprofile",
        "subtitle": "Versandkonfiguration und Liefervoranmeldungen",
        "adapter": {"type": "native", "sourceId": "logistik/versandprofile", "temporary": False},
        "dataSources": [
            {"key": "profile", "endpoint": "/api/v1/logistik/versand/profile", "pageSize": 100},
            {"key": "avise", "endpoint": "/api/v1/logistik/versand/avise", "pageSize": 100},
        ],
        "summary": [
            {"key": "profile", "label": "Profile", "value": "0"},
            {"key": "avise", "label": "Avise", "value": "0"},
        ],
        "workflow": {"processKey": "logistik.versandprofile"},
        "actions": [
            {
                "key": "profil",
                "label": "Profil speichern",
                "command": "versand.saveProfile",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Legt das Versandprofil an.",
            },
            {
                "key": "avis",
                "label": "Avis speichern",
                "command": "versand.saveAvis",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Legt ein Lieferavis an.",
            },
        ],
        "tabs": [
            {
                "key": "profile",
                "label": "Versandprofile",
                "fields": [
                    {"key": "profil_nr", "label": "Profil-Nr", "type": "text", "placeholder": "Nummer"},
                    {"key": "bezeichnung", "label": "Bezeichnung", "type": "text"},
                    {"key": "versandart", "label": "Versandart", "type": "select", "options": versandarten},
                    {"key": "absender_email", "label": "Absender E-Mail", "type": "text"},
                    {"key": "absender_name", "label": "Absender Name", "type": "text"},
                    {"key": "betreff_vorlage", "label": "Betreff-Vorlage", "type": "text"},
                ],
                "tables": [
                    {
                        "key": "profile",
                        "label": "Versandprofile",
                        "dataSourceKey": "profile",
                        "serverPagination": False,
                        "pageSize": 50,
                        "virtualized": True,
                        "rowHeight": 44,
                        "rowDetail": False,
                        "rowActions": [
                            {
                                "key": "loeschen",
                                "label": "Löschen",
                                "command": "versand.deleteProfile",
                                "dangerLevel": "moderate",
                                "disabledWhen": {"field": "gesperrt", "values": [True]},
                            },
                        ],
                        "columns": [
                            {"key": "profil_nr", "label": "Nummer", "sortable": True, "filterable": True, "priority": "primary"},
                            {"key": "bezeichnung", "label": "Bezeichnung", "filterable": True, "priority": "primary"},
                            {"key": "versandart", "label": "Versandart", "priority": "secondary"},
                            {"key": "absender_email", "label": "Absender", "priority": "tertiary"},
                        ],
                    },
                ],
            },
            {
                "key": "avise",
                "label": "Lieferavise",
                "fields": [
                    {"key": "avis_datum", "label": "Avis-Datum", "type": "date"},
                    {"key": "lieferdatum_erwartet", "label": "Lieferdatum", "type": "date"},
                    {"key": "lieferant_nr", "label": "Lieferant-Nr", "type": "text"},
                    {"key": "kunden_nr", "label": "Kunden-Nr", "type": "text"},
                    {"key": "artikel_nr", "label": "Artikel-Nr", "type": "text"},
                    {"key": "menge", "label": "Menge", "type": "number"},
                    {"key": "notiz", "label": "Notiz", "type": "text"},
                ],
                "tables": [
                    {
                        "key": "avise",
                        "label": "Lieferavise",
                        "dataSourceKey": "avise",
                        "serverPagination": False,
                        "pageSize": 50,
                        "virtualized": True,
                        "rowHeight": 44,
                        "rowDetail": False,
                        "columns": [
                            {"key": "avis_datum", "label": "Avis-Datum", "renderKind": "date", "sortable": True, "filterable": True, "priority": "primary"},
                            {"key": "lieferdatum_erwartet", "label": "Lieferdatum", "renderKind": "date", "priority": "primary"},
                            {"key": "lieferant_nr", "label": "Lieferant", "priority": "secondary"},
                            {"key": "artikel_nr", "label": "Artikel", "priority": "secondary"},
                            {"key": "menge", "label": "Menge", "numeric": True, "priority": "tertiary"},
                            {"key": "notiz", "label": "Notiz", "priority": "tertiary"},
                        ],
                    },
                ],
            },
        ],
        "noWorkflowReason": "Der Stand folgt den hinterlegten Profilen.",
        "agentContract": {
            "businessPurpose": "Versandprofile und Lieferavise anlegen. Der Stand folgt den Profilen.",
            "examplePrompts": ["Welches Versandprofil fehlt noch?"],
            "sensitiveFields": [],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-logistik/versandprofile']",
                "primaryAction": "[data-testid='action-profil']",
            },
        },
        "layout": {
            "floorplan": "worklist",
            "density": "compact",
            "contextRail": "none",
            "tableProfile": "standard",
            "columnNavigation": "single",
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
            "summaryPlacement": "footer",
            "statusPlacement": "afterFields",
        },
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": True,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_fuhrpark_terminarten_screen_definition() -> dict[str, Any]:
    """Terminarten des Fuhrparks. Die Seite speichert, der Builder zeichnet die Liste."""
    return {
        "schemaVersion": 1,
        "id": "fuhrpark/terminarten",
        "domain": "logistics",
        "mode": "list",
        "title": "Terminarten",
        "subtitle": "Wartungsintervalle nach Monaten und Kilometern",
        "adapter": {"type": "native", "sourceId": "fuhrpark/terminarten", "temporary": False},
        "dataSources": [
            {"key": "terminarten", "endpoint": "/api/v1/fuhrpark/terminarten", "pageSize": 100},
        ],
        "summary": [
            {"key": "terminarten", "label": "Terminarten", "value": "0"},
        ],
        "fields": [
            {"key": "terminart", "label": "Terminart", "type": "text", "placeholder": "Bezeichnung"},
            {"key": "intervall_monate", "label": "Intervall Monate", "type": "number"},
            {"key": "intervall_km", "label": "Intervall km", "type": "number"},
        ],
        "workflow": {"processKey": "fuhrpark.terminarten"},
        "actions": [
            {
                "key": "speichern",
                "label": "Speichern",
                "command": "fuhrpark.saveTerminart",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Legt eine Terminart an oder aktualisiert die gewaehlte.",
            },
            {
                "key": "neu",
                "label": "Neu",
                "command": "fuhrpark.newTerminart",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Leert die Eingabe fuer eine neue Terminart.",
            },
        ],
        "tables": [
            {
                "key": "terminarten",
                "label": "Terminarten",
                "dataSourceKey": "terminarten",
                "serverPagination": False,
                "pageSize": 50,
                "virtualized": True,
                "rowHeight": 44,
                "rowDetail": False,
                "rowActions": [
                    {
                        "key": "loeschen",
                        "label": "Löschen",
                        "command": "fuhrpark.deleteTerminart",
                        "dangerLevel": "moderate",
                        "disabledWhen": {"field": "gesperrt", "values": [True]},
                    },
                ],
                "columns": [
                    {"key": "terminart", "label": "Terminart", "sortable": True, "filterable": True, "priority": "primary"},
                    {"key": "intervall_monate", "label": "Monate", "numeric": True, "priority": "secondary"},
                    {"key": "intervall_km", "label": "Kilometer", "numeric": True, "priority": "tertiary"},
                ],
            },
        ],
        "noWorkflowReason": "Der Stand folgt den hinterlegten Terminarten.",
        "agentContract": {
            "businessPurpose": "Wartungsintervalle der Terminarten anlegen und aendern.",
            "examplePrompts": ["Welche Terminart hat noch kein Kilometerintervall?"],
            "sensitiveFields": [],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-fuhrpark/terminarten']",
                "primaryAction": "[data-testid='action-speichern']",
            },
        },
        "layout": {
            "floorplan": "worklist",
            "density": "compact",
            "contextRail": "none",
            "tableProfile": "standard",
            "columnNavigation": "single",
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
            "summaryPlacement": "footer",
            "statusPlacement": "afterFields",
        },
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_fuhrpark_rechnungen_screen_definition() -> dict[str, Any]:
    """Fuhrpark-Rechnungen. Die Seite speichert, der Builder zeichnet die Liste."""
    return {
        "schemaVersion": 1,
        "id": "fuhrpark/rechnungen",
        "domain": "logistics",
        "mode": "list",
        "title": "Fuhrpark-Rechnungen",
        "subtitle": "Kostenbelege zu Fahrzeugen",
        "adapter": {"type": "native", "sourceId": "fuhrpark/rechnungen", "temporary": False},
        "dataSources": [
            {"key": "rechnungen", "endpoint": "/api/v1/fuhrpark/rechnungen", "pageSize": 100},
        ],
        "summary": [
            {"key": "rechnungen", "label": "Rechnungen", "value": "0"},
            {"key": "betrag", "label": "Betrag EUR", "value": "0"},
        ],
        "fields": [
            {"key": "rechnungs_nr", "label": "Rechnungs-Nr", "type": "text", "placeholder": "Nummer"},
            {"key": "datum", "label": "Datum", "type": "date"},
            {"key": "fahrzeug_kennzeichen", "label": "Fahrzeug", "type": "text"},
            {"key": "sachkonto", "label": "Sachkonto", "type": "text"},
            {"key": "kostenart", "label": "Kostenart", "type": "text"},
            {"key": "betrag_eur", "label": "Betrag EUR", "type": "number"},
            {"key": "notiz", "label": "Notiz", "type": "text"},
        ],
        "workflow": {"processKey": "fuhrpark.rechnungen"},
        "actions": [
            {
                "key": "speichern",
                "label": "Speichern",
                "command": "fuhrpark.saveRechnung",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Legt eine Rechnung an oder aktualisiert die gewaehlte.",
            },
            {
                "key": "neu",
                "label": "Neu",
                "command": "fuhrpark.newRechnung",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Leert die Eingabe fuer eine neue Rechnung.",
            },
        ],
        "tables": [
            {
                "key": "rechnungen",
                "label": "Rechnungen",
                "dataSourceKey": "rechnungen",
                "serverPagination": False,
                "pageSize": 50,
                "virtualized": True,
                "rowHeight": 44,
                "rowDetail": False,
                "rowActions": [
                    {
                        "key": "loeschen",
                        "label": "Löschen",
                        "command": "fuhrpark.deleteRechnung",
                        "dangerLevel": "moderate",
                        "disabledWhen": {"field": "gesperrt", "values": [True]},
                    },
                ],
                "columns": [
                    {"key": "rechnungs_nr", "label": "Nummer", "sortable": True, "filterable": True, "priority": "primary"},
                    {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "primary"},
                    {"key": "fahrzeug_kennzeichen", "label": "Fahrzeug", "priority": "secondary"},
                    {"key": "betrag_eur", "label": "Betrag EUR", "numeric": True, "renderKind": "currency", "priority": "secondary"},
                    {"key": "sachkonto", "label": "Sachkonto", "priority": "tertiary"},
                    {"key": "kostenart", "label": "Kostenart", "priority": "tertiary"},
                    {"key": "notiz", "label": "Notiz", "priority": "tertiary"},
                ],
            },
        ],
        "noWorkflowReason": "Der Stand folgt den hinterlegten Rechnungen.",
        "agentContract": {
            "businessPurpose": "Fuhrpark-Rechnungen anlegen und aendern. Der Betrag folgt den Belegen.",
            "examplePrompts": ["Welche Fuhrpark-Rechnung hat noch kein Fahrzeug?"],
            "sensitiveFields": [],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-fuhrpark/rechnungen']",
                "primaryAction": "[data-testid='action-speichern']",
            },
        },
        "layout": {
            "floorplan": "worklist",
            "density": "compact",
            "contextRail": "none",
            "tableProfile": "financial",
            "columnNavigation": "single",
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
            "summaryPlacement": "footer",
            "statusPlacement": "afterFields",
        },
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_fuhrpark_ausgehende_dokumente_screen_definition() -> dict[str, Any]:
    """Belegtypen fuer ausgehende Dokumente. Die Seite speichert, der Builder zeichnet die Liste."""
    return {
        "schemaVersion": 1,
        "id": "fuhrpark/ausgehende-dokumente",
        "domain": "logistics",
        "mode": "list",
        "title": "Ausgehende Belege",
        "subtitle": "Belegtypen, Formulare und Zielmodule",
        "adapter": {"type": "native", "sourceId": "fuhrpark/ausgehende-dokumente", "temporary": False},
        "dataSources": [
            {"key": "dokumente", "endpoint": "/api/v1/fuhrpark/ausgehende-dokumente", "pageSize": 100},
        ],
        "summary": [
            {"key": "belege", "label": "Belege", "value": "0"},
            {"key": "ohne_formular", "label": "Ohne Formular", "value": "0"},
        ],
        "fields": [
            {"key": "beleg_typ", "label": "Beleg-Typ", "type": "text", "placeholder": "Bezeichnung"},
            {"key": "formular", "label": "Formular", "type": "text"},
            {"key": "ziel_modul", "label": "Ziel-Modul", "type": "text"},
            {"key": "beschreibung", "label": "Beschreibung", "type": "text"},
            {"key": "aktiv", "label": "Aktiv", "type": "boolean"},
        ],
        "workflow": {"processKey": "fuhrpark.ausgehende-dokumente"},
        "actions": [
            {
                "key": "speichern",
                "label": "Speichern",
                "command": "fuhrpark.saveDokument",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Legt einen Belegtyp an oder aktualisiert den gewaehlten.",
            },
            {
                "key": "neu",
                "label": "Neu",
                "command": "fuhrpark.newDokument",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Leert die Eingabe fuer einen neuen Belegtyp.",
            },
        ],
        "tables": [
            {
                "key": "dokumente",
                "label": "Belegtypen",
                "dataSourceKey": "dokumente",
                "serverPagination": False,
                "pageSize": 50,
                "virtualized": True,
                "rowHeight": 44,
                "rowDetail": False,
                "rowActions": [
                    {
                        "key": "loeschen",
                        "label": "Löschen",
                        "command": "fuhrpark.deleteDokument",
                        "dangerLevel": "moderate",
                        "disabledWhen": {"field": "gesperrt", "values": [True]},
                    },
                ],
                "columns": [
                    {"key": "beleg_typ", "label": "Beleg-Typ", "sortable": True, "filterable": True, "priority": "primary"},
                    {"key": "formular", "label": "Formular", "priority": "secondary"},
                    {"key": "ziel_modul", "label": "Ziel-Modul", "priority": "secondary"},
                    {"key": "beschreibung", "label": "Beschreibung", "priority": "tertiary"},
                    {"key": "aktiv", "label": "Aktiv", "priority": "tertiary"},
                ],
            },
        ],
        "tiles": [
            {"key": "frachtdokumente", "label": "Frachtdokumente", "targetScreenId": "versand/frachtdokumente", "targetRoute": "/versand/frachtdokumente"},
            {"key": "paket", "label": "Paket-Etikett", "targetScreenId": "versand/paket-etikett", "targetRoute": "/versand/paket-etikett"},
            {"key": "avis", "label": "Versand-Avis", "targetScreenId": "versand/versand-avis", "targetRoute": "/versand/versand-avis"},
            {"key": "produktion", "label": "Produktions-Dokumente", "targetScreenId": "produktion/dokumente-drucken", "targetRoute": "/produktion/produktions-dokumente-drucken"},
            {"key": "kommission", "label": "Kommissions-Aufträge", "targetScreenId": "verkauf/kommissions-auftraege", "targetRoute": "/verkauf/kommissions-auftraege"},
            {"key": "betrieb", "label": "Betriebs-Aufträge", "targetScreenId": "verkauf/betriebsauftrag", "targetRoute": "/verkauf/betriebs-auftraege"},
        ],
        "noWorkflowReason": "Der Stand folgt den Belegtypen und ihren Formularen.",
        "agentContract": {
            "businessPurpose": "Belegtypen fuer ausgehende Dokumente anlegen. Der Stand folgt dem Formular.",
            "examplePrompts": ["Welcher Belegtyp hat noch kein Formular?"],
            "sensitiveFields": [],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-fuhrpark/ausgehende-dokumente']",
                "primaryAction": "[data-testid='action-speichern']",
            },
        },
        "layout": {
            "floorplan": "worklist",
            "density": "compact",
            "contextRail": "none",
            "tableProfile": "standard",
            "columnNavigation": "single",
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
            "summaryPlacement": "footer",
            "statusPlacement": "afterFields",
        },
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_fuhrpark_fahrzeug_stamm_screen_definition() -> dict[str, Any]:
    """Fahrzeugakte. Die Seite speichert, der Builder zeichnet die Register."""
    return {
        "schemaVersion": 1,
        "id": "fuhrpark/fahrzeug-stamm",
        "domain": "logistics",
        "mode": "detail",
        "title": "Fahrzeug-Stamm",
        "subtitle": "Kennzeichen, Technik, Erwerb und Termine",
        "identityField": "kennzeichen",
        "adapter": {"type": "native", "sourceId": "fuhrpark/fahrzeug-stamm", "temporary": False},
        "dataSources": [
            {"key": "fahrzeug", "endpoint": "/api/v1/fuhrpark/fahrzeuge", "pageSize": 1},
        ],
        "summary": [
            {"key": "kilometerstand", "label": "Km-Stand", "value": "0"},
            {"key": "tuev", "label": "Naechster TUEV", "value": "offen"},
        ],
        "workflow": {"processKey": "fuhrpark.fahrzeug-stamm"},
        "actions": [
            {
                "key": "speichern",
                "label": "Speichern",
                "command": "fuhrpark.saveFahrzeug",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Legt das Fahrzeug an oder aktualisiert die Akte.",
            },
            {
                "key": "liste",
                "label": "Zur Liste",
                "command": "fuhrpark.openFahrzeugListe",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Wechselt zur Fahrzeugliste.",
            },
            {
                "key": "drucker",
                "label": "Drucker einrichten",
                "command": "fuhrpark.setupDrucker",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Hinterlegt den Drucker an der Fahrzeugakte.",
            },
            {
                "key": "drucken",
                "label": "Drucken",
                "command": "fuhrpark.printAkte",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Druckt die Fahrzeugakte.",
            },
            {
                "key": "unfall",
                "label": "Unfall-Anzeige",
                "command": "fuhrpark.reportUnfall",
                "kind": "secondary",
                "dangerLevel": "moderate",
                "zone": "footer",
                "stubReason": "Erfasst eine Unfallanzeige zum Fahrzeug.",
            },
            {
                "key": "loeschen",
                "label": "Fahrzeug löschen",
                "command": "fuhrpark.deleteFahrzeug",
                "kind": "secondary",
                "dangerLevel": "destructive",
                "zone": "footer",
                "requiresConfirmation": True,
                "stubReason": "Loescht die Fahrzeugakte nach Bestaetigung.",
            },
        ],
        "tabs": [
            {
                "key": "allgemein",
                "label": "Allgemein",
                "fields": [
                    {"key": "ro_nummer", "label": "RO-Nummer", "type": "text"},
                    {"key": "is_neu", "label": "Neu", "type": "boolean"},
                    {"key": "betrieb", "label": "Betrieb", "type": "text"},
                    {"key": "bereich", "label": "Bereich", "type": "text"},
                    {"key": "pol_kennzeichen", "label": "Pol. Kennzeichen", "type": "text"},
                    {"key": "kennzeichen", "label": "Kennzeichen", "type": "text"},
                ],
            },
            {
                "key": "technik",
                "label": "Technik",
                "fields": [
                    {"key": "verwendung", "label": "Verwendung", "type": "text"},
                    {"key": "kfz_brief_nummer", "label": "Kfz-Brief-Nummer", "type": "text"},
                    {"key": "typ", "label": "Typ", "type": "text"},
                    {"key": "schadstoffgruppe", "label": "Schadstoffgruppe", "type": "text"},
                    {"key": "leistung_kw", "label": "Leistung (kW)", "type": "number"},
                    {"key": "kraftstoff", "label": "Kraftstoff", "type": "text"},
                    {"key": "fahrgestellnummer", "label": "Fahrgestellnummer", "type": "text"},
                    {"key": "erstzulassung", "label": "Erstzulassung", "type": "date"},
                    {"key": "ausstattung", "label": "Ausstattung", "type": "textarea"},
                    {"key": "fahrtenschreiber_vorhanden", "label": "Fahrtenschreiber vorhanden", "type": "boolean"},
                    {"key": "ahk_vorhanden", "label": "AHK vorhanden", "type": "boolean"},
                    {"key": "ladekran_vorhanden", "label": "Ladekran vorhanden", "type": "boolean"},
                    {"key": "fahrer_name", "label": "Fahrer Name", "type": "text"},
                    {"key": "fahrer_vorname", "label": "Fahrer Vorname", "type": "text"},
                ],
            },
            {
                "key": "erwerb",
                "label": "Erwerb",
                "fields": [
                    {"key": "bestellnummer", "label": "Bestellnummer", "type": "text"},
                    {"key": "bestelldatum", "label": "Bestelldatum", "type": "date"},
                    {"key": "haendler", "label": "Haendler", "type": "text"},
                    {"key": "zustand", "label": "Zustand", "type": "text"},
                    {"key": "kaufsumme_eur", "label": "Kaufsumme EUR", "type": "number"},
                    {"key": "kaufdatum", "label": "Kaufdatum", "type": "date"},
                    {"key": "verkaufsdatum", "label": "Verkaufsdatum", "type": "date"},
                    {"key": "abmeldedatum", "label": "Abmeldedatum", "type": "date"},
                    {"key": "kostenstelle", "label": "Kostenstelle", "type": "text"},
                    {"key": "abschreibungsart", "label": "Abschreibungsart", "type": "text"},
                    {"key": "afa_jahre", "label": "Afa Jahre", "type": "number"},
                    {"key": "afa_eur_jaehrlich", "label": "Afa EUR jaehrlich", "type": "number"},
                    {"key": "afa_eur_monatlich", "label": "Afa EUR monatlich", "type": "number"},
                    {"key": "leasingdauer_monate", "label": "Leasingdauer (Mon.)", "type": "number"},
                    {"key": "leasinggesellschaft", "label": "Leasinggesellschaft", "type": "text"},
                    {"key": "leasingrate_eur", "label": "Leasingrate EUR", "type": "number"},
                    {"key": "kfz_steuer_eur", "label": "KFZ-Steuer EUR", "type": "number"},
                    {"key": "kfz_steuernummer", "label": "KFZ-Steuernummer", "type": "text"},
                    {"key": "kontierung", "label": "Kontierung", "type": "text"},
                    {"key": "finanzamt", "label": "Finanzamt", "type": "text"},
                    {"key": "versicherungs_gesellschaft", "label": "Versicherungs-Gesellschaft", "type": "text"},
                    {"key": "versicherungsschein_nr", "label": "Versicherungsschein-Nr.", "type": "text"},
                    {"key": "versicherung_satz_eur_monat", "label": "Satz EUR / Monat", "type": "number"},
                    {"key": "versicherung_haftpflicht", "label": "Haftpflicht", "type": "boolean"},
                    {"key": "versicherung_kasko", "label": "Kasko", "type": "boolean"},
                ],
            },
            {
                "key": "termine",
                "label": "Termine",
                "fields": [
                    {"key": "naechster_tuev_termin", "label": "Naechster TUEV-Termin", "type": "date"},
                    {"key": "naechster_asu_termin", "label": "Naechster ASU-Termin", "type": "date"},
                    {"key": "naechste_inspektion", "label": "Naechste Inspektion", "type": "date"},
                    {"key": "kilometerstand", "label": "Km-Stand", "type": "number"},
                    {"key": "km_stand_alle_eintraege", "label": "Alle Eintraege", "type": "boolean"},
                    {"key": "leergewicht_kg", "label": "Leergewicht (kg)", "type": "number"},
                    {"key": "nutzlast_kg", "label": "Nutzlast (kg)", "type": "number"},
                    {"key": "gesamtgewicht_kg", "label": "Gesamtgewicht (kg)", "type": "number"},
                    {"key": "anhaengerlast_kg", "label": "Anhaengerlast (kg)", "type": "number"},
                    {"key": "winterreifen_vorhanden", "label": "Winterreifen vorhanden", "type": "boolean"},
                    {"key": "winterreifen_eingelagert", "label": "Eingelagert", "type": "boolean"},
                    {"key": "handy_freisprecheinrichtung", "label": "Handy-Freispr.-Einr.", "type": "boolean"},
                    {"key": "handy_fabrikat", "label": "Handy-Fabrikat", "type": "text"},
                    {"key": "handy_rufnummer", "label": "Handy-Ruf-Nummer", "type": "text"},
                ],
            },
            {
                "key": "funktionen",
                "label": "Funktionen",
                "fields": [
                    {"key": "drucker_name", "label": "Drucker", "type": "text", "placeholder": "Druckername"},
                    {"key": "unfall_ort", "label": "Unfall-Ort", "type": "text"},
                    {"key": "unfall_beschreibung", "label": "Unfall-Beschreibung", "type": "text"},
                ],
            },
        ],
        "noWorkflowReason": "Der Stand folgt Kennzeichen, Typ und den Terminen der Akte.",
        "agentContract": {
            "businessPurpose": "Fahrzeugakte anlegen und aendern. Der Stand folgt Kennzeichen und Typ.",
            "examplePrompts": ["Welches Fahrzeug hat noch keinen TUEV-Termin?"],
            "sensitiveFields": [],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-fuhrpark/fahrzeug-stamm']",
                "primaryAction": "[data-testid='action-speichern']",
            },
        },
        "layout": {
            "floorplan": "objectPage",
            "density": "compact",
            "contextRail": "workflow",
            "tableProfile": "standard",
            "columnNavigation": "single",
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
            "summaryPlacement": "footer",
            "statusPlacement": "afterFields",
        },
        "performance": {
            "initialPayloadBudgetKb": 48,
            "requiresLazyTabs": False,
            "requiresVirtualTables": False,
            "lookupMinChars": 2,
            "bundleGroup": "logistics",
        },
    }


def build_personal_qualifikationen_screen_definition() -> dict[str, Any]:
    """Qualifikationsprofile. Die Seite speichert, der Builder zeichnet die Liste."""
    return {
        "schemaVersion": 1,
        "id": "personal/qualifikationen",
        "domain": "hr",
        "mode": "list",
        "title": "Qualifikationen",
        "subtitle": "Rollenbezogene Qualifikationsprofile",
        "adapter": {"type": "native", "sourceId": "personal/qualifikationen", "temporary": False},
        "dataSources": [
            {"key": "qualifikationen", "endpoint": "/api/v1/training/qualifications", "pageSize": 100},
        ],
        "summary": [
            {"key": "profile", "label": "Profile", "value": "0"},
            {"key": "ohne_gueltigkeit", "label": "Ohne Gueltigkeit", "value": "0"},
        ],
        "fields": [
            {"key": "employee_ref", "label": "Mitarbeiter-Referenz", "type": "text"},
            {"key": "role_code", "label": "Rollen-Code", "type": "text"},
            {
                "key": "qualification_level",
                "label": "Level",
                "type": "select",
                "options": [
                    {"value": "basic", "label": "Grundkenntnis"},
                    {"value": "advanced", "label": "Fortgeschritten"},
                    {"value": "expert", "label": "Experte"},
                ],
            },
            {"key": "skills", "label": "Skills", "type": "text", "placeholder": "kommagetrennt"},
            {"key": "valid_until", "label": "Gueltig bis", "type": "date"},
        ],
        "workflow": {"processKey": "personal.qualifikationen"},
        "actions": [
            {
                "key": "speichern",
                "label": "Speichern",
                "command": "personal.saveQualifikation",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Legt ein Qualifikationsprofil an.",
            },
            {
                "key": "neu",
                "label": "Neu",
                "command": "personal.newQualifikation",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Leert die Eingabe fuer ein neues Profil.",
            },
        ],
        "tables": [
            {
                "key": "qualifikationen",
                "label": "Profile",
                "dataSourceKey": "qualifikationen",
                "serverPagination": False,
                "pageSize": 50,
                "virtualized": True,
                "rowHeight": 44,
                "rowDetail": False,
                "rowActions": [
                    {
                        "key": "loeschen",
                        "label": "Löschen",
                        "command": "personal.deleteQualifikation",
                        "dangerLevel": "moderate",
                        "disabledWhen": {"field": "gesperrt", "values": [True]},
                    },
                ],
                "columns": [
                    {"key": "employee_ref", "label": "Mitarbeiter", "sortable": True, "filterable": True, "priority": "primary"},
                    {"key": "role_code", "label": "Rolle", "sortable": True, "priority": "primary"},
                    {"key": "qualification_level", "label": "Level", "priority": "secondary"},
                    {"key": "skills", "label": "Skills", "priority": "tertiary"},
                    {"key": "valid_until", "label": "Gueltig bis", "renderKind": "date", "priority": "tertiary"},
                ],
            },
        ],
        "noWorkflowReason": "Der Stand folgt den Profilen und ihrer Gueltigkeit.",
        "agentContract": {
            "businessPurpose": "Qualifikationsprofile anlegen. Der Stand folgt der Gueltigkeit.",
            "examplePrompts": ["Welches Profil hat noch kein Gueltig-bis?"],
            "sensitiveFields": [],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-personal/qualifikationen']",
                "primaryAction": "[data-testid='action-speichern']",
            },
        },
        "layout": {
            "floorplan": "worklist",
            "density": "compact",
            "contextRail": "none",
            "tableProfile": "standard",
            "columnNavigation": "single",
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
            "summaryPlacement": "footer",
            "statusPlacement": "afterFields",
        },
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "hr",
        },
    }


def build_personal_onboarding_screen_definition() -> dict[str, Any]:
    """Einarbeitungslaeufe. Die Seite legt den Lauf an, der Builder zeichnet die Liste."""
    return {
        "schemaVersion": 1,
        "id": "personal/onboarding",
        "domain": "hr",
        "mode": "list",
        "title": "Onboarding",
        "subtitle": "Checklisten und Einarbeitungslaeufe",
        "adapter": {"type": "native", "sourceId": "personal/onboarding", "temporary": False},
        "dataSources": [
            {"key": "laeufe", "endpoint": "/api/v1/training/onboarding/runs", "pageSize": 100},
        ],
        "summary": [
            {"key": "laeufe", "label": "Laeufe", "value": "0"},
            {"key": "offen", "label": "Offen", "value": "0"},
        ],
        "fields": [
            {"key": "employee_ref", "label": "Mitarbeiter-Referenz", "type": "text"},
            {"key": "checklist_id", "label": "Checkliste", "type": "select", "options": []},
            {"key": "assigned_by", "label": "Zugewiesen von", "type": "text"},
            {"key": "due_date", "label": "Faellig bis", "type": "date"},
        ],
        "workflow": {"processKey": "personal.onboarding"},
        "actions": [
            {
                "key": "speichern",
                "label": "Speichern",
                "command": "personal.saveOnboarding",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Legt einen Einarbeitungslauf an.",
            },
            {
                "key": "neu",
                "label": "Neu",
                "command": "personal.newOnboarding",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Leert die Eingabe fuer einen neuen Lauf.",
            },
        ],
        "tables": [
            {
                "key": "laeufe",
                "label": "Laeufe",
                "dataSourceKey": "laeufe",
                "serverPagination": False,
                "pageSize": 50,
                "virtualized": True,
                "rowHeight": 44,
                "rowDetail": False,
                "rowActions": [
                    {
                        "key": "loeschen",
                        "label": "Löschen",
                        "command": "personal.deleteOnboarding",
                        "dangerLevel": "moderate",
                        "disabledWhen": {"field": "gesperrt", "values": [True]},
                    },
                ],
                "columns": [
                    {"key": "employee_ref", "label": "Mitarbeiter", "sortable": True, "filterable": True, "priority": "primary"},
                    {"key": "checkliste", "label": "Checkliste", "priority": "secondary"},
                    {"key": "status", "label": "Stand", "priority": "secondary"},
                    {"key": "fortschritt", "label": "Fortschritt", "priority": "tertiary"},
                    {"key": "due_date", "label": "Faellig", "renderKind": "date", "priority": "tertiary"},
                    {"key": "assigned_by", "label": "Zugewiesen von", "priority": "tertiary"},
                ],
            },
        ],
        "noWorkflowReason": "Der Stand folgt den Einarbeitungslaeufen.",
        "agentContract": {
            "businessPurpose": "Einarbeitungslaeufe anlegen. Der Stand folgt den offenen Laeufen.",
            "examplePrompts": ["Welcher Lauf ist noch nicht abgeschlossen?"],
            "sensitiveFields": [],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-personal/onboarding']",
                "primaryAction": "[data-testid='action-speichern']",
            },
        },
        "layout": {
            "floorplan": "worklist",
            "density": "compact",
            "contextRail": "none",
            "tableProfile": "standard",
            "columnNavigation": "single",
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
            "summaryPlacement": "footer",
            "statusPlacement": "afterFields",
        },
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "hr",
        },
    }


def build_personal_schulungen_screen_definition() -> dict[str, Any]:
    """Schulungszuweisungen. Die Seite legt die Zuweisung an, der Builder zeichnet die Liste."""
    return {
        "schemaVersion": 1,
        "id": "personal/schulungen",
        "domain": "hr",
        "mode": "list",
        "title": "Schulungen",
        "subtitle": "Nachweise suchen und pruefen",
        "adapter": {"type": "native", "sourceId": "personal/schulungen", "temporary": False},
        "dataSources": [
            {"key": "schulungen", "endpoint": "/api/v1/training/assignments", "pageSize": 100},
        ],
        "summary": [
            {"key": "gesamt", "label": "Gesamt", "value": "0"},
            {"key": "ablaufend", "label": "Ablaufend", "value": "0"},
        ],
        "fields": [
            {"key": "employee_ref", "label": "Mitarbeiter-Referenz", "type": "text"},
            {"key": "course_id", "label": "Schulungskurs", "type": "select", "options": []},
            {"key": "assigned_by", "label": "Zugewiesen von", "type": "text"},
            {"key": "due_date", "label": "Faellig bis", "type": "date"},
        ],
        "workflow": {"processKey": "personal.schulungen"},
        "actions": [
            {
                "key": "speichern",
                "label": "Speichern",
                "command": "personal.saveSchulung",
                "kind": "primary",
                "dangerLevel": "safe",
                "zone": "header",
                "stubReason": "Legt eine Schulungszuweisung an.",
            },
            {
                "key": "neu",
                "label": "Neu",
                "command": "personal.newSchulung",
                "kind": "secondary",
                "dangerLevel": "safe",
                "zone": "footer",
                "stubReason": "Leert die Eingabe fuer eine neue Zuweisung.",
            },
        ],
        "tables": [
            {
                "key": "schulungen",
                "label": "Schulungen",
                "dataSourceKey": "schulungen",
                "serverPagination": False,
                "pageSize": 50,
                "virtualized": True,
                "rowHeight": 44,
                "rowDetail": False,
                "rowActions": [
                    {
                        "key": "loeschen",
                        "label": "Löschen",
                        "command": "personal.deleteSchulung",
                        "dangerLevel": "moderate",
                        "disabledWhen": {"field": "gesperrt", "values": [True]},
                    },
                ],
                "columns": [
                    {"key": "employee_ref", "label": "Mitarbeiter", "sortable": True, "filterable": True, "priority": "primary"},
                    {"key": "kurs", "label": "Kurs", "priority": "secondary"},
                    {"key": "status", "label": "Stand", "priority": "secondary"},
                    {"key": "due_date", "label": "Faellig", "renderKind": "date", "priority": "tertiary"},
                    {"key": "assigned_by", "label": "Zugewiesen von", "priority": "tertiary"},
                ],
            },
        ],
        "noWorkflowReason": "Der Stand folgt den Schulungsnachweisen und ihrer Faelligkeit.",
        "agentContract": {
            "businessPurpose": "Schulungszuweisungen anlegen. Der Stand folgt den offenen Nachweisen.",
            "examplePrompts": ["Welche Schulung laeuft in den naechsten 60 Tagen ab?"],
            "sensitiveFields": [],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-personal/schulungen']",
                "primaryAction": "[data-testid='action-speichern']",
            },
        },
        "layout": {
            "floorplan": "worklist",
            "density": "compact",
            "contextRail": "none",
            "tableProfile": "standard",
            "columnNavigation": "single",
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
            "summaryPlacement": "footer",
            "statusPlacement": "afterFields",
        },
        "performance": {
            "initialPayloadBudgetKb": 32,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "hr",
        },
    }
