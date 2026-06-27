from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COVERAGE_XML = PROJECT_ROOT / "coverage.xml"

CRITICAL_THRESHOLDS: dict[str, float] = {
    # ── Infra / Governance ────────────────────────────────────────────────────
    "middleware/tenant_enforcement.py": 0.97,       # 100.0% measured  (COV-RATCHET-004: +7pp)
    "services/secrets_vault.py": 0.49,              #  50.4% measured — knapper Puffer
    "domains/shared/events.py": 0.62,               #  62.2% measured in CI 2026-06-27 (COV-RATCHET-010 baseline)
    "services/integration_bootstrap.py": 0.92,      #  94.6% measured

    # ── Finance / FIBU Core (COV-FIN-002/003) ────────────────────────────────
    "api/v1/endpoints/finance_actions.py": 0.78,    #  78.2% measured in CI 2026-06-27 (COV-RATCHET-010 baseline)
    "api/v1/endpoints/finance_followup.py": 0.71,   #  73.4% measured  (COV-RATCHET-004: +1pp)
    "api/v1/endpoints/fibu_connectors.py": 0.78,    #  81.0% measured  (COV-RATCHET-004: -2pp Puffer)
    "api/v1/endpoints/dunning.py": 0.85,            #  87.5% measured  (COV-RATCHET-004: +5pp)
    "api/v1/endpoints/payment_runs.py": 0.84,       #  86.7% measured  (COV-RATCHET-004: +4pp)
    "api/v1/endpoints/exchange_rates.py": 0.77,     #  79.6% measured  (COV-RATCHET-004: +2pp)
    "api/v1/endpoints/booking_templates.py": 0.62,  #  63.6% measured  (COV-RATCHET-004: +2pp)
    "api/v1/endpoints/chart_of_accounts.py": 0.63,  #  65.2% measured  (COV-RATCHET-004: +3pp)
    "api/v1/endpoints/finance_read_models.py": 0.87, #  89.5% measured  (COV-RATCHET-004: +2pp)
    # Finance ergänzend (neu)
    "api/v1/endpoints/journal_entries.py": 0.25,    #  COV-RATCHET-002: +6pp (Ziel 30%)
    "api/v1/endpoints/open_items.py": 0.42,         #  COV-RATCHET-002: +3pp
    "api/v1/endpoints/financial_reports.py": 0.25,  #  25.4% measured in CI 2026-06-27 (COV-RATCHET-010 baseline)

    # ── Inventory / Warehouse (COV-INV-001/002) ───────────────────────────────
    "api/v1/endpoints/waage.py": 0.88,              #  91.1% measured  (COV-RATCHET-004: +3pp)
    "api/v1/endpoints/warehouses.py": 0.95,         #  97.1% measured
    "api/v1/endpoints/warehouse_transfers.py": 0.65, #  67.8% measured  (COV-RATCHET-004: +5pp)
    "api/v1/endpoints/inventory_counts.py": 0.57,   #  59.9% measured  (+7pp)
    "api/v1/endpoints/inventory_operations.py": 0.52, #  52.4% measured in CI 2026-06-25

    # ── Feed production chain (FEED-CHAIN-004 / COV-RATCHET-FEED-001) ─────────
    "services/feed_inventory_link_service.py": 0.55,
    "api/v1/endpoints/produktion_mischfutter.py": 0.35,

    # ── DOM-CON-004: Kontrakt Lifecycle / Fixing / Settlement ─────────────────
    "services/kontrakt_lifecycle_service.py": 0.80,   #  83% measured
    "services/kontrakt_fixing_service.py": 0.58,      #  61% measured
    "services/kontrakt_settlement_service.py": 0.60,  #  63% measured
    "api/v1/endpoints/kontrakt_actions.py": 0.58,     #  62% measured

    # ── DOM-FEED-PROD-004: Mischfutter-Produktion ─────────────────────────────
    "services/feed_produktion_lifecycle_service.py": 0.73, #  76% measured
    "services/feed_rezeptur_service.py": 0.50,             #  53% measured
    "api/v1/endpoints/feed_produktion_actions.py": 0.62,   #  66% measured

    # ── DOM-POS-004: Tagesabschluss + TSE-Simulation ─────────────────────────
    "services/pos_tagesabschluss_service.py": 0.76,        #  79% measured
    "api/v1/endpoints/pos_tagesabschluss_actions.py": 0.50, #  53% measured

    # ── DOM-DOC-004: Nachweisraum + GoBD-Export ───────────────────────────────
    "services/doc_nachweisraum_lifecycle_service.py": 0.73, #  76% measured
    "api/v1/endpoints/doc_nachweisraum_actions.py": 0.62,   #  65% measured

    # ── DOM-HRM-004: Zeiterfassung + Abwesenheit ──────────────────────────────
    "services/hrm_zeiterfassung_service.py": 0.74,    #  77% measured
    "services/hrm_abwesenheit_service.py": 0.78,      #  81% measured
    "api/v1/endpoints/hrm_lifecycle_actions.py": 0.63, #  66% measured

    # ── DOM-MEL-004: Meldewesen (Intrastat/ELSTER/ATLAS) ─────────────────────
    "services/meldewesen_lifecycle_service.py": 0.87,  #  90% measured
    "api/v1/endpoints/meldewesen_lifecycle_actions.py": 0.65, #  68% measured

    # ── Landhandel-Kern (COV-RATCHET-004 angehoben) ───────────────────────────
    "api/v1/endpoints/kontrakte.py": 0.27,          #  28.5% measured  (+5pp)
    "api/v1/endpoints/harvest_acceptance.py": 0.28,  #  COV-RATCHET-002: +4pp (Agrar-Kern)
    "api/v1/endpoints/articles.py": 0.23,           #  23.7% measured  (+5pp)
    "api/v1/endpoints/sales_orders.py": 0.38,       #  39.8% measured  (+6pp)
    "api/v1/endpoints/ap_invoices.py": 0.42,        #  43.6% measured  (+7pp)

    # ── Agrar-Differenziator ──────────────────────────────────────────────────
    "api/v1/endpoints/agrar_p0.py": 0.57,           #  57.8% measured in CI 2026-06-25
    "api/v1/endpoints/agrar_contracts.py": 0.51,    #  53.5% measured  (+6pp)
    "api/v1/endpoints/silo.py": 0.31,               #  32.6% measured  (+6pp)

    # ── Security / Compliance ─────────────────────────────────────────────────
    "api/v1/endpoints/audit.py": 0.38,              #  39.8% measured  (+6pp)
    "api/v1/endpoints/gdpr.py": 0.28,               #  29.8% measured  (+6pp)
    "api/v1/endpoints/security_monitoring.py": 0.69, #  71.4% measured  (+4pp)

    # ── Neue Pfade (COV-RATCHET-004 / DOMAIN-PARITY-COV-001) ─────────────────
    "api/v1/endpoints/strecke.py": 0.22,             #  COV-RATCHET-002: +4pp (Streckenhandel)

    # ── Wave 2026-05-17b: Agrar/Compliance/Finance-Erweiterungen ──────────────
    "api/v1/endpoints/gdpr_art30_ropa.py": 0.80,    #  83% measured — DSGVO Art. 30 ROPA
    "api/v1/endpoints/gdpr_art33_breach.py": 0.94,  #  97% measured — DSGVO Art. 33 Datenpanne
    "api/v1/endpoints/genossenschaft.py": 0.58,     #  61% measured — Genossenschaftsverwaltung
    "api/v1/endpoints/intrastat.py": 0.57,          #  60% measured — EU Intrastat
    "api/v1/endpoints/gelangensbestaetigung.py": 0.57,  #  60% measured — §17a UStDV
    "api/v1/endpoints/gs1_barcode.py": 0.63,        #  66% measured — GS1 Barcode Parse
    "api/v1/endpoints/kontrakt_hedging.py": 0.74,   #  77% measured — MATIF Hedging
    "api/v1/endpoints/kontrakt_klassen.py": 0.75,   #  78% measured — Kontraktklassen
    "api/v1/endpoints/price_calculation.py": 0.83,  #  86% measured — Preiskalkulation
    "api/v1/endpoints/sanctions_compliance.py": 0.66,  #  69% measured — Sanktionsliste
    "api/v1/endpoints/webhook_system.py": 0.61,     #  64% measured — Webhook-System
    "api/v1/endpoints/erechnung_import.py": 0.78,   #  81% measured — E-Rechnung Import
    "api/v1/endpoints/sales_invoice_einvoice.py": 0.30,  #  33% measured — XRechnung/ZUGFeRD Export
    "api/v1/endpoints/waagen_vorlagen.py": 0.50,    #  53% measured — Waagenvorlagen
    "api/v1/endpoints/rohware_sammelabrechnung.py": 0.32,  #  35% measured — Sammelabrechnung

    # ── COV-RATCHET-009 (2026-06-26): Welle-13-Endpoints ────────────────────
    "api/v1/endpoints/futtermittel_qs.py": 0.40,       # FEED-QS-001: HACCP/VLOG/QS-Pruefpunkte
    "domains/agrar/api/psm_proplanta.py": 0.15,        # 15.8% measured in CI 2026-06-27 (COV-RATCHET-010 baseline)

    # ── COV-RATCHET-008 (2026-06-26): Welle-9-Endpoints ─────────────────────
    "api/v1/endpoints/einkauf_lieferschein.py": 0.45,  # EINKAUF-LS-REPAIR-001: GET/POST/PATCH Lieferschein

    # ── COV-RATCHET-007 (2026-06-26): Welle-5/6-Endpoints ───────────────────
    "api/v1/endpoints/logistik_frachtbriefe.py": 0.60,  # LOG-FRACHTBRIEF-001: GET/POST/PATCH + Enum-Check
    "api/v1/endpoints/silo_target_cell.py": 0.50,       # WM-AGRI-MAP-001: Zielzellen-Vorschlag
    "api/v1/endpoints/policies.py": 0.40,               # RUNTIME-KAT-C-002: policy/list (success-Key-Fix)
    "api/v1/endpoints/kaeufergruppe.py": 0.41,          # 41.5% measured in CI 2026-06-27 (COV-RATCHET-010 baseline)
    "api/v1/endpoints/messages.py": 0.35,               # RUNTIME-KAT-C-002: health dict[str,str]-Fix

    # ── MCP-ERP-TOOLS-001 (2026-06-25) ────────────────────────────────────────
    "services/mcp_tool_registry_service.py": 0.85,        #  88% measured
    "api/v1/endpoints/mcp_tool_registry.py": 0.50,        #  53% estimated

    # ── EXTERNAL-MOCK-HARNESS-001 (2026-06-25) ────────────────────────────────
    "services/external_mock_harness_service.py": 0.88,    #  91% measured
    "api/v1/endpoints/external_mock_harness.py": 0.50,    #  53% estimated

    # ── OPERATOR-AGENT-001 (2026-06-25) ───────────────────────────────────────
    "services/operator_agent_service.py": 0.85,           #  88% measured
    "api/v1/endpoints/operator_agent.py": 0.43,           #  43.8% measured in CI 2026-06-25

    # ── P2.1 PROCESS-MAP-001 (2026-06-25) ────────────────────────────────────
    "services/process_map_service.py": 0.82,              #  85% measured
    "api/v1/endpoints/process_map.py": 0.45,              #  45.5% measured in CI 2026-06-25

    # ── P2.2 AI-METRICS-001 (2026-06-25) ─────────────────────────────────────
    "services/ai_engineering_metrics_service.py": 0.38,   #  38.5% measured in CI 2026-06-27 (COV-RATCHET-010 baseline)
    "api/v1/endpoints/ai_engineering_metrics.py": 0.50,   #  53% estimated

    # ── P2.3 AI-DATA-CLASSES-001 (2026-06-25) ────────────────────────────────
    "services/ai_data_classification_service.py": 0.85,   #  88% measured
    "api/v1/endpoints/ai_data_classification.py": 0.50,   #  53% estimated

    # ── WM-SILO-RULE-ENGINE-001 (2026-06-25) ─────────────────────────────────
    "services/silo_rule_engine_service.py": 0.80,          #  ~82% estimated
    "api/v1/endpoints/silo_target_cell.py": 0.50,          #  ~55% estimated

    # ── WM-SILO-RULE-UPGRADE-001 (2026-06-25) ────────────────────────────────
    "services/agri_lot_link_booking_service.py": 0.50,     #  ~52% estimated (Regelengine-Fallback)

    # ── HRM-ABWESENHEIT-ANTRAG-001 (2026-06-25) ──────────────────────────────
    "api/v1/endpoints/hrm_abwesenheit.py": 0.43,           #  43.7% measured in CI 2026-06-27 (COV-RATCHET-010 baseline)

    # ── WF-COCKPIT-PERSIST-001 (2026-06-25) ──────────────────────────────────
    "services/wf_cockpit_persist_service.py": 0.70,        #  70.9% measured in CI 2026-06-27 (COV-RATCHET-010 baseline)
    "services/wf_cockpit_nats_projector.py": 0.75,         #  COV-RATCHET-007 2026-06-27: echter Unit-Test (14 Tests, NATS-unabhaengig)
    "api/v1/endpoints/wf_cockpit_persist.py": 0.44,        #  44.9% measured in CI 2026-06-27 (COV-RATCHET-010 baseline)

    # ── PORTAL-PREISSPIEGEL-001 (2026-06-25) ─────────────────────────────────
    "services/portal_preisspiegel_service.py": 0.70,
    "api/v1/endpoints/portal_preisspiegel.py": 0.52,

    # ── PORTAL-INTELLIGENCE-001 (2026-06-25) ─────────────────────────────────
    "services/portal_intelligence_service.py": 0.72,
    "api/v1/endpoints/portal_intelligence.py": 0.50,

    # ── PORTAL-LOHNDIENST-001 (2026-06-25) ───────────────────────────────────
    "services/portal_lohndienst_service.py": 0.75,
    "api/v1/endpoints/portal_lohndienst.py": 0.50,

    # ── PORTAL-INTERESSENT-001 (2026-06-25) ──────────────────────────────────
    "services/portal_interessent_service.py": 0.78,
    "api/v1/endpoints/portal_interessent.py": 0.50,

    # ── PORTAL-INNENDIENST-001 (2026-06-25) ──────────────────────────────────
    "api/v1/endpoints/portal_innendienst.py": 0.30,        #  30.2% measured in CI 2026-06-27 (COV-RATCHET-010 baseline)

    # ── OPERATOR-AGENT Execute-Erweiterung + Externe Gates (2026-06-26) ───────
    "api/v1/endpoints/external_gates.py": 0.70,           # Gate-Dashboard Produktiv-API
    "api/v1/endpoints/quality_evidence.py": 0.70,       # Qualitäts-Cockpit API
}


def _normalise(filename: str) -> str:
    return filename.replace("\\", "/").lstrip("./")


def main() -> None:
    if not COVERAGE_XML.exists():
        raise SystemExit("coverage.xml not found. Run pytest with coverage reporting first.")

    tree = ET.parse(COVERAGE_XML)
    root = tree.getroot()

    measured: dict[str, float] = {}
    for cls in root.findall(".//class"):
        filename = _normalise(cls.attrib.get("filename", ""))
        line_rate = float(cls.attrib.get("line-rate", "0"))
        measured[filename] = line_rate

    failures: list[str] = []
    for filename, threshold in CRITICAL_THRESHOLDS.items():
        actual = measured.get(filename)
        if actual is None:
            failures.append(f"{filename}: not present in coverage.xml")
            continue
        if actual < threshold:
            failures.append(
                f"{filename}: {actual:.1%} below threshold {threshold:.1%}"
            )

    if failures:
        raise SystemExit("Critical backend coverage below ratchet:\n- " + "\n- ".join(failures))

    print("Critical backend coverage OK.")


if __name__ == "__main__":
    main()
