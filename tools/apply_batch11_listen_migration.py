"""Batch-11: Listen-ScreenDefinitions + NativeListPage fuer 59 Seiten."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LISTEN = ROOT / "app/core/screen_definitions_listen.py"
PAGES = ROOT / "packages/frontend-web/src/pages"
OPENAPI = json.loads((ROOT / "docs/schnittstellen/openapi.json").read_text(encoding="utf-8"))
GET_PATHS = {
    p for p, spec in OPENAPI.get("paths", {}).items() if "get" in spec or "GET" in spec
}

# page relpath -> (screen_id, route_path, builder_suffix, spec kwargs for _liste)
BATCH11: list[tuple[str, str, str, dict]] = [
    ("admin/audit-log.tsx", "admin/audit-log-liste", "/admin/audit-log", {
        "domain": "admin", "title": "Audit-Log", "subtitle": "System-Aktivitaeten und Aenderungen",
        "endpoint": "/api/v1/admin/audit-log", "row_route": None, "bundle": "admin",
        "columns": [
            {"key": "zeitstempel", "label": "Zeitstempel", "sortable": True, "priority": "primary"},
            {"key": "benutzer", "label": "Benutzer", "filterable": True, "priority": "primary"},
            {"key": "aktion", "label": "Aktion", "filterable": True, "priority": "secondary"},
            {"key": "objekt", "label": "Objekt", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Audit-Ereignisse nachvollziehen und exportieren.",
        "prompts": ["Welche Aenderungen gab es heute?", "Wer hat den Datensatz geaendert?"],
    }),
    ("agrar/bodenproben/liste.tsx", "agrar/bodenproben-liste", "/agrar/bodenproben/liste", {
        "domain": "agrar", "title": "Bodenproben", "subtitle": "Proben je Schlag und Labor",
        "endpoint": "/api/v1/labor/proben", "row_route": "/agrar/bodenprobe/{id}", "bundle": "agrar",
        "columns": [
            {"key": "schlag", "label": "Schlag", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "labor", "label": "Labor", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Bodenproben finden und Ergebnisse oeffnen.",
        "prompts": ["Welche Proben warten auf Labor?", "Zeige Proben fuer Schlag X."],
    }),
    ("agrar/ernte-annahme-energiemais.tsx", "agrar/ernte-annahme-energiemais-liste", "/agrar/ernte-annahme-energiemais", {
        "domain": "agrar", "title": "Ernte Annahme Energiemais", "subtitle": "Annahmen Energiemais",
        "endpoint": "/api/v1/agrar/ernte", "row_route": "/agrar/ernte/{id}", "bundle": "agrar",
        "columns": [
            {"key": "schlag", "label": "Schlag", "filterable": True, "priority": "primary"},
            {"key": "kultur", "label": "Kultur", "filterable": True, "priority": "primary"},
            {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Energiemais-Ernten in der Annahme verfolgen.",
        "prompts": ["Welche Energiemais-Lieferungen sind offen?"],
    }),
    ("agrar/feldbuch/ackerschlagkartei.tsx", "agrar/feldbuch-schlagkartei-liste", "/agrar/feldbuch/ackerschlagkartei", {
        "domain": "agrar", "title": "Ackerschlagkartei", "subtitle": "Schlaege und Flaechen",
        "endpoint": "/api/v1/agrar/schlaege", "row_route": "/agrar/feldbuch/schlag/{id}", "bundle": "agrar",
        "columns": [
            {"key": "name", "label": "Schlag", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "flaeche", "label": "Flaeche (ha)", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "kultur", "label": "Kultur", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Schlaege in der Ackerschlagkartei finden.",
        "prompts": ["Welche Schlaege sind aktiv?", "Zeige Flaeche je Kultur."],
    }),
    ("agrar/feldbuch/flurstueck-kataster.tsx", "agrar/feldbuch-flurstueck-kataster-liste", "/agrar/feldbuch/flurstueck-kataster", {
        "domain": "agrar", "title": "Flurstueck-Kataster", "subtitle": "Flurstuecke und Geometrie",
        "endpoint": "/api/v1/agrar/schlaege", "row_route": None, "bundle": "agrar",
        "columns": [
            {"key": "flurstueck", "label": "Flurstueck", "filterable": True, "priority": "primary"},
            {"key": "schlag", "label": "Schlag", "filterable": True, "priority": "primary"},
            {"key": "flaeche", "label": "Flaeche", "numeric": True, "priority": "secondary"},
        ],
        "purpose": "Flurstuecke im Kataster finden.",
        "prompts": ["Welche Flurstuecke gehoeren zu Schlag X?"],
    }),
    ("agrar/kultur-stamm.tsx", "agrar/kultur-stamm-liste", "/agrar/kultur-stamm", {
        "domain": "agrar", "title": "Kulturen", "subtitle": "Kultur-Stamm und Fruchtfolge",
        "endpoint": "/api/v1/agrar/kulturen", "row_route": "/agrar/kultur/{id}", "bundle": "agrar",
        "columns": [
            {"key": "name", "label": "Kultur", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "code", "label": "Code", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Kulturen im Stamm finden.",
        "prompts": ["Welche Kulturen sind aktiv?"],
    }),
    ("agrar/maschinen-auslastung.tsx", "agrar/maschinen-auslastung-liste", "/agrar/maschinen-auslastung", {
        "domain": "agrar", "title": "Maschinenauslastung", "subtitle": "Maschinen und Stunden",
        "endpoint": "/api/v1/agrar/maschinen", "row_route": "/agrar/maschine/{id}", "bundle": "agrar",
        "columns": [
            {"key": "name", "label": "Maschine", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Maschinenauslastung im Blick behalten.",
        "prompts": ["Welche Maschinen sind in Wartung?"],
    }),
    ("agrar/nachhaltigkeit-eudr.tsx", "agrar/nachhaltigkeit-eudr-liste", "/agrar/nachhaltigkeit-eudr", {
        "domain": "agrar", "title": "EUDR Nachhaltigkeit", "subtitle": "Sorgfaltserklaerungen und Risiko",
        "endpoint": "/api/v1/eudr/sorgfaltserklaerungen", "row_route": None, "bundle": "agrar",
        "columns": [
            {"key": "referenz", "label": "Referenz", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        "purpose": "EUDR-Sorgfaltserklaerungen verfolgen.",
        "prompts": ["Welche Erklaerungen sind offen?"],
    }),
    ("agrar/pflanzenschutz-applikationen.tsx", "agrar/pflanzenschutz-applikationen-liste", "/agrar/pflanzenschutz-applikationen", {
        "domain": "agrar", "title": "Pflanzenschutz-Applikationen", "subtitle": "Ausbringungen je Schlag",
        "endpoint": "/api/v1/agrar/feldbuch/massnahmen", "row_route": None, "bundle": "agrar",
        "columns": [
            {"key": "schlag", "label": "Schlag", "filterable": True, "priority": "primary"},
            {"key": "mittel", "label": "Mittel", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Pflanzenschutz-Applikationen dokumentieren und finden.",
        "prompts": ["Welche Applikationen diese Woche?"],
    }),
    ("agrar/psm/abgabedokumentation.tsx", "agrar/psm-abgabedokumentation-liste", "/agrar/psm/abgabedokumentation", {
        "domain": "agrar", "title": "PSM Abgabedokumentation", "subtitle": "Abgaben und Nachweise",
        "endpoint": "/api/v1/agrar/psm/", "row_route": "/agrar/psm/abgabedokumentation/{id}", "bundle": "agrar",
        "columns": [
            {"key": "name", "label": "Mittel", "filterable": True, "priority": "primary"},
            {"key": "kunde", "label": "Kunde", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        "purpose": "PSM-Abgabedokumentation finden.",
        "prompts": ["Welche Abgaben fehlen noch?"],
    }),
    ("agrar/psm/beratung.tsx", "agrar/psm-beratung-liste", "/agrar/psm/beratung", {
        "domain": "agrar", "title": "PSM Beratung", "subtitle": "Beratungsvorgaenge Pflanzenschutz",
        "endpoint": "/api/v1/agrar/psm/", "row_route": None, "bundle": "agrar",
        "columns": [
            {"key": "name", "label": "Mittel", "filterable": True, "priority": "primary"},
            {"key": "wirkstoff", "label": "Wirkstoff", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "PSM-Beratung mit Sortimentsdaten.",
        "prompts": ["Welche Mittel fuer Weizen?"],
    }),
    ("agrar/psm/sachkunde-register.tsx", "agrar/psm-sachkunde-register-liste", "/agrar/psm/sachkunde-register", {
        "domain": "agrar", "title": "PSM Sachkunde", "subtitle": "Sachkundenachweise Kunden",
        "endpoint": "/api/v1/compliance/sachkunde-register", "row_route": "/agrar/psm/sachkunde/{id}/edit", "bundle": "agrar",
        "columns": [
            {"key": "kunde", "label": "Kunde", "filterable": True, "priority": "primary"},
            {"key": "nachweisNr", "label": "Nachweis-Nr.", "filterable": True, "priority": "primary"},
            {"key": "gueltigBis", "label": "Gueltig bis", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Sachkundenachweise fuer PSM-Abgabe pruefen.",
        "prompts": ["Welche Nachweise laufen ab?"],
    }),
    ("agrar/psm/wasserschutz.tsx", "agrar/psm-wasserschutz-liste", "/agrar/psm/wasserschutz", {
        "domain": "agrar", "title": "Wasserschutz", "subtitle": "Wasserschutz-Zonen und Auflagen",
        "endpoint": "/api/v1/agrar/psm/wasserschutz-zonen", "row_route": None, "bundle": "agrar",
        "columns": [
            {"key": "zone", "label": "Zone", "filterable": True, "priority": "primary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Wasserschutzzonen und PSM-Auflagen pruefen.",
        "prompts": ["Welche Zonen sind betroffen?"],
    }),
    ("agrar/saatgut/bestellungen.tsx", "agrar/saatgut-bestellungen-liste", "/agrar/saatgut/bestellungen", {
        "domain": "agrar", "title": "Saatgut-Bestellungen", "subtitle": "Bestellungen Sorten und Mengen",
        "endpoint": "/api/v1/agrar/saatgut/", "row_route": "/agrar/saatgut/bestellung/{id}", "bundle": "agrar",
        "columns": [
            {"key": "sorte", "label": "Sorte", "filterable": True, "priority": "primary"},
            {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Saatgut-Bestellungen verfolgen.",
        "prompts": ["Welche Bestellungen sind offen?"],
    }),
    ("agrar/saatgut/sortenregister.tsx", "agrar/saatgut-sortenregister-liste", "/agrar/saatgut/sortenregister", {
        "domain": "agrar", "title": "Sortenregister", "subtitle": "Zugelassene Sorten",
        "endpoint": "/api/v1/agrar/varieties/", "row_route": "/agrar/saatgut/sorte/{id}", "bundle": "agrar",
        "columns": [
            {"key": "name", "label": "Sorte", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "crop_type", "label": "Kultur", "filterable": True, "priority": "primary"},
            {"key": "zuechter", "label": "Zuechter", "filterable": True, "priority": "secondary"},
            {"key": "aktiv", "label": "Aktiv", "renderKind": "boolean", "filterable": True, "priority": "secondary"},
        ],
        "purpose": "Sortenregister durchsuchen.",
        "prompts": ["Welche Sorten sind aktiv?"],
    }),
    ("agrar/schlaege/index.tsx", "agrar/schlaege-liste", "/agrar/schlaege", {
        "domain": "agrar", "title": "Schlaege", "subtitle": "Schlagstamm und Flaechen",
        "endpoint": "/api/v1/agrar/schlaege", "row_route": "/agrar/schlag/{id}", "bundle": "agrar",
        "columns": [
            {"key": "name", "label": "Schlag", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "flaeche", "label": "Flaeche", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "kultur", "label": "Kultur", "filterable": True, "priority": "secondary"},
        ],
        "purpose": "Schlaege finden und oeffnen.",
        "prompts": ["Welche Schlaege haben Weizen?"],
    }),
    ("agrar/schlaege/karte.tsx", "agrar/schlaege-karte-liste", "/agrar/schlaege/karte", {
        "domain": "agrar", "title": "Schlagkarte", "subtitle": "Schlaege auf der Karte",
        "endpoint": "/api/v1/agrar/schlaege", "row_route": "/agrar/schlag/{id}", "bundle": "agrar",
        "columns": [
            {"key": "name", "label": "Schlag", "filterable": True, "priority": "primary"},
            {"key": "flaeche", "label": "Flaeche", "numeric": True, "priority": "secondary"},
        ],
        "purpose": "Schlaege fuer die Kartenansicht laden.",
        "prompts": ["Zeige alle Schlaege mit Geometrie."],
    }),
    ("agrar/schlaege/kulturhistorie.tsx", "agrar/schlaege-kulturhistorie-liste", "/agrar/schlaege/kulturhistorie", {
        "domain": "agrar", "title": "Kulturhistorie", "subtitle": "Fruchtfolge je Schlag",
        "endpoint": "/api/v1/agrar/schlaege", "row_route": "/agrar/schlag/{id}", "bundle": "agrar",
        "columns": [
            {"key": "schlag", "label": "Schlag", "filterable": True, "priority": "primary"},
            {"key": "kultur", "label": "Kultur", "filterable": True, "priority": "primary"},
            {"key": "jahr", "label": "Jahr", "numeric": True, "sortable": True, "priority": "secondary"},
        ],
        "purpose": "Kulturhistorie der Schlaege einsehen.",
        "prompts": ["Welche Kultur war letztes Jahr auf Schlag X?"],
    }),
    ("agrar/vertrag-kontingente.tsx", "agrar/vertrag-kontingente-liste", "/agrar/vertrag-kontingente", {
        "domain": "agrar", "title": "Vertrag-Kontingente", "subtitle": "Restmengen und Kontingente",
        "endpoint": "/api/v1/kontrakte", "row_route": "/agrar/kontrakt/{id}", "bundle": "agrar",
        "columns": [
            {"key": "nummer", "label": "Kontrakt", "filterable": True, "priority": "primary"},
            {"key": "partner", "label": "Partner", "filterable": True, "priority": "primary"},
            {"key": "restmenge", "label": "Restmenge", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Kontrakt-Kontingente und Restmengen pruefen.",
        "prompts": ["Welche Kontingente sind ausgeschoepft?"],
    }),
    ("charge/wareneingang.tsx", "charge/wareneingang-liste", "/charge/wareneingang", {
        "domain": "lager", "title": "Wareneingang Chargen", "subtitle": "Chargen aus Wareneingaengen",
        "endpoint": "/api/v1/chargen", "row_route": "/charge/stamm/{id}", "bundle": "lager",
        "columns": [
            {"key": "charge", "label": "Charge", "filterable": True, "priority": "primary"},
            {"key": "artikel", "label": "Artikel", "filterable": True, "priority": "primary"},
            {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Wareneingaenge als Chargen erfassen und finden.",
        "prompts": ["Welche Chargen kamen heute rein?"],
    }),
    ("compliance/bvl-umsatzmeldung.tsx", "compliance/bvl-umsatzmeldung-liste", "/compliance/bvl-umsatzmeldung", {
        "domain": "compliance", "title": "BVL Umsatzmeldung", "subtitle": "Pflanzenschutz-Umsatzmeldungen",
        "endpoint": "/api/v1/compliance/bvl-umsaetze", "row_route": None, "bundle": "compliance",
        "columns": [
            {"key": "periode", "label": "Periode", "filterable": True, "priority": "primary"},
            {"key": "umsatz", "label": "Umsatz", "numeric": True, "renderKind": "currency", "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "BVL-Umsatzmeldungen verfolgen.",
        "prompts": ["Welche Meldungen sind faellig?"],
    }),
    ("compliance/CrossCompliancePage.tsx", "compliance/cross-compliance-liste", "/compliance/cross-compliance", {
        "domain": "compliance", "title": "Cross-Compliance", "subtitle": "Anforderungen und Nachweise",
        "endpoint": "/api/v1/compliance/cross-compliance", "row_route": None, "bundle": "compliance",
        "columns": [
            {"key": "bereich", "label": "Bereich", "filterable": True, "priority": "primary"},
            {"key": "anforderung", "label": "Anforderung", "filterable": True, "priority": "primary"},
            {"key": "erfuellt", "label": "Erfuellt", "renderKind": "boolean", "filterable": True, "priority": "primary"},
            {"key": "frist", "label": "Frist", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        "purpose": "Cross-Compliance-Anforderungen pruefen.",
        "prompts": ["Welche Anforderungen sind offen?"],
    }),
    ("compliance/eudr-compliance.tsx", "compliance/eudr-compliance-liste", "/compliance/eudr-compliance", {
        "domain": "compliance", "title": "EUDR Compliance", "subtitle": "Sorgfalt und Lieferketten",
        "endpoint": "/api/v1/eudr/sorgfaltserklaerungen", "row_route": None, "bundle": "compliance",
        "columns": [
            {"key": "referenz", "label": "Referenz", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "EUDR-Compliance-Faelle finden.",
        "prompts": ["Welche Lieferketten sind ungeprueft?"],
    }),
    ("compliance/export-pruefung.tsx", "compliance/export-pruefung-liste", "/compliance/export-pruefung", {
        "domain": "compliance", "title": "Export-Pruefung", "subtitle": "Exportfaehigkeit pruefen",
        "endpoint": "/api/v1/export/entities", "row_route": None, "bundle": "compliance",
        "columns": [
            {"key": "entity", "label": "Entitaet", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Export-Pruefungen nachvollziehen.",
        "prompts": ["Welche Exporte sind blockiert?"],
    }),
    ("compliance/gefahrstoff-doku.tsx", "compliance/gefahrstoff-doku-liste", "/compliance/gefahrstoff-doku", {
        "domain": "compliance", "title": "Gefahrstoff-Doku", "subtitle": "Gefahrstoffdokumentation",
        "endpoint": "/api/v1/compliance/exports/gefahrstoffdoku", "row_route": None, "bundle": "compliance",
        "columns": [
            {"key": "produkt", "label": "Produkt", "filterable": True, "priority": "primary"},
            {"key": "klasse", "label": "Klasse", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Gefahrstoffdokumentation einsehen.",
        "prompts": ["Welche Produkte brauchen Update?"],
    }),
    ("compliance/qs-checkliste.tsx", "compliance/qs-checkliste-liste", "/compliance/qs-checkliste", {
        "domain": "compliance", "title": "QS-Checkliste", "subtitle": "QS-Pruefpunkte",
        "endpoint": "/api/v1/compliance/qs-checkliste", "row_route": None, "bundle": "compliance",
        "columns": [
            {"key": "bereich", "label": "Bereich", "filterable": True, "priority": "primary"},
            {"key": "pruefpunkt", "label": "Pruefpunkt", "filterable": True, "priority": "primary"},
            {"key": "erfuellt", "label": "Erfuellt", "renderKind": "boolean", "filterable": True, "priority": "primary"},
        ],
        "purpose": "QS-Checkliste abarbeiten.",
        "prompts": ["Welche Punkte sind offen?"],
    }),
    ("compliance/sachkunde-register.tsx", "compliance/sachkunde-liste", "/compliance/sachkunde-register", {
        "domain": "compliance", "title": "Sachkundenachweise", "subtitle": "Register Sachkunde",
        "endpoint": "/api/v1/compliance/sachkunde-register", "row_route": None, "bundle": "compliance",
        "columns": [
            {"key": "kunde", "label": "Kunde", "filterable": True, "priority": "primary"},
            {"key": "nachweisNr", "label": "Nachweis-Nr.", "filterable": True, "priority": "primary"},
            {"key": "gueltigBis", "label": "Gueltig bis", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Sachkundenachweise verfolgen.",
        "prompts": ["Welche Nachweise laufen ab?"],
    }),
    ("compliance/vvvo-register.tsx", "compliance/vvvo-liste", "/compliance/vvvo-register", {
        "domain": "compliance", "title": "VVVO-Register", "subtitle": "Betriebe und VVVO-Nummern",
        "endpoint": "/api/v1/compliance/vvvo-register", "row_route": None, "bundle": "compliance",
        "columns": [
            {"key": "betriebsname", "label": "Betrieb", "filterable": True, "priority": "primary"},
            {"key": "vvvo", "label": "VVVO", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "VVVO-Register durchsuchen.",
        "prompts": ["Welche Betriebe sind inaktiv?"],
    }),
    ("compliance/zulassungen-register.tsx", "compliance/zulassungen-liste", "/compliance/zulassungen-register", {
        "domain": "compliance", "title": "Zulassungsregister", "subtitle": "Produktzulassungen",
        "endpoint": "/api/v1/compliance/zulassungen-register", "row_route": None, "bundle": "compliance",
        "columns": [
            {"key": "produkt", "label": "Produkt", "filterable": True, "priority": "primary"},
            {"key": "nummer", "label": "Nummer", "filterable": True, "priority": "primary"},
            {"key": "gueltigBis", "label": "Gueltig bis", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Zulassungen und Ablaufdaten pruefen.",
        "prompts": ["Welche Zulassungen laufen ab?"],
    }),
    ("controlling/plan-ist.tsx", "controlling/plan-ist-liste", "/controlling/plan-ist", {
        "domain": "controlling", "title": "Plan-Ist", "subtitle": "KPIs Plan vs. Ist",
        "endpoint": "/api/v1/controlling/kpis", "row_route": None, "bundle": "controlling",
        "columns": [
            {"key": "name", "label": "KPI", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "kpi_code", "label": "Code", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Plan-Ist-KPIs vergleichen.",
        "prompts": ["Wo weicht Ist vom Plan ab?"],
    }),
    ("crm/contact-detail.tsx", "crm/contact-detail-liste", "/crm/contact-detail", {
        "domain": "crm", "title": "Kontakte", "subtitle": "Kontaktliste zur Detailansicht",
        "endpoint": "/api/v1/crm/contacts", "row_route": "/crm/kontakt/{id}", "bundle": "crm",
        "columns": [
            {"key": "name", "label": "Name", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "email", "label": "E-Mail", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Kontakte finden und Detail oeffnen.",
        "prompts": ["Welche Kontakte haben offene Aufgaben?"],
    }),
    ("crm/kontakt-management.tsx", "crm/kontakt-management-liste", "/crm/kontakt-management", {
        "domain": "crm", "title": "Kontakt-Management", "subtitle": "Kontakte und Follow-ups",
        "endpoint": "/api/v1/crm/contacts", "row_route": "/crm/kontakt/{id}", "bundle": "crm",
        "columns": [
            {"key": "name", "label": "Name", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "firma", "label": "Firma", "filterable": True, "priority": "primary"},
            {"key": "email", "label": "E-Mail", "filterable": True, "priority": "secondary"},
            {"key": "prioritaet", "label": "Prioritaet", "filterable": True, "priority": "secondary"},
        ],
        "purpose": "Kontakte im Management finden.",
        "prompts": ["Welche Kontakte sind ueberfaellig?"],
    }),
    ("crm/kunden-liste.tsx", "crm/kunden-liste", "/crm/kunden-liste", {
        "domain": "crm", "title": "Kunden", "subtitle": "Operativer Kundenstamm",
        "endpoint": "/api/v1/crm/customers/lookup?q=&limit=1000", "row_route": "/crm/kunden/{id}", "bundle": "crm",
        "columns": [
            {"key": "firma", "label": "Firma", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "ort", "label": "Ort", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Kunden finden und Kundenakte oeffnen.",
        "prompts": ["Welche Kunden in PLZ 24xxx?"],
    }),
    ("crm/lead-detail.tsx", "crm/leads-liste", "/crm/lead-detail", {
        "domain": "crm", "title": "Leads", "subtitle": "Vertriebs-Leads",
        "endpoint": "/api/v1/crm/leads", "row_route": "/crm/leads/{id}", "bundle": "crm",
        "columns": [
            {"key": "name", "label": "Lead", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Leads finden und qualifizieren.",
        "prompts": ["Welche Leads sind neu?"],
    }),
    ("crm/lieferanten-liste.tsx", "crm/lieferanten-liste", "/crm/lieferanten-liste", {
        "domain": "crm", "title": "Lieferanten", "subtitle": "Lieferantenstamm CRM",
        "endpoint": "/api/v1/crm/suppliers", "row_route": "/crm/lieferanten/{id}", "bundle": "crm",
        "columns": [
            {"key": "firma", "label": "Firma", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "ort", "label": "Ort", "filterable": True, "priority": "secondary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Lieferanten finden und Stammdaten oeffnen.",
        "prompts": ["Welche Lieferanten sind aktiv?"],
    }),
    ("dokumente/ablage.tsx", "dokumente/ablage-liste", "/dokumente/ablage", {
        "domain": "dms", "title": "Dokumentenablage", "subtitle": "Dokumente nach Kategorie",
        "endpoint": "/api/v1/dokumente", "row_route": None, "bundle": "dms",
        "columns": [
            {"key": "name", "label": "Name", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "kategorie", "label": "Kategorie", "filterable": True, "priority": "secondary"},
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "secondary"},
        ],
        "purpose": "Dokumente in der Ablage finden.",
        "prompts": ["Welche Vertraege wurden hochgeladen?"],
    }),
    ("einkauf/anfragen-create.tsx", "einkauf/anfragen-create-liste", "/einkauf/anfragen-create", {
        "domain": "einkauf", "title": "Anfragen", "subtitle": "Bedarfsanforderungen anlegen",
        "endpoint": "/api/v1/einkauf/anfragen", "row_route": "/einkauf/anfrage/{id}", "bundle": "einkauf",
        "columns": [
            {"key": "anfrageNummer", "label": "Anfrage-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Anfragen vor Anlage finden.",
        "prompts": ["Welche Anfragen sind Entwurf?"],
    }),
    ("einkauf/angebote-vergleich.tsx", "einkauf/angebote-vergleich-liste", "/einkauf/angebote-vergleich", {
        "domain": "einkauf", "title": "Angebotsvergleich", "subtitle": "Lieferantenangebote vergleichen",
        "endpoint": "/api/v1/einkauf/angebote", "row_route": "/einkauf/angebot/{id}", "bundle": "einkauf",
        "columns": [
            {"key": "angebotNummer", "label": "Angebot-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "primary"},
            {"key": "preis", "label": "Preis", "numeric": True, "renderKind": "currency", "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Angebote zum Vergleich finden.",
        "prompts": ["Welche Angebote zur Anfrage X?"],
    }),
    ("einkauf/bestellvorschlaege.tsx", "einkauf/bestellvorschlaege-liste", "/einkauf/bestellvorschlaege", {
        "domain": "einkauf", "title": "Bestellvorschlaege", "subtitle": "Automatische Bestellvorschlaege",
        "endpoint": "/api/v1/einkauf/bestellvorschlaege", "row_route": None, "bundle": "einkauf",
        "columns": [
            {"key": "artikel", "label": "Artikel", "filterable": True, "priority": "primary"},
            {"key": "vorschlagMenge", "label": "Vorschlag", "numeric": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "secondary"},
        ],
        "purpose": "Bestellvorschlaege pruefen und bestellen.",
        "prompts": ["Welche Artikel sind unter Mindestbestand?"],
    }),
    ("einkauf/dienstleistungen-haltung.tsx", "einkauf/dienstleistungen-haltung-liste", "/einkauf/dienstleistungen-haltung", {
        "domain": "einkauf", "title": "Dienstleistungen Haltung", "subtitle": "DL-Bestellungen Tierhaltung",
        "endpoint": "/api/v1/einkauf/bestellungen", "row_route": "/einkauf/bestellung/{id}", "bundle": "einkauf",
        "columns": [
            {"key": "bestellNummer", "label": "Bestell-Nr.", "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Dienstleistungsbestellungen finden.",
        "prompts": ["Welche DL-Bestellungen sind offen?"],
    }),
    ("einkauf/EinkaufVorgangPage.tsx", "einkauf/einkauf-vorgang-liste", "/einkauf/vorgang", {
        "domain": "einkauf", "title": "Einkaufsvorgaenge", "subtitle": "Vorgaenge im Einkauf",
        "endpoint": "/api/v1/einkauf/bestellungen", "row_route": "/einkauf/bestellung/{id}", "bundle": "einkauf",
        "columns": [
            {"key": "nummer", "label": "Vorgang", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Einkaufsvorgaenge finden.",
        "prompts": ["Welche Vorgaenge warten auf Freigabe?"],
    }),
    ("einkauf/kontrakte-service.tsx", "einkauf/kontrakte-service-liste", "/einkauf/kontrakte-service", {
        "domain": "einkauf", "title": "Kontrakte Service", "subtitle": "Einkaufskontrakte Service",
        "endpoint": "/api/v1/kontrakte", "row_route": "/einkauf/kontrakt/{id}", "bundle": "einkauf",
        "columns": [
            {"key": "nummer", "label": "Kontrakt", "filterable": True, "priority": "primary"},
            {"key": "partner", "label": "Partner", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Service-Kontrakte im Einkauf finden.",
        "prompts": ["Welche Kontrakte laufen aus?"],
    }),
    ("einkauf/rechnung-abgleich.tsx", "einkauf/rechnung-abgleich-liste", "/einkauf/rechnung-abgleich", {
        "domain": "einkauf", "title": "Rechnungsabgleich", "subtitle": "Eingangsrechnungen abgleichen",
        "endpoint": "/api/v1/einkauf/rechnungseingaenge", "row_route": "/belege/purchase_invoice/{id}", "bundle": "einkauf",
        "columns": [
            {"key": "rechnungsNummer", "label": "Rechnung-Nr.", "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Rechnungen zum Abgleich finden.",
        "prompts": ["Welche Rechnungen passen nicht zur Bestellung?"],
    }),
    ("einkauf/rechnungseingaenge-liste.tsx", "einkauf/rechnungseingaenge-liste", "/einkauf/rechnungseingaenge-liste", {
        "domain": "einkauf", "title": "Rechnungseingaenge", "subtitle": "Eingangsrechnungen",
        "endpoint": "/api/v1/einkauf/rechnungseingaenge", "row_route": "/belege/purchase_invoice/{id}", "bundle": "einkauf",
        "columns": [
            {"key": "rechnungsNummer", "label": "Rechnung-Nr.", "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Rechnungseingaenge vor Freigabe finden.",
        "prompts": ["Welche Rechnungen warten auf Freigabe?"],
    }),
    ("einkauf/retouren.tsx", "einkauf/retouren-liste", "/einkauf/retouren", {
        "domain": "einkauf", "title": "Retouren", "subtitle": "Einkaufsretouren",
        "endpoint": "/api/v1/einkauf/retouren", "row_route": "/einkauf/retouren/{id}", "bundle": "einkauf",
        "columns": [
            {"key": "nummer", "label": "Retoure-Nr.", "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Retouren verfolgen.",
        "prompts": ["Welche Retouren sind offen?"],
    }),
    ("etiketten/druck.tsx", "etiketten/druck-liste", "/etiketten/druck", {
        "domain": "lager", "title": "Etikettendruck", "subtitle": "Druckauftraege Etiketten",
        "endpoint": "/api/v1/etiketten/druckauftrag", "row_route": None, "bundle": "lager",
        "columns": [
            {"key": "auftrag", "label": "Auftrag", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Etikettendruck-Auftraege finden.",
        "prompts": ["Welche Druckauftraege sind offen?"],
    }),
    ("export/intrastat-meldung.tsx", "export/intrastat-meldung-liste", "/export/intrastat-meldung", {
        "domain": "compliance", "title": "Intrastat-Meldung", "subtitle": "Intrastat Meldezeitraeume",
        "endpoint": "/api/v1/intrastat/meldungen", "row_route": None, "bundle": "compliance",
        "columns": [
            {"key": "periode", "label": "Periode", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Intrastat-Meldungen verfolgen.",
        "prompts": ["Welche Meldungen sind faellig?"],
    }),
    ("export/umsatzsteuer-voranmeldung.tsx", "export/umsatzsteuer-voranmeldung-liste", "/export/umsatzsteuer-voranmeldung", {
        "domain": "finance", "title": "USt-Voranmeldung", "subtitle": "Umsatzsteuer-Voranmeldungen",
        "endpoint": "/api/v1/compliance/ustva", "row_route": None, "bundle": "finance",
        "columns": [
            {"key": "periode", "label": "Periode", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "USt-Voranmeldungen einsehen.",
        "prompts": ["Welche Voranmeldung ist faellig?"],
    }),
    ("fibu/anlagen.tsx", "fibu/anlagen-liste", "/fibu/anlagen", {
        "domain": "finance", "title": "Anlagen", "subtitle": "Anlagevermoegen",
        "endpoint": "/api/v1/finance/fixed-assets/detail", "row_route": "/fibu/anlage/{id}", "bundle": "finance",
        "table_profile": "financial",
        "columns": [
            {"key": "anlagennr", "label": "Anlage-Nr.", "filterable": True, "priority": "primary"},
            {"key": "bezeichnung", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "buchwert", "label": "Buchwert", "numeric": True, "renderKind": "currency", "priority": "primary"},
        ],
        "purpose": "Anlagen finden und oeffnen.",
        "prompts": ["Welche Anlagen haben niedrigen Buchwert?"],
    }),
    ("fibu/buchungsjournal.tsx", "fibu/buchungsjournal-liste", "/fibu/buchungsjournal", {
        "domain": "finance", "title": "Buchungsjournal", "subtitle": "Journalbuchungen",
        "endpoint": "/api/v1/journal-entries/", "row_route": None, "bundle": "finance",
        "table_profile": "financial",
        "columns": [
            {"key": "belegnr", "label": "Beleg-Nr.", "filterable": True, "priority": "primary"},
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "betrag", "label": "Betrag", "numeric": True, "renderKind": "currency", "priority": "primary"},
        ],
        "purpose": "Buchungen im Journal finden.",
        "prompts": ["Welche Buchungen heute?"],
    }),
    ("fibu/debitoren.tsx", "fibu/debitoren-liste", "/fibu/debitoren", {
        "domain": "finance", "title": "Debitoren OP", "subtitle": "Offene Posten Debitoren",
        "endpoint": "/api/v1/finance/open-items?typ=debitor", "row_route": "/sales/invoice/{id}", "bundle": "finance",
        "table_profile": "financial",
        "columns": [
            {"key": "rechnungsnr", "label": "Rechnung", "filterable": True, "priority": "primary"},
            {"key": "kunde", "label": "Kunde", "filterable": True, "priority": "primary"},
            {"key": "offen", "label": "Offen", "numeric": True, "renderKind": "currency", "priority": "primary"},
            {"key": "faelligkeit", "label": "Faellig", "renderKind": "date", "sortable": True, "priority": "secondary"},
        ],
        "purpose": "Offene Debitorenposten finden.",
        "prompts": ["Welche Posten sind ueberfaellig?"],
    }),
    ("fibu/hauptbuch.tsx", "fibu/hauptbuch-liste", "/fibu/hauptbuch", {
        "domain": "finance", "title": "Hauptbuch", "subtitle": "Hauptbuch-Buchungen",
        "endpoint": "/api/v1/journal-entries/", "row_route": None, "bundle": "finance",
        "table_profile": "financial",
        "columns": [
            {"key": "belegnummer", "label": "Beleg", "filterable": True, "priority": "primary"},
            {"key": "konto", "label": "Konto", "filterable": True, "priority": "primary"},
            {"key": "soll", "label": "Soll", "numeric": True, "priority": "secondary"},
            {"key": "haben", "label": "Haben", "numeric": True, "priority": "secondary"},
        ],
        "purpose": "Hauptbuch-Buchungen einsehen.",
        "prompts": ["Welche Buchungen auf Konto 1200?"],
    }),
    ("fibu/kassenbuch.tsx", "fibu/kassenbuch-liste", "/fibu/kassenbuch", {
        "domain": "finance", "title": "Kassenbuch", "subtitle": "Kassenbuchungen",
        "endpoint": "/api/v1/kasse/tagesabschluss/aktuell", "row_route": None, "bundle": "finance",
        "table_profile": "financial",
        "columns": [
            {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "priority": "primary"},
            {"key": "saldo", "label": "Saldo", "numeric": True, "renderKind": "currency", "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Kassenbuch und Tagesabschluesse finden.",
        "prompts": ["Ist der heutige Abschluss offen?"],
    }),
    ("fibu/kostenstellenrechnung.tsx", "fibu/kostenstellen-liste", "/fibu/kostenstellenrechnung", {
        "domain": "finance", "title": "Kostenstellen", "subtitle": "Kostenstellenrechnung",
        "endpoint": "/api/v1/finance/kostenstellen", "row_route": None, "bundle": "finance",
        "table_profile": "financial",
        "columns": [
            {"key": "nummer", "label": "Kostenstelle", "filterable": True, "priority": "primary"},
            {"key": "bezeichnung", "label": "Bezeichnung", "sortable": True, "filterable": True, "priority": "primary"},
        ],
        "purpose": "Kostenstellen finden.",
        "prompts": ["Welche Kostenstellen haben Abweichung?"],
    }),
    ("fibu/kreditoren.tsx", "fibu/kreditoren-liste", "/fibu/kreditoren", {
        "domain": "finance", "title": "Kreditoren OP", "subtitle": "Offene Posten Kreditoren",
        "endpoint": "/api/v1/finance/open-items?typ=kreditor", "row_route": "/belege/purchase_invoice/{id}", "bundle": "finance",
        "table_profile": "financial",
        "columns": [
            {"key": "rechnungsnr", "label": "Rechnung", "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "primary"},
            {"key": "offen", "label": "Offen", "numeric": True, "renderKind": "currency", "priority": "primary"},
        ],
        "purpose": "Offene Kreditorenposten finden.",
        "prompts": ["Welche Verbindlichkeiten sind faellig?"],
    }),
    ("fibu/offene-posten.tsx", "fibu/offene-posten-liste", "/fibu/offene-posten", {
        "domain": "finance", "title": "Offene Posten", "subtitle": "Debitoren und Kreditoren",
        "endpoint": "/api/v1/finance/open-items", "row_route": None, "bundle": "finance",
        "table_profile": "financial",
        "columns": [
            {"key": "rechnungsNr", "label": "Rechnung", "filterable": True, "priority": "primary"},
            {"key": "betrag", "label": "Betrag", "numeric": True, "renderKind": "currency", "priority": "primary"},
            {"key": "offen", "label": "Offen", "numeric": True, "renderKind": "currency", "priority": "primary"},
        ],
        "purpose": "Alle offenen Posten finden.",
        "prompts": ["Welche Posten sind ueberfaellig?"],
    }),
    ("fibu/schnittstelle-fibu.tsx", "fibu/schnittstelle-fibu-liste", "/fibu/schnittstelle-fibu", {
        "domain": "finance", "title": "FIBU-Schnittstelle", "subtitle": "Buchungsuebergabe Exporte",
        "endpoint": "/api/v1/finance/connectors/profiles", "row_route": None, "bundle": "finance",
        "columns": [
            {"key": "typ", "label": "Typ", "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "FIBU-Schnittstellen-Exporte verfolgen.",
        "prompts": ["Welcher Export ist fehlgeschlagen?"],
    }),
    ("fibu/verbindlichkeiten.tsx", "fibu/verbindlichkeiten-liste", "/fibu/verbindlichkeiten", {
        "domain": "finance", "title": "Verbindlichkeiten", "subtitle": "Offene Verbindlichkeiten",
        "endpoint": "/api/v1/finance/open-items?typ=kreditor", "row_route": "/fibu/verbindlichkeit/{id}", "bundle": "finance",
        "table_profile": "financial",
        "columns": [
            {"key": "rechnungsNr", "label": "Rechnung", "filterable": True, "priority": "primary"},
            {"key": "lieferant", "label": "Lieferant", "filterable": True, "priority": "primary"},
            {"key": "offen", "label": "Offen", "numeric": True, "renderKind": "currency", "priority": "primary"},
        ],
        "purpose": "Verbindlichkeiten finden.",
        "prompts": ["Welche Verbindlichkeiten sind offen?"],
    }),
    ("fibu/zahlungslaeufe.tsx", "fibu/zahlungslaeufe-liste", "/fibu/zahlungslaeufe", {
        "domain": "finance", "title": "Zahlungslaeufe", "subtitle": "SEPA-Zahlungslaeufe",
        "endpoint": "/api/v1/finance/payment-runs", "row_route": "/fibu/zahlungslaeufe/{id}", "bundle": "finance",
        "table_profile": "financial",
        "columns": [
            {"key": "laufNr", "label": "Lauf-Nr.", "filterable": True, "priority": "primary"},
            {"key": "betrag", "label": "Betrag", "numeric": True, "renderKind": "currency", "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
        ],
        "purpose": "Zahlungslaeufe planen und freigeben.",
        "prompts": ["Welcher Lauf wartet auf Freigabe?"],
    }),
]


def _slug(screen_id: str) -> str:
    return screen_id.replace("/", "_").replace("-", "_")


def _validate_endpoint(endpoint: str) -> None:
    base = endpoint.split("?", 1)[0]
    if base not in GET_PATHS:
        # trailing slash variants
        alt = base.rstrip("/") + "/"
        if base.endswith("/"):
            alt = base.rstrip("/")
        if alt not in GET_PATHS:
            raise SystemExit(f"GET path missing in openapi.json: {endpoint}")


def _col_repr(col: dict) -> str:
    parts = [f'"key": "{col["key"]}"', f'"label": "{col["label"]}"']
    for k in ("sortable", "filterable", "numeric"):
        if k in col:
            parts.append(f'"{k}": {str(col[k]).lower()}')
    if "renderKind" in col:
        parts.append(f'"renderKind": "{col["renderKind"]}"')
    if "priority" in col:
        parts.append(f'"priority": "{col["priority"]}"')
    return "{" + ", ".join(parts) + "}"


def _render_builder(fn: str, screen_id: str, spec: dict) -> str:
    _validate_endpoint(spec["endpoint"])
    cols = ",\n            ".join(_col_repr(c) for c in spec["columns"])
    row_route = spec.get("row_route")
    rr = f'row_route="{row_route}"' if row_route else "row_route=None"
    table_profile = spec.get("table_profile", "standard")
    prompts = spec.get("prompts", ["Liste oeffnen."])
    purpose = spec["purpose"]
    no_wf = "Listenmaske ohne eigenen Ablauf; Status steht am Datensatz."
    lines = [
        f"def {fn}() -> dict[str, Any]:",
        f'    return _liste(',
        f'        screen_id="{screen_id}", domain="{spec["domain"]}", title="{spec["title"]}",',
        f'        subtitle="{spec["subtitle"]}", endpoint="{spec["endpoint"]}", {rr}, bundle="{spec["bundle"]}",',
    ]
    if table_profile != "standard":
        lines.append(f'        table_profile="{table_profile}",')
    lines.extend([
        "        columns=[",
        f"            {cols},",
        "        ],",
        "        actions=[_EXPORT],",
        "        row_actions=[],",
        f'        purpose="{purpose}",',
        f"        prompts={prompts!r},",
        f'        no_workflow="{no_wf}",',
        "    )",
        "",
    ])
    return "\n".join(lines)


def _tsx_content(page: str, screen_id: str, title: str) -> str:
    comp = "".join(p.capitalize() for p in re.sub(r"[^a-zA-Z0-9]+", " ", page).split()) + "Page"
    if comp.endswith(".tsxPage"):
        comp = comp.replace(".tsxPage", "Page")
    return (
        "import { NativeListPage } from '@/components/mask-builder/NativeListPage'\n\n"
        f"/** {title} aus der ScreenDefinition `{screen_id}`. */\n"
        f"export default function {comp}(): JSX.Element {{\n"
        "  return (\n"
        f'    <NativeListPage screenId="{screen_id}" testId="screen-{screen_id}" />\n'
        "  )\n"
        "}\n"
    )


def main() -> None:
    text = LISTEN.read_text(encoding="utf-8")
    existing_ids = set(re.findall(r'screen_id="([^"]+)"', text))
    new_builders: list[str] = []
    registry_add: list[tuple[str, str]] = []
    route_add: dict[str, str] = {}
    synonym_add: dict[str, list[str]] = {}

    for page, screen_id, route_path, spec in BATCH11:
        fn = f"build_{_slug(screen_id)}"
        if screen_id not in existing_ids:
            new_builders.append(_render_builder(fn, screen_id, spec))
            registry_add.append((screen_id, fn))
            existing_ids.add(screen_id)
        route_add[screen_id] = route_path
        synonym_add[screen_id] = [screen_id.split("/")[-1].replace("-liste", ""), spec["title"].lower()]

        rel = PAGES / page
        rel.parent.mkdir(parents=True, exist_ok=True)
        rel.write_text(_tsx_content(page, screen_id, spec["title"]), encoding="utf-8")

    if new_builders:
        marker = "\n\nLISTEN_SCREEN_BUILDERS = {"
        if marker not in text:
            raise SystemExit("LISTEN_SCREEN_BUILDERS marker not found")
        text = text.replace(marker, "\n\n" + "".join(new_builders) + marker)

    # extend LISTEN_SCREEN_BUILDERS
    for screen_id, fn in registry_add:
        entry = f'    "{screen_id}": {fn},\n'
        if f'"{screen_id}":' not in text:
            text = text.replace(
                "\n}\nLISTEN_ROUTEN = {",
                entry + "}\nLISTEN_ROUTEN = {",
                1,
            )

    # LISTEN_ROUTEN entries
    for sid, path in route_add.items():
        if f'"{sid}":' not in text.split("LISTEN_ROUTEN = {", 1)[-1].split("LISTEN_SYNONYME", 1)[0]:
            text = text.replace(
                "\n                \"compliance/saatgut-nachbau-liste\": \"/compliance/saatgut-nachbau\"}",
                f'\n                "compliance/saatgut-nachbau-liste": "/compliance/saatgut-nachbau",\n                "{sid}": "{path}"}}',
                1,
            )

    # LISTEN_SYNONYME
    for sid, syns in synonym_add.items():
        block = text.split("LISTEN_SYNONYME = {", 1)[-1]
        if f'"{sid}":' not in block.split("}", 1)[0]:
            text = text.replace(
                '\n                   "compliance/saatgut-nachbau-liste": ["saatgut nachbau", "nachbauflaeche"]}',
                f'\n                   "compliance/saatgut-nachbau-liste": ["saatgut nachbau", "nachbauflaeche"],\n                   "{sid}": {syns!r}}}',
                1,
            )

    LISTEN.write_text(text, encoding="utf-8")
    print(f"Added {len(new_builders)} builders; wrote {len(BATCH11)} pages")


if __name__ == "__main__":
    main()
