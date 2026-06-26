#!/usr/bin/env python3
"""Migrates docs/cards/*.md: prepends YAML frontmatter from CHAIN_REGISTRY."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS_DIR = ROOT / "docs" / "cards"
AUDIT_SCRIPT = ROOT / "scripts" / "cards-inventory-audit.py"

FLOW_SPINE = {
    "harvest-to-settlement": "flow-spine-harvest-to-settlement",
    "order-to-cash": "flow-spine-order-to-cash",
    "procure-to-pay": "flow-spine-procure-to-pay",
    "finance-to-close": "flow-spine-finance-to-close",
    "inventory-to-settlement": "flow-spine-inventory-to-settlement",
    "contract-to-settlement": "flow-spine-contract-to-settlement",
    "complaint-to-resolution": "flow-spine-complaint-to-resolution",
    "compliance-to-report": "flow-spine-compliance-to-report",
    "service-to-customer": "flow-spine-service-to-customer",
}


def load_chain_registry() -> dict:
    spec = importlib.util.spec_from_file_location("cards_inventory_audit", AUDIT_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.CHAIN_REGISTRY


def card_id_from_stem(stem: str) -> str:
    parts = stem.split("-", 2)
    if len(parts) >= 2 and parts[1].isdigit():
        return f"{parts[0]}-{parts[1]}"
    return stem


def guess_workflow_doc(stem: str) -> str | None:
    wf_dir = ROOT / "docs" / "workflows"
    slug = stem.lower()
    exact = wf_dir / f"{slug}.md"
    if exact.exists():
        return f"docs/workflows/{exact.name}"
    prefix = "-".join(stem.split("-")[:2]).lower()
    matches = sorted(wf_dir.glob(f"{prefix}*.md"))
    if matches:
        return f"docs/workflows/{matches[0].name}"
    if stem.startswith("P2P-"):
        p2p = wf_dir / "p2p-001-procure-to-pay-direktbestellung.md"
        if p2p.exists():
            return f"docs/workflows/{p2p.name}"
    if stem.startswith("DOM-"):
        dom = wf_dir / f"{slug}.md"
        if dom.exists():
            return f"docs/workflows/{dom.name}"
    return None


def has_frontmatter(text: str) -> bool:
    if not text.startswith("---"):
        return False
    end = text.find("\n---", 3)
    if end == -1:
        return False
    block = text[3:end]
    return "card_id:" in block or "chain:" in block


def build_frontmatter(stem: str, meta: dict) -> str:
    cid = card_id_from_stem(stem)
    lines = ["---", f"card_id: {cid}"]

    chain = meta.get("chain")
    if chain is not None:
        lines.append(f"chain: {chain}")
    elif meta.get("related_chain"):
        lines.append("chain: null")
        lines.append(f"related_chain: {meta['related_chain']}")

    step = meta.get("chain_step")
    if step is not None:
        lines.append(f"chain_step: {step}")
    elif meta.get("card_type") == "cross-cutting":
        lines.append("chain_step: null")

    lines.append(f"card_type: {meta.get('card_type', 'process-step')}")

    if meta.get("parent_card"):
        lines.append(f"parent_card: {meta['parent_card']}")
    if meta.get("domain"):
        lines.append(f"domain: {meta['domain']}")

    if chain and chain in FLOW_SPINE:
        lines.append(f"flow_spine: {FLOW_SPINE[chain]}")

    wf = guess_workflow_doc(stem)
    if wf:
        lines.append(f"workflow_doc: {wf}")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def find_card_path(stem: str) -> Path | None:
    matches = list(CARDS_DIR.rglob(f"{stem}.md"))
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]
    return sorted(matches, key=lambda p: len(str(p)))[0]


def migrate(*, dry_run: bool = False) -> tuple[int, int, int]:
    registry = load_chain_registry()
    updated = skipped = missing = 0

    for stem, meta in sorted(registry.items()):
        path = find_card_path(stem)
        if not path:
            print(f"  MISSING file for {stem}")
            missing += 1
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if has_frontmatter(text):
            skipped += 1
            continue
        block = build_frontmatter(stem, meta)
        new_text = block + text.lstrip("\n")
        if dry_run:
            print(f"  WOULD migrate {path.relative_to(ROOT)}")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"  migrated {path.relative_to(ROOT)}")
        updated += 1

    return updated, skipped, missing


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    print(f"migrate-cards-frontmatter {'(dry-run)' if dry_run else ''}")
    updated, skipped, missing = migrate(dry_run=dry_run)
    print(f"done: updated={updated} skipped={skipped} missing={missing}")


if __name__ == "__main__":
    main()
