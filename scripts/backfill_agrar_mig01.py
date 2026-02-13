#!/usr/bin/env python3
"""
AGRAR-MIG-01 backfill script.

Backfills legacy operations objects into new agrar entities:
- domain_ops.ops_wiegungen -> domain_inventory.weighing_tickets
- domain_ops.ops_chargen -> domain_inventory.silo_lots (+ silos, movements, snapshots)

Idempotency:
- deterministic legacy IDs for migrated records
- re-run safe (existing records are skipped/updated)
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import SessionLocal  # noqa: E402
from app.domains.operations.models import Charge, Wiegung  # noqa: E402
from app.infrastructure.models import (  # noqa: E402
    Silo,
    SiloLot,
    SiloLotMovement,
    SiloQualitySnapshot,
    WeighingTicket,
)


def _q3(value: float | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def normalize_silo_number(lagerort: str | None) -> str:
    raw = (lagerort or "LEGACY-DEFAULT").strip().upper()
    raw = re.sub(r"[^A-Z0-9]+", "-", raw).strip("-")
    if not raw:
        raw = "LEGACY-DEFAULT"
    return raw[:50]


def sanitize_weights(brutto: float, tara: float, netto: float | None) -> tuple[Decimal, Decimal, Decimal, bool]:
    b = _q3(max(float(brutto or 0), 0.0))
    t = _q3(max(float(tara or 0), 0.0))
    if t > b:
        t = b
    expected_net = _q3(b - t)
    n = _q3(float(netto)) if netto is not None else expected_net
    corrected = False
    if n < 0 or abs(n - expected_net) > Decimal("0.001"):
        n = expected_net
        corrected = True
    return b, t, n, corrected


@dataclass
class ReportCounters:
    weighing_seen: int = 0
    weighing_created: int = 0
    weighing_skipped: int = 0
    weighing_corrected: int = 0
    silos_seen: int = 0
    silos_created: int = 0
    silos_skipped: int = 0
    lots_seen: int = 0
    lots_created: int = 0
    lots_skipped: int = 0
    lots_corrected: int = 0
    movements_created: int = 0
    snapshots_upserted: int = 0
    errors: int = 0


def _upsert_silo_snapshot(db, silo: Silo, tenant_id: str) -> None:
    lots = db.query(SiloLot).filter(SiloLot.silo_id == silo.id, SiloLot.tenant_id == tenant_id, SiloLot.status == "active").all()

    total_qty = sum(float(l.quantity_tons or 0) for l in lots)
    lot_count = len(lots)

    def _weighted(field: str) -> Decimal | None:
        weighted_sum = 0.0
        weighted_qty = 0.0
        for lot in lots:
            metric = getattr(lot, field)
            if metric is None:
                continue
            qty = float(lot.quantity_tons or 0)
            weighted_sum += float(metric) * qty
            weighted_qty += qty
        if weighted_qty <= 0:
            return None
        return _q3(weighted_sum / weighted_qty)

    snap_id = f"LEGACY-SNAP-{silo.id}"
    snap = db.query(SiloQualitySnapshot).filter(SiloQualitySnapshot.id == snap_id).first()
    if not snap:
        snap = SiloQualitySnapshot(id=snap_id, silo_id=silo.id, tenant_id=tenant_id)
        db.add(snap)

    snap.total_quantity_tons = _q3(total_qty)
    snap.moisture_avg_pct = _weighted("moisture_pct")
    snap.protein_avg_pct = _weighted("protein_pct")
    snap.impurities_avg_pct = _weighted("impurities_pct")
    snap.hl_weight_avg = _weighted("hl_weight")
    snap.lot_count = lot_count


def run_backfill(*, tenant_id: str, dry_run: bool) -> dict[str, Any]:
    counters = ReportCounters()
    notes: list[str] = []

    db = SessionLocal()
    try:
        legacy_wiegungen = db.query(Wiegung).all()
        for src in legacy_wiegungen:
            counters.weighing_seen += 1
            target_id = f"LEGACY-WG-{src.id}"
            existing = db.query(WeighingTicket).filter(WeighingTicket.id == target_id).first()
            if existing:
                counters.weighing_skipped += 1
                continue

            b, t, n, corrected = sanitize_weights(src.brutto or 0, src.tara or 0, src.netto)
            if corrected:
                counters.weighing_corrected += 1

            ticket = WeighingTicket(
                id=target_id,
                ticket_number=str(src.id),
                scale_id=src.waage_id,
                vehicle_plate=src.kennzeichen,
                gross_weight=b,
                tare_weight=t,
                net_weight=n,
                billing_weight=n,
                first_weighing_at=src.zeitstempel,
                second_weighing_at=src.zeitstempel,
                direction="in",
                status="open",
                reference_doc=f"legacy_wiegung:{src.id}",
                quality_data={"migration_source": "domain_ops.ops_wiegungen", "legacy_id": src.id, "legacy_chargennummer": src.chargennummer},
                tenant_id=tenant_id,
            )
            db.add(ticket)
            counters.weighing_created += 1

        legacy_charges = db.query(Charge).all()
        silos_by_number: dict[str, Silo] = {
            s.silo_number: s
            for s in db.query(Silo).filter(Silo.tenant_id == tenant_id).all()
        }

        touched_silos: set[str] = set()
        for charge in legacy_charges:
            counters.lots_seen += 1
            silo_number = normalize_silo_number(charge.lagerort)
            counters.silos_seen += 1
            silo = silos_by_number.get(silo_number)
            if silo is None:
                silo = Silo(
                    id=f"LEGACY-SILO-{silo_number}",
                    silo_number=silo_number,
                    name=f"Legacy {charge.lagerort or 'Silo'}",
                    article_id=charge.artikel_id,
                    capacity_tons=Decimal("1000.000"),
                    tenant_id=tenant_id,
                    is_active=True,
                )
                db.add(silo)
                silos_by_number[silo_number] = silo
                counters.silos_created += 1
            else:
                counters.silos_skipped += 1

            qty = float(charge.menge or 0)
            if qty < 0:
                qty = abs(qty)
                counters.lots_corrected += 1
                notes.append(f"Negative quantity corrected for charge {charge.id}")

            lot_id = f"LEGACY-LOT-{charge.id}"
            lot = db.query(SiloLot).filter(SiloLot.id == lot_id).first()
            if lot:
                counters.lots_skipped += 1
            else:
                lot = SiloLot(
                    id=lot_id,
                    silo_id=silo.id,
                    virtual_lot_number=charge.chargen_id or str(charge.id),
                    source_ticket_id=f"LEGACY-WG-{charge.id}" if charge.id else None,
                    source_partner_id=charge.herkunft,
                    article_id=charge.artikel_id,
                    quantity_tons=_q3(qty),
                    status="active",
                    tenant_id=tenant_id,
                )
                db.add(lot)
                counters.lots_created += 1

            movement_id = f"LEGACY-MOV-{charge.id}"
            mov_exists = db.query(SiloLotMovement).filter(SiloLotMovement.id == movement_id).first()
            if not mov_exists:
                db.add(
                    SiloLotMovement(
                        id=movement_id,
                        silo_lot_id=lot.id,
                        movement_type="in",
                        quantity_tons=lot.quantity_tons,
                        note="Migrated from domain_ops.ops_chargen",
                        tenant_id=tenant_id,
                    )
                )
                counters.movements_created += 1

            touched_silos.add(silo.id)

        for silo_id in touched_silos:
            silo = db.query(Silo).filter(Silo.id == silo_id).first()
            if silo:
                _upsert_silo_snapshot(db, silo, tenant_id)
                counters.snapshots_upserted += 1

        if dry_run:
            db.rollback()
        else:
            db.commit()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "dry_run": dry_run,
            "counters": asdict(counters),
            "notes": notes,
        }
    except Exception as exc:
        db.rollback()
        counters.errors += 1
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "dry_run": dry_run,
            "counters": asdict(counters),
            "notes": notes,
            "error": str(exc),
        }
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="AGRAR-MIG-01 backfill script")
    parser.add_argument("--tenant-id", default="system")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report-file", default="reports/migrations/agrar-mig-01-report.json")
    args = parser.parse_args()

    report = run_backfill(tenant_id=args.tenant_id, dry_run=args.dry_run)
    report_path = Path(args.report_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    print("AGRAR-MIG-01 completed")
    print(json.dumps(report, indent=2, ensure_ascii=True))
    print(f"Report written to: {report_path}")


if __name__ == "__main__":
    main()
