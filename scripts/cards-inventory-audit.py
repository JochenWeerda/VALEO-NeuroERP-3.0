#!/usr/bin/env python3
"""Inventarisiert docs/cards, Workflow-Ketten und schreibt interne Reports."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS_DIR = ROOT / "docs" / "cards"
OUT_MD = ROOT / "docs" / "_internal" / "cards-inventory.md"
OUT_JSON = ROOT / "docs" / "_internal" / "cards-inventory.json"

# Kanonische Zuordnung Card-Stamm → Kette (Fallback wenn kein YAML-Frontmatter).
# Siehe docs/_internal/workflow-chains.md
CHAIN_REGISTRY: dict[str, dict] = {
    # harvest-to-settlement
    "VK-010-ernte-annahme": {"chain": "harvest-to-settlement", "chain_step": 0, "card_type": "overview"},
    "VK-010-ernte-annahme-standardmaske": {"chain": "harvest-to-settlement", "chain_step": 1, "card_type": "process-step", "parent_card": "VK-010"},
    "VK-011-qp-handover-und-lkw-validierung": {"chain": "harvest-to-settlement", "chain_step": 2, "card_type": "process-step"},
    "VK-012-annahme-abrechnung": {"chain": "harvest-to-settlement", "chain_step": 7, "card_type": "process-step"},
    "VK-013-kampagnenabschluss": {"chain": "harvest-to-settlement", "chain_step": 8, "card_type": "process-step"},
    "VK-014-settlement-kampagnenreferenz": {"chain": "harvest-to-settlement", "chain_step": 9, "card_type": "process-step"},
    "VK-015-settlement-kampagnen-backfill": {"chain": "harvest-to-settlement", "chain_step": 10, "card_type": "process-step"},
    "VK-016-queue-cta-und-artikel-api": {"chain": "harvest-to-settlement", "chain_step": 3, "card_type": "process-step"},
    "VK-017-queue-article-id": {"chain": "harvest-to-settlement", "chain_step": 4, "card_type": "process-step"},
    "VK-018-klaerungsprozess-gesperrt": {"chain": "harvest-to-settlement", "chain_step": 6, "card_type": "process-step"},
    "VK-019-queue-repair-article-id": {"chain": "harvest-to-settlement", "chain_step": 5, "card_type": "process-step"},
    "VK-020-rohware-wizard-schrittvalidierung": {"chain": "harvest-to-settlement", "chain_step": 11, "card_type": "process-step"},
    # order-to-cash
    "OTC-010-order-to-cash": {"chain": "order-to-cash", "chain_step": 0, "card_type": "overview"},
    "OTC-011-zahlungseingang-und-abstimmung": {"chain": "order-to-cash", "chain_step": 1, "card_type": "process-step", "parent_card": "OTC-010"},
    # procure-to-pay
    "P2P-020-direktbestellung-standardmaske": {"chain": "procure-to-pay", "chain_step": 1, "card_type": "process-step"},
    "P2P-040-vorbelegung-standardmaske": {"chain": "procure-to-pay", "chain_step": 2, "card_type": "process-step"},
    "P2P-041-vorbelegung-aus-anfrage-und-vertrag": {"chain": "procure-to-pay", "chain_step": 3, "card_type": "process-step"},
    "P2P-050-wizard-schrittvalidierung": {"chain": "procure-to-pay", "chain_step": None, "card_type": "cross-cutting"},
    # finance
    "FIN-001-finance-to-close": {"chain": "finance-to-close", "chain_step": 0, "card_type": "overview"},
    "FIN-001-finance-to-reporting": {"chain": "finance-to-close", "chain_step": 0, "card_type": "overview"},
    # other lanes
    "INV-001-inventory-to-settlement": {"chain": "inventory-to-settlement", "chain_step": 0, "card_type": "overview"},
    "CTS-001-contract-to-settlement": {"chain": "contract-to-settlement", "chain_step": 0, "card_type": "overview"},
    "CTS-009-rohwaren-positionsmonitor": {"chain": "contract-to-settlement", "chain_step": 1, "card_type": "process-step"},
    "REK-001-complaint-to-resolution": {"chain": "complaint-to-resolution", "chain_step": 0, "card_type": "overview"},
    "CMP-001-compliance-to-report": {"chain": "compliance-to-report", "chain_step": 0, "card_type": "overview"},
    "COM-001-compliance-to-audit": {"chain": "compliance-to-report", "chain_step": 0, "card_type": "overview"},
    "SVC-001-service-to-customer": {"chain": "service-to-customer", "chain_step": 0, "card_type": "overview"},
    "CRM-001-crm-to-revenue": {"chain": None, "related_chain": "order-to-cash", "card_type": "overview"},
    # domain deepening (no E2E chain)
    "DOM-CRM-003-fall-und-ownership": {"chain": None, "card_type": "cross-cutting", "domain": "crm"},
    "DOM-DOC-003-nachweis-und-rueckmeldung": {"chain": None, "card_type": "cross-cutting", "domain": "doc"},
    "DOM-FIN-003-fibu-operatorparitaet": {"chain": None, "card_type": "cross-cutting", "domain": "finance"},
    "DOM-CON-003-fixierung-markt-mahnung": {"chain": None, "card_type": "cross-cutting", "domain": "contracts"},
    "DOM-PROC-003-beschaffungsausnahmen": {"chain": None, "card_type": "cross-cutting", "domain": "procurement"},
    "DOM-SUPPLY-003-physische-kette": {"chain": None, "card_type": "cross-cutting", "domain": "supply"},
}

CROSS_CUTTING_PREFIXES = ("SEC-", "NC-", "INT-SG-")

STATUS_PATTERNS = [
    re.compile(r"\*\*Status:\*\*\s*([^\n|]+)"),
    re.compile(r"^\s*-\s*Status:\s*(.+)$", re.M),
    re.compile(r"\|\s*\*\*Status\*\*\s*\|\s*([^|]+?)\s*\|"),
    re.compile(r"^\s*-\s*\*\*Stand:\*\*\s*(abgeschlossen|umgesetzt|erledigt)[^\n]*", re.M | re.I),
]

CLOSED_KEYWORDS = ("abgeschlossen", "umgesetzt", "erledigt", "done", "complete")
OPEN_KEYWORDS = ("in arbeit", "teilweise", "offen", "geplant", "blockiert")


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip()
    data: dict = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key in ("chain_step",):
            try:
                data[key] = int(val) if val and val.lower() != "null" else None
            except ValueError:
                data[key] = val
        elif key == "related_cards":
            data[key] = [x.strip() for x in val.strip("[]").split(",") if x.strip()]
        else:
            data[key] = None if val.lower() == "null" else val
    return data


def extract_status(text: str) -> str | None:
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            body = text[end + 4 :]
    for pat in STATUS_PATTERNS:
        m = pat.search(body)
        if m:
            val = m.group(1).strip()
            if val.lower() in ("abgeschlossen", "umgesetzt", "erledigt"):
                return val.lower()
            return val
    return None


def is_closed(status: str | None) -> bool:
    if not status:
        return False
    low = status.lower()
    if any(k in low for k in OPEN_KEYWORDS):
        return False
    return any(k in low for k in CLOSED_KEYWORDS)


def has_open_section(text: str) -> list[str]:
    found: list[str] = []
    for sec in ("Offene Gaps", "Offene Punkte", "Offene Folgearbeit", "Fehlende Umsetzung"):
        m = re.search(rf"(?:^|\n)(?:##\s*)?{re.escape(sec)}[^\n]*\n([\s\S]*?)(?=\n## |\Z)", text)
        if not m:
            continue
        body = m.group(1).strip()
        if not body or body in ("-", "—", "keine", "keine."):
            continue
        lines = [
            ln
            for ln in body.splitlines()
            if ln.strip()
            and not ln.strip().startswith("~~")
            and "**behoben**" not in ln
            and "erledigt" not in ln.lower()
            and not re.match(r"^\|\s*~~", ln)
        ]
        if lines:
            found.append(sec)
    return found


def resolve_chain(card_id: str, fm: dict) -> dict:
    merged = dict(CHAIN_REGISTRY.get(card_id, {}))
    merged.update({k: v for k, v in fm.items() if v is not None and k != "title"})
    if not merged.get("chain") and not merged.get("related_chain"):
        if card_id.startswith(CROSS_CUTTING_PREFIXES):
            merged["card_type"] = merged.get("card_type") or "hardening"
            merged["chain"] = None
        elif card_id.startswith("DOM-"):
            merged["card_type"] = merged.get("card_type") or "cross-cutting"
            merged["chain"] = None
    return merged


def main() -> None:
    entries: list[dict] = []
    for path in sorted(CARDS_DIR.rglob("*.md")):
        if path.name in ("card-template.md", "README.md"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(CARDS_DIR).as_posix()
        card_id = path.stem
        fm = parse_frontmatter(text)
        chain_meta = resolve_chain(card_id, fm)
        status = extract_status(text)
        closed = is_closed(status)
        open_secs = has_open_section(text)
        chain = chain_meta.get("chain") or chain_meta.get("related_chain")
        card_type = chain_meta.get("card_type")
        unassigned = (
            chain is None
            and card_type not in ("hardening", "cross-cutting")
            and not card_id.startswith(CROSS_CUTTING_PREFIXES)
            and not card_id.startswith("DOM-")
        )
        entries.append(
            {
                "id": card_id,
                "file": rel,
                "status": status,
                "closed": closed,
                "open_sections": open_secs,
                "needs_review": (not closed) or bool(open_secs),
                "chain": chain_meta.get("chain"),
                "related_chain": chain_meta.get("related_chain"),
                "chain_step": chain_meta.get("chain_step"),
                "card_type": card_type,
                "unassigned_chain": unassigned,
                "has_frontmatter": bool(fm),
            }
        )

    closed_n = sum(1 for e in entries if e["closed"])
    review_n = sum(1 for e in entries if e["needs_review"])
    unassigned_n = sum(1 for e in entries if e["unassigned_chain"])
    no_fm_process = sum(
        1
        for e in entries
        if not e["has_frontmatter"]
        and e["card_type"] in ("overview", "process-step")
        and (e["chain"] or e["related_chain"])
    )

    by_status: dict[str, int] = {}
    for e in entries:
        key = e["status"] or "(kein Status-Feld)"
        by_status[key] = by_status.get(key, 0) + 1

    by_chain: dict[str, list[str]] = {}
    for e in entries:
        key = e["chain"] or e["related_chain"] or "(querschnitt/plattform)"
        by_chain.setdefault(key, []).append(e["id"])

    today = date.today().isoformat()
    lines = [
        "---",
        "title: Cards-Inventar (intern)",
        "type: reference",
        "audience: [entwickler, product, docs]",
        "owner: Cursor",
        "status: aktiv",
        f"last_reviewed: {today}",
        "version: 3.0.0",
        "---",
        "",
        "# Cards-Inventar (intern)",
        "",
        "Konsolidierter Stand der Workflow-Cards unter `docs/cards/`.",
        "Ketten-Referenz: [`workflow-chains.md`](workflow-chains.md).",
        "",
        f"**Generiert:** {today} via `scripts/cards-inventory-audit.py`",
        "",
        "## Kennzahlen",
        "",
        "| Metrik | Wert |",
        "|--------|------|",
        f"| Cards gesamt | {len(entries)} |",
        f"| Status abgeschlossen/umgesetzt | {closed_n} |",
        f"| Review empfohlen | {review_n} |",
        f"| Ohne Ketten-Zuordnung (Registry) | {unassigned_n} |",
        f"| Prozess-Cards ohne YAML-Frontmatter | {no_fm_process} |",
        "",
        "## Ketten (Card-Anzahl)",
        "",
        "| Kette | Cards |",
        "|-------|-------|",
    ]
    for chain_name, ids in sorted(by_chain.items(), key=lambda x: (-len(x[1]), x[0])):
        lines.append(f"| `{chain_name}` | {len(ids)} |")

    lines.extend(["", "## Status-Verteilung", "", "| Status | Anzahl |", "|--------|--------|"])
    for status, count in sorted(by_status.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| `{status}` | {count} |")

    lines.extend(
        [
            "",
            "## Ohne Ketten-Zuordnung",
            "",
            "Process-Cards ohne Eintrag in `CHAIN_REGISTRY` / Frontmatter `chain`.",
            "",
            "| Card | Typ |",
            "|------|-----|",
        ]
    )
    for e in sorted(entries, key=lambda x: x["id"]):
        if e["unassigned_chain"]:
            lines.append(f"| `{e['id']}` | {e['card_type'] or '?'} |")
    if unassigned_n == 0:
        lines.append("| *(keine)* | — |")

    lines.extend(
        [
            "",
            "## Review-Queue",
            "",
            "| Card | Status | Offene Abschnitte | Kette |",
            "|------|--------|-------------------|-------|",
        ]
    )
    for e in sorted(entries, key=lambda x: x["id"]):
        if not e["needs_review"]:
            continue
        secs = ", ".join(e["open_sections"]) if e["open_sections"] else "—"
        chain = e["chain"] or e["related_chain"] or "—"
        lines.append(f"| `{e['id']}` | {e['status'] or '—'} | {secs} | {chain} |")

    lines.extend(
        [
            "",
            "## Pflege",
            "",
            "- Registry: `docs/_internal/workflow-chains.md` + `CHAIN_REGISTRY` im Script",
            "- Frontmatter-Vorlage: `docs/cards/card-template.md`",
            "- Offene Fixes: `docs/agent-ops/active-workboard.md` (CARD-AUDIT-Follow-up)",
            "",
        ]
    )

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT_JSON.write_text(
        json.dumps({"generated": today, "entries": entries, "by_chain": by_chain}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(entries)} cards -> {OUT_MD.relative_to(ROOT)}")
    print(f"  unassigned_chain={unassigned_n}  review_queue={review_n}")


if __name__ == "__main__":
    main()
