from __future__ import annotations

import copy
import json as _json
from datetime import UTC, datetime
from typing import Any


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


GERMAN_TRANSLATIONS: dict[str, str] = {
    "Order-to-Cash": "Auftrag bis Zahlung",
    "Procure-to-Pay": "Bedarf bis Zahlung",
    "Inventory-to-Settlement": "Lager bis Abrechnung",
    "Harvest-to-Settlement": "Ernte bis Abrechnung",
    "Contract-to-Settlement": "Kontrakt bis Abrechnung",
    "Complaint-to-Resolution": "Reklamation bis Loesung",
    "Service-to-Customer": "Service bis Kunde",
    "Finance-to-Close": "Finanzen bis Abschluss",
    "Compliance-to-Report": "Compliance bis Bericht",
    "Flow Spine UI": "Flow Spine",
    "Flow": "Ablauf",
    "Operations Lead": "Betriebsleitung",
    "Procurement Lead": "Einkaufsleitung",
    "Warehouse Ops": "Lagerleitung",
    "Quality Service Lead": "Qualitaetsservice-Leitung",
    "Service Coordinator": "Servicekoordination",
    "Finance Lead": "Finanzleitung",
    "Compliance Lead": "Compliance-Leitung",
    "Beschaffungsprozess Uebersicht": "Beschaffungsprozess-Uebersicht",
    "Inventory-to-Settlement": "Lager bis Abrechnung",
    "Service-to-Customer": "Service bis Kunde",
    "Finance-to-Close": "Finanzen bis Abschluss",
    "Compliance-to-Report": "Compliance bis Bericht",
    "Aktive Steuerung der Order-to-Cash Kette mit AI Copilot, Statuskarten und Deep Links in die operativen Masken.": "Aktive Steuerung der Auftrag-bis-Zahlung-Kette mit KI-Copilot, Statuskarten und Deep Links in die operativen Masken.",
    "Lager, Versand und Settlement als gemeinsamer Steuerraum fuer Wellen, Rampen und Margen.": "Lager, Versand und Abrechnung als gemeinsamer Steuerraum fuer Wellen, Rampen und Margen.",
    "Reklamationen mit CRM, DMS und Audit-Trail als durchgehender Prozessraum.": "Reklamationen mit CRM, DMS und Audit-Trail als durchgaengiger Prozessraum.",
    "Serviceanfrage, Disposition, Ausfuehrung und Rueckmeldung in einem agentenfaehigen Raum.": "Serviceanfrage, Disposition, Ausfuehrung und Rueckmeldung in einem agentenfaehigen Arbeitsraum.",
    "Buchung, Abstimmung, Meldewesen und Abschluss als periodischer Steuerraum.": "Buchung, Abstimmung, Meldewesen und Abschluss als periodischer Steuerraum.",
    "Nachhaltigkeit, Compliance, Freigabe und Reporting als auditierbarer End-to-End-Prozess.": "Nachhaltigkeit, Compliance, Freigabe und Berichtswesen als auditierbarer End-to-End-Prozess.",
    "Lager, Versand und Settlement als gemeinsamer Operations-Flow.": "Lager, Versand und Abrechnung als gemeinsamer Ablauf.",
    "Suche in Prozessen, Auftraegen oder Rechnungen ...": "Suche in Prozessen, Auftraegen oder Rechnungen ...",
    "Suche in Bestellungen, Lieferanten oder Wareneingaengen ...": "Suche in Bestellungen, Lieferanten oder Wareneingaengen ...",
    "Suche in Wellen, Chargen, Rampen oder Settlement ...": "Suche in Wellen, Chargen, Rampen oder Abrechnung ...",
    "Settlement": "Abrechnung",
    "Reporting": "Berichtswesen",
    "Collection": "Datensammlung",
    "Validation": "Validierung",
    "Approval": "Freigabe",
    "sales": "Vertrieb",
    "procurement": "Einkauf",
    "inventory": "Lager",
    "agrar": "Agrar",
    "quality": "Qualitaet",
    "service": "Service",
    "finance": "Finanzen",
    "compliance": "Compliance",
    "workflow": "Prozesse",
}


def _normalize_lang(lang: str | None) -> str:
    if not lang:
        return ""
    return lang.split("-")[0].lower()


def _translate_value(value: Any, translations: dict[str, str]) -> Any:
    if isinstance(value, str):
        return translations.get(value, value)
    if isinstance(value, list):
        return [_translate_value(item, translations) for item in value]
    if isinstance(value, dict):
        return {key: _translate_value(item, translations) for key, item in value.items()}
    return value


def _localize_payload(payload: dict[str, Any], lang: str | None) -> dict[str, Any]:
    normalized = _normalize_lang(lang)
    if normalized != "de":
        return payload
    return _translate_value(payload, GERMAN_TRANSLATIONS)


CATALOG: list[dict[str, str]] = [
    {
        "key": "order-to-cash",
        "label": "Order-to-Cash",
        "route_path": "/workflow/flow-spine-order-to-cash",
        "summary": "Vertrieb, Lieferung, Faktura und Zahlung in einem agentenfaehigen Steuerraum.",
        "domain": "sales",
    },
    {
        "key": "procure-to-pay",
        "label": "Procure-to-Pay",
        "route_path": "/workflow/flow-spine-procure-to-pay",
        "summary": "Bedarf, Bestellung, Wareneingang, Rechnung und Zahlung mit ETA- und Match-Fokus.",
        "domain": "procurement",
    },
    {
        "key": "inventory-to-settlement",
        "label": "Inventory-to-Settlement",
        "route_path": "/workflow/flow-spine-inventory-to-settlement",
        "summary": "Lager, Versand und Settlement als gemeinsamer Operations-Flow.",
        "domain": "inventory",
    },
    {
        "key": "harvest-to-settlement",
        "label": "Harvest-to-Settlement",
        "route_path": "/workflow/flow-spine-harvest-to-settlement",
        "summary": "Ernteannahme, Trocknung, Einlagerung und Abrechnung als Kampagnenfluss.",
        "domain": "agrar",
    },
    {
        "key": "contract-to-settlement",
        "label": "Contract-to-Settlement",
        "route_path": "/workflow/flow-spine-contract-to-settlement",
        "summary": "Kontrakt, Annahme, Qualitaet und Settlement ohne Medienbruch.",
        "domain": "agrar",
    },
    {
        "key": "complaint-to-resolution",
        "label": "Complaint-to-Resolution",
        "route_path": "/workflow/flow-spine-complaint-to-resolution",
        "summary": "Reklamationen End-to-End ueber CRM, DMS und Freigaben.",
        "domain": "quality",
    },
    {
        "key": "service-to-customer",
        "label": "Service-to-Customer",
        "route_path": "/workflow/flow-spine-service-to-customer",
        "summary": "Serviceanfragen, Einsatzsteuerung und Rueckmeldung in einem Arbeitsraum.",
        "domain": "service",
    },
    {
        "key": "finance-to-close",
        "label": "Finance-to-Close",
        "route_path": "/workflow/flow-spine-finance-to-close",
        "summary": "Buchung, Abstimmung, Meldewesen und Abschluss als periodischer Steuerraum.",
        "domain": "finance",
    },
    {
        "key": "compliance-to-report",
        "label": "Compliance-to-Report",
        "route_path": "/workflow/flow-spine-compliance-to-report",
        "summary": "Nachhaltigkeit, Compliance, Freigabe und Reporting als auditierbarer End-to-End-Prozess.",
        "domain": "compliance",
    },
]


def _nav(active_key: str) -> list[dict[str, str | bool]]:
    return [
        {
            "key": item["key"],
            "label": item["label"],
            "route_path": item["route_path"],
            "active": item["key"] == active_key,
        }
        for item in CATALOG
    ]


def _node(
    node_id: str,
    label: str,
    status: str,
    icon: str,
    metric: str,
    submetric: str,
    insight: str,
    detail_rows: list[tuple[str, str]],
    kpis: list[tuple[str, str]],
    documents: list[tuple[str, str]],
    actions: list[tuple[str, str, str, str]],
    agent: tuple[str, str, list[str]],
) -> dict:
    return {
        "id": node_id,
        "label": label,
        "status": status,
        "icon": icon,
        "metric": metric,
        "submetric": submetric,
        "timestamp": _now(),
        "insight": insight,
        "detail_rows": [{"label": key, "value": value} for key, value in detail_rows],
        "kpis": [{"label": key, "value": value} for key, value in kpis],
        "documents": [{"label": key, "href": href} for key, href in documents],
        "actions": [
            {"label": label_value, "href": href, "variant": variant, "api_path": api_path}
            for label_value, href, variant, api_path in actions
        ],
        "agent": {
            "headline": agent[0],
            "message": agent[1],
            "reasons": agent[2],
            "actions": ["Uebernehmen", "Anpassen", "Ignorieren"],
        },
    }


def _workspace(
    process_key: str,
    title: str,
    subtitle: str,
    instance_label: str,
    user_role: str,
    mode: str,
    search_placeholder: str,
    badges: list[tuple[str, str]],
    favorites: list[str],
    recent_items: list[str],
    role_switches: list[str],
    resources: list[tuple[str, str]],
    linked_modules: list[tuple[str, str, str]],
    focus_node_id: str,
    nodes: list[dict],
    footer_cards: list[tuple[str, list[str]]],
    domain: str,
) -> dict:
    return {
        "schema_version": 1,
        "manifest_kind": "FLOW_SPINE_WORKSPACE",
        "generated_at": _now(),
        "process_key": process_key,
        "title": title,
        "subtitle": subtitle,
        "instance_label": instance_label,
        "breadcrumb": ["Flow Spine UI", title, instance_label],
        "search_placeholder": search_placeholder,
        "mode": mode,
        "user_role": user_role,
        "left_navigation": {
            "processes": _nav(process_key),
            "favorites": favorites,
            "recent_items": recent_items,
            "role_switches": role_switches,
        },
        "badges": [{"label": label, "tone": tone} for label, tone in badges],
        "focus_node_id": focus_node_id,
        "nodes": nodes,
        "right_panel": {
            "resources": [{"label": label, "href": href} for label, href in resources],
            "linked_modules": [
                {"label": label, "href": href, "api_path": api_path}
                for label, href, api_path in linked_modules
            ],
            "domain": domain,
        },
        "footer_cards": [{"title": title_value, "items": items} for title_value, items in footer_cards],
    }


# JSON string cache for catalog: key = lang code (default "de")
_catalog_json_cache: dict[str, str] = {}


def get_flow_spine_catalog(lang: str | None = None) -> dict:
    lang_key = lang or "de"
    cached = _catalog_json_cache.get(lang_key)
    if cached is None:
        payload = {
            "schema_version": 1,
            "manifest_kind": "FLOW_SPINE_PROCESS_CATALOG",
            "generated_at": _now(),
            "processes": CATALOG,
        }
        localized = _localize_payload(payload, lang)
        cached = _json.dumps(localized, ensure_ascii=False)
        _catalog_json_cache[lang_key] = cached
    return _json.loads(cached)


WORKSPACES: dict[str, dict] = {}

WORKSPACES["order-to-cash"] = _workspace(
    "order-to-cash",
    "Auftragsprozess Uebersicht",
    "Aktive Steuerung der Order-to-Cash Kette mit AI Copilot, Statuskarten und Deep Links in die operativen Masken.",
    "Auftrag AU-2026-4711",
    "Operations Lead",
    "Flow",
    "Suche in Prozessen, Auftraegen oder Rechnungen ...",
    [("SLA stabil", "ok"), ("1 kritische Abweichung", "warning")],
    ["Wichtige Kunden", "Monatsbericht"],
    ["AU-2024-001", "RE-992-B"],
    ["Sales Manager", "Finance Controller"],
    [("Lieferantenvertrag_2024.pdf", "/dokumente/ablage"), ("SLA_TechLogistics.docx", "/dokumente/ablage")],
    [
        ("Auftragsanlage", "/sales/orders/new", "/api/v1/sales/orders"),
        ("Lieferungen", "/sales/lieferungen", "/api/v1/sales-shipping/delivery-notes"),
        ("Rechnungen", "/sales/rechnungen", "/api/v1/finance/invoices"),
    ],
    "delivery",
    [
        _node("order", "Auftrag", "ok", "Package", "EUR 48.200", "12. Okt, 09:15", "Auftrag komplett, Bonitaet bestaetigt und Lieferfenster reserviert.", [("Kunde", "Ultrasharp Agrarhandel"), ("Auftrag", "AU-2026-4711"), ("Kanal", "Direktvertrieb")], [("Deckungsbeitrag", "18,4%"), ("Auftragswert", "EUR 48.200"), ("SLA", "98%")], [("Auftragsbestaetigung.pdf", "/sales/auftraege")], [("Auftrag oeffnen", "/sales/order", "primary", "/api/v1/sales/orders"), ("Kundenstamm", "/crm/kunden", "secondary", "/api/v1/crm/customers")], ("Auftrag ist freigabefaehig", "Kreditlimit, Lieferfenster und Preisfreigabe sind konsistent.", ["Kreditlimit gruen", "Preislistenregel getroffen"])),
        _node("check", "Pruefung", "ok", "ShieldCheck", "3 Checks", "12. Okt, 14:30", "Freigaben und Policy-Regeln wurden ohne Abweichung durchlaufen.", [("Policy", "Preis + Kredit + Lieferfenster"), ("Freigaben", "3/3"), ("Status", "ABGESCHLOSSEN")], [("Freigabezeit", "2 Min"), ("Retry Safety", "99,9%"), ("Audit", "vollstaendig")], [("Policy-Protokoll", "/admin/ai-approvals")], [("Freigaben anzeigen", "/workflows/approval", "primary", "/api/v1/process/approval-density/overview")], ("Keine Richtlinienverletzung", "Freigabe wurde policy-konform und auditierbar abgeschlossen.", ["Preis innerhalb Toleranz", "Lieferfenster verfuegbar"])),
        _node("delivery", "Lieferung", "active", "Truck", "In Zustellung", "Live-Tracking", "Supply Chain Alert: Verzoegerung um 4-6 Tage moeglich, Expressoption empfohlen.", [("Logistikpartner", "Global Express Logistics"), ("Tracking", "GXL-7782-XQ"), ("Geplanter Erhalt", "Morgen, 10:00 - 12:00")], [("KPI Health", "92%"), ("OTD", "92%"), ("ETA Drift", "+45 Min")], [("Lieferschein LS-884", "/sales/lieferungen")], [("Lieferung starten", "/sales/delivery", "primary", "/api/v1/channels/slack/process-actions/execute"), ("Freigabe senden", "/workflows/approval", "secondary", "/api/v1/channels/slack/process-actions"), ("Rechnung erzeugen", "/sales/invoice", "secondary", "/api/v1/finance/invoices")], ("Supply Chain Alert", "Alternativ-Sourcing oder Express-Versand mit Aufpreis wird empfohlen.", ["Lieferant A verspaetet", "Lagerbestand kritisch"])),
        _node("invoice", "Rechnung", "warning", "Receipt", "Pending", "1 wartend", "Rechnung wartet auf belastbare Lieferbestaetigung und Zustellstatus.", [("Invoice Queue", "1"), ("Skonto", "2% moeglich"), ("Status", "WARTET")], [("Faktura SLA", "81%"), ("Queue", "1"), ("Cash Forecast", "EUR 41.700")], [("Rechnungsvorschau.xml", "/sales/invoices/new")], [("Rechnungseditor", "/sales/invoices/new", "primary", "/api/v1/finance/invoices")], ("Faktura wartet auf Lieferbestaetigung", "Vorgelagerter Lieferstatus muss gruen sein, bevor Faktura freigegeben wird.", ["Delivery POD fehlt"])),
        _node("payment", "Zahlung", "warning", "Wallet", "Skonto offen", "T+10", "Fruehe Zahlung steigert Marge, wenn Zustellung termingerecht bleibt.", [("Faelligkeit", "T+10"), ("Skonto", "2%"), ("Forecast", "EUR 41.700")], [("Cash In", "EUR 41.700"), ("Skonto Potenzial", "EUR 834"), ("Mahnrisiko", "niedrig")], [("Zahlungslauf.pdf", "/finance/zahlungslauf-kreditoren")], [("Zahlungslauf", "/finance/zahlungslauf-kreditoren", "primary", "/api/v1/finance/payment-runs")], ("Skonto-Fenster sichern", "Zahlung frueh terminieren, sobald Rechnung freigegeben ist.", ["2% Skonto moeglich"])),
        _node("close", "Abschluss", "critical", "BookOpen", "1 Risiko", "T+30", "Abschluss ist von Liefer- und Zahlungsstatus abhaengig; Korrekturbedarf moeglich.", [("Abschlussstatus", "RISIKO"), ("Marge", "gefaehrdet"), ("Korrekturen", "1 moeglich")], [("Abschlussquote", "84%"), ("Marge", "14,8%"), ("Audit", "vollstaendig")], [("Abschlussprotokoll", "/finance/abschluss")], [("Abschlusspruefung", "/finance/abschluss", "primary", "/api/v1/process/settlement/completion/evaluate")], ("Abschluss noch nicht stabil", "Bitte Lieferabweichung und Faktura zuerst bereinigen.", ["ETA Drift", "Faktura wartet"])),
    ],
    [("Operative Heatmap", ["Region Nord", "Region West", "Region Ost"]), ("Agent Events", ["Delay Prediction aktualisiert", "Skonto-Potenzial erkannt"]), ("Naechste Schritte", ["Live-Daten anbinden", "R3F-Spine ausbauen", "Action Layer erweitern"])],
    "workflow",
)

WORKSPACES["procure-to-pay"] = _workspace(
    "procure-to-pay",
    "Beschaffungsprozess Uebersicht",
    "Bedarf bis Zahlung mit ETA, Match-Abweichung und Lieferantensteuerung.",
    "Bestellung PO-2026-188",
    "Procurement Lead",
    "Fokus",
    "Suche in Bestellungen, Lieferanten oder Wareneingaengen ...",
    [("Budget im Rahmen", "ok"), ("1 Lieferfenster kippt", "warning")],
    ["PO-2026-188", "TechLogistics"],
    ["Lieferavis aktualisiert", "3-way-Match auffaellig"],
    ["Einkauf", "Kreditoren"],
    [("Bestellung_PO-2026-188.pdf", "/einkauf/bestellungen"), ("Lieferavis.xml", "/einkauf/anlieferavis")],
    [
        ("Bestellungen", "/einkauf/bestellungen", "/api/v1/einkauf-bestellvorschlag"),
        ("Wareneingang", "/einkauf/wareneingang", "/api/v1/einkauf/wareneingang"),
        ("Rechnungsabgleich", "/einkauf/rechnung-abgleich", "/api/v1/finance/ap/invoices"),
    ],
    "purchase-order",
    [
        _node("requisition", "Bedarf", "ok", "BookOpen", "3 Positionen", "07:42", "Anforderung vollstaendig mit Budgetbezug und Warengruppe.", [("Anforderung", "BANF-442"), ("Budget", "freigegeben"), ("Warengruppe", "Logistik")], [("Budgetabweichung", "0%"), ("Freigabezeit", "14 Min"), ("Bedarf", "3 Positionen")], [("Bedarfsanforderung.pdf", "/einkauf/anfragen")], [("Bedarf oeffnen", "/einkauf/anfragen", "primary", "/api/v1/einkauf/anfragen")], ("Bedarf ist komplett", "Budget und Warengruppe sind freigabefaehig.", ["Budgetbezug vorhanden"])),
        _node("approval", "Freigabe", "ok", "ShieldCheck", "2 Stufen", "07:49", "Freigabekette innerhalb der Policy abgeschlossen.", [("Stufen", "2"), ("Eskalationen", "0"), ("Policy", "aktiv")], [("Freigabequote", "100%"), ("Audit", "vollstaendig"), ("Policy Hits", "7")], [("Freigabeprotokoll.pdf", "/workflows/approval")], [("Freigaben", "/workflows/approval", "primary", "/api/v1/finance/ap/approval-rules")], ("Keine Eskalation", "Freigabepfad ist policy-konform.", ["Betrag innerhalb Toleranz"])),
        _node("purchase-order", "Bestellung", "active", "ShoppingCart", "PO-2026-188", "Heute", "Bestellung laeuft, Liefertermin und Incoterm werden aktiv ueberwacht.", [("Lieferant", "TechLogistics"), ("Incoterm", "DAP"), ("Spend", "EUR 18.420")], [("Spend", "EUR 18.420"), ("OTD", "89%"), ("ETA Drift", "+2 Tage")], [("Bestellung.pdf", "/einkauf/bestellungen"), ("SLA_TechLogistics.docx", "/dokumente/ablage")], [("Bestellung oeffnen", "/einkauf/bestellungen", "primary", "/api/v1/einkauf-bestellvorschlag"), ("Lieferantenanfrage", "/einkauf/anfragen", "secondary", "/api/v1/messages")], ("ETA bedroht Skonto-Fenster", "Expressoption oder Zweitlieferant empfohlen.", ["Hafenverzoegerung", "kritische Position"])),
        _node("goods-receipt", "Wareneingang", "warning", "Package", "ETA +2 Tage", "Morgen", "Lieferfenster kippt, Expressoption und Zweitquelle verfuegbar.", [("ETA", "+2 Tage"), ("Wareneingang", "vorbereitet"), ("Dock", "Rampe 3")], [("Wareneingang SLA", "89%"), ("Slot Risk", "hoch"), ("Abweichungen", "1")], [("Lieferavis.xml", "/einkauf/anlieferavis")], [("Wareneingang", "/einkauf/wareneingang", "primary", "/api/v1/einkauf/wareneingang")], ("Lieferfenster kippt", "Wareneingang und Folgeprozesse neu terminieren.", ["ETA +2 Tage"])),
        _node("invoice", "Rechnung", "warning", "Receipt", "2-way Match", "T+1", "Preisabweichung von 1,8% erwartet, Vorpruefung empfohlen.", [("Match", "2-way"), ("Abweichung", "1,8%"), ("Status", "wartet")], [("Match Quote", "96%"), ("Queue", "2"), ("Risk", "mittel")], [("Rechnungseingang.xml", "/einkauf/rechnungseingang")], [("Rechnungsabgleich", "/einkauf/rechnung-abgleich", "primary", "/api/v1/finance/ap/invoices")], ("Preisabweichung erkannt", "Vor Freigabe die Preisabweichung pruefen.", ["1,8% uebersetzt Toleranz"])),
        _node("payment", "Zahlung", "critical", "Wallet", "Skonto offen", "T+10", "Skontofenster gefaehrdet, wenn Wareneingang weiter rutscht.", [("Faelligkeit", "T+10"), ("Skonto", "2%"), ("Cash Impact", "EUR 370")], [("Skonto", "2%"), ("Cash Impact", "EUR 370"), ("Risk", "hoch")], [("Zahlungsvorschlag.pdf", "/finance/zahlungslauf-kreditoren")], [("Zahlungslauf", "/finance/zahlungslauf-kreditoren", "primary", "/api/v1/finance/payment-runs")], ("Skonto-Fenster gefaehrdet", "Wareneingang und AP-Freigabe priorisieren.", ["ETA Drift", "Rechnung wartet"])),
    ],
    [("Lieferanten-Heatmap", ["TechLogistics", "Nordhafen", "Import Route A"]), ("Agent Events", ["ETA-Warnung aktualisiert", "Preisabweichung erkannt"]), ("Naechste Schritte", ["Match Engine verfeinern", "ETA-Dispatch live schalten"])],
    "workflow",
)

WORKSPACES["inventory-to-settlement"] = _workspace(
    "inventory-to-settlement",
    "Inventory-to-Settlement",
    "Lager, Versand und Settlement als gemeinsamer Steuerraum fuer Wellen, Rampen und Margen.",
    "Welle INV-2026-031",
    "Warehouse Ops",
    "Uebersicht",
    "Suche in Wellen, Chargen, Rampen oder Settlement ...",
    [("Bestand stabil", "ok"), ("Rampenkonflikt erkannt", "warning")],
    ["Welle INV-2026-031", "Rampe 4 / Hallenbereich B"],
    ["Rampenfenster neu zugeordnet", "Versandavis angestossen"],
    ["Lagerleitung", "Settlement Desk"],
    [("Wellenliste.pdf", "/lager/lagerbewegungen"), ("ASN-442.xml", "/verladung")],
    [
        ("Bestandsuebersicht", "/lager/bestandsuebersicht", "/api/v1/inventory"),
        ("Verladung", "/verladung", "/api/v1/tours"),
        ("Abrechnung", "/annahme/abrechnung", "/api/v1/agrar/settlements"),
    ],
    "picking",
    [
        _node("inventory-check", "Bestandsaufnahme", "ok", "Warehouse", "99,8% exakt", "06:15", "Bestand und Chargenstatus wurden ohne Differenz abgeglichen.", [("Genauigkeit", "99,8%"), ("Hallen", "2"), ("Differenzen", "0")], [("Inventurdifferenz", "0"), ("Lagerplaetze", "234"), ("Chargenstatus", "gruen")], [("Inventurprotokoll.pdf", "/lager/inventur")], [("Lagerbestand", "/lager/bestandsuebersicht", "primary", "/api/v1/inventory")], ("Bestand stabil", "Keine Differenz im laufenden Abgleich.", ["Chargenstatus sauber"])),
        _node("transfer", "Umlagerung", "ok", "ArrowLeftRight", "1,2k Einheiten", "06:40", "Umlagerung abgeschlossen, Kommissionierzone ist aufgefuellt.", [("Menge", "1,2k"), ("Sperrplaetze", "0"), ("Zone", "Kommissionierung")], [("Transfer SLA", "97%"), ("Queue", "0"), ("Wellenbezug", "3")], [("Transferliste.pdf", "/lager/auslagerung")], [("Umlagerung", "/lager/auslagerung", "primary", "/api/v1/warehouses/transfers")], ("Umlagerung abgeschlossen", "Kommissionierzone ist bereit.", ["Zone aufgefuellt"])),
        _node("picking", "Kommissionierung", "active", "Package", "85% erledigt", "Heute", "Kommissionierung laeuft, Prioritaetswelle 2 benoetigt Engpasssteuerung.", [("Completion", "85%"), ("Wellen", "3 aktiv"), ("Engpass", "Welle 2")], [("Wave Completion", "85%"), ("Queue", "12"), ("Risk Score", "69/100")], [("Wellenliste.pdf", "/lager/lagerbewegungen")], [("Kommissionierung", "/lager/terminal", "primary", "/api/v1/pick-lists")], ("Welle 2 benoetigt Eingriff", "Engpasssteuerung oder Rampenwechsel empfohlen.", ["Prioritaetswelle blockiert"])),
        _node("dispatch", "Versand", "warning", "Truck", "ETA +4h", "Heute", "Rampenkonflikt erkannt, Umlenkung oder Zeitslot-Verschiebung empfohlen.", [("ETA", "+4h"), ("Dock", "4"), ("Slot Risk", "hoch")], [("Dock SLA", "86%"), ("ETA Drift", "+4h"), ("Offene Konflikte", "1")], [("Versandavis ASN-442", "/verladung")], [("Verladung", "/verladung", "primary", "/api/v1/tours")], ("Rampenkonflikt", "Dock 4 ueberbucht, Slotwechsel fuer Welle 3 empfohlen.", ["Dock 4 belegt"])),
        _node("billing", "Faktura", "warning", "FileText", "12 im Puffer", "T+0", "Faktura wartet auf Versandbestaetigung aus Welle 3.", [("Queue", "12"), ("Versandstatus", "wartet"), ("Abhaengigkeit", "Welle 3")], [("Queue", "12"), ("SLA", "83%"), ("Status", "wartet")], [("Faktura-Puffer.xlsx", "/sales/rechnungen")], [("Rechnungen", "/sales/rechnungen", "primary", "/api/v1/finance/invoices")], ("Faktura im Puffer", "Versandbestaetigung zuerst stabilisieren.", ["Shipping confirmation fehlt"])),
        _node("settlement", "Settlement", "critical", "Landmark", "T+1 Ziel", "T+1", "Settlement kippt, wenn Versandfenster und Faktura nicht stabilisiert werden.", [("Cycle Time", "T+1"), ("Marge", "sensibel"), ("Status", "RISIKO")], [("Settlement Forecast", "EUR 64.200"), ("Cycle Time", "T+1"), ("Risk", "hoch")], [("Settlement-Puffer.xlsx", "/annahme/abrechnung")], [("Settlement pruefen", "/annahme/abrechnung", "primary", "/api/v1/process/settlement/completion/evaluate")], ("Settlement gefaehrdet", "Versand und Faktura muessen vor T+1 stabilisiert werden.", ["Rampenkonflikt", "Faktura wartet"])),
    ],
    [("Lager-Heatmap", ["Dock 4", "Halle B", "Welle 3"]), ("Agent Events", ["Rampenwarnung aktualisiert", "Settlement-Risiko gestiegen"]), ("Naechste Schritte", ["Rampendaten live anbinden", "Settlement-Automation koppeln"])],
    "workflow",
)

WORKSPACES["harvest-to-settlement"] = _workspace(
    "harvest-to-settlement",
    "Harvest-to-Settlement",
    "Ernteannahme, Trocknung, Einlagerung und Abrechnung als gesteuerter Kampagnenraum.",
    "Kampagne ERN-2026-004",
    "Agrar Operations",
    "Flow",
    "Suche in Annahmen, Trocknern, Silos oder Abrechnungen ...",
    [("Qualitaet stabil", "ok"), ("1 Trocknungsstufe kritisch", "warning")],
    ["Kampagne ERN-2026-004", "Kontrakt K-2026-188"],
    ["Trocknungsgrad aktualisiert", "Kontrakt zugeordnet"],
    ["Lagerleitung", "Abrechnungs-Desk"],
    [("Annahme-Protokoll ERN-2026.pdf", "/agrar/ernte-annahme-erfassung"), ("Trockner-Log T-3.xlsx", "/dokumente/ablage")],
    [
        ("Ernteannahme", "/agrar/ernte-annahme-erfassung", "/api/v1/agrar/harvest-acceptance"),
        ("Silo-Kapazitaeten", "/silo/kapazitaeten", "/api/v1/inventory"),
        ("Abrechnung", "/annahme/abrechnung", "/api/v1/agrar/settlements"),
    ],
    "trocknung",
    [
        _node("annahme", "Annahme", "ok", "Truck", "12,4 t Weizen", "06:30", "Rohware angenommen, Qualitaetspruefung ohne Beanstandungen.", [("Charge", "ERN-2026-004"), ("Feuchte", "18,2%"), ("Wiegeschein", "WT-32091")], [("Menge", "12,4 t"), ("Queue", "3 LKW"), ("Qualitaet", "grün")], [("Annahmeprotokoll.pdf", "/agrar/ernte-annahme-erfassung")], [("Annahme oeffnen", "/agrar/ernte-annahme-erfassung", "primary", "/api/v1/agrar/harvest-acceptance")], ("Annahme abgeschlossen", "Rohware und Ticket sind verknuepft.", ["Wiegeschein vorhanden", "Qualitaet erfasst"])),
        _node("trocknung", "Trocknung", "active", "Sparkles", "8,1 t aktiv", "Heute", "Trocknung aktiv, Zielfeuchte 14% wird in 4h erreicht.", [("Trockner", "Linie T-3"), ("Zielfeuchte", "14%"), ("Restlaufzeit", "4h")], [("Trocknungsgrad", "94%"), ("Energie", "1,8 MWh"), ("Kapazitaet", "78%")], [("Trockner-Log.xlsx", "/dokumente/ablage")], [("Trockner planen", "/workflow/workflow-monitoring", "primary", "/api/v1/background-jobs/queues"), ("Silokapazitaet pruefen", "/silo/kapazitaeten", "secondary", "/api/v1/inventory")], ("Trocknungskapazitaet an Grenze", "Umlagerung oder Dritttrockner empfohlen.", ["Silo 3 kritisch", "Feuchtegrad schwankt"])),
        _node("einlagerung", "Einlagerung", "warning", "Warehouse", "Silo 3 90%", "Heute", "Silo 3 fast voll, Umlagerung in Silo 5 empfohlen.", [("Silo", "3"), ("Belegung", "90%"), ("Alternative", "Silo 5")], [("Auslastung", "90%"), ("ETA", "+1h"), ("Risk", "mittel")], [("Silobelegung.pdf", "/silo/kapazitaeten")], [("Siloansicht", "/silo/kapazitaeten", "primary", "/api/v1/inventory")], ("Silokapazitaet bedroht Folgefluss", "Einlagerung muss vor Abrechnung stabil sein.", ["Silo 3 kritisch"])),
        _node("kontrakt", "Kontrakt", "warning", "BookOpen", "K-2026-188", "T+2", "Qualitaetsabweichung erkannt, Kontraktruecksprache erforderlich.", [("Kontrakt", "K-2026-188"), ("Abweichung", "Protein"), ("Status", "in Klaerung")], [("Abweichungen", "1"), ("SLA", "95%"), ("Owner", "Kontrakt Desk")], [("Kontrakt-K-2026-188.pdf", "/kontrakte")], [("Kontrakt pruefen", "/kontrakte", "primary", "/api/v1/agrar/contracts")], ("Ruecksprache noetig", "Qualitaetsabweichung muss dokumentiert werden.", ["Abweichung erkannt"])),
        _node("abrechnung", "Abrechnung", "critical", "Receipt", "EUR 4.820", "T+5", "Abrechnung kippt, wenn Trocknungsgrad nicht stabil bleibt.", [("Settlement", "SET-2026-188"), ("Forecast", "EUR 4.820"), ("Marge", "sensibel")], [("Forecast", "EUR 4.820"), ("Cycle", "T+5"), ("Risk", "hoch")], [("Abrechnungsvorschau.pdf", "/annahme/abrechnung")], [("Abrechnung pruefen", "/annahme/abrechnung", "primary", "/api/v1/agrar/settlements")], ("Abrechnung gefaehrdet", "Vor Settlement Trocknung und Kontrakt klaeren.", ["Trocknung offen", "Kontrakt offen"])),
        _node("zahlung", "Zahlung", "critical", "Wallet", "Skonto offen", "T+10", "Skontofenster gefaehrdet, wenn Abrechnung weiter rutscht.", [("Faelligkeit", "T+10"), ("Skonto", "2%"), ("Cash", "EUR 96")], [("Skonto", "2%"), ("Cash Forecast", "EUR 96"), ("Risk", "hoch")], [("Zahlungsvorschlag.pdf", "/finance/zahlungslauf-kreditoren")], [("Zahlungslauf", "/finance/zahlungslauf-kreditoren", "primary", "/api/v1/finance/payment-runs")], ("Skonto-Fenster bedroht", "Abrechnung stabilisieren und Zahlung terminieren.", ["Abrechnung verzogen"])),
    ],
    [("Silo-Heatmap", ["Silo 3", "Trockner T-3", "Kampagne ERN-2026-004"]), ("Agent Events", ["Trocknungswarnung aktualisiert", "Abrechnungsrisiko angestiegen"]), ("Naechste Schritte", ["Umlagerung anstoßen", "Abrechnung freigeben"])],
    "workflow",
)

WORKSPACES["contract-to-settlement"] = _workspace(
    "contract-to-settlement", "Contract-to-Settlement", "Agrarischer Kernfluss ohne Medienbruch von Kontrakt bis Abrechnung.", "Kette CTS-2026-014", "Agrar Operations", "Flow",
    "Suche in Kontrakten, Annahmen, Qualitaetsprotokollen oder Settlements ...",
    [("3 von 4 Gliedern gruen", "ok"), ("Settlement-Freigabe offen", "warning")],
    ["Kette CTS-2026-014", "Kontrakt KNT-884"], ["Annahme aktualisiert", "Qualitaetsprotokoll bestaetigt"], ["Kontraktmanagement", "Annahmeleitung", "Settlement Desk"],
    [("Kontrakt_884.pdf", "/kontrakte"), ("Qualitaetsprotokoll_884.pdf", "/annahme/qualitaets-check")],
    [("Kontrakte", "/kontrakte", "/api/v1/agrar/contracts"), ("Ernteannahme", "/agrar/ernte-annahme-erfassung", "/api/v1/agrar/harvest-acceptance"), ("Qualitaetscheck", "/annahme/qualitaets-check", "/api/v1/agrar/quality-protocols"), ("Abrechnung", "/annahme/abrechnung", "/api/v1/agrar/settlements")],
    "acceptance",
    [
        _node("contract", "Kontrakt", "ok", "BookOpen", "KNT-884", "08:10", "Lieferkontrakt ist vollstaendig digital verknuepft.", [("Kontrakt", "KNT-884"), ("Menge", "240 t"), ("Preis", "EUR 225,50")], [("Kontraktwert", "EUR 54.120"), ("Status", "aktiv"), ("Verknuepfung", "digital")], [("Kontrakt_884.pdf", "/kontrakte")], [("Kontrakt oeffnen", "/kontrakte", "primary", "/api/v1/agrar/contracts")], ("Kontrakt ist konsistent", "Preis, Menge und Lieferfenster stimmen.", ["Digitale Verknuepfung vorhanden"])),
        _node("acceptance", "Annahme", "active", "Truck", "ANH-551", "Heute", "Ernteannahme ist erfasst und referenziert den Kontrakt ohne Medienbruch.", [("Annahme", "ANH-551"), ("Wiegeschein", "WT-9911"), ("Menge", "24,8 t")], [("Queue", "2"), ("Wartezeit", "11 Min"), ("Link Score", "100%")], [("Wiegeschein WT-9911", "/waage/wiegungen")], [("Annahme bearbeiten", "/agrar/ernte-annahme-erfassung", "primary", "/api/v1/agrar/harvest-acceptance")], ("Annahme sauber verknuepft", "Kontrakt- und Ticketbezug sind vollstaendig.", ["Kein Medienbruch"])),
        _node("quality", "Qualitaet", "ok", "ShieldCheck", "Prot-884", "Heute", "Qualitaetsprotokoll liegt vor und ist der Annahme zugeordnet.", [("Protein", "12,6%"), ("Feuchte", "13,9%"), ("Status", "freigegeben")], [("Protokoll", "vorhanden"), ("Abweichungen", "0"), ("SLA", "97%")], [("Qualitaetsprotokoll.pdf", "/annahme/qualitaets-check")], [("Qualitaet oeffnen", "/annahme/qualitaets-check", "primary", "/api/v1/agrar/quality-protocols")], ("Qualitaet innerhalb Toleranz", "Keine Abweichung zum Kontraktprofil.", ["Feuchte ok", "Protein ok"])),
        _node("settlement", "Settlement", "warning", "Receipt", "SET-551", "T+1", "Settlement ist vorbereitet, wartet aber auf finale Freigabe und Journal-Posting.", [("Settlement", "SET-551"), ("Netto", "EUR 5.492"), ("Freigabe", "offen")], [("Forecast", "EUR 5.492"), ("GoBD Check", "bereit"), ("Freigabe", "offen")], [("Settlement-Vorschau.pdf", "/annahme/abrechnung")], [("Abrechnung", "/annahme/abrechnung", "primary", "/api/v1/agrar/settlements"), ("Abschlusspruefung", "/finance/abschluss", "secondary", "/api/v1/process/settlement/completion/evaluate")], ("Freigabe noch offen", "Settlement-Journal und Abschlussvertrag zuerst pruefen.", ["Freigabe offen"])),
    ],
    [("Medienbruch-KPI", ["95% Ziel", "digitale Kette aktiv", "keine Nebenliste"]), ("Agent Events", ["Qualitaet bestaetigt", "Settlement Preview aktualisiert"]), ("Naechste Schritte", ["Freigabe abschliessen", "Journal posten", "Blockchain-Anchor setzen"])],
    "annahme",
)

WORKSPACES["complaint-to-resolution"] = _workspace(
    "complaint-to-resolution", "Complaint-to-Resolution", "Reklamationen mit CRM, DMS und Audit-Trail als durchgehender Prozessraum.", "Reklamation REK-2026-044", "Quality Service Lead", "Fokus",
    "Suche in Reklamationen, CRM-Cases oder DMS-Referenzen ...",
    [("SLA im Ziel", "ok"), ("1 Eskalation aktiv", "warning")],
    ["REK-2026-044", "Case CRM-551"], ["DMS-Referenz nachgezogen", "Kulanzoption bewertet"], ["Service Desk", "Qualitaet", "Vertrieb"],
    [("Schadensfoto_884.jpg", "/dokumente/ablage"), ("Reklamationsakte.pdf", "/qualitaet/reklamationen")],
    [("Reklamationen", "/qualitaet/reklamationen", "/api/v1/reklamationen"), ("CRM Cases", "/crm/kunden", "/api/v1/crm/cases"), ("Dokumentenablage", "/dokumente/ablage", "/api/v1/docflow")],
    "triage",
    [
        _node("capture", "Erfassung", "ok", "FileText", "REK-2026-044", "08:05", "Reklamation wurde mit CRM- und DMS-Bezug erfasst.", [("Case", "CRM-551"), ("DMS", "2 Referenzen"), ("Kunde", "Muster Agrar")], [("Erfassungszeit", "4 Min"), ("Anhange", "2"), ("SLA Start", "aktiv")], [("Reklamationsakte.pdf", "/qualitaet/reklamationen")], [("Reklamation oeffnen", "/qualitaet/reklamationen", "primary", "/api/v1/reklamationen")], ("DMS und CRM verknuepft", "Erfassung ist vollstaendig angelegt.", ["CRM-Case vorhanden", "DMS-Referenzen vorhanden"])),
        _node("triage", "Triage", "active", "ShieldCheck", "Prioritaet hoch", "Heute", "Triage bewertet SLA, Ursache und Eskalationspfad.", [("Prioritaet", "hoch"), ("SLA", "24h"), ("Eskalation", "aktiv")], [("SLA Rest", "9h"), ("Risiko", "78%"), ("Owner", "Service Desk")], [("Triage-Notiz.pdf", "/qualitaet/reklamationen")], [("Case aktualisieren", "/qualitaet/reklamationen", "primary", "/api/v1/reklamationen/REK-2026-044/transition")], ("Kulanzpfad empfohlen", "Risiko fuer Kundenabwanderung ist erhoeht.", ["Wiederholungskunde", "SLA knapp"])),
        _node("investigation", "Analyse", "warning", "Search", "DMS + CRM", "Heute", "Dokumente, Fotos und CRM-Historie werden zusammengefuehrt.", [("Belege", "5"), ("Fotos", "2"), ("Auffaelligkeit", "Charge")], [("Dokumentquote", "100%"), ("Analysezeit", "38 Min"), ("Auffaelligkeiten", "1")], [("Schadensfoto.jpg", "/dokumente/ablage")], [("DMS ansehen", "/dokumente/ablage", "primary", "/api/v1/docflow")], ("Charge auffaellig", "Vergleich mit aehnlichen Faellen vorgeschlagen.", ["Auffaellige Charge"])),
        _node("resolution", "Loesung", "warning", "Sparkles", "Kulanz offen", "T+1", "Loesungsweg ist vorbereitet, Freigabe fuer Kulanz steht noch aus.", [("Option", "Kulanz"), ("Wert", "EUR 620"), ("Status", "wartet")], [("Freigabe", "offen"), ("Kulanzwert", "EUR 620"), ("SLA", "im Ziel")], [("Kulanzfreigabe.pdf", "/workflows/approval")], [("Freigabe senden", "/workflows/approval", "primary", "/api/v1/reklamationen/REK-2026-044/transition")], ("Kulanzpfad plausibel", "Freigabe durch Vertrieb oder Qualitaet noetig.", ["Kundenwert hoch"])),
        _node("closure", "Abschluss", "critical", "BookOpen", "Audit offen", "T+2", "Abschluss erfordert finalen Audit-Trail und Rueckmeldung an den Kunden.", [("Audit", "offen"), ("Rueckmeldung", "ausstehend"), ("Status", "RISIKO")], [("SLA", "95%"), ("Abschlussquote", "88%"), ("Kundenfeedback", "ausstehend")], [("Audit-Trail.pdf", "/admin/audit-log")], [("Audit oeffnen", "/admin/audit-log", "primary", "/api/v1/reklamationen/REK-2026-044/audit")], ("Audit noch nicht komplett", "Rueckmeldung an Kunde und Abschlussbuchung fehlen.", ["Audit offen"])),
    ],
    [("SLA-Board", ["24h Erstreaktion", "Kulanzqueue", "Abschlussquote"]), ("Agent Events", ["Kulanzpfad bewertet", "DMS-Link nachgezogen"]), ("Naechste Schritte", ["Freigabe abschliessen", "Kundenfeedback buchen"])],
    "quality",
)

WORKSPACES["service-to-customer"] = _workspace(
    "service-to-customer", "Service-to-Customer", "Serviceanfrage, Disposition, Ausfuehrung und Rueckmeldung in einem agentenfaehigen Raum.", "Servicefall SVC-2026-071", "Service Coordinator", "Flow",
    "Suche in Servicefaellen, Einsaetzen oder Kunden ...",
    [("Tour im Plan", "ok"), ("1 Termin kritisch", "warning")],
    ["SVC-2026-071", "Route Nordwest"], ["Einsatz priorisiert", "Kundenfenster geaendert"], ["Service Desk", "Field Service", "Customer Success"],
    [("Serviceauftrag_071.pdf", "/service/anfragen"), ("Anfahrtsskizze.png", "/agribusiness/field-service-tasks")],
    [("Serviceanfragen", "/service/anfragen", "/api/v1/crm/cases"), ("Field Service", "/agribusiness/field-service-tasks", "/api/v1/crm/cases"), ("Aktivitaeten", "/crm/aktivitaeten", "/api/v1/crm/activities")],
    "dispatch",
    [
        _node("request", "Anfrage", "ok", "FileText", "SVC-2026-071", "07:55", "Serviceanfrage ist aufgenommen und dem Kunden zugeordnet.", [("Fall", "SVC-2026-071"), ("Kunde", "Hofgemeinschaft West"), ("Kategorie", "Vor-Ort-Service")], [("Anlagezeit", "6 Min"), ("Kundensegment", "A"), ("Status", "neu")], [("Serviceauftrag.pdf", "/service/anfragen")], [("Anfrage oeffnen", "/service/anfragen", "primary", "/api/v1/crm/cases")], ("Anfrage ist eindeutig", "Kundendaten und Dringlichkeit sind vorhanden.", ["Anfrage vollstaendig"])),
        _node("planning", "Disposition", "ok", "Calendar", "2 Slots", "08:20", "Einsatz und Techniker wurden disponiert.", [("Techniker", "2"), ("Route", "Nordwest"), ("Fenster", "09:00 - 11:00")], [("Auslastung", "84%"), ("Puenktlichkeit", "93%"), ("Terminreserve", "45 Min")], [("Tagesroute.pdf", "/agribusiness/field-service-tasks")], [("Disposition", "/agribusiness/field-service-tasks", "primary", "/api/v1/crm/cases")], ("Route ist optimiert", "Termin und Fahrzeit sind innerhalb SLA.", ["Route optimiert"])),
        _node("dispatch", "Einsatz", "active", "Truck", "Vor Ort", "Heute", "Techniker ist unterwegs, Live-Rueckmeldung und ETA laufen.", [("ETA", "09:40"), ("Techniker", "Team 2"), ("Kunde", "bestaetigt")], [("ETA", "09:40"), ("SLA", "97%"), ("No-Show Risk", "niedrig")], [("Anfahrtsskizze.png", "/agribusiness/field-service-tasks")], [("Field Task", "/agribusiness/field-service-tasks", "primary", "/api/v1/crm/cases")], ("Kunde informiert", "ETA stabil, Vorbereitung auf Rueckmeldung.", ["Kunde bestaetigt"])),
        _node("report", "Rueckmeldung", "warning", "BookOpen", "Befund offen", "Heute", "Technikerbericht ist begonnen, Materialverbrauch muss noch erfasst werden.", [("Bericht", "begonnen"), ("Material", "offen"), ("Fotos", "1")], [("Report Completion", "60%"), ("Materialerfassung", "offen"), ("Kundenfreigabe", "wartet")], [("Technikerbericht.pdf", "/crm/aktivitaeten")], [("Aktivitaet buchen", "/crm/aktivitaeten", "primary", "/api/v1/crm/activities")], ("Materialverbrauch fehlt", "Rueckmeldung vor Kundenabschluss vervollstaendigen.", ["Material offen"])),
        _node("closure", "Kundenabschluss", "warning", "UserCircle2", "Feedback ausstehend", "T+1", "Kundenrueckmeldung und Abschlussbewertung fehlen noch.", [("Feedback", "ausstehend"), ("Status", "wartet"), ("CSAT", "-")], [("First-Time-Fix", "91%"), ("CSAT", "ausstehend"), ("Abschlusszeit", "T+1")], [("Abschlussnotiz.pdf", "/service/anfragen")], [("Abschluss senden", "/service/anfragen", "primary", "/api/v1/crm/cases")], ("Kundenfeedback fehlt", "Finale Rueckmeldung fuer sauberen Abschluss einholen.", ["Feedback ausstehend"])),
    ],
    [("Tourenstatus", ["Route Nordwest", "ETA stabil", "1 kritischer Termin"]), ("Agent Events", ["Kundenfenster geaendert", "Techniker ETA aktualisiert"]), ("Naechste Schritte", ["Rueckmeldung vervollstaendigen", "Feedback sichern"])],
    "service",
)

WORKSPACES["finance-to-close"] = _workspace(
    "finance-to-close",
    "Finance-to-Close",
    "Buchung, Abstimmung, Meldewesen und Abschluss als periodischer Steuerraum.",
    "Periode Maerz 2026",
    "Finance Lead",
    "Fokus",
    "Suche in Buchungen, Konten, Abstimmungen oder Meldungen ...",
    [("Buchungen vollstaendig", "ok"), ("1 Abstimmung offen", "warning")],
    ["Periode Maerz 2026", "Sachkonto 1200"],
    ["Abstimmung aktualisiert", "USTVA eingereicht"],
    ["Buchhalter", "Controller"],
    [("Buchungsjournal_Maerz.xlsx", "/finance/bookings/new"), ("USTVA-Vordruck.pdf", "/finance/ustva")],
    [
        ("Buchungserfassung", "/finance/bookings/new", "/api/v1/journal-entries"),
        ("Abschluss-Cockpit", "/fibu/abschluss-cockpit", "/api/v1/finance/close-readiness"),
        ("USTVA", "/finance/ustva", "/api/v1/compliance/ustva"),
    ],
    "abstimmung",
    [
        _node("buchung", "Buchung", "ok", "BookOpen", "1.284 Belege", "08:00", "Alle Buchungen fuer Maerz sind erfasst und validiert.", [("Periode", "03/2026"), ("Buchungen", "1.284"), ("Status", "vollstaendig")], [("Quote", "100%"), ("Validierungen", "18"), ("Fehler", "0")], [("Buchungsjournal.xlsx", "/finance/bookings/new")], [("Buchungen oeffnen", "/finance/bookings/new", "primary", "/api/v1/journal-entries")], ("Buchungen sind stabil", "Periodenstart fuer den Abschluss ist sauber vorbereitet.", ["Keine offenen Fehler"])),
        _node("abstimmung", "Abstimmung", "active", "ArrowLeftRight", "3 Konten offen", "Heute", "Abstimmung laeuft, 3 Sachkonten zeigen kleine Abweichungen.", [("Konten", "1200, 1576, 8400"), ("Differenz", "EUR 240"), ("Owner", "Finance Lead")], [("Abstimmungsquote", "97%"), ("Differenz", "EUR 240"), ("Risk", "mittel")], [("Abstimmungsprotokoll.pdf", "/finance/nebenbuch-abstimmung")], [("Nebenbuch-Abstimmung", "/finance/nebenbuch-abstimmung", "primary", "/api/v1/finance/reconciliation")], ("Abstimmungsabweichung erkannt", "Klaerung vor USTVA und Sign-off noetig.", ["Konto 1200 offen"])),
        _node("meldewesen", "Meldewesen", "warning", "FileText", "USTVA faellig", "T+3", "USTVA-Frist in 3 Tagen, Vorbereitungsgrad bei 82%.", [("Frist", "10. April"), ("Status", "in Vorbereitung"), ("Vollstaendigkeit", "82%")], [("Readiness", "82%"), ("Frist", "T+3"), ("Risk", "mittel")], [("USTVA-Vordruck.pdf", "/finance/ustva")], [("USTVA oeffnen", "/finance/ustva", "primary", "/api/v1/compliance/ustva")], ("USTVA-Frist naehert sich", "Abstimmung abschliessen und Meldung vorbereiten.", ["Deadline T+3"])),
        _node("abschluss-check", "Abschluss-Check", "warning", "ShieldCheck", "2 Hinweise", "T+5", "Zwei Hinweise aus Plausibilitaetspruefung, Klaerung erforderlich.", [("Hinweise", "2"), ("Pruefquote", "94%"), ("Owner", "Controlling")], [("Check Quote", "94%"), ("Hinweise", "2"), ("Risk", "mittel")], [("Abschluss-Check.docx", "/finance/abschluss")], [("Abschluss pruefen", "/finance/abschluss", "primary", "/api/v1/process/settlement/completion/evaluate")], ("Plausibilitaet noch nicht sauber", "Vor Sign-off Abschluss-Check bereinigen.", ["2 Hinweise offen"])),
        _node("genehmigung", "Genehmigung", "critical", "UserCircle2", "CFO Sign-off", "T+7", "Genehmigungsfrist kippt, wenn Abstimmung nicht abgeschlossen wird.", [("Freigabe", "CFO"), ("Frist", "T+7"), ("Status", "wartet")], [("Sign-off", "offen"), ("Deadline", "T+7"), ("Risk", "hoch")], [("CFO-Signoff.pdf", "/workflows/approval")], [("Sign-off anfordern", "/workflows/approval", "primary", "/api/v1/channels/slack/process-actions/execute")], ("Sign-off gefaehrdet", "Abstimmung und Meldung zuerst stabilisieren.", ["Freigabe offen"])),
        _node("abschluss", "Abschluss", "critical", "Landmark", "T+10 Ziel", "T+10", "Abschluss gefaehrdet, wenn Genehmigung und USTVA nicht rechtzeitig vorliegen.", [("Ziel", "T+10"), ("Marge", "sensibel"), ("Status", "RISIKO")], [("Abschlussquote", "84%"), ("Periodenertrag", "EUR 284.000"), ("Risk", "hoch")], [("Abschlussprotokoll.pdf", "/finance/abschluss")], [("Abschluss cockpit", "/fibu/abschluss-cockpit", "primary", "/api/v1/finance/close-readiness")], ("Abschluss nicht stabil", "Offene Vorstufen blockieren den finalen Close.", ["USTVA offen", "Sign-off offen"])),
    ],
    [("Abschluss-Heatmap", ["Periode 03/2026", "Konto 1200", "USTVA"]), ("Agent Events", ["Abstimmungsabweichung erkannt", "USTVA-Frist aktualisiert"]), ("Naechste Schritte", ["Abstimmung abschliessen", "CFO Sign-off sichern"])],
    "workflow",
)

WORKSPACES["compliance-to-report"] = _workspace(
    "compliance-to-report",
    "Compliance-to-Report",
    "Nachhaltigkeit, Compliance, Freigabe und Reporting als auditierbarer End-to-End-Prozess.",
    "Reporting CO2-2026-Q1",
    "Compliance Lead",
    "Uebersicht",
    "Suche in EUDR, CO2-Bilanzen, Meldungen oder Reports ...",
    [("Audit-Trail vollstaendig", "ok"), ("1 Freigabe offen", "warning")],
    ["CO2-2026-Q1", "EUDR Batch 551"],
    ["CO2-Daten aktualisiert", "EUDR-Nachweis importiert"],
    ["Compliance", "Nachhaltigkeit", "Management"],
    [("CO2_Bilanz_Q1.pdf", "/nachhaltigkeit/co2-bilanz"), ("EUDR_Nachweis_551.pdf", "/nachhaltigkeit/eudr-compliance")],
    [
        ("CO2 Bilanz", "/nachhaltigkeit/co2-bilanz", "/api/v1/sustainability/read-model"),
        ("EUDR Compliance", "/nachhaltigkeit/eudr-compliance", "/api/v1/compliance/eudr"),
        ("ESG Report", "/nachhaltigkeit/esg-report", "/api/v1/sustainability/read-model"),
    ],
    "aggregation",
    [
        _node("collection", "Datensammlung", "ok", "Database", "12 Quellen", "Heute", "Datenquellen fuer Compliance und Nachhaltigkeit sind konsolidiert.", [("Quellen", "12"), ("Deckung", "98%"), ("Status", "vollstaendig")], [("Coverage", "98%"), ("Imports", "12"), ("Fehler", "0")], [("Importprotokoll.pdf", "/admin/data-quality")], [("Datenqualitaet", "/admin/data-quality", "primary", "/api/v1/data-quality/rules")], ("Datenbasis ist tragfaehig", "Keine kritischen Luecken in den Quelldaten.", ["12 Quellen aktiv"])),
        _node("aggregation", "Aggregation", "active", "Calculator", "Q1 konsolidiert", "Heute", "CO2- und Compliance-Metriken werden fuer das Quartal berechnet.", [("Periode", "Q1 2026"), ("CO2", "284 t"), ("EUDR", "Batch 551")], [("CO2", "284 t"), ("Readiness", "91%"), ("Risk", "niedrig")], [("CO2_Bilanz_Q1.pdf", "/nachhaltigkeit/co2-bilanz")], [("CO2 Bilanz", "/nachhaltigkeit/co2-bilanz", "primary", "/api/v1/sustainability/read-model")], ("Aggregation laeuft", "Eine Management-Freigabe steht noch aus.", ["Q1 konsolidiert"])),
        _node("validation", "Validierung", "warning", "ShieldCheck", "1 Ausnahme", "T+1", "Ein Herkunftsnachweis benoetigt manuelle Freigabe.", [("Ausnahmen", "1"), ("Quelle", "EUDR Batch 551"), ("Status", "wartet")], [("Validierungsquote", "96%"), ("Ausnahmen", "1"), ("Risk", "mittel")], [("EUDR_Nachweis_551.pdf", "/nachhaltigkeit/eudr-compliance")], [("EUDR pruefen", "/nachhaltigkeit/eudr-compliance", "primary", "/api/v1/compliance/eudr")], ("Herkunftsnachweis offen", "Vor Report-Freigabe die Ausnahme bereinigen.", ["1 Ausnahme"])),
        _node("approval", "Freigabe", "warning", "UserCircle2", "Management offen", "T+2", "Management-Freigabe fuer das Quartalsreporting fehlt noch.", [("Freigabe", "Management"), ("Status", "offen"), ("Deadline", "T+2")], [("Freigabequote", "75%"), ("Owner", "Compliance Lead"), ("Risk", "mittel")], [("Freigabeprotokoll.pdf", "/workflows/approval")], [("Freigabe senden", "/workflows/approval", "primary", "/api/v1/channels/slack/process-actions/execute")], ("Freigabe steht aus", "Report kann nach Ausnahme-Klaerung direkt in Freigabe gehen.", ["Management offen"])),
        _node("reporting", "Reporting", "critical", "FileText", "Versand wartet", "T+3", "ESG- und Compliance-Report sind vorbereitet, aber noch nicht publiziert.", [("Report", "Q1 2026"), ("Status", "wartet"), ("Empfaenger", "Vorstand + Genossenschaft")], [("Readiness", "88%"), ("Distribution", "wartet"), ("Audit", "vollstaendig")], [("ESG_Report_Q1.pdf", "/nachhaltigkeit/esg-report")], [("ESG Report", "/nachhaltigkeit/esg-report", "primary", "/api/v1/sustainability/read-model")], ("Versand wartet auf Freigabe", "Publikation erst nach finalem Sign-off.", ["Freigabe offen"])),
    ],
    [("Compliance Board", ["CO2", "EUDR", "ESG Report"]), ("Agent Events", ["EUDR-Ausnahme erkannt", "CO2-Daten aktualisiert"]), ("Naechste Schritte", ["Ausnahme klaeren", "Freigabe einholen", "Report publizieren"])],
    "workflow",
)

# JSON string cache for workspaces: key = (process_key, lang code)
_workspace_json_cache: dict[tuple[str, str], str] = {}


def get_flow_spine_workspace(process_key: str, lang: str | None = None) -> dict:
    lang_key = lang or "de"
    cache_key = (process_key, lang_key)

    cached_json = _workspace_json_cache.get(cache_key)
    if cached_json is None:
        try:
            raw = WORKSPACES[process_key]
        except KeyError as exc:
            raise KeyError(process_key) from exc
        # Localize once, serialize to JSON string, cache it
        localized = _localize_payload(copy.deepcopy(raw), lang)
        cached_json = _json.dumps(localized, ensure_ascii=False)
        _workspace_json_cache[cache_key] = cached_json

    # Fast deserialization is much cheaper than deepcopy of a complex dict
    return _json.loads(cached_json)


def invalidate_flow_spine_cache(process_key: str | None = None) -> None:
    """Clear cached workspace JSON. Call after registry changes in tests or admin."""
    if process_key:
        keys_to_remove = [k for k in _workspace_json_cache if k[0] == process_key]
        for k in keys_to_remove:
            del _workspace_json_cache[k]
    else:
        _workspace_json_cache.clear()
        _catalog_json_cache.clear()


def merge_instance_statuses(workspace: dict, instance: dict) -> dict:
    """
    Overlay node statuses from an instance onto a workspace dict.

    Iterates workspace["nodes"] and, for each node whose id appears in
    instance["node_statuses"], sets node["status"] to the stored value.
    Also stamps instance_label and instance_id at the workspace root.

    Returns the modified workspace (already a deep copy from get_flow_spine_workspace).
    """
    node_statuses: dict[str, str] = instance.get("node_statuses") or {}
    for node in workspace.get("nodes", []):
        node_id = node.get("id")
        if node_id and node_id in node_statuses:
            node["status"] = node_statuses[node_id]

    if instance.get("label"):
        workspace["instance_label"] = instance["label"]
    if instance.get("instance_id"):
        workspace["instance_id"] = instance["instance_id"]

    return workspace
