"""Versioned customer-master field metadata shared by Studio and command validation."""
from __future__ import annotations

import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

CATALOG = Path(__file__).resolve().parents[2] / "config" / "customer_master_profile.json"
PREFIX = "partner_"


@lru_cache(maxsize=1)
def master_catalog() -> dict[str, Any]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    if catalog.get("schemaVersion") != 1:
        raise ValueError("Unsupported customer master catalog version")
    fields = [field["key"] for group in catalog["groups"] for field in group["fields"]]
    if len(fields) != len(set(fields)):
        raise ValueError("Customer master fields must have one authoritative group")
    return catalog


def master_fields() -> dict[str, dict[str, Any]]:
    return {field["key"]: field for group in master_catalog()["groups"] for field in group["fields"]}


def editable_master_fields() -> dict[str, dict[str, Any]]:
    return {key: field for key, field in master_fields().items() if not field.get("readOnly")}


def master_input_fields() -> list[dict[str, Any]]:
    """Field groups are presentation metadata; the server independently checks every write."""
    fields = []
    for group in master_catalog()["groups"]:
        for field in group["fields"]:
            if field.get("readOnly"):
                continue
            item = deepcopy(field)
            item["key"] = PREFIX + field["key"]
            item["section"] = group["label"]
            if item["type"] == "currency":
                item["type"] = "number"
            fields.append(item)
    return fields


def apply_customer_master_profile(definition: dict[str, Any]) -> None:
    """Enrich the existing Studio customer page; never introduce another customer form."""
    agent = definition.setdefault("agentContract", {})
    sensitive_groups = {"banking", "finance", "contactData", "gdpr", "marketingConsent"}
    sensitive = [PREFIX + field["key"] for group in master_catalog()["groups"]
                 if group["key"] in sensitive_groups for field in group["fields"]]
    agent["sensitiveFields"] = list(dict.fromkeys([
        *agent.get("sensitiveFields", []), "iban", "bic", "bankname", "kontoinhaber",
        "partner_account_holder", "email", "telefon", *sensitive,
    ]))
    for source in definition.get("dataSources", []):
        if source["key"] == "entity":
            source["endpoint"] = "/api/v1/crm/customers/{entity_id}/master-profile"
    # These old projections are a subset of the canonical partner groups below.
    replaced = {"tax", "bank", "system", "quality_compliance", "marketing", "cooperative", "output", "interfaces"}
    definition["tabs"] = [tab for tab in definition.get("tabs", []) if tab["key"] not in replaced]
    sections = [
        ("identity", "Partnerdaten", {"coreIdentity", "roles", "contactData"}),
        ("payment", "Zahlung und Bank", {"banking", "finance", "legacy_payment"}),
        ("agrar", "Agrar und Lieferung", {"agrarExtension", "logistics", "legacy_logistics"}),
        ("billing", "Rechnung und Versand", {"legacy_billing"}),
        ("profile", "Konditionen und Profil", {"legacy_pricing", "legacy_profile"}),
        ("privacy", "Kontakt und Datenschutz", {"marketingConsent", "gdpr"}),
        ("interfaces", "Schnittstellen", {"legacy_interfaces"}),
        ("cooperative", "Genossenschaft", {"legacy_cooperative"}),
        ("audit", "Pruefspur", {"audit"}),
    ]
    for key, label, groups in sections:
        fields = [dict(deepcopy(field), key=PREFIX + field["key"], readOnly=True)
                  for group in master_catalog()["groups"] if group["key"] in groups
                  for field in group["fields"] if field["key"] not in {"tenant_id", "partner_id"}]
        definition["tabs"].append({"key": "partner_" + key, "label": label,
                                   "dataSourceKey": "entity", "lazy": True,
                                   "keepAlive": True, "fields": fields})
    definition["actions"].append({
        "key": "stammdaten_pflegen", "label": "Weitere Stammdaten pflegen", "kind": "secondary",
        "dangerLevel": "moderate", "permission": "crm.customer.update", "zone": "header",
        "commandEndpoint": "/api/v1/crm/customers/{entity_id}/master-profile/actions/bearbeiten",
        "method": "POST", "requiresIdempotencyKey": True, "requiresExpectedVersion": True,
        "inputPrefill": "entity",
        "auditReasonRequired": True, "requiresConfirmation": False,
        "enabledWhen": {"path": "business_partner_id", "exists": True},
        "inputFields": master_input_fields(),
    })
