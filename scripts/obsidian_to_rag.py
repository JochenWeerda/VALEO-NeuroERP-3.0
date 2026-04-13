#!/usr/bin/env python3
"""
Obsidian-to-RAG Sync Job (RAG-002)

Reads Markdown files from an Obsidian vault directory, upserts them into
the ``domain_shared.knowledge_objects`` / ``knowledge_versions`` tables,
and triggers RAG vector-store indexing via the existing RAG indexer.

Usage:
    # One-shot sync (default tenant)
    python scripts/obsidian_to_rag.py

    # Specific tenant
    python scripts/obsidian_to_rag.py --tenant-id my-tenant

    # Custom vault path (overrides OBSIDIAN_VAULT_PATH env var)
    python scripts/obsidian_to_rag.py --vault /path/to/vault

    # Dry-run — report what would change, don't write to DB
    python scripts/obsidian_to_rag.py --dry-run

Environment:
    OBSIDIAN_VAULT_PATH  — root directory of the Obsidian vault
    DATABASE_URL         — PostgreSQL connection string

The sync is idempotent: files are matched by a stable key derived from
their relative path inside the vault.  New files create new knowledge
objects; changed files add a new version; unchanged files are skipped.
Deleted vault files are *not* removed from the DB (soft-archive model).
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Bootstrap — make sure repo root is on sys.path so ``app.*`` imports work
# when the script is invoked standalone.
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from sqlalchemy import text as sql_text  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
)
logger = logging.getLogger("obsidian_to_rag")

# ---------------------------------------------------------------------------
# Obsidian front-matter parser (lightweight, no YAML dependency required)
# ---------------------------------------------------------------------------

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    """Return (frontmatter-dict, body-without-frontmatter)."""
    m = _FM_RE.match(raw)
    if not m:
        return {}, raw

    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip().lower()] = val.strip().strip('"').strip("'")

    body = raw[m.end():]
    return fm, body


def _stable_key(vault_root: Path, file_path: Path) -> str:
    """Deterministic key from relative vault path (forward slashes, no ext)."""
    rel = file_path.relative_to(vault_root).with_suffix("")
    return str(rel).replace("\\", "/")


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Core sync logic
# ---------------------------------------------------------------------------


def collect_markdown_files(vault_root: Path) -> list[Path]:
    """Recursively collect all .md files, skipping hidden dirs / .trash."""
    results: list[Path] = []
    for p in vault_root.rglob("*.md"):
        parts = p.relative_to(vault_root).parts
        # Skip hidden directories and Obsidian internals
        if any(part.startswith(".") or part == ".trash" for part in parts):
            continue
        results.append(p)
    results.sort()
    return results


def sync_vault(
    vault_root: Path,
    tenant_id: str,
    *,
    dry_run: bool = False,
) -> dict[str, int]:
    """Sync all .md files from *vault_root* into knowledge_objects.

    Returns dict with counts: created, updated, skipped.
    """
    from app.core.uuid7 import uuid7  # deferred — needs app context

    files = collect_markdown_files(vault_root)
    logger.info("Found %d Markdown files in %s", len(files), vault_root)

    stats = {"created": 0, "updated": 0, "skipped": 0}
    db = SessionLocal()
    try:
        for fpath in files:
            raw = fpath.read_text(encoding="utf-8", errors="replace")
            fm, body = _parse_frontmatter(raw)
            stable = _stable_key(vault_root, fpath)
            chash = _content_hash(body)

            titel = fm.get("title") or fm.get("titel") or fpath.stem.replace("-", " ").replace("_", " ")
            typ = fm.get("type") or fm.get("typ") or "sop"
            tags_raw = fm.get("tags", "")
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []
            zielrollen_raw = fm.get("zielrollen", fm.get("roles", ""))
            zielrollen = [r.strip() for r in zielrollen_raw.split(",") if r.strip()] if zielrollen_raw else []

            # Check if object already exists (match by quelle = obsidian:<stable_key>)
            quelle = f"obsidian:{stable}"
            row = db.execute(sql_text(
                "SELECT ko.knowledge_id, kv.inhalt "
                "FROM domain_shared.knowledge_objects ko "
                "LEFT JOIN domain_shared.knowledge_versions kv "
                "  ON kv.knowledge_id = ko.knowledge_id "
                "  AND kv.version = ("
                "    SELECT MAX(kv2.version) FROM domain_shared.knowledge_versions kv2 "
                "    WHERE kv2.knowledge_id = ko.knowledge_id"
                "  ) "
                "WHERE ko.tenant_id = :tid "
                "  AND kv.quelle = :quelle "
                "LIMIT 1"
            ), {"tid": tenant_id, "quelle": quelle}).first()

            if row:
                # Exists — check if content changed
                existing_hash = _content_hash(row.inhalt) if row.inhalt else ""
                if existing_hash == chash:
                    stats["skipped"] += 1
                    continue

                if dry_run:
                    logger.info("  [DRY-RUN] WOULD UPDATE: %s", stable)
                    stats["updated"] += 1
                    continue

                # Add new version
                kid = row.knowledge_id
                max_ver = db.execute(sql_text(
                    "SELECT COALESCE(MAX(version), 0) FROM domain_shared.knowledge_versions "
                    "WHERE knowledge_id = :kid"
                ), {"kid": kid}).scalar()

                vid = uuid7()
                db.execute(sql_text(
                    "INSERT INTO domain_shared.knowledge_versions "
                    "(id, knowledge_id, version, format, inhalt, strukturierte_daten, quelle, erstellt_am) "
                    "VALUES (:id, :kid, :ver, 'markdown', :inhalt, '{}', :quelle, NOW())"
                ), {
                    "id": vid, "kid": kid, "ver": max_ver + 1,
                    "inhalt": body, "quelle": quelle,
                })

                # Update object metadata
                import json as _json
                db.execute(sql_text(
                    "UPDATE domain_shared.knowledge_objects "
                    "SET titel = :titel, typ = :typ, tags = :tags, "
                    "    zielrollen = :zielrollen, updated_at = NOW() "
                    "WHERE knowledge_id = :kid"
                ), {
                    "kid": kid, "titel": titel, "typ": typ,
                    "tags": _json.dumps(tags), "zielrollen": _json.dumps(zielrollen),
                })

                logger.info("  UPDATED: %s (v%d)", stable, max_ver + 1)
                stats["updated"] += 1
            else:
                # New entry
                if dry_run:
                    logger.info("  [DRY-RUN] WOULD CREATE: %s", stable)
                    stats["created"] += 1
                    continue

                kid = uuid7()
                vid = uuid7()
                import json as _json

                db.execute(sql_text(
                    "INSERT INTO domain_shared.knowledge_objects "
                    "(knowledge_id, tenant_id, titel, typ, status, beschreibung, "
                    " tags, zielrollen, agentenfreigabe, created_at, updated_at) "
                    "VALUES (:kid, :tid, :titel, :typ, 'published', :beschreibung, "
                    " :tags, :zielrollen, true, NOW(), NOW())"
                ), {
                    "kid": kid, "tid": tenant_id, "titel": titel, "typ": typ,
                    "beschreibung": f"Importiert aus Obsidian: {stable}",
                    "tags": _json.dumps(tags), "zielrollen": _json.dumps(zielrollen),
                })

                db.execute(sql_text(
                    "INSERT INTO domain_shared.knowledge_versions "
                    "(id, knowledge_id, version, format, inhalt, strukturierte_daten, quelle, erstellt_am) "
                    "VALUES (:id, :kid, 1, 'markdown', :inhalt, '{}', :quelle, NOW())"
                ), {
                    "id": vid, "kid": kid, "inhalt": body, "quelle": quelle,
                })

                logger.info("  CREATED: %s", stable)
                stats["created"] += 1

        if not dry_run:
            db.commit()
            logger.info(
                "Sync complete — created=%d, updated=%d, skipped=%d",
                stats["created"], stats["updated"], stats["skipped"],
            )
        else:
            db.rollback()
            logger.info(
                "DRY-RUN complete — would create=%d, would update=%d, unchanged=%d",
                stats["created"], stats["updated"], stats["skipped"],
            )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return stats


def trigger_rag_reindex(tenant_id: str) -> None:
    """Trigger RAG vector-store reindex for knowledge collection."""
    import asyncio
    from app.infrastructure.rag.indexer import get_indexer

    db = SessionLocal()
    try:
        indexer = get_indexer()
        count = asyncio.run(indexer.index_knowledge(db, tenant_id))
        logger.info("RAG reindex complete — %d knowledge entries indexed", count)
    except Exception as exc:
        logger.warning("RAG reindex skipped: %s", exc)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync Obsidian vault into VALEO NeuroERP Knowledge Core + RAG",
    )
    parser.add_argument(
        "--vault",
        type=str,
        default=os.environ.get("OBSIDIAN_VAULT_PATH", ""),
        help="Path to Obsidian vault root (default: $OBSIDIAN_VAULT_PATH)",
    )
    parser.add_argument(
        "--tenant-id",
        type=str,
        default=settings.DEFAULT_TENANT_ID,
        help="Tenant ID (default: DEFAULT_TENANT_ID from config)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing to DB",
    )
    parser.add_argument(
        "--skip-rag",
        action="store_true",
        help="Skip RAG vector-store reindex after sync",
    )
    args = parser.parse_args()

    if not args.vault:
        logger.error(
            "No vault path specified.  Set OBSIDIAN_VAULT_PATH in .env "
            "or pass --vault /path/to/vault"
        )
        sys.exit(1)

    vault_root = Path(args.vault).resolve()
    if not vault_root.is_dir():
        logger.error("Vault path does not exist or is not a directory: %s", vault_root)
        sys.exit(1)

    stats = sync_vault(vault_root, args.tenant_id, dry_run=args.dry_run)

    if not args.dry_run and not args.skip_rag and (stats["created"] or stats["updated"]):
        trigger_rag_reindex(args.tenant_id)


if __name__ == "__main__":
    main()
