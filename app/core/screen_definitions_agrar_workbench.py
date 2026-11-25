"""Agrar-Fachoberflaechen (Schlagkartei, Milchvieh-Karte) im Universal-Runtime."""
from __future__ import annotations

from typing import Any


def _cmd(
    key: str,
    label: str,
    *,
    endpoint: str,
    method: str = "POST",
    permission: str,
    fields: list[dict[str, Any]] | None = None,
    primary: bool = False,
) -> dict[str, Any]:
    action: dict[str, Any] = {
        "key": key,
        "label": label,
        "kind": "primary" if primary else "secondary",
        "zone": "header",
        "dangerLevel": "moderate" if method in ("POST", "PUT", "PATCH", "DELETE") else "safe",
        "permission": permission,
        "commandEndpoint": endpoint,
        "method": method,
        "forbiddenForAgents": True,
    }
    if fields:
        action["inputFields"] = fields
    return action


def build_agrar_kunden_schlagkartei() -> dict[str, Any]:
    """Innendienst-Kundenschlagkartei — PortalKontoGate + Lohndienst/Ankauf (Feldparitaet)."""
    return {
        "schemaVersion": 1,
        "id": "agrar/kunden-schlagkartei",
        "domain": "agrar",
        "mode": "cockpit",
        "title": "Kundenschlagkartei",
        "subtitle": "Schlaege und Massnahmen je Kundenkonto; Lohndienst und Ankaufsangebote",
        "adapter": {"type": "native", "sourceId": "agrar/kunden-schlagkartei", "temporary": False},
        "layout": {
            "floorplan": "cockpit",
            "density": "compact",
            "contextRail": "workflow",
            "tableProfile": "standard",
        },
        "fields": [
            {"key": "kunden_nr", "label": "Kunden-Nr.", "type": "text", "readOnly": True},
            {"key": "schlag_count", "label": "Schlaege", "type": "number", "readOnly": True},
            {"key": "massnahme_count", "label": "Massnahmen", "type": "number", "readOnly": True},
            {"key": "gesamt_flaeche_ha", "label": "Flaeche ha", "type": "number", "readOnly": True},
        ],
        "actions": [
            _cmd(
                "lohn_spritz",
                "Lohnspritz-Auftrag",
                endpoint="/api/v1/portal/lohndienste",
                permission="agrar.schlagkartei.write",
                primary=True,
                fields=[
                    {"key": "typ", "label": "Typ", "type": "text", "required": True, "defaultValue": "lohn_spritz"},
                    {"key": "schlag_beschreibung", "label": "Schlag", "type": "text", "required": False},
                    {"key": "flaeche_ha", "label": "Flaeche ha", "type": "number", "required": False},
                    {"key": "wunsch_datum", "label": "Wunschdatum", "type": "date", "required": False},
                    {"key": "kultur", "label": "Kultur", "type": "text", "required": False},
                    {"key": "menge_dt", "label": "Menge dt", "type": "number", "required": False},
                    {"key": "anmerkung", "label": "Anmerkung", "type": "textarea", "required": False},
                ],
            ),
            _cmd(
                "mahl_misch",
                "Mahl+Misch-Termin",
                endpoint="/api/v1/portal/lohndienste",
                permission="agrar.schlagkartei.write",
                fields=[
                    {"key": "typ", "label": "Typ", "type": "text", "required": True, "defaultValue": "mahl_misch"},
                    {"key": "schlag_beschreibung", "label": "Schlag", "type": "text", "required": False},
                    {"key": "flaeche_ha", "label": "Flaeche ha", "type": "number", "required": False},
                    {"key": "wunsch_datum", "label": "Wunschdatum", "type": "date", "required": False},
                    {"key": "tierart", "label": "Tierart", "type": "text", "required": False},
                    {"key": "tiere_anzahl", "label": "Tiere", "type": "number", "required": False},
                    {"key": "getreide_art", "label": "Getreide", "type": "text", "required": False},
                    {"key": "menge_dt", "label": "Menge dt", "type": "number", "required": False},
                    {"key": "anmerkung", "label": "Anmerkung", "type": "textarea", "required": False},
                ],
            ),
            _cmd(
                "ankaufsangebot",
                "Ankaufsangebot erstellen",
                endpoint="/api/v1/portal/empfehlungen/generieren/schlagkartei",
                permission="agrar.schlagkartei.write",
                fields=[
                    {"key": "kunden_nr", "label": "Kunden-Nr.", "type": "text", "required": True},
                    {"key": "ernte_jahr", "label": "Erntejahr", "type": "number", "required": True},
                    {"key": "flaeche_ha", "label": "Flaeche ha", "type": "number", "required": False},
                ],
            ),
        ],
        "specialized": {"type": "agrar_workbench", "id": "agrar/kunden-schlagkartei"},
        "noWorkflowReason": "Innendienst-Arbeitsplatz ohne eigenen Beleg-Lebenszyklus; Auftraege laufen ueber Portal-Endpunkte.",
        "noProcessChainReason": "Schlagkartei ist Konto-Arbeitsplatz, keine Belegkette.",
        "performance": {
            "initialPayloadBudgetKb": 120,
            "requiresLazyTabs": True,
            "requiresVirtualTables": False,
            "lookupMinChars": 2,
            "bundleGroup": "agrar",
        },
        "agentContract": {
            "businessPurpose": "Kundenschlaege und Massnahmen einsehen; Lohndienst und Ankaufsangebote ausloesen.",
            "examplePrompts": [
                "Lege einen Lohnspritz-Auftrag an.",
                "Erstelle Ankaufsangebote fuer die Schlagkartei.",
            ],
            "sensitiveFields": ["kunden_nr"],
            "forbiddenAgentTasks": ["Portal-Konto ohne menschliche Wahl setzen"],
            "testSelectors": {"screenRoot": "[data-testid='native-cockpit-agrar-kunden-schlagkartei']"},
        },
    }


def build_agrar_milchvieh_karte() -> dict[str, Any]:
    """CRM-Karte Milchvieh — MapLibre-Surface + Cross-Sell-Map-API."""
    return {
        "schemaVersion": 1,
        "id": "agrar/milchvieh-karte",
        "domain": "agrar",
        "mode": "cockpit",
        "title": "Milchvieh-Karte",
        "subtitle": "POIs nach Hygiene-Bedarf; Hover zeigt Betriebskennzahlen",
        "adapter": {"type": "native", "sourceId": "agrar/milchvieh-karte", "temporary": False},
        "layout": {
            "floorplan": "cockpit",
            "density": "compact",
            "contextRail": "combined",
            "tableProfile": "standard",
        },
        "dataSources": [
            {
                "key": "entity",
                "endpoint": "/api/v1/agrar/milchvieh-crosssell/map",
                "staleTimeMs": 30_000,
            },
        ],
        "fields": [
            {"key": "feature_count", "label": "Betriebe", "type": "number", "readOnly": True},
        ],
        "actions": [
            {
                "key": "refresh",
                "label": "Aktualisieren",
                "kind": "secondary",
                "zone": "header",
                "dangerLevel": "safe",
                "permission": "agrar.milchvieh.read",
                "localEffect": "refetch",
            },
        ],
        "specialized": {"type": "agrar_workbench", "id": "agrar/milchvieh-karte"},
        "noWorkflowReason": "Karten-Arbeitsplatz ohne eigenen Objekt-Lebenszyklus.",
        "noProcessChainReason": "Geodaten-Visualisierung ohne Belegkette.",
        "performance": {
            "initialPayloadBudgetKb": 200,
            "requiresLazyTabs": False,
            "requiresVirtualTables": False,
            "lookupMinChars": 2,
            "bundleGroup": "agrar",
        },
        "agentContract": {
            "businessPurpose": "Milchvieh-Betriebe geografisch nach Hygiene- und Cross-Sell-Signalen einsehen.",
            "examplePrompts": ["Zeig die Milchvieh-Karte mit Hygiene-Filter."],
            "sensitiveFields": [],
            "forbiddenAgentTasks": [],
            "testSelectors": {"screenRoot": "[data-testid='native-cockpit-agrar-milchvieh-karte']"},
        },
    }


def build_agrar_ernte_annahme_erfassung() -> dict[str, Any]:
    """Ernte-Annahme-Erfassung — voller Legacy-Surface + Harvest-Acceptance-Commands."""
    base = "/api/v1/agrar/harvest-acceptance"
    perm = "agrar.ernte_annahme.write"
    create_fields = [
        {"key": "customer_id", "label": "Kunden-ID", "type": "text", "required": True},
        {"key": "delivery_date", "label": "Lieferdatum", "type": "date", "required": True},
        {"key": "article_id", "label": "Artikel-ID", "type": "text", "required": False},
        {"key": "warehouse_id", "label": "Lager-ID", "type": "text", "required": False},
        {"key": "contract_id", "label": "Kontrakt-ID", "type": "text", "required": False},
        {"key": "weighing_ticket_id", "label": "Wiegeschein-ID", "type": "text", "required": False},
        {"key": "vehicle_plate", "label": "Kennzeichen", "type": "text", "required": False},
        {"key": "remarks", "label": "Bemerkungen", "type": "textarea", "required": False},
    ]
    return {
        "schemaVersion": 1,
        "id": "agrar/ernte-annahme-erfassung",
        "domain": "agrar",
        "mode": "cockpit",
        "title": "Ernte-Annahme-Erfassung",
        "subtitle": "Annahmeschein mit Positionen, Qualitaet und Freigabe (Gewohnheits-Prinzip)",
        "adapter": {"type": "native", "sourceId": "agrar/ernte-annahme-erfassung", "temporary": False},
        "layout": {
            "floorplan": "cockpit",
            "density": "compact",
            "contextRail": "workflow",
            "tableProfile": "standard",
        },
        "fields": [
            {"key": "acceptance_number", "label": "Annahmenr.", "type": "text", "readOnly": True},
            {"key": "customer_id", "label": "Kunde", "type": "text", "readOnly": True},
            {"key": "release_status", "label": "Freigabe", "type": "text", "readOnly": True},
            {"key": "delivery_date", "label": "Lieferdatum", "type": "date", "readOnly": True},
        ],
        "actions": [
            _cmd("anlegen", "Annahme anlegen", endpoint=base, permission=perm, primary=True, fields=create_fields),
            _cmd(
                "speichern",
                "Annahme speichern",
                endpoint=f"{base}/{{entity_id}}",
                method="PUT",
                permission=perm,
                fields=create_fields,
            ),
            _cmd("berechnen", "Berechnen", endpoint=f"{base}/{{entity_id}}/calculate", permission=perm),
            _cmd(
                "freigeben",
                "Freigeben",
                endpoint=f"{base}/{{entity_id}}/release",
                permission=perm,
                fields=[{"key": "reason", "label": "Grund", "type": "textarea", "required": False}],
            ),
            _cmd("loeschen", "Loeschen", endpoint=f"{base}/{{entity_id}}", method="DELETE", permission=perm),
        ],
        "specialized": {"type": "agrar_workbench", "id": "agrar/ernte-annahme-erfassung"},
        "noWorkflowReason": "Annahme-Lebenszyklus wird im spezialisierten Arbeitsbereich und ueber Harvest-Acceptance-Commands gefuehrt.",
        "noProcessChainReason": "Belegkette laeuft ueber Harvest-to-Settlement; diese Maske ist die Erfassungsstufe.",
        "performance": {
            "initialPayloadBudgetKb": 180,
            "requiresLazyTabs": True,
            "requiresVirtualTables": False,
            "lookupMinChars": 2,
            "bundleGroup": "agrar",
        },
        "agentContract": {
            "businessPurpose": "Ernte-Annahmen anlegen, speichern, berechnen und freigeben.",
            "examplePrompts": ["Lege eine Ernte-Annahme an.", "Berechne Annahme {entity_id}."],
            "sensitiveFields": ["customer_id"],
            "forbiddenAgentTasks": ["Freigabe ohne menschliche Bestaetigung"],
            "testSelectors": {"screenRoot": "[data-testid='native-cockpit-agrar-ernte-annahme-erfassung']"},
        },
    }


def build_annahme_abrechnung() -> dict[str, Any]:
    """Selbstabrechner-Abrechnung — Legacy-Surface + Settlement-Commands."""
    base = "/api/v1/agrar/settlements"
    perm = "agrar.settlement.write"
    return {
        "schemaVersion": 1,
        "id": "annahme/abrechnung",
        "domain": "agrar",
        "mode": "cockpit",
        "title": "Annahme-Abrechnung",
        "subtitle": "Selbstabrechner: Vorschau, Anlegen, FiBu, Freigabe, Storno",
        "adapter": {"type": "native", "sourceId": "annahme/abrechnung", "temporary": False},
        "layout": {
            "floorplan": "cockpit",
            "density": "compact",
            "contextRail": "workflow",
            "tableProfile": "financial",
        },
        "dataSources": [
            {"key": "settlements", "endpoint": base, "pageSize": 50, "staleTimeMs": 15_000},
        ],
        "fields": [
            {"key": "settlement_count", "label": "Abrechnungen", "type": "number", "readOnly": True},
        ],
        "actions": [
            _cmd(
                "billing_preview",
                "Abrechnungsgewicht Vorschau",
                endpoint=f"{base}/billing-weight/preview",
                permission=perm,
                fields=[
                    {"key": "net_weight_kg", "label": "Nettogewicht kg", "type": "number", "required": True},
                    {"key": "moisture_pct", "label": "Feuchte %", "type": "number", "required": True},
                    {"key": "impurities_pct", "label": "Verunreinigung %", "type": "number", "required": False},
                ],
            ),
            _cmd(
                "drying_compute",
                "Trocknung berechnen",
                endpoint=f"{base}/drying/compute",
                permission=perm,
                fields=[
                    {"key": "crop_code", "label": "Kulturcode", "type": "text", "required": True},
                    {"key": "net_weight_kg", "label": "Nettogewicht kg", "type": "number", "required": True},
                    {"key": "moisture_pct", "label": "Feuchte %", "type": "number", "required": True},
                ],
            ),
            _cmd(
                "settlement_preview",
                "Abrechnung Vorschau",
                endpoint=f"{base}/preview",
                permission=perm,
                fields=[
                    {"key": "supplier_id", "label": "Lieferant-ID", "type": "text", "required": True},
                    {"key": "article_id", "label": "Artikel-ID", "type": "text", "required": True},
                    {"key": "gross_quantity_kg", "label": "Brutto kg", "type": "number", "required": True},
                    {"key": "billing_quantity_kg", "label": "Abrechnungsgewicht kg", "type": "number", "required": True},
                    {"key": "unit_price_eur_per_ton", "label": "Preis EUR/t", "type": "number", "required": True},
                ],
            ),
            _cmd(
                "anlegen",
                "Abrechnung anlegen",
                endpoint=base,
                permission=perm,
                primary=True,
                fields=[
                    {"key": "supplier_id", "label": "Lieferant-ID", "type": "text", "required": True},
                    {"key": "article_id", "label": "Artikel-ID", "type": "text", "required": True},
                    {"key": "gross_quantity_kg", "label": "Brutto kg", "type": "number", "required": True},
                    {"key": "billing_quantity_kg", "label": "Abrechnungsgewicht kg", "type": "number", "required": True},
                    {"key": "unit_price_eur_per_ton", "label": "Preis EUR/t", "type": "number", "required": True},
                    {"key": "campaign_id", "label": "Kampagne-ID", "type": "text", "required": False},
                    {"key": "note", "label": "Notiz", "type": "textarea", "required": False},
                ],
            ),
            _cmd(
                "post_fibu",
                "FiBu buchen",
                endpoint=f"{base}/{{entity_id}}/post-fibu",
                permission=perm,
                fields=[
                    {"key": "debit_account", "label": "Sollkonto", "type": "text", "required": True, "defaultValue": "5000"},
                    {"key": "credit_account_supplier", "label": "Haben Lieferant", "type": "text", "required": True, "defaultValue": "3300"},
                    {"key": "credit_account_deductions", "label": "Haben Abzuege", "type": "text", "required": True, "defaultValue": "5490"},
                    {"key": "expected_row_version", "label": "Row-Version", "type": "number", "required": True},
                ],
            ),
            _cmd(
                "freigabe",
                "Freigabe",
                endpoint=f"{base}/{{entity_id}}/freigabe",
                permission=perm,
                fields=[
                    {"key": "actor_id", "label": "Akteur-ID", "type": "text", "required": True},
                    {"key": "actor_type", "label": "Akteur-Typ", "type": "text", "required": True},
                    {"key": "target_status", "label": "Zielstatus", "type": "text", "required": True},
                    {"key": "reason", "label": "Grund", "type": "textarea", "required": False},
                    {"key": "expected_row_version", "label": "Row-Version", "type": "number", "required": True},
                ],
            ),
            _cmd(
                "stornieren",
                "Stornieren",
                endpoint=f"{base}/{{entity_id}}/cancel",
                permission=perm,
                fields=[{"key": "expected_row_version", "label": "Row-Version", "type": "number", "required": True}],
            ),
        ],
        "specialized": {"type": "agrar_workbench", "id": "annahme/abrechnung"},
        "noWorkflowReason": "Settlement-Lebenszyklus laeuft ueber die spezifizierten Settlement-Commands.",
        "noProcessChainReason": "Abrechnung ist Settlement-Stufe der Harvest-to-Settlement-Kette.",
        "performance": {
            "initialPayloadBudgetKb": 160,
            "requiresLazyTabs": True,
            "requiresVirtualTables": False,
            "lookupMinChars": 2,
            "bundleGroup": "agrar",
        },
        "agentContract": {
            "businessPurpose": "Selbstabrechner-Abrechnungen berechnen, anlegen, verbuchen und freigeben.",
            "examplePrompts": ["Lege eine Annahme-Abrechnung an.", "Buche Settlement {entity_id} in die FiBu."],
            "sensitiveFields": ["supplier_id"],
            "forbiddenAgentTasks": ["FiBu-Buchung ohne menschliche Bestaetigung"],
            "testSelectors": {"screenRoot": "[data-testid='native-cockpit-annahme-abrechnung']"},
        },
    }


AGRAR_WORKBENCH_BUILDERS = {
    "agrar/kunden-schlagkartei": build_agrar_kunden_schlagkartei,
    "agrar/milchvieh-karte": build_agrar_milchvieh_karte,
    "agrar/ernte-annahme-erfassung": build_agrar_ernte_annahme_erfassung,
    "annahme/abrechnung": build_annahme_abrechnung,
}
