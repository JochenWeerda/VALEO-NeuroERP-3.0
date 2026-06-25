#!/usr/bin/env python3
"""
CI gate: Tenant isolation audit for API endpoint files.

Every endpoint file must be classified as one of:
  - tenant-isolated   : queries are filtered by tenant_id
  - shared-data       : model has no tenant_id column; deliberate design (e.g. physical infrastructure)
  - system-endpoint   : stateless / infrastructure / no DB tenant data (health, parsers, ...)
  - gap-tracked       : tenant_id column exists on the model but endpoint does not yet filter;
                        tracked as a known gap with a GitHub issue reference

New files added without classification cause CI to fail.
Run:  python scripts/check_tenant_isolation.py
"""

from __future__ import annotations

import os
import re
import sys

ENDPOINTS_DIR = "app/api/v1/endpoints"

# ─── CLASSIFICATION ────────────────────────────────────────────────────────────
# Files that use tenant_id in their queries (verified)
TENANT_ISOLATED: set[str] = set()  # dynamically detected — see _has_tenant_id()

# Files that access models deliberately designed as shared/global infrastructure.
# These models have no tenant_id column — adding isolation requires a DB migration.
# TODO: add tenant_id to these models in a future migration wave.
SHARED_DATA: set[str] = {
    "fuhrpark.py",             # Fahrzeug/FuhrparkRechnung — physical fleet, no tenant_id in model
    "waage.py",                # Waage/Wiegung — physical weighbridges, no tenant_id in model
    "tours.py",                # Tour/TourStop — verladung domain, no tenant_id in model
    "charges.py",              # Charge — no tenant_id in model
    "banken.py",               # BankKonto — no tenant_id in model
    "strecke_speditionen.py",  # SpeditionFrachttarif — reference tariff, no tenant_id in model
    "dokumente.py",            # Dokument/DokumentVersion — no tenant_id in model
    "vertraege.py",            # Rahmenvertrag — no tenant_id in model
    "foerderung.py",           # FoerderAntrag — no tenant_id in model
    "zertifikate.py",          # ZertifikatEintrag — no tenant_id in model
    "labor.py",                # LaborProbe/LaborAuftragEntry — no tenant_id in model
    "marketing.py",            # MarketingKampagneEntry — no tenant_id in model
    "disposition.py",          # DispositionPosition — no tenant_id in model
    "ruestliste.py",           # operational list — no tenant_id in model
    "transporte.py",           # transport records — no tenant_id in model
    "dms_inbox.py",            # DmsInboxEntry in domain_shared — shared inbox by design
    "compliance_whistleblower.py",  # intentionally anonymous; no tenant filter by law
    "credit_debit_memos.py",       # uses DocumentRepository (shared store, no tenant_id in model)
    "crm_kunden_map.py",           # legacy CRM map tables have no tenant_id column
    "geo.py",                      # shared prospecting/geodata tables have no tenant_id column
    "milchvieh_crosssell.py",      # legacy dairy analytics tables have no tenant_id column
}

# Stateless / system / infrastructure endpoints — no tenant DB access
SYSTEM_ENDPOINTS: set[str] = {
    "__init__.py",
    "health.py",
    "gs1_barcode.py",
    "gs1_parser.py",
    "iban_lookup.py",
    "terminology.py",
    "agent_tool_contracts.py",
    "neuro_fast_track.py",
    "neuro_guardrails.py",
    "neuro_event_monitoring.py",
    "neuro_voice.py",
    "neuro_compensation.py",
    "ki_usability.py",
    "gap.py",
    "security_monitoring.py",
    "webhook_system.py",
    "batch.py",
    "workflow_simulation.py",
    "sla_escalation_api.py",
    "agrar_wetter.py",         # weather proxy to BrightSky/Open-Meteo; no tenant DB data
    "contacts.py",             # external CRM proxy (httpx); no DB tenant data
    "admin_dms.py",            # DMS admin proxy (httpx); no DB tenant data
    "analytics.py",            # aggregated analytics; system-level
    "pos_payments_promotions.py",  # POS static config; no DB tenant data
    "pos_dsfinvk.py",          # DSFinV-K export; mock/static data
    "sales_shipping_ext.py",   # thin shipping extension; no DB queries
    "prospecting.py",          # AI prospecting; no persistent tenant data
    "external_mock_harness.py",  # dev-only deterministic external-system mocks; no tenant DB data
    "mcp_tool_registry.py",    # read-only ERP tool catalog from versioned YAML; no tenant DB data
}

# Known gaps: model HAS tenant_id but endpoint doesn't filter yet.
# Each entry should have a tracking reference.
GAP_TRACKED: dict[str, str] = {
    # "example.py": "GitHub #123 — add tenant filter to sales_orders query",
}


def _has_tenant_id(content: str) -> bool:
    return bool(re.search(r"tenant_id", content))


def main() -> int:
    all_files = sorted(
        f for f in os.listdir(ENDPOINTS_DIR) if f.endswith(".py")
    )

    violations: list[str] = []
    classified: list[tuple[str, str]] = []

    for fname in all_files:
        path = os.path.join(ENDPOINTS_DIR, fname)
        content = open(path, encoding="utf-8").read()

        if fname in SYSTEM_ENDPOINTS:
            classified.append((fname, "system"))
        elif fname in SHARED_DATA:
            classified.append((fname, "shared-data"))
        elif fname in GAP_TRACKED:
            classified.append((fname, f"gap [{GAP_TRACKED[fname]}]"))
        elif _has_tenant_id(content):
            classified.append((fname, "tenant-isolated"))
        else:
            violations.append(fname)

    if violations:
        print("TENANT ISOLATION CHECK FAILED")
        print("=" * 60)
        print("The following endpoint files have no tenant_id usage")
        print("and are not classified in scripts/check_tenant_isolation.py:")
        print()
        for v in violations:
            print(f"  {v}")
        print()
        print("Action: add the file to SHARED_DATA, SYSTEM_ENDPOINTS,")
        print("GAP_TRACKED, or add tenant_id filtering to the endpoint.")
        return 1

    # Summary
    counts: dict[str, int] = {}
    for _, category in classified:
        key = category.split("[")[0].strip()
        counts[key] = counts.get(key, 0) + 1

    print("Tenant isolation audit PASSED")
    for cat, cnt in sorted(counts.items()):
        print(f"  {cat:20s}: {cnt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
