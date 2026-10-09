"""Contract: mcp_mask_action_map stays aligned with generator rules."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_mcp_mask_action_map_check_passes():
    import subprocess
    import sys

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/generate_mcp_mask_action_map.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_mcp_mask_action_map_covers_top_writes_and_blocks_fin_close():
    data = yaml.safe_load((ROOT / "config/mcp_mask_action_map.yaml").read_text(encoding="utf-8"))
    assert "crm.activity.create" in data["mcp_write_tools"]
    assert "crm.contact.log" in data["mcp_write_tools"]
    assert data["fin_close"]["status"] == "blocked_adr_076"
    assert data["fin_close"]["mcp_tool_id"] is None

    by_id = {m["mask_action_id"]: m for m in data["mappings"]}
    assert by_id["mask:crm/customer-360:create_activity"]["mcp_tool_id"] == "crm.activity.create"
    assert by_id["mask:crm/opportunity:create_activity"]["mcp_tool_id"] == "crm.activity.create"
    assert by_id["mask:finance/payment-run:freigeben"]["coverage"] == "open_high"
    assert by_id["mask:finance/ap-invoice:freigeben"]["coverage"] == "mapped"
    assert by_id["mask:finance/ap-invoice:freigeben"]["mcp_tool_id"] == "finance.ap_invoice.freigeben"

    native = {n["mcp_tool_id"] for n in data["mcp_native_writes"]}
    assert native >= {
        "crm.contact.log",
        "sales.invoice.propose",
        "sales.invoice.post",
        "finance.ap_invoice.propose",
    }

    assert by_id["mask:produktion/produktionsleitstand:sync"]["mcp_tool_id"] == "produktion.control.sync"
    assert by_id["mask:planung/kalender:reproject"]["mcp_tool_id"] == "planung.calendar.reproject"
    assert by_id["mask:schnittstelle/mde-inbox:process_pending"]["mcp_tool_id"] == (
        "mobile.sync.process_pending"
    )
    assert by_id["mask:lager/inventur-nebenlaeufe:create_opening"]["coverage"] == (
        "mapped_propose_only"
    )
    assert by_id["mask:lager/inventur-nebenlaeufe:create_opening"]["mcp_tool_id"] == (
        "lager.inventur.propose_opening"
    )
    assert by_id["mask:auswertungen/sanktionspruefung-kunden:check"]["mcp_tool_id"] == (
        "compliance.sanctions.check"
    )
    assert by_id["mask:auswertungen/sanktionspruefung-personal:check"]["mcp_tool_id"] == (
        "compliance.sanctions.check"
    )
    assert by_id["mask:logistik/frachttabellen:anlegen"]["mcp_tool_id"] == (
        "logistik.frachttabelle.anlegen"
    )
    assert by_id["mask:personal/bewerbungen:neu"]["coverage"] == "local_ui"
    assert data.get("classification_complete") is True
    assert data["stats"]["by_coverage"].get("open_medium", 0) == 0
    assert data["stats"]["by_coverage"].get("open_high", 0) == 1
    assert data["stats"]["by_coverage"].get("mapped_propose_only", 0) == 1
    assert by_id["mask:auswertungen/bonus-berechnung:calculate"]["mcp_tool_id"] == (
        "reporting.bonus.calculate"
    )
    assert by_id["mask:auswertungen/abfrage-center:import"]["mcp_tool_id"] == (
        "reporting.query.import_signed"
    )
    assert by_id["mask:einkauf/supplier:neue_bestellung"]["coverage"] == "local_ui"
    assert by_id["mask:admin/postfaecher:neu"]["coverage"] == "local_ui"
    assert by_id["mask:logistik/tourenplanung:anlegen"]["mcp_tool_id"] == "logistik.tour.anlegen"
    assert by_id["mask:einkauf/purchase-order:speichern"]["mcp_tool_id"] == (
        "einkauf.bestellung.speichern"
    )
    assert data["stats"]["by_coverage"].get("mapped", 0) == 41
    assert data["stats"]["by_coverage"].get("blocked_no_endpoint", 0) == 0
    assert data["stats"]["by_coverage"].get("blocked_missing_tenant", 0) == 0
    assert data["stats"]["by_coverage"].get("local_ui", 0) == 13
