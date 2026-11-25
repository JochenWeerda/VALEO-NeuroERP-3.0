"""Konditionen-/Pricing-Fachoberflaechen im Universal-Runtime."""
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
    surface_only: bool = True,
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
        "surfaceOnly": surface_only,
    }
    if fields:
        action["inputFields"] = fields
    return action


def build_konditionen_konditionssystem() -> dict[str, Any]:
    """Konditionssystem KOND-001 — Preislisten, Rabatte, Individualpreise, Preisfindung."""
    perm = "agrar.konditionen.write"
    price_lists = "/api/v1/price-lists/"
    rabatt = "/api/v1/preise/rabatte"
    individual = "/api/v1/preise/individualpreise"
    pricing = "/api/v1/pricing/calculate"
    return {
        "schemaVersion": 1,
        "id": "konditionen/konditionssystem",
        "domain": "agrar",
        "mode": "cockpit",
        "title": "Konditionssystem",
        "subtitle": "Preislisten · Rabatte · Individualpreise · Preisfindung (KOND-001)",
        "adapter": {"type": "native", "sourceId": "konditionen/konditionssystem", "temporary": False},
        "layout": {
            "floorplan": "cockpit",
            "density": "compact",
            "contextRail": "combined",
            "tableProfile": "pricing",
        },
        "dataSources": [
            {"key": "preislisten", "endpoint": price_lists, "pageSize": 100, "staleTimeMs": 15_000},
            {"key": "rabattgruppen", "endpoint": f"{rabatt}/gruppen", "pageSize": 100, "staleTimeMs": 15_000},
            {"key": "rabattklassen", "endpoint": f"{rabatt}/klassen", "pageSize": 100, "staleTimeMs": 15_000},
            {"key": "rabattsaetze", "endpoint": f"{rabatt}/saetze", "pageSize": 100, "staleTimeMs": 15_000},
            {"key": "individualpreise", "endpoint": individual, "pageSize": 100, "staleTimeMs": 15_000},
        ],
        "fields": [
            {"key": "preisliste_count", "label": "Preislisten", "type": "number", "readOnly": True},
            {"key": "rabattgruppe_count", "label": "Rabattgruppen", "type": "number", "readOnly": True},
            {"key": "individualpreis_count", "label": "Individualpreise", "type": "number", "readOnly": True},
        ],
        "actions": [
            _cmd(
                "preisliste_anlegen",
                "Preisliste anlegen",
                endpoint=price_lists,
                permission=perm,
                primary=True,
                fields=[
                    {"key": "name", "label": "Name", "type": "text", "required": True},
                    {"key": "price_list_type", "label": "Typ", "type": "text", "required": True},
                    {"key": "currency", "label": "Waehrung", "type": "text", "required": False, "defaultValue": "EUR"},
                    {"key": "valid_from", "label": "Gueltig von", "type": "text", "required": False},
                    {"key": "valid_until", "label": "Gueltig bis", "type": "text", "required": False},
                ],
            ),
            _cmd(
                "preisliste_loeschen",
                "Preisliste loeschen",
                endpoint=f"{price_lists}{{id}}",
                method="DELETE",
                permission=perm,
                fields=[{"key": "id", "label": "Preisliste-ID", "type": "text", "required": True}],
            ),
            _cmd(
                "rabattgruppe_anlegen",
                "Rabattgruppe anlegen",
                endpoint=f"{rabatt}/gruppen",
                permission=perm,
                fields=[
                    {"key": "gruppe_nr", "label": "Gruppen-Nr", "type": "text", "required": True},
                    {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                    {"key": "richtung", "label": "Richtung", "type": "text", "required": True},
                ],
            ),
            _cmd(
                "rabattgruppe_loeschen",
                "Rabattgruppe loeschen",
                endpoint=f"{rabatt}/gruppen/{{id}}",
                method="DELETE",
                permission=perm,
                fields=[{"key": "id", "label": "Gruppen-ID", "type": "text", "required": True}],
            ),
            _cmd(
                "rabattklasse_anlegen",
                "Rabattklasse anlegen",
                endpoint=f"{rabatt}/klassen",
                permission=perm,
                fields=[
                    {"key": "klasse_nr", "label": "Klassen-Nr", "type": "text", "required": True},
                    {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                    {"key": "richtung", "label": "Richtung", "type": "text", "required": True},
                ],
            ),
            _cmd(
                "rabattklasse_loeschen",
                "Rabattklasse loeschen",
                endpoint=f"{rabatt}/klassen/{{id}}",
                method="DELETE",
                permission=perm,
                fields=[{"key": "id", "label": "Klassen-ID", "type": "text", "required": True}],
            ),
            _cmd(
                "rabattsatz_anlegen",
                "Rabattsatz anlegen",
                endpoint=f"{rabatt}/saetze",
                permission=perm,
                fields=[
                    {"key": "rabattgruppe_nr", "label": "Gruppen-Nr", "type": "text", "required": True},
                    {"key": "rabattklasse_nr", "label": "Klassen-Nr", "type": "text", "required": True},
                    {"key": "richtung", "label": "Richtung", "type": "text", "required": True},
                    {"key": "rabatt_prozent", "label": "Rabatt %", "type": "number", "required": True},
                    {"key": "ab_menge", "label": "Ab Menge", "type": "number", "required": False},
                    {"key": "gueltig_ab", "label": "Gueltig ab", "type": "text", "required": False},
                ],
            ),
            _cmd(
                "rabattsatz_loeschen",
                "Rabattsatz loeschen",
                endpoint=f"{rabatt}/saetze/{{id}}",
                method="DELETE",
                permission=perm,
                fields=[{"key": "id", "label": "Satz-ID", "type": "text", "required": True}],
            ),
            _cmd(
                "individualpreis_anlegen",
                "Individualpreis anlegen",
                endpoint=individual,
                permission=perm,
                fields=[
                    {"key": "preis_typ", "label": "Preis-Typ", "type": "text", "required": True},
                    {"key": "artikel_nr", "label": "Artikel-Nr", "type": "text", "required": True},
                    {"key": "partner_nr", "label": "Partner-Nr", "type": "text", "required": False},
                    {"key": "preis_eur", "label": "Preis EUR", "type": "number", "required": True},
                    {"key": "gueltig_von", "label": "Gueltig von", "type": "text", "required": True},
                    {"key": "gueltig_bis", "label": "Gueltig bis", "type": "text", "required": False},
                    {"key": "staffel_menge", "label": "Staffelmenge", "type": "number", "required": False},
                    {"key": "waehrung", "label": "Waehrung", "type": "text", "required": False, "defaultValue": "EUR"},
                ],
            ),
            _cmd(
                "individualpreis_loeschen",
                "Individualpreis loeschen",
                endpoint=f"{individual}/{{id}}",
                method="DELETE",
                permission=perm,
                fields=[{"key": "id", "label": "Preis-ID", "type": "text", "required": True}],
            ),
            _cmd(
                "preis_berechnen",
                "Preis berechnen",
                endpoint=pricing,
                method="GET",
                permission="agrar.konditionen.read",
                surface_only=True,
                fields=[
                    {"key": "article_id", "label": "Artikel", "type": "text", "required": True},
                    {"key": "customer_id", "label": "Kunde", "type": "text", "required": False},
                    {"key": "quantity", "label": "Menge", "type": "number", "required": False},
                ],
            ),
        ],
        "specialized": {"type": "pricing_workbench", "id": "konditionen/konditionssystem"},
        "noWorkflowReason": "Konditions-Arbeitsplatz; Mutationen laufen ueber Pricing-/Rabatt-Commands.",
        "noProcessChainReason": "Konditionen ohne eigene Belegkette in dieser Maske.",
        "performance": {
            "initialPayloadBudgetKb": 180,
            "requiresLazyTabs": True,
            "requiresVirtualTables": False,
            "lookupMinChars": 2,
            "bundleGroup": "pricing",
        },
        "agentContract": {
            "businessPurpose": "Preislisten, Rabattgruppen/-klassen/-saetze und Individualpreise pflegen sowie Preise finden.",
            "examplePrompts": [
                "Lege eine Preisliste an.",
                "Berechne den Preis fuer Artikel X.",
            ],
            "sensitiveFields": [],
            "forbiddenAgentTasks": ["Rabatt ohne menschliche Bestaetigung loeschen"],
            "testSelectors": {"screenRoot": "[data-testid='native-cockpit-konditionen-konditionssystem']"},
        },
    }


PRICING_WORKBENCH_BUILDERS = {
    "konditionen/konditionssystem": build_konditionen_konditionssystem,
}
