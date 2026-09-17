"""Besitzregeln fuer domain_*-Tabellen.

Technischer Custodian ist das PostgreSQL-Schema. Die fachliche Domain kommt
aus Architecture OS. Tabellennamen mit festem Praefix muessen im erwarteten
Schema liegen — oder als Legacy begruendet sein.
"""

from __future__ import annotations

from typing import Any

# Physisches Schema → Architecture-Index-Domain. Neue Schemas fallen durch,
# bis sie hier stehen (only-up).
SCHEMA_TO_DOMAIN: dict[str, str] = {
    "domain_agrar": "agrar",
    "domain_compliance": "dms-compliance",
    "domain_controlling": "finance",
    "domain_crm": "crm",
    "domain_dev_mock": "platform",
    "domain_docflow": "dms-compliance",
    "domain_docs": "platform",
    "domain_einkauf": "procurement",
    "domain_erp": "finance",
    "domain_finance": "finance",
    "domain_futtermittel": "agrar",
    "domain_hr": "hr",
    "domain_hrm": "hr",
    "domain_integration": "platform",
    "domain_inventory": "inventory",
    "domain_kontrakte": "agrar",
    "domain_log": "platform",
    "domain_logistics": "logistics",
    "domain_meldewesen": "finance",
    "domain_nachweisraum": "dms-compliance",
    "domain_ops": "inventory",
    "domain_portal": "crm",
    "domain_pos": "finance",
    "domain_pricing": "finance",
    "domain_procurement": "procurement",
    "domain_reporting": "finance",
    "domain_sales": "crm",
    "domain_shared": "platform",
    "domain_workflow": "platform",
}

EXACT_TABLE_OWNERSHIP: dict[str, tuple[str, ...]] = {
    "domain_shared": ("tenants", "users", "audit_logs"),
    "domain_crm": ("business_partners", "customers"),
    "domain_erp": ("journal_entries", "journal_entry_lines", "chart_of_accounts"),
    "domain_inventory": ("articles", "inventory_stock_movements", "inventory_counts"),
    "domain_einkauf": ("bestellungen", "lieferanten"),
    "domain_sales": ("delivery_notes", "sales_credit_notes", "sales_returns"),
    "domain_ops": ("ops_wiegungen", "ops_chargen", "ops_labor_proben"),
    "domain_docflow": ("document_headers", "document_items", "document_artifacts"),
    "domain_agrar": ("agrar_saatgut", "agrar_duenger"),
    "domain_controlling": ("kpi_definitions", "kpi_timeseries"),
}

# Laengstes Praefix gewinnt. Nur Namen, die ein Schema *kodieren*.
PREFIX_SCHEMA_RULES: dict[str, str] = {
    "ops_": "domain_ops",
    "agrar_": "domain_agrar",
    "sales_": "domain_sales",
    "kpi_": "domain_controlling",
    "document_": "domain_docflow",
}

TOLERATED_LEGACY_LOCATIONS: dict[tuple[str, str], str] = {
    ("domain_inventory", "lkw_annahme_queue"): "Annahme-Queue liegt historisch bei Inventory.",
    ("domain_einkauf", "kontrakte"): "Kontrakte liegen historisch im Einkaufsschema.",
    ("domain_crm", "sales_offers"): "Sales-Angebote liegen historisch im CRM-Schema.",
    ("domain_crm", "sales_offer_items"): "Sales-Angebotspositionen liegen historisch im CRM-Schema.",
    ("domain_crm", "sales_orders"): "Sales-Auftraege liegen historisch im CRM-Schema.",
    ("domain_crm", "sales_order_items"): "Sales-Auftragspositionen liegen historisch im CRM-Schema.",
    ("domain_finance", "sales_order"): "FIBU-Referenzobjekt sales_order liegt historisch in domain_finance.",
    ("domain_inventory", "agrar_contracts"): "Agrar-Kontrakte liegen historisch im Inventory-Schema.",
    ("domain_inventory", "agrar_contract_allocations"): "Agrar-Kontraktallokationen liegen historisch im Inventory-Schema.",
    ("domain_inventory", "agrar_settlements"): "Agrar-Abrechnungen liegen historisch im Inventory-Schema.",
    ("domain_inventory", "agrar_settlement_deductions"): "Agrar-Abzuege liegen historisch im Inventory-Schema.",
    ("domain_shared", "agrar_sorten"): "Agrar-Sorten liegen historisch im Shared-Schema.",
    ("domain_ops", "document_control_exceptions"):
        "Belegkontroll-Worklist ist ein Prozessvorrat in domain_ops, kein Belegartefakt.",
    ("domain_ops", "document_control_audit"):
        "Audit-Spur der Belegkontroll-Worklist, liegt beim Prozess in domain_ops.",
}

_PREFIX_ORDER = tuple(
    sorted(PREFIX_SCHEMA_RULES.items(), key=lambda item: len(item[0]), reverse=True)
)


def matching_prefix(table: str) -> tuple[str, str] | None:
    for prefix, schema in _PREFIX_ORDER:
        if table.startswith(prefix):
            return prefix, schema
    return None


def classify_table(schema: str, table: str) -> dict[str, Any]:
    """Ordnet eine Tabelle. Unbekanntes Schema oder Praefix-Konflikt ohne Legacy ist ein Fehler."""
    owner = SCHEMA_TO_DOMAIN.get(schema)
    if owner is None:
        return {
            "owner_domain": None,
            "placement": "unknown_schema",
            "ok": False,
            "reason": f"Schema {schema} fehlt in SCHEMA_TO_DOMAIN.",
        }

    legacy = TOLERATED_LEGACY_LOCATIONS.get((schema, table))
    if legacy:
        return {
            "owner_domain": owner,
            "placement": "legacy",
            "ok": True,
            "reason": legacy,
        }

    matched = matching_prefix(table)
    if matched:
        prefix, expected = matched
        if schema != expected:
            return {
                "owner_domain": owner,
                "placement": "prefix_mismatch",
                "ok": False,
                "reason": f"Praefix '{prefix}' erwartet {expected}, gefunden {schema}.",
            }
        return {
            "owner_domain": owner,
            "placement": "prefix",
            "ok": True,
            "reason": f"Praefix '{prefix}' → {expected}.",
        }

    return {
        "owner_domain": owner,
        "placement": "native",
        "ok": True,
        "reason": f"Custodian {schema} / Domain {owner}.",
    }


def schemas_by_domain() -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for schema, domain in SCHEMA_TO_DOMAIN.items():
        grouped.setdefault(domain, []).append(schema)
    return {domain: sorted(schemas) for domain, schemas in grouped.items()}
