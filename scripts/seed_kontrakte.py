from __future__ import annotations

import random
from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.core.uuid7 import uuid7
from app.domains.operations.models import KonContract, KonContractLine, KonContractMovement


TENANT_ID = "00000000-0000-0000-0000-000000000001"


def seed() -> None:
    db = SessionLocal()
    try:
        existing = db.query(KonContract).filter(KonContract.tenant_id == TENANT_ID).count()
        if existing >= 20:
            print("seed_kontrakte: already seeded")
            return

        contract_types = ["VERKAUF"] * 10 + ["ZUKAUF"] * 5 + ["EINKAUF"] * 5
        random.shuffle(contract_types)
        base_date = datetime.utcnow() - timedelta(days=20)
        for idx, ctype in enumerate(contract_types, start=1):
            contract_id = uuid7()
            total_qty = round(random.uniform(100, 1500), 3)
            contract = KonContract(
                contract_id=contract_id,
                contract_no=f"{ctype[:3]}-SEED-{idx:04d}",
                contract_type=ctype,
                branch_id=f"NL-{(idx % 4) + 1}",
                clerk_id=f"USR-{(idx % 6) + 1}",
                party_id=f"PARTY-{(idx % 15) + 1}",
                contract_date=base_date + timedelta(days=idx),
                valid_from=base_date + timedelta(days=idx),
                valid_to=base_date + timedelta(days=idx + 120),
                quantity_type="GESAMTKONTRAKT" if idx % 2 == 0 else "EINZELMENGEN",
                total_quantity=total_qty,
                unit="kg",
                allow_overdelivery=(idx % 3 == 0),
                status="OFFEN",
                notes="Seed-Kontrakt",
                payment_terms="30 Tage netto",
                pricing_model=random.choice(["fixed", "follow", "pool", "mindestpreis", "praemie"]),
                tenant_id=TENANT_ID,
                created_by="seed_kontrakte",
                updated_by="seed_kontrakte",
            )
            db.add(contract)
            db.flush()

            line_count = random.randint(2, 5)
            per_line = total_qty / line_count
            line_ids = []
            for l in range(line_count):
                line_id = uuid7()
                line_ids.append(line_id)
                db.add(
                    KonContractLine(
                        line_id=line_id,
                        contract_id=contract_id,
                        position_no=l + 1,
                        article_id=f"ART-{(idx + l) % 30 + 1}",
                        description1=f"Seed Artikel {(idx + l) % 30 + 1}",
                        qty_contract=round(per_line, 3),
                        price_unit="kg",
                        unit_price=round(random.uniform(0.12, 1.75), 4),
                        discount_pct=0,
                        surcharge=0,
                        tenant_id=TENANT_ID,
                        created_by="seed_kontrakte",
                        updated_by="seed_kontrakte",
                    )
                )

            movement_rows = random.randint(1, 6)
            for m in range(movement_rows):
                db.add(
                    KonContractMovement(
                        movement_id=uuid7(),
                        contract_id=contract_id,
                        line_id=random.choice(line_ids),
                        order_no=f"AUF-{idx:04d}-{m+1}",
                        delivery_note_no=f"LS-{idx:04d}-{m+1}",
                        invoice_no=(f"RE-{idx:04d}-{m+1}" if m % 2 == 0 else None),
                        movement_date=base_date + timedelta(days=idx + m),
                        quantity=round(random.uniform(5, per_line / 2), 3),
                        unit_price=round(random.uniform(0.12, 1.75), 4),
                        route_no=f"ST-{(idx + m) % 12 + 1}",
                        is_invoiced=(m % 2 == 0),
                        is_archived=(m % 5 == 0),
                        tenant_id=TENANT_ID,
                        created_by="seed_kontrakte",
                    )
                )
        db.commit()
        print("seed_kontrakte: done")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
