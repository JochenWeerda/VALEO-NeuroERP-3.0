"""Native ScreenDefinition payloads for Universal Mask Generator."""

from __future__ import annotations

from typing import Any

from app.core.mask_rollout_catalog import ROLLOUT_WAVES_42_51


def build_crm_customer_360_screen_definition() -> dict[str, Any]:
    """Canonical ScreenDefinition for crm/customer-360 (Wave 29)."""

    return {
        "schemaVersion": 1,
        "id": "crm/customer-360",
        "domain": "crm",
        "mode": "detail",
        "title": "Kundenstamm",
        "subtitle": "CRM 360",
        "adapter": {
            "type": "native",
            "sourceId": "crm/customer-360",
            "temporary": False,
        },
        "summaryEndpoint": "/api/v1/crm/customers/{customer_id}/screen-summary",
        "tabs": [
            {"key": "masterdata", "label": "Stammdaten", "lazy": True, "keepAlive": True},
            {"key": "address", "label": "Adresse & Kommunikation", "lazy": True, "keepAlive": True},
            {"key": "contacts", "label": "Ansprechpartner", "lazy": True, "keepAlive": True},
            {"key": "finance", "label": "Finanzen", "lazy": True, "keepAlive": True},
            {"key": "auftraege", "label": "Auftraege", "lazy": True, "keepAlive": True},
            {"key": "aktivitaeten", "label": "Aktivitaeten", "lazy": True, "keepAlive": True},
            {"key": "dokumente", "label": "Dokumente", "lazy": True, "keepAlive": True},
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "permission": "crm.customer.update"},
            {"key": "create_activity", "label": "Aktivitaet anlegen", "kind": "secondary", "permission": "crm.activity.create"},
        ],
        "layout": {
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
        },
        "performance": {
            "initialPayloadBudgetKb": 48,
            "requiresLazyTabs": True,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "crm",
        },
    }


def build_sales_order_screen_definition() -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "id": "sales/sales-order",
        "domain": "sales",
        "mode": "detail",
        "title": "Verkaufsauftrag",
        "subtitle": "Sales Order",
        "adapter": {
            "type": "native",
            "sourceId": "sales/sales-order",
            "temporary": False,
        },
        "summaryEndpoint": "/api/v1/sales/orders/{order_id}/screen-summary",
        "tabs": [
            {"key": "kopf", "label": "Kopfdaten", "lazy": True, "keepAlive": True},
            {"key": "positionen", "label": "Positionen", "lazy": True, "keepAlive": True},
            {"key": "lieferung", "label": "Lieferung", "lazy": True, "keepAlive": True},
            {"key": "dokumente", "label": "Dokumente", "lazy": True, "keepAlive": True},
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "permission": "sales.order.update"},
        ],
        "layout": {
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
        },
        "performance": {
            "initialPayloadBudgetKb": 56,
            "requiresLazyTabs": True,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "sales",
        },
    }


def build_agrar_kontrakt_screen_definition() -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "id": "agrar/kontrakte",
        "domain": "agrar",
        "mode": "detail",
        "title": "Kontrakt",
        "subtitle": "Agrar-Kontrakt",
        "adapter": {
            "type": "native",
            "sourceId": "agrar/kontrakte",
            "temporary": False,
        },
        "summaryEndpoint": "/api/v1/kontrakte/{contract_id}/screen-summary",
        "tabs": [
            {"key": "kopf", "label": "Kopfdaten", "lazy": True, "keepAlive": True},
            {"key": "positionen", "label": "Positionen", "lazy": True, "keepAlive": True},
            {"key": "umsaetze", "label": "Umsaetze", "lazy": True, "keepAlive": True},
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "permission": "kontrakt.update"},
        ],
        "layout": {
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
        },
        "performance": {
            "initialPayloadBudgetKb": 52,
            "requiresLazyTabs": True,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "agrar",
        },
    }


_SCREEN_DEFINITIONS: dict[str, Any] = {
    "crm/customer-360": build_crm_customer_360_screen_definition,
    "sales/sales-order": build_sales_order_screen_definition,
    "agrar/kontrakte": build_agrar_kontrakt_screen_definition,
}


_TAB_LABELS: dict[str, str] = {
    "details": "Details",
    "bestand": "Bestand",
    "bewegungen": "Bewegungen",
    "positionen": "Positionen",
    "lieferungen": "Lieferungen",
    "kontakte": "Kontakte",
    "bestellungen": "Bestellungen",
    "aktivitaeten": "Aktivitaeten",
    "angebote": "Angebote",
    "abzuege": "Abzuege",
    "zahlungen": "Zahlungen",
    "belege": "Belege",
    "auftraege": "Auftraege",
    "fehler": "Fehler",
}


def _col(key: str, label: str, **kwargs: Any) -> dict[str, Any]:
    return {"key": key, "label": label, **kwargs}


def _num(key: str, label: str, render_kind: str = "number", **kwargs: Any) -> dict[str, Any]:
    return _col(key, label, numeric=True, sortable=True, renderKind=render_kind, **kwargs)


def _date(key: str, label: str) -> dict[str, Any]:
    return _col(key, label, sortable=True, renderKind="date", width=110)


def _status(key: str, label: str) -> dict[str, Any]:
    return _col(key, label, renderKind="status", width=100)


def _txt(key: str, label: str, **kwargs: Any) -> dict[str, Any]:
    return _col(key, label, **kwargs)


_ROLLOUT_TAB_COLUMNS: dict[str, dict[str, list[dict[str, Any]]]] = {
    "lager/stock-movement": {
        "details": [
            _date("datum", "Datum"),
            _txt("typ", "Typ", width=100),
            _txt("beleg_nr", "Beleg-Nr.", width=120),
            _txt("lagerort", "Lagerort"),
            _status("status", "Status"),
        ],
        "positionen": [
            _txt("pos_nr", "Pos.", width=50),
            _txt("artikel_nr", "Artikel-Nr.", width=120),
            _txt("bezeichnung", "Bezeichnung", width=200),
            _num("menge", "Menge"),
            _txt("einheit", "Einheit", width=70),
            _txt("charge", "Charge", width=120),
        ],
    },
    "lager/article-stock": {
        "bestand": [
            _txt("lagerort_nr", "Lagerort-Nr.", width=120),
            _txt("lagerort_bezeichnung", "Bezeichnung", width=180),
            _num("bestand_menge", "Bestand"),
            _txt("einheit", "Einheit", width=70),
            _num("reserviert", "Reserviert"),
            _num("mindestbestand", "Mindestbest."),
        ],
        "bewegungen": [
            _date("datum", "Datum"),
            _txt("typ", "Typ", width=100),
            _num("menge", "Menge"),
            _txt("einheit", "Einheit", width=70),
            _txt("beleg_nr", "Beleg-Nr.", width=120),
        ],
    },
    "finance/ap-invoice": {
        "positionen": [
            _txt("pos_nr", "Pos.", width=50),
            _txt("bezeichnung", "Bezeichnung", width=200),
            _num("menge", "Menge"),
            _txt("einheit", "Einheit", width=70),
            _num("einzelpreis", "Einzelpreis", render_kind="currency"),
            _num("betrag", "Betrag", render_kind="currency"),
            _txt("konto", "Konto", width=100),
        ],
        "zahlungen": [
            _date("datum", "Datum"),
            _num("betrag", "Betrag", render_kind="currency"),
            _txt("zahlungsart", "Zahlungsart", width=120),
            _txt("bank_ref", "Bank-Referenz", width=160),
        ],
        "belege": [
            _txt("beleg_art", "Beleg-Art", width=100),
            _txt("beleg_nr", "Beleg-Nr.", width=120),
            _date("datum", "Datum"),
            _num("betrag", "Betrag", render_kind="currency"),
        ],
    },
    "finance/ar-open-item": {
        "details": [
            _txt("beleg_art", "Beleg-Art", width=100),
            _txt("beleg_nr", "Beleg-Nr.", width=130),
            _date("faellig_am", "Faellig am"),
            _num("brutto", "Brutto", render_kind="currency"),
            _num("offen", "Offen", render_kind="currency"),
            _num("skonto", "Skonto", render_kind="currency"),
        ],
        "zahlungen": [
            _date("datum", "Datum"),
            _num("betrag", "Betrag", render_kind="currency"),
            _txt("zahlungsart", "Zahlungsart", width=120),
            _txt("eingang_bank", "Eingang Bank", width=160),
        ],
    },
    "einkauf/purchase-order": {
        "positionen": [
            _txt("pos_nr", "Pos.", width=50),
            _txt("artikel_nr", "Artikel-Nr.", width=120),
            _txt("bezeichnung", "Bezeichnung", width=200),
            _num("menge", "Menge"),
            _txt("einheit", "Einheit", width=70),
            _num("einzelpreis", "Einzelpreis", render_kind="currency"),
            _num("betrag", "Betrag", render_kind="currency"),
            _date("lieferdatum", "Lieferdatum"),
        ],
        "lieferungen": [
            _date("datum", "Datum"),
            _txt("lieferschein_nr", "LS-Nr.", width=130),
            _num("menge", "Menge"),
            _txt("einheit", "Einheit", width=70),
            _txt("lagerort", "Lagerort"),
        ],
        "belege": [
            _txt("beleg_art", "Beleg-Art", width=100),
            _txt("beleg_nr", "Beleg-Nr.", width=130),
            _date("datum", "Datum"),
            _num("betrag", "Betrag", render_kind="currency"),
        ],
    },
    "einkauf/supplier": {
        "kontakte": [
            _txt("name", "Name", width=180),
            _txt("funktion", "Funktion", width=140),
            _txt("telefon", "Telefon", width=130),
            _txt("email", "E-Mail", width=200),
        ],
        "bestellungen": [
            _txt("bestell_nr", "Bestell-Nr.", width=130),
            _date("datum", "Datum"),
            _status("status", "Status"),
            _num("betrag", "Betrag", render_kind="currency"),
            _txt("waehrung", "Waehrung", width=70),
        ],
    },
    "crm/opportunity": {
        "aktivitaeten": [
            _date("datum", "Datum"),
            _txt("typ", "Typ", width=100),
            _txt("betreff", "Betreff", width=220),
            _txt("verantwortlich", "Verantwortlich", width=140),
            _status("status", "Status"),
        ],
        "angebote": [
            _txt("angebot_nr", "Angebot-Nr.", width=130),
            _date("datum", "Datum"),
            _num("wert", "Wert", render_kind="currency"),
            _txt("waehrung", "Waehrung", width=70),
            _status("status", "Status"),
        ],
    },
    "sales/delivery-note": {
        "positionen": [
            _txt("pos_nr", "Pos.", width=50),
            _txt("artikel_nr", "Artikel-Nr.", width=120),
            _txt("bezeichnung", "Bezeichnung", width=200),
            _num("menge", "Menge"),
            _txt("einheit", "Einheit", width=70),
            _txt("charge", "Charge", width=120),
            _txt("lagerort", "Lagerort"),
        ],
        "auftraege": [
            _txt("auftrag_nr", "Auftrag-Nr.", width=130),
            _date("datum", "Datum"),
            _txt("pos_nr", "Pos.", width=50),
            _num("auftragsmenge", "Auftr.-Menge"),
        ],
    },
    "agrar/harvest-settlement": {
        "positionen": [
            _txt("lieferschein_nr", "LS-Nr.", width=130),
            _date("datum", "Datum"),
            _txt("sorte", "Sorte", width=140),
            _num("feuchtigkeit", "Feuchte %", render_kind="number"),
            _num("menge", "Menge"),
            _txt("einheit", "Einheit", width=70),
            _txt("qualitaet", "Qualitaet", width=100),
        ],
        "abzuege": [
            _txt("abzug_art", "Abzug-Art", width=140),
            _txt("beschreibung", "Beschreibung", width=200),
            _num("menge", "Menge"),
            _num("betrag", "Betrag", render_kind="currency"),
        ],
        "zahlungen": [
            _date("datum", "Datum"),
            _num("betrag", "Betrag", render_kind="currency"),
            _txt("bank_ref", "Bank-Referenz", width=160),
            _txt("auszahlungs_art", "Art", width=100),
        ],
    },
    "finance/payment-run": {
        "zahlungen": [
            _txt("kreditoren_nr", "Kreditor-Nr.", width=120),
            _txt("name", "Name", width=200),
            _num("betrag", "Betrag", render_kind="currency"),
            _txt("bank", "Bank", width=140),
            _txt("iban", "IBAN", width=200),
            _date("faellig_am", "Faellig am"),
            _status("status", "Status"),
        ],
        "fehler": [
            _txt("kreditoren_nr", "Kreditor-Nr.", width=120),
            _txt("name", "Name", width=200),
            _num("betrag", "Betrag", render_kind="currency"),
            _txt("fehlertyp", "Fehlertyp", width=130),
            _txt("meldung", "Meldung", width=300),
        ],
    },
}


def _build_rollout_screen_definition_from_spec(spec: Any) -> dict[str, Any]:
    """Builds a ScreenDefinition from a RolloutWaveSpec with dataSources and typed columns."""
    tab_columns = _ROLLOUT_TAB_COLUMNS.get(spec.screen_id, {})

    data_sources = [
        {
            "key": tab_key,
            "endpoint": f"{spec.api_prefix}/{{entity_id}}/tabs/{tab_key}",
            "pageSize": 25,
        }
        for tab_key in spec.available_tabs
    ]

    tabs = [
        {
            "key": tab_key,
            "label": _TAB_LABELS.get(tab_key, tab_key.title()),
            "lazy": True,
            "keepAlive": False,
            "tables": [
                {
                    "key": tab_key,
                    "label": _TAB_LABELS.get(tab_key, tab_key.title()),
                    "dataSourceKey": tab_key,
                    "serverPagination": True,
                    "pageSize": 25,
                    "virtualized": True,
                    "rowHeight": 52,
                    "columns": tab_columns.get(tab_key, [
                        {"key": "id", "label": "ID", "width": 100},
                        {"key": "bezeichnung", "label": "Bezeichnung"},
                    ]),
                }
            ],
        }
        for tab_key in spec.available_tabs
    ]

    return {
        "schemaVersion": 1,
        "id": spec.screen_id,
        "domain": spec.domain,
        "mode": "detail",
        "title": spec.label,
        "subtitle": f"Rollout Pilot",
        "adapter": {
            "type": "native",
            "sourceId": spec.screen_id,
            "temporary": True,
        },
        "summaryEndpoint": f"{spec.api_prefix}/{{entity_id}}/screen-summary",
        "dataSources": data_sources,
        "tabs": tabs,
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary"},
        ],
        "layout": {
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
        },
        "performance": {
            "initialPayloadBudgetKb": spec.budget_kb,
            "requiresLazyTabs": True,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": spec.domain,
        },
    }


for _spec in ROLLOUT_WAVES_42_51:
    def _make_builder(_s: Any = _spec) -> Any:
        def _builder() -> dict[str, Any]:
            return _build_rollout_screen_definition_from_spec(_s)
        return _builder

    _SCREEN_DEFINITIONS[_spec.screen_id] = _make_builder()


def get_screen_definition(mask_id: str) -> dict[str, Any] | None:
    builder = _SCREEN_DEFINITIONS.get(mask_id)
    if builder is None:
        return None
    return builder()
