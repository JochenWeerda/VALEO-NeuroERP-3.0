#!/usr/bin/env python3
"""Generate config/mcp_mask_action_map.yaml from mask actions + MCP catalog.

Curated MCP mappings live in MAPPED_RULES / BLOCKED_RULES. Remaining create/save/
post/log-style mutations are classified open_medium or open_high by domain.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
ACTIONS_PATH = ROOT / "services/ki-usability/app/data/screen_mask_actions.json"
TOOLS_PATH = ROOT / "config/mcp_erp_tools.yaml"
OUT_PATH = ROOT / "config/mcp_mask_action_map.yaml"

MUT_KEY = re.compile(
    r"(create|neu|anlegen|save|speichern|post|buchen|freigeben|approve|submit|"
    r"log|activity|kontakt|versenden|bestellen|mahnen|qualifizieren|"
    r"wareneingang|import|calculate|check|activate|retire|schedule|archive|"
    r"configure|loesch|delete|storno|stornieren|release|reject|abschliess|"
    r"sync|reproject|process)",
    re.I,
)

# Explicit Mask-ID → MCP tool (writes or supporting reads for same workflow).
MAPPED_RULES: dict[str, dict[str, str]] = {
    "mask:crm/customer-360:create_activity": {
        "mcp_tool_id": "crm.activity.create",
        "coverage": "mapped",
        "notes": "Top-Write MCP-WRITE-20261008; Kunden-Aktivität aus Token-Mandant.",
    },
    "mask:crm/opportunity:create_activity": {
        "mcp_tool_id": "crm.activity.create",
        "coverage": "mapped",
        "notes": "Gleicher Activity-Adapter; Opportunity-Kontext via kunden_nr/entity.",
    },
    "mask:crm/lead:qualifizieren": {
        "mcp_tool_id": "crm.lead.qualify",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-TOP-20261008; crm_lead_service.qualify, Token-Mandant.",
    },
    "mask:einkauf/purchase-order:versenden": {
        "mcp_tool_id": "einkauf.bestellung.versenden",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-TOP-20261008; Versand ohne Obligo-Journal.",
    },
    "mask:einkauf/angebot:bestellen": {
        "mcp_tool_id": "einkauf.angebot.bestellen",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-NEXT-20261008; Angebot→Bestellung via EinkaufCompatService.",
    },
    "mask:einkauf/anlieferavis:wareneingang": {
        "mcp_tool_id": "einkauf.anlieferavis.wareneingang",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-NEXT-20261008; WE aus Avis, Lagerzugang ohne FIBU.",
    },
    "mask:lager/stock-movement:stornieren": {
        "mcp_tool_id": "lager.stock_movement.stornieren",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-NEXT-20261008; Gegenbuchung via storno_korrektur.",
    },
    "mask:agrar/ration:submit_review": {
        "mcp_tool_id": "agrar.ration.transition",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-BATCH3-20261008; action_key=submit_review.",
    },
    "mask:agrar/ration:approve": {
        "mcp_tool_id": "agrar.ration.transition",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-BATCH3-20261008; action_key=approve.",
    },
    "mask:agrar/ration:schedule": {
        "mcp_tool_id": "agrar.ration.transition",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-BATCH3-20261008; action_key=schedule + feeding_start.",
    },
    "mask:agrar/ration:activate": {
        "mcp_tool_id": "agrar.ration.transition",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-BATCH3-20261008; action_key=activate.",
    },
    "mask:agrar/ration:retire": {
        "mcp_tool_id": "agrar.ration.transition",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-BATCH4-20261008; action_key=retire (reason Pflicht).",
    },
    "mask:agrar/ration:archive": {
        "mcp_tool_id": "agrar.ration.transition",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-BATCH4-20261008; action_key=archive (reason Pflicht).",
    },
    "mask:agrar/feed-readiness:create_handoff": {
        "mcp_tool_id": "agrar.feeding.supply_handoff",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-BATCH4-20261008; FeedingSupplyService.create_handoff.",
    },
    "mask:agrar/feeding-actuals:create_measure": {
        "mcp_tool_id": "agrar.feeding.actual_measure",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-BATCH4-20261008; FeedingActualMeasureService.create_measure.",
    },
    "mask:agrar/feeding-actuals:configure_threshold": {
        "mcp_tool_id": "agrar.feeding.configure_threshold",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-BATCH5-20261008; FeedingActualMeasureService.create_policy.",
    },
    "mask:futtermittel/analyse:release": {
        "mcp_tool_id": "agrar.feed_analysis.transition",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-BATCH5-20261008; action_key=release.",
    },
    "mask:futtermittel/analyse:reject": {
        "mcp_tool_id": "agrar.feed_analysis.transition",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-BATCH5-20261008; action_key=reject.",
    },
    "mask:qualitaet/reklamation:abschliessen": {
        "mcp_tool_id": "qualitaet.reklamation.abschliessen",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-BATCH5-20261008; Status→geschlossen, Token-Mandant.",
    },
    "mask:produktion/produktionsleitstand:sync": {
        "mcp_tool_id": "produktion.control.sync",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-REMAINING-20261008; ProductionControlService.sync_production_orders.",
    },
    "mask:planung/kalender:reproject": {
        "mcp_tool_id": "planung.calendar.reproject",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-REMAINING-20261008; CalendarProjectionService.reproject.",
    },
    "mask:schnittstelle/mde-inbox:process_pending": {
        "mcp_tool_id": "mobile.sync.process_pending",
        "coverage": "mapped",
        "notes": "MCP-MASK-WRITES-REMAINING-20261008; MobileSyncService.process_pending.",
    },
    "mask:crm/customer-360:edit": {
        "mcp_tool_id": "crm.customer.open",
        "coverage": "mapped_read",
        "notes": "Kein Write-Tool; Deep-Link/open + summary360 für Agent-Navigation.",
    },
    "mask:finance/ar-open-item:mahnen": {
        "mcp_tool_id": "fibu.dunning.status",
        "coverage": "mapped_read",
        "notes": "Mahnlauf-Write bewusst nicht; Status-Read vorhanden.",
    },
    "mask:sales/delivery-note:drucken": {
        "mcp_tool_id": "sales.invoice.propose",
        "coverage": "adjacent",
        "notes": "Druck ≠ Rechnung; Invoice-Propose/Post sind MCP-Writes der Belegkette.",
    },
    "mask:finance/ap-invoice:freigeben": {
        "mcp_tool_id": "finance.ap_invoice.freigeben",
        "coverage": "mapped",
        "notes": (
            "MCP-AP-FREIGABE-20261008; Freigabe nur nach approved Proposal "
            "(finance.ap_invoice.propose); echter CommandEndpoint; kein Journal/FIN-CLOSE."
        ),
    },
    "mask:lager/inventur-nebenlaeufe:create_opening": {
        "mcp_tool_id": "lager.inventur.propose_opening",
        "coverage": "mapped_propose_only",
        "notes": (
            "MCP-INVENTUR-OPENING-PROPOSE-20261008; propose-only (pending, execute 501); "
            "kein CommandEndpoint, kein Booking/Journal — Uebernahme nur UI Vier-Augen."
        ),
    },
    "mask:auswertungen/sanktionspruefung-kunden:check": {
        "mcp_tool_id": "compliance.sanctions.check",
        "coverage": "mapped",
        "notes": (
            "MCP-MASK-CE-SANCTIONS-FRACHT-20261009; CE "
            "/api/v1/compliance/sanctions/actions/pruefen/customers; kein Auto-Freigeben."
        ),
    },
    "mask:auswertungen/sanktionspruefung-personal:check": {
        "mcp_tool_id": "compliance.sanctions.check",
        "coverage": "mapped",
        "notes": (
            "MCP-MASK-CE-SANCTIONS-FRACHT-20261009; CE "
            "/api/v1/compliance/sanctions/actions/pruefen/personal; kein Auto-Freigeben."
        ),
    },
    "mask:logistik/frachttabellen:anlegen": {
        "mcp_tool_id": "logistik.frachttabelle.anlegen",
        "coverage": "mapped",
        "notes": (
            "MCP-MASK-CE-SANCTIONS-FRACHT-20261009; CE "
            "/api/v1/logistik/frachttabellen/actions/anlegen; Token-Mandant."
        ),
    },
    "mask:auswertungen/bonus-berechnung:calculate": {
        "mcp_tool_id": "reporting.bonus.calculate",
        "coverage": "mapped",
        "notes": (
            "MCP-MASK-CE-BATCH2-20261009; CE "
            "/api/v1/l3-report-catalog/bonus-runs/actions/calculate; L3ReportCatalogService."
        ),
    },
    "mask:auswertungen/abfrage-center:import": {
        "mcp_tool_id": "reporting.query.import_signed",
        "coverage": "mapped",
        "notes": (
            "MCP-MASK-CE-BATCH2-20261009; CE "
            "/api/v1/query-center/actions/import; signierter Import."
        ),
    },
    "mask:logistik/tourenplanung:anlegen": {
        "mcp_tool_id": "logistik.tour.anlegen",
        "coverage": "mapped",
        "notes": (
            "MCP-MASK-CE-BATCH2-20261009; CE "
            "/api/v1/logistik/tours/actions/anlegen; Token-Mandant."
        ),
    },
    "mask:einkauf/purchase-order:speichern": {
        "mcp_tool_id": "einkauf.bestellung.speichern",
        "coverage": "mapped",
        "notes": (
            "MCP-MASK-CE-BATCH2-20261009; CE "
            "/api/v1/einkauf/bestellungen/{entity_id}/actions/speichern; "
            "Kopf-Felder ohne Status/Summen; Token-Mandant."
        ),
    },
    "mask:personal/bewerbungen:speichern": {
        "mcp_tool_id": "hr.bewerbung.speichern",
        "coverage": "mapped",
        "notes": (
            "MCP-MASK-CE-BATCH3-20261009; CE "
            "/api/v1/personal/applications/actions/speichern; Token-Mandant."
        ),
    },
    "mask:personal/einwilligungserklaerungen:anlegen": {
        "mcp_tool_id": "hr.einwilligung.anlegen",
        "coverage": "mapped",
        "notes": (
            "MCP-MASK-CE-BATCH3-20261009; CE "
            "/api/v1/personal/applications/einwilligungserklaerungen/actions/anlegen; "
            "Token-Mandant."
        ),
    },
    "mask:admin/postfaecher:speichern": {
        "mcp_tool_id": "admin.postfach.speichern",
        "coverage": "mapped",
        "notes": (
            "MCP-MASK-CE-BATCH3-20261009; CE "
            "/api/v1/admin/postfaecher/actions/speichern; Token-Mandant; "
            "Passwort nicht im Audit."
        ),
    },
    "mask:personal/onboarding:speichern": {
        "mcp_tool_id": "hr.onboarding.speichern",
        "coverage": "mapped",
        "notes": (
            "MCP-MASK-CE-BATCH4-20261009; CE "
            "/api/v1/training/onboarding/runs/actions/speichern; Token-Mandant; "
            "Checkliste tenant-gebunden."
        ),
    },
    "mask:personal/qualifikationen:speichern": {
        "mcp_tool_id": "hr.qualifikation.speichern",
        "coverage": "mapped",
        "notes": (
            "MCP-MASK-CE-BATCH4-20261009; CE "
            "/api/v1/training/qualifications/actions/speichern; Token-Mandant."
        ),
    },
    "mask:personal/schulungen:speichern": {
        "mcp_tool_id": "hr.schulung.speichern",
        "coverage": "mapped",
        "notes": (
            "MCP-MASK-CE-BATCH4-20261009; CE "
            "/api/v1/training/assignments/actions/speichern; Token-Mandant; "
            "Kurs tenant-gebunden."
        ),
    },
}

# Verified UI-only actions; "neu" alone never proves absence of a mutation.
# The inventory retains these entries, but excludes them from mutation counts.
LOCAL_UI_RULES: dict[str, dict[str, str]] = {
    **{
        f"mask:{screen}:neu": {
            "coverage": "local_ui",
            "local_effect": "form_reset",
            "notes": "Neues Formular: setzt ausschliesslich lokale Eingabefelder zurueck. Speichern bleibt separater Fachcommand; kein HTTP-Mutationsendpoint fuer Reset erforderlich.",
        }
        for screen in (
            "personal/bewerbungen",
            "personal/einwilligungserklaerungen",
            "personal/onboarding",
            "personal/qualifikationen",
            "personal/schulungen",
            "fuhrpark/ausgehende-dokumente",
            "fuhrpark/rechnungen",
            "fuhrpark/terminarten",
        )
    },
    "mask:fuhrpark/fahrzeuge:neu": {
        "coverage": "local_ui",
        "local_effect": "navigation",
        "notes": "Oeffnet /fuhrpark/fahrzeug/neu; legt kein Fahrzeug an. Der separate Speichervorgang braucht seinen Fachvertrag.",
    },
    "mask:transporte/fahrer:neu": {
        "coverage": "local_ui",
        "local_effect": "navigation",
        "notes": "Oeffnet /transporte/fahrer/neu; legt keinen Fahrer an. Der separate Speichervorgang braucht seinen Fachvertrag.",
    },
    "mask:logistik/verladung:neu": {
        "coverage": "local_ui",
        "local_effect": "navigation",
        "notes": (
            "SD navigationRoute /verladung/lkw-beladung; legt keine Beladung an. "
            "MCP-MASK-CE-SANCTIONS-FRACHT-20261009."
        ),
    },
    "mask:einkauf/supplier:neue_bestellung": {
        "coverage": "local_ui",
        "local_effect": "navigation",
        "notes": (
            "SD navigationRoute /einkauf/bestellungen/neu; legt keine Bestellung an. "
            "MCP-MASK-CE-BATCH2-20261009."
        ),
    },
    "mask:admin/postfaecher:neu": {
        "coverage": "local_ui",
        "local_effect": "form_reset",
        "notes": (
            "SD stubReason: leert Eingabe fuer neues Postfach; kein HTTP-Mutation. "
            "MCP-MASK-CE-BATCH2-20261009. Speichern bleibt blocked (Postfach-WIP)."
        ),
    },
}

BLOCKED_RULES: dict[str, dict[str, str]] = {
    "mask:finance/payment-run:freigeben": {
        "coverage": "open_high",
        "notes": "Zahlauf-Freigabe HIGH; nahe Journal/Kasse — ADR-076-Umfeld; forbiddenForAgents.",
    },
    # Fuhrpark: REST vorhanden, aber ohne tenant_id — kein MCP-Write bis Folge-Claim.
    **{
        mid: {
            "coverage": "blocked_missing_tenant",
            "notes": (
                "blocked_missing_tenant: Fuhrpark-Repository ohne tenant_id-Spalte/"
                "Token-Filter. Folge-Claim: additive tenant_id + Mandanten-SQL, "
                "dann CE+MCP. Kein Write ohne Isolation. MCP-MASK-CE-BATCH4-20261009."
            ),
        }
        for mid in (
            "mask:fuhrpark/ausgehende-dokumente:speichern",
            "mask:fuhrpark/fahrzeug-stamm:loeschen",
            "mask:fuhrpark/fahrzeug-stamm:speichern",
            "mask:fuhrpark/rechnungen:speichern",
            "mask:fuhrpark/terminarten:speichern",
        )
    },
}

HIGH_DOMAINS = frozenset({"finance", "fibu"})
MCP_NATIVE_WRITES = (
    {
        "mcp_tool_id": "crm.contact.log",
        "mask_action_id": None,
        "coverage": "mcp_native",
        "notes": "Kein mask:* Eintrag; MCP-Write ohne Mask-ID-Parität.",
    },
    {
        "mcp_tool_id": "sales.invoice.propose",
        "mask_action_id": None,
        "coverage": "mcp_native",
        "notes": "Belegkette MCP; keine 1:1-Mask-Action create-invoice in Katalog.",
    },
    {
        "mcp_tool_id": "sales.invoice.post",
        "mask_action_id": None,
        "coverage": "mcp_native",
        "notes": "Post nur nach approved Proposal; kein Mask-ID.",
    },
    {
        "mcp_tool_id": "finance.ap_invoice.propose",
        "mask_action_id": None,
        "coverage": "mcp_native",
        "notes": "AP-Freigabe-Vorschlag; Freigeben ist mask:finance/ap-invoice:freigeben.",
    },
)

FIN_CLOSE = {
    "status": "blocked_adr_076",
    "adr": "docs/adr/adr-076-cash-close-retirement.md",
    "http": "POST finance/cash/close-day → 409, kein Journal-DML",
    "mcp_tool_id": None,
    "notes": (
        "FIN-CLOSE absichtlich nicht als MCP-Tool. Kein Adapter, kein Scheinabschluss. "
        "Bleibt offener Fachvertrag ausserhalb Mask-Write-Parität."
    ),
}


def _load_json(path: Path) -> Any:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _is_mutation(action: dict[str, Any]) -> bool:
    key = str(action.get("source", {}).get("actionKey") or "")
    return bool(MUT_KEY.search(key))


def build_map() -> dict[str, Any]:
    catalog = _load_json(ACTIONS_PATH)
    actions = catalog["actions"]
    tools = yaml.safe_load(TOOLS_PATH.read_text(encoding="utf-8"))["tools"]
    write_tools = [
        t["tool_id"]
        for t in tools
        if "write" in str(t.get("scope", "")) or t.get("audit") == "write"
    ]
    read_tools = [t["tool_id"] for t in tools if t["tool_id"] not in write_tools]

    by_id = {a["id"]: a for a in actions}
    include_ids = {
        a["id"]
        for a in actions
        if _is_mutation(a) or a["id"] in MAPPED_RULES or a["id"] in BLOCKED_RULES or a["id"] in LOCAL_UI_RULES
    }
    mappings: list[dict[str, Any]] = []
    for mid in sorted(include_ids):
        action = by_id[mid]
        domain = str(action.get("domain") or "")
        src = action.get("source") or {}
        entry: dict[str, Any] = {
            "mask_action_id": mid,
            "mask": action.get("mask"),
            "domain": domain,
            "action_key": src.get("actionKey"),
            "label": action.get("label"),
            "command_endpoint": src.get("commandEndpoint"),
            "command": src.get("command"),
        }
        if mid in LOCAL_UI_RULES:
            if src.get("commandEndpoint"):
                raise ValueError(f"Local UI action {mid} gained a commandEndpoint; review its business classification")
            entry.update(LOCAL_UI_RULES[mid])
            entry["mcp_tool_id"] = None
        elif mid in MAPPED_RULES:
            entry.update(MAPPED_RULES[mid])
        elif mid in BLOCKED_RULES:
            entry.update(BLOCKED_RULES[mid])
            entry["mcp_tool_id"] = None
        elif domain in HIGH_DOMAINS:
            entry["mcp_tool_id"] = None
            entry["coverage"] = "open_high"
            entry["notes"] = "Finance/HIGH — bewusst ohne MCP-Write."
        else:
            entry["mcp_tool_id"] = None
            entry["coverage"] = "open_medium"
            entry["notes"] = (
                "Mutation mit Ausführungspfad in Mask-Katalog; noch kein MCP-Write-Adapter."
            )
        mappings.append(entry)

    by_cov = Counter(m["coverage"] for m in mappings)
    return {
        "schema_version": "1.0",
        "slice_id": "MCP-MASK-WRITE-PARITY-20261008",
        "generated_on": date.today().isoformat(),
        "sources": {
            "screen_mask_actions": str(ACTIONS_PATH.relative_to(ROOT)).replace("\\", "/"),
            "mcp_erp_tools": str(TOOLS_PATH.relative_to(ROOT)).replace("\\", "/"),
            "action_stats": catalog.get("stats"),
        },
        "mcp_write_tools": write_tools,
        "mcp_read_tools_count": len(read_tools),
        "mcp_native_writes": list(MCP_NATIVE_WRITES),
        "fin_close": FIN_CLOSE,
        "stats": {
            "mask_actions_considered": len(mappings),
            "mask_mutations_considered": len(mappings) - by_cov.get("local_ui", 0),
            "by_coverage": dict(sorted(by_cov.items())),
        },
        "mappings": mappings,
        "next_medium_candidates": [],
        "classification_complete": True,
        "classification_notes": (
            "MCP-MASK-CE-BATCH4-20261009: Personal onboarding/qualifikationen/schulungen "
            "mapped (Training-REST+Mandant); Fuhrpark blocked_missing_tenant "
            f"{by_cov.get('blocked_missing_tenant', 0)} (keine tenant_id). "
            f"Rest: open_high nur Zahlauf; blocked_no_endpoint {by_cov.get('blocked_no_endpoint', 0)}; "
            f"local_ui {by_cov.get('local_ui', 0)}; FIN-CLOSE blocked_adr_076."
        ),
    }


def dump_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=100,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if committed map drifts")
    args = parser.parse_args()
    data = build_map()
    text = dump_yaml(data)
    if args.check:
        if not OUT_PATH.exists():
            print(f"MISSING {OUT_PATH}", file=sys.stderr)
            return 1
        cur = yaml.safe_load(OUT_PATH.read_text(encoding="utf-8"))
        new = yaml.safe_load(text)
        cur.pop("generated_on", None)
        new.pop("generated_on", None)
        if cur != new:
            print("DRIFT: config/mcp_mask_action_map.yaml outdated", file=sys.stderr)
            return 1
        print(f"OK {OUT_PATH.relative_to(ROOT)} ({data['stats']})")
        return 0
    OUT_PATH.write_text(text, encoding="utf-8")
    print(f"Wrote {OUT_PATH.relative_to(ROOT)} stats={data['stats']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
