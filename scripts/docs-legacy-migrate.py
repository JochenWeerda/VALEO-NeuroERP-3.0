#!/usr/bin/env python3
"""
Legacy-Doku-Migration: inventarisieren, Duplikate erkennen, per git mv archivieren.

Ziel: Altbestände nach docs/_internal/archive/ konsolidieren (nichts löschen).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ARCHIVE = DOCS / "_internal" / "archive"
INVENTORY_MD = DOCS / "_internal" / "legacy-docs-inventory.md"
INVENTORY_JSON = DOCS / "_internal" / "legacy-docs-inventory.json"

# Inhaltliche Card-Duplikate: Schlüssel = Duplikat, Wert = kanonischer Pfad.
CARD_DUPLICATE_CANONICAL: dict[str, str] = {
    "docs/cards/inventory/INV-001-inventory-to-settlement.md": (
        "docs/cards/lager/INV-001-inventory-to-settlement.md"
    ),
}

CARD_STUB_TEMPLATE = """\
---
card_id: {card_id}
canonical: {canonical}
status: redirect-stub
---

# {card_id} — Weiterleitung

Kanonische Card: [{card_id}](../lager/{basename})

Das Duplikat unter `docs/cards/inventory/` wurde nach
`docs/_internal/archive/cards-duplicates/` archiviert ({date}).
"""

# Kuratierte Bereiche — nicht verschieben.
KEEP_PREFIXES = (
    "docs/index.md",
    "docs/MASKEN.md",
    "docs/benutzerhandbuch/",
    "docs/admin/",
    "docs/entwickler/",
    "docs/schnittstellen/",
    "docs/agent-docs/",
    "docs/compliance/",
    "docs/referenz/",
    "docs/dokumentation/",
    "docs/agent-ops/",
    "docs/project-context/",
    "docs/workflows/",
    "docs/cards/",
    "docs/architecture/",
    "docs/adr/",
    "docs/runbooks/",
    "docs/roadmap/README.md",
    "docs/quality-assurance/",
    "docs/_internal/",
)

ARCHIVE_PATTERNS = [
    (re.compile(r"(?i)complete|completion|abgeschlossen"), "completion-reports"),
    (re.compile(r"(?i)summary|zusammenfassung|bericht$|report$"), "summaries"),
    (re.compile(r"(?i)debugging|root-cause|-fix\.|fixed|bugs-fixed"), "debug-fix"),
    (re.compile(r"(?i)uat|test-protokoll|test-ergebnis|test-results"), "uat-test"),
    (re.compile(r"(?i)^dom-[a-z]+-004-"), "dom-slice-snapshots"),
    (re.compile(r"(?i)^ernte-annahme-|^harvest-acceptance-"), "agrar-ernte"),
    (re.compile(r"(?i)^lieferschein-"), "verkauf-lieferschein"),
    (re.compile(r"(?i)^gap-|^GAP-"), "gap-analysis"),
    (re.compile(r"(?i)^i18n-"), "i18n-legacy"),
    (re.compile(r"(?i)^crm-|^crm_"), "crm-legacy"),
    (re.compile(r"(?i)^dom-"), "dom-legacy"),
    (re.compile(r"(?i)^PHASE-"), "phase-reports"),
    (re.compile(r"(?i)PROJEKT|PRODUCTION|RELEASE_NOTES|TODO-STATUS|GESAMTSTAND"), "project-status"),
]

BULK_ARCHIVE_DIRS = (
    "docs/archive",  # legacy repo archive → konsolidieren
    "docs/wiki",
    "docs/user",
    "docs/analysis",
    "docs/uat",
    "docs/testing",
    "docs/deployment",
    "docs/design",
    "docs/specs",
    "docs/valeo-reference",
    "docs/hrm-go-live-templates",
    "docs/migration",
    "docs/data",
    "docs/db",
    "docs/config",
    "docs/perf",
    "docs/policies",
    "docs/quality",
    "docs/setup",
    "docs/screenshots",
    "docs/standards",
    "docs/integrations",
    "docs/operations",
    "docs/operations",
    "docs/api",
)


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def should_keep(path: Path) -> bool:
    r = rel(path)
    if r in ("docs/index.md", "docs/MASKEN.md"):
        return True
    return any(r.startswith(k.rstrip("/") + "/") or r == k.rstrip("/") for k in KEEP_PREFIXES if k.endswith("/")) or r in KEEP_PREFIXES


def classify(path: Path) -> str:
    name = path.name
    for pat, bucket in ARCHIVE_PATTERNS:
        if pat.search(name):
            return bucket
    if path.parent == DOCS:
        return "root-misc"
    return "misc-legacy"


def is_tracked(path: Path) -> bool:
    r = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path)],
        cwd=ROOT,
        capture_output=True,
    )
    return r.returncode == 0


def git_mv(src: Path, dst: Path, dry_run: bool) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        stem, suffix = dst.stem, dst.suffix
        n = 2
        while dst.exists():
            dst = dst.with_name(f"{stem}__dup{n}{suffix}")
            n += 1
    if dry_run:
        mode = "git mv" if is_tracked(src) else "mv+git add"
        print(f"  WOULD ({mode}): {rel(src)} -> {rel(dst)}")
        return
    if is_tracked(src):
        subprocess.run(["git", "mv", str(src), str(dst)], check=True, cwd=ROOT)
    else:
        shutil.move(str(src), str(dst))
        subprocess.run(["git", "add", str(dst)], check=True, cwd=ROOT)
        # Entferne ggf. früher getrackten Pfad aus dem Index
        subprocess.run(["git", "rm", "--cached", "-f", str(src)], cwd=ROOT, capture_output=True)


def collect_md_files() -> list[Path]:
    files: list[Path] = []
    for p in DOCS.rglob("*.md"):
        if "_internal/archive" in p.as_posix().replace("\\", "/"):
            continue
        files.append(p)
    return sorted(files)


def build_inventory(files: list[Path]) -> dict:
    by_name: dict[str, list[str]] = defaultdict(list)
    to_archive: list[dict] = []
    kept: list[str] = []
    seen_resolved: set[str] = set()

    for p in files:
        resolved = str(p.resolve())
        if resolved in seen_resolved:
            continue
        seen_resolved.add(resolved)
        r = rel(p)
        # Archiv-Kopien und Card-Redirect-Stubs nicht als Duplikat zählen.
        if "_internal/archive/" in r or "status: redirect-stub" in p.read_text(encoding="utf-8", errors="ignore")[:400]:
            pass
        else:
            by_name[p.name.lower()].append(r)
        if should_keep(p):
            kept.append(r)
            continue
        parent_rel = rel(p.parent)
        if parent_rel in BULK_ARCHIVE_DIRS:
            bucket = "repo-archive" if parent_rel == "docs/archive" else parent_rel.replace("docs/", "").replace("/", "-")
            to_archive.append({"from": r, "bucket": bucket, "reason": "bulk-dir"})
        elif p.parent == DOCS:
            to_archive.append({"from": r, "bucket": classify(p), "reason": "root-loose"})
        elif classify(p) != "misc-legacy":
            to_archive.append({"from": r, "bucket": classify(p), "reason": "pattern"})

    duplicates = {k: v for k, v in by_name.items() if len(v) > 1}
    return {
        "generated": date.today().isoformat(),
        "total_md": len(seen_resolved),
        "keep_count": len(kept),
        "archive_candidates": to_archive,
        "duplicate_basenames": duplicates,
        "card_duplicates_resolved": list(CARD_DUPLICATE_CANONICAL.keys()),
    }


def write_inventory(data: dict) -> None:
    lines = [
        "---",
        "title: Legacy-Docs-Inventar (intern)",
        "type: reference",
        "audience: [entwickler, docs]",
        "owner: Cursor",
        "status: aktiv",
        f"last_reviewed: {data['generated']}",
        "version: 1.0.0",
        "---",
        "",
        "# Legacy-Docs-Inventar",
        "",
        f"**Generiert:** {data['generated']} via `scripts/docs-legacy-migrate.py`",
        "",
        "## Kennzahlen",
        "",
        f"| Metrik | Wert |",
        f"|--------|------|",
        f"| Markdown-Dateien gesamt | {data['total_md']} |",
        f"| Kuratiert (behalten) | {data['keep_count']} |",
        f"| Archiv-Kandidaten | {len(data['archive_candidates'])} |",
        f"| Doppelte Dateinamen | {len(data['duplicate_basenames'])} |",
        "",
        "## Archiv-Buckets (Kandidaten)",
        "",
    ]
    buckets: dict[str, int] = defaultdict(int)
    for item in data["archive_candidates"]:
        buckets[item["bucket"]] += 1
    lines.append("| Bucket | Anzahl |")
    lines.append("|--------|--------|")
    for b, c in sorted(buckets.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| `{b}` | {c} |")

    lines.extend(["", "## Doppelte Dateinamen (Top 30)", "", "| Dateiname | Vorkommen |", "|-----------|-----------|"])
    dup_items = sorted(data["duplicate_basenames"].items(), key=lambda x: -len(x[1]))[:30]
    for name, paths in dup_items:
        lines.append(f"| `{name}` | {len(paths)} |")

    lines.extend(
        [
            "",
            "## Card-Duplikate (kanonisch aufgelöst)",
            "",
            "| Duplikat (archiviert) | Kanonisch |",
            "|-----------------------|-----------|",
        ]
    )
    for dup, canon in CARD_DUPLICATE_CANONICAL.items():
        lines.append(f"| `{dup}` | `{canon}` |")

    lines.extend(
        [
            "",
            "## Pflege",
            "",
            "- Migration: `python scripts/docs-legacy-migrate.py --apply`",
            "- Dry-run: `python scripts/docs-legacy-migrate.py --dry-run`",
            "- Card-Dedupe: `python scripts/docs-legacy-migrate.py --dedupe-cards`",
            "- Roadmap-Status: `python scripts/docs-legacy-migrate.py --archive-roadmap-status --apply`",
            "- Roadmap-Purge: `python scripts/docs-legacy-migrate.py --purge-roadmap --apply`",
            "- Ziel: `docs/_internal/archive/` (einheitlich)",
            "",
        ]
    )
    INVENTORY_MD.parent.mkdir(parents=True, exist_ok=True)
    INVENTORY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    INVENTORY_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def apply_migration(data: dict, dry_run: bool) -> int:
    moved = 0
    skipped = 0
    for item in data["archive_candidates"]:
        src = ROOT / item["from"]
        if not src.exists():
            skipped += 1
            continue
        bucket = item["bucket"]
        dst = ARCHIVE / bucket / src.name
        git_mv(src, dst, dry_run)
        moved += 1
    if skipped:
        print(f"  skipped (already moved/missing): {skipped}")
    return moved


def write_consolidation_indexes(data: dict, dry_run: bool) -> None:
    """Kurzindex pro Cluster — verweist auf archivierte Dateien, ersetzt keine Inhalte."""
    clusters = {
        "agrar-ernte": "Ernte-Annahme / Harvest (historische Root- und Summary-Docs)",
        "verkauf-lieferschein": "Lieferschein (historische Analysen, UAT, Fixes)",
        "dom-slice-snapshots": "DOM-004 Slice-Snapshots (datiert 2026-06)",
        "repo-archive": "Ehemals docs/archive/ (Gap-Analysen, Phase-Reports 2024–2025)",
    }
    for bucket, title in clusters.items():
        files = [i["from"] for i in data["archive_candidates"] if i["bucket"] == bucket]
        if not files:
            continue
        idx_path = ARCHIVE / bucket / "README.md"
        if idx_path.exists() and not dry_run:
            continue
        body = [
            f"# {title}",
            "",
            f"Konsolidierter Index ({len(files)} Dateien). Aktive Doku:",
            "",
            "- Agrar: `docs/benutzerhandbuch/`, `docs/workflows/vk-010-*`",
            "- Verkauf: `docs/workflows/otc-010-*`, `docs/benutzerhandbuch/verkauf/`",
            "- DOM-Slices: `docs/agent-ops/slices/`, `docs/project-context/open-gaps-and-known-issues.md`",
            "- Gap/Archiv: `docs/_internal/cards-inventory.md`, Process-Kernel STATUS",
            "",
            "## Archivierte Dateien",
            "",
        ]
        for f in sorted(files):
            name = Path(f).name
            body.append(f"- `{name}` (ehem. `{f}`)")
        content = "\n".join(body) + "\n"
        if dry_run:
            print(f"  WOULD write index {rel(idx_path)} ({len(files)} entries)")
        else:
            idx_path.parent.mkdir(parents=True, exist_ok=True)
            if not idx_path.exists():
                idx_path.write_text(content, encoding="utf-8")


def apply_card_dedupe(dry_run: bool) -> int:
    """Archiviert kanonisch markierte Card-Duplikate und legt Redirect-Stubs an."""
    moved = 0
    archive = ARCHIVE / "cards-duplicates"
    today = date.today().isoformat()

    for dup_rel, canon_rel in CARD_DUPLICATE_CANONICAL.items():
        src = ROOT / dup_rel
        canon = ROOT / canon_rel
        if not canon.exists():
            print(f"  SKIP canonical missing: {canon_rel}")
            continue
        if not src.exists():
            print(f"  SKIP duplicate already resolved: {dup_rel}")
            continue

        dst = archive / src.name
        git_mv(src, dst, dry_run)
        moved += 1

        m = re.match(r"^([A-Z]+-\d+)", src.stem)
        card_id = m.group(1) if m else src.stem
        stub = CARD_STUB_TEMPLATE.format(
            card_id=card_id,
            canonical=canon_rel,
            basename=Path(canon_rel).name,
            date=today,
        )
        if dry_run:
            print(f"  WOULD write stub: {dup_rel}")
        else:
            src.parent.mkdir(parents=True, exist_ok=True)
            src.write_text(stub, encoding="utf-8")
            if is_tracked(dst):
                subprocess.run(["git", "add", str(src)], check=True, cwd=ROOT)

    return moved


def git_rm(path: Path, dry_run: bool) -> bool:
    if not path.exists():
        return False
    if dry_run:
        mode = "git rm" if is_tracked(path) else "rm"
        print(f"  WOULD ({mode}): {rel(path)}")
        return True
    if is_tracked(path):
        subprocess.run(["git", "rm", "-f", str(path)], check=True, cwd=ROOT)
    else:
        path.unlink()
    return True


def apply_purge_completed_roadmaps(dry_run: bool) -> int:
    """Entfernt abgearbeitete Roadmap-Snapshots und Legacy-Planungsdocs."""
    removed = 0
    targets: list[Path] = []

    archive_dir = ARCHIVE / "roadmap-status"
    if archive_dir.is_dir():
        targets.extend(p for p in archive_dir.rglob("*") if p.is_file())

    roadmap_dir = DOCS / "roadmap"
    if roadmap_dir.is_dir():
        for p in roadmap_dir.iterdir():
            if p.name == "README.md":
                continue
            if p.is_file():
                targets.append(p)
        status_dir = roadmap_dir / "status"
        if status_dir.is_dir():
            targets.extend(p for p in status_dir.rglob("*") if p.is_file())

    for path in sorted(set(targets)):
        if git_rm(path, dry_run):
            removed += 1

    readme = roadmap_dir / "README.md"
    body = (
        "# Roadmap (ersetzt)\n\n"
        "Historische Roadmap- und Gap-Snapshots wurden entfernt (abgearbeitet).\n\n"
        "## Operativer Lieferstand\n\n"
        "| Quelle | Pfad |\n"
        "|--------|------|\n"
        "| Process Kernel | `docs/architecture/process-kernel/STATUS.md` |\n"
        "| Open Gaps | `docs/project-context/open-gaps-and-known-issues.md` |\n"
        "| Active Workboard | `docs/agent-ops/active-workboard.md` |\n"
    )
    if dry_run:
        print(f"  WOULD write {rel(readme)}")
    else:
        readme.parent.mkdir(parents=True, exist_ok=True)
        readme.write_text(body, encoding="utf-8")
        if is_tracked(readme):
            subprocess.run(["git", "add", str(readme)], check=True, cwd=ROOT)
        else:
            subprocess.run(["git", "add", str(readme)], check=True, cwd=ROOT)

    # Leeres status-Verzeichnis entfernen
    status_dir = roadmap_dir / "status"
    if not dry_run and status_dir.is_dir() and not any(status_dir.iterdir()):
        status_dir.rmdir()

    return removed


def apply_archive_roadmap_status(dry_run: bool) -> int:
    """Verschiebt datierte roadmap/status-Snapshots ins interne Archiv."""
    src_dir = DOCS / "roadmap" / "status"
    dst_dir = ARCHIVE / "roadmap-status"
    moved = 0
    if not src_dir.is_dir():
        print("  SKIP: docs/roadmap/status/ not found")
        return 0
    for src in sorted(src_dir.glob("*.md")):
        dst = dst_dir / src.name
        git_mv(src, dst, dry_run)
        moved += 1
    idx = dst_dir / "README.md"
    archived = sorted(f.name for f in dst_dir.glob("*.md") if f.name != "README.md")
    body = [
        "# Roadmap-Status-Snapshots (historisch)",
        "",
        f"Konsolidiert aus `docs/roadmap/status/` ({len(archived)} Dateien).",
        "",
        "**Operativer Lieferstand:**",
        "- `docs/architecture/process-kernel/STATUS.md`",
        "- `docs/project-context/open-gaps-and-known-issues.md`",
        "",
        "## Archivierte Dateien",
        "",
    ]
    body.extend(f"- `{name}`" for name in archived)
    content = "\n".join(body) + "\n"
    if dry_run:
        print(f"  WOULD write {rel(idx)}")
    else:
        idx.parent.mkdir(parents=True, exist_ok=True)
        idx.write_text(content, encoding="utf-8")
    return moved


def main() -> None:
    parser = argparse.ArgumentParser(description="Legacy docs migration")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--inventory-only", action="store_true")
    parser.add_argument("--dedupe-cards", action="store_true")
    parser.add_argument("--archive-roadmap-status", action="store_true")
    parser.add_argument("--purge-roadmap", action="store_true")
    args = parser.parse_args()
    dry_run = args.dry_run or (
        not args.apply
        and not args.dedupe_cards
        and not args.archive_roadmap_status
        and not args.purge_roadmap
    )

    files = collect_md_files()
    data = build_inventory(files)
    write_inventory(data)
    print(f"Inventory: {len(data['archive_candidates'])} archive candidates, {data['keep_count']} kept")

    if args.dedupe_cards:
        dedupe_dry = not args.apply
        label = "DRY-RUN" if dedupe_dry else "APPLY"
        print(f"\n{label}: card dedupe ...")
        n = apply_card_dedupe(dry_run=dedupe_dry)
        print(f"done: card_dedupe={n}")
        return

    if args.archive_roadmap_status:
        arch_dry = not args.apply
        label = "DRY-RUN" if arch_dry else "APPLY"
        print(f"\n{label}: archive roadmap/status ...")
        n = apply_archive_roadmap_status(dry_run=arch_dry)
        print(f"done: roadmap_status_archived={n}")
        return

    if args.purge_roadmap:
        purge_dry = not args.apply
        label = "DRY-RUN" if purge_dry else "APPLY"
        print(f"\n{label}: purge completed roadmaps ...")
        n = apply_purge_completed_roadmaps(dry_run=purge_dry)
        print(f"done: roadmap_purged={n}")
        return

    if args.inventory_only:
        return

    if dry_run and not args.dry_run:
        print("Use --dry-run or --apply")
        return

    label = "DRY-RUN" if dry_run else "APPLY"
    print(f"\n{label}: migrating to docs/_internal/archive/ ...")
    moved = apply_migration(data, dry_run=dry_run)
    write_consolidation_indexes(data, dry_run=dry_run)
    print(f"done: moved={moved}")


if __name__ == "__main__":
    main()
