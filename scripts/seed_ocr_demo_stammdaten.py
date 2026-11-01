#!/usr/bin/env python3
"""OCR-Demo-Stammdaten aus Übungsfixtures (Pseudonyme) — ADAPTIVE.

Idempotent: Lieferantennummer / Artikelnummer DEMO-* werden bei erneutem Lauf
uebersprungen (kein Duplikat). Schreibt in die DB aus DATABASE_URL
(standard: valeo_neuro_erp).

Lauf:
    python -m scripts.seed_ocr_demo_stammdaten
    python -m scripts.seed_ocr_demo_stammdaten --with-inbox
    OCR_DEMO_TENANT_ID=00000000-0000-0000-0000-000000000051 \\
        python -m scripts.seed_ocr_demo_stammdaten --with-inbox

Hinweis: Namen sind Pseudonyme fuer Demo/Investor — siehe
evidence/ocr-training/README.md und --print-plan.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ocr_demo_stammdaten_catalog import build_demo_seed_plan  # noqa: E402

DEFAULT_TENANT = "00000000-0000-0000-0000-000000000051"


def _tenant() -> str:
    return (os.getenv("OCR_DEMO_TENANT_ID") or DEFAULT_TENANT).strip()


def upsert_suppliers(db: Any, tenant_id: str, suppliers: list[dict[str, Any]]) -> dict[str, int]:
    from app.core.uuid7 import uuid7
    from app.infrastructure.models.einkauf_models import EinkaufLieferant

    created = skipped = 0
    for row in suppliers:
        nr = row["lieferantennummer"]
        existing = (
            db.query(EinkaufLieferant)
            .filter(
                EinkaufLieferant.tenant_id == tenant_id,
                EinkaufLieferant.lieferantennummer == nr,
            )
            .first()
        )
        if existing:
            skipped += 1
            continue
        db.add(
            EinkaufLieferant(
                id=uuid7(),
                tenant_id=tenant_id,
                lieferantennummer=nr,
                firmenname=row["firmenname"],
                ort=row.get("ort") or None,
                land=row.get("land") or "Deutschland",
                notiz=row.get("notiz"),
                aktiv=True,
            )
        )
        created += 1
    return {"created": created, "skipped": skipped}


def upsert_articles(db: Any, tenant_id: str, articles: list[dict[str, Any]]) -> dict[str, int]:
    from app.core.uuid7 import uuid7
    from app.infrastructure.models import Article

    created = skipped = 0
    for row in articles:
        nr = row["article_number"]
        existing = (
            db.query(Article)
            .filter(
                Article.tenant_id == tenant_id,
                Article.article_number == nr,
                Article.deleted_at.is_(None),
            )
            .first()
        )
        if existing:
            skipped += 1
            continue
        db.add(
            Article(
                id=uuid7(),
                tenant_id=tenant_id,
                article_number=nr,
                name=row["name"][:100],
                unit=row.get("unit") or "t",
                category=row.get("category") or "Sonstige",
                sales_price=row.get("sales_price") or 0,
                currency="EUR",
                supplier_number=row.get("supplier_number"),
                is_active=True,
                lagerorte=[],
            )
        )
        created += 1
    return {"created": created, "skipped": skipped}


def inbox_demo_item_id(supplier_nr: str) -> str:
    """Kanonische Demo-Inbox-ID: supplier_nr ist bereits DEMO-* → INBOX-DEMO-LF-….

    Frueher f\"INBOX-DEMO-{supplier_nr}\" erzeugte INBOX-DEMO-DEMO-… (Bug).
    """
    nr = (supplier_nr or "").strip()
    if nr.upper().startswith("DEMO-"):
        return f"INBOX-{nr}"
    return f"INBOX-DEMO-{nr}"


def inbox_demo_legacy_double_id(supplier_nr: str) -> str:
    """Alte fehlerhafte Doppel-DEMO-ID (nur Cleanup eigener Seed-Zeilen)."""
    return f"INBOX-DEMO-{(supplier_nr or '').strip()}"


def seed_inbox_samples(
    db: Any,
    tenant_id: str,
    samples: list[dict[str, Any]],
    *,
    limit: int = 2,
) -> dict[str, int]:
    """1–2 pending Inbox-Zeilen mit Pseudonym-OCR + positionen (Queue-Demo)."""
    from sqlalchemy import text

    created = skipped = cleaned = 0
    has_tenant = (
        db.execute(
            text(
                """
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'domain_shared'
                  AND table_name = 'dms_inbox'
                  AND column_name = 'tenant_id'
                """
            )
        ).scalar()
        is not None
    )
    if not has_tenant:
        return {"created": 0, "skipped": 0, "cleaned_legacy": 0, "note": "keine tenant_id-Spalte"}

    # Alle eigenen Doppel-DEMO-Legacy-Zeilen dieses Tenants (nicht nur aktuelle Samples)
    sweep = db.execute(
        text(
            """
            DELETE FROM domain_shared.dms_inbox
            WHERE tenant_id = :tenant_id
              AND id LIKE 'INBOX-DEMO-DEMO-%'
            """
        ),
        {"tenant_id": tenant_id},
    )
    cleaned += int(getattr(sweep, "rowcount", 0) or 0)

    for sample in samples[:limit]:
        supplier_nr = sample["supplier_nr"]
        item_id = inbox_demo_item_id(supplier_nr)

        exists = db.execute(
            text("SELECT 1 FROM domain_shared.dms_inbox WHERE id = :id"),
            {"id": item_id},
        ).scalar()
        if exists:
            skipped += 1
            continue
        parsed = {
            "invoice_number": sample["invoice_number"],
            "supplier": sample["supplier_name"],
            "supplier_id": sample["supplier_nr"],
            "domain": "purchase",
            "document_type": "supplier_invoice",
            "positionen": sample["positionen"],
        }
        cols = (
            "id, dms_document_id, dms_url, ocr_text, parsed_fields, confidence, status, tenant_id"
        )
        vals = (
            ":id, 92001, 'http://localhost/doc/demo-ocr', :ocr, "
            "CAST(:parsed AS jsonb), 0.85, 'pending', :tenant_id"
        )
        db.execute(
            text(f"INSERT INTO domain_shared.dms_inbox ({cols}) VALUES ({vals})"),
            {
                "id": item_id,
                "ocr": sample["ocr_excerpt"],
                "parsed": json.dumps(parsed, ensure_ascii=False),
                "tenant_id": tenant_id,
            },
        )
        created += 1
    return {"created": created, "skipped": skipped, "cleaned_legacy": cleaned}


def _partner_gap_inbox_sample(matched_sample: dict[str, Any] | None) -> dict[str, Any]:
    """Zweite Demo-Zeile: bekannter Pseudonym-Name, aber Lieferantennr. nicht im Stamm.

    Erzeugt partner_nicht_gefunden + Lieferant-anlegen-Vorschlag, solange kein BP
    mit DEMO-LF-GAP existiert. Positionen bleiben aus dem Match-Sample (Artikel-Demo).
    """
    positionen = (matched_sample or {}).get("positionen") or [
        {
            "artikel_name": "Demo-Schrot Weizen",
            "artikel_nr": "DEMO-GAP-WHEAT",
            "menge": 12.5,
            "einheit": "t",
            "einzelpreis": 210.0,
        }
    ]
    supplier_nr = "DEMO-LF-GAP"
    supplier_name = "Nordkorn Handelsgesellschaft Demo OHG"
    return {
        "fixture": "synthetic_partner_gap",
        "supplier_key": "partner_gap",
        "supplier_name": supplier_name,
        "supplier_nr": supplier_nr,
        "invoice_number": "DEMO-GAP-LS-001",
        "positionen": positionen[:5],
        "ocr_excerpt": (
            f"{supplier_name}\nLieferantennr.: {supplier_nr}\nRechnung DEMO-GAP\n"
            + "\n".join(
                f"{i+1} {p.get('artikel_nr')} {p['artikel_name']} "
                f"{p.get('menge') or ''} {p.get('einheit') or ''}"
                for i, p in enumerate(positionen[:3])
            )
        ),
    }


def run_seed(*, with_inbox: bool = False, dry_run: bool = False) -> dict[str, Any]:
    from app.core.database import SessionLocal

    plan = build_demo_seed_plan()
    tenant_id = _tenant()
    result: dict[str, Any] = {
        "tenant_id": tenant_id,
        "plan_suppliers": len(plan["suppliers"]),
        "plan_articles": len(plan["articles"]),
        "plan_inbox_samples": len(plan["inbox_samples"]),
        "pseudonym_map": plan["pseudonym_map"],
    }
    if dry_run:
        result["dry_run"] = True
        return result

    db = SessionLocal()
    try:
        result["suppliers"] = upsert_suppliers(db, tenant_id, plan["suppliers"])
        result["articles"] = upsert_articles(db, tenant_id, plan["articles"])
        if with_inbox:
            # 1× Match-Zeile (Pseudonym-Stamm + Positionen) + 1× Partner-Gap
            matched = plan["inbox_samples"][:1]
            samples = list(matched) + [_partner_gap_inbox_sample(matched[0] if matched else None)]
            result["inbox"] = seed_inbox_samples(db, tenant_id, samples, limit=2)
            result["inbox_ids"] = [inbox_demo_item_id(s["supplier_nr"]) for s in samples]
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OCR-Demo Stammdaten (Pseudonyme) seeden")
    parser.add_argument("--with-inbox", action="store_true", help="1–2 dms_inbox Demo-Zeilen anlegen")
    parser.add_argument("--print-plan", action="store_true", help="Nur Plan/Mapping ausgeben, kein DB-Write")
    parser.add_argument("--dry-run", action="store_true", help="Plan-Metadaten ohne Commit")
    args = parser.parse_args(argv)

    if args.print_plan:
        plan = build_demo_seed_plan()
        print(json.dumps({
            "suppliers": len(plan["suppliers"]),
            "articles": len(plan["articles"]),
            "inbox_samples": len(plan["inbox_samples"]),
            "pseudonym_map": plan["pseudonym_map"],
            "sample_articles": [
                {"article_number": a["article_number"], "name": a["name"], "unit": a["unit"]}
                for a in plan["articles"][:8]
            ],
        }, ensure_ascii=False, indent=2))
        return 0

    result = run_seed(with_inbox=args.with_inbox, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
