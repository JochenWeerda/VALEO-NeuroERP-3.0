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
}

BLOCKED_RULES: dict[str, dict[str, str]] = {
    "mask:finance/payment-run:freigeben": {
        "coverage": "open_high",
        "notes": "Zahlauf-Freigabe HIGH; nahe Journal/Kasse — ADR-076-Umfeld; forbiddenForAgents.",
    },
    # Restliche medium ohne HTTP-CommandEndpoint: nur ActionRuntime-Command-Namen
    # oder Human-Input-Flow ohne kanonischen MCP-Write-Vertrag — nicht fingieren.
    **{
        mid: {
            "coverage": "blocked_no_endpoint",
            "notes": (
                "Kein HTTP-CommandEndpoint mit Mandanten-Service-Vertrag; "
                "nur ActionRuntime-Command oder UI-Flow — MCP-MASK-WRITES-REMAINING-20261008."
            ),
        }
        for mid in (
            "mask:admin/postfaecher:neu",
            "mask:admin/postfaecher:speichern",
            "mask:auswertungen/abfrage-center:import",
            "mask:auswertungen/bonus-berechnung:calculate",
            "mask:auswertungen/sanktionspruefung-kunden:check",
            "mask:auswertungen/sanktionspruefung-personal:check",
            "mask:einkauf/purchase-order:speichern",
            "mask:einkauf/supplier:neue_bestellung",
            "mask:fuhrpark/ausgehende-dokumente:neu",
            "mask:fuhrpark/ausgehende-dokumente:speichern",
            "mask:fuhrpark/fahrzeug-stamm:loeschen",
            "mask:fuhrpark/fahrzeug-stamm:speichern",
            "mask:fuhrpark/fahrzeuge:neu",
            "mask:fuhrpark/rechnungen:neu",
            "mask:fuhrpark/rechnungen:speichern",
            "mask:fuhrpark/terminarten:neu",
            "mask:fuhrpark/terminarten:speichern",
            "mask:logistik/frachttabellen:anlegen",
            "mask:logistik/tourenplanung:anlegen",
            "mask:logistik/verladung:neu",
            "mask:personal/bewerbungen:neu",
            "mask:personal/bewerbungen:speichern",
            "mask:personal/einwilligungserklaerungen:anlegen",
            "mask:personal/einwilligungserklaerungen:neu",
            "mask:personal/onboarding:neu",
            "mask:personal/onboarding:speichern",
            "mask:personal/qualifikationen:neu",
            "mask:personal/qualifikationen:speichern",
            "mask:personal/schulungen:neu",
            "mask:personal/schulungen:speichern",
            "mask:transporte/fahrer:neu",
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
        if _is_mutation(a) or a["id"] in MAPPED_RULES or a["id"] in BLOCKED_RULES
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
        if mid in MAPPED_RULES:
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
            "mask_mutations_considered": len(mappings),
            "by_coverage": dict(sorted(by_cov.items())),
        },
        "mappings": mappings,
        "next_medium_candidates": [],
        "classification_complete": True,
        "classification_notes": (
            "MCP-INVENTUR-OPENING-PROPOSE-20261008: Inventur-Opening mapped_propose_only. "
            "Rest: open_high nur Zahlauf; blocked_no_endpoint 31; FIN-CLOSE blocked_adr_076."
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
