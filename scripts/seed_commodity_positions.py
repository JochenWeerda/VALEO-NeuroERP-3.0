"""
Seed data for Commodity Position Matrix: articles (Raps, Sojaschrot, Maismehl, Dünger),
EK/VK contracts over Apr–Jul 2026, rules, and one override.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.core.database import SessionLocal
from app.core.uuid7 import uuid7
from app.domains.operations.models import (
    KonContract,
    KonContractLine,
    KonContractMovement,
    PosPositionRule,
    PosPositionOverride,
)

TENANT_ID = "00000000-0000-0000-0000-000000000001"
ARTICLES = ["Raps", "Sojaschrot", "Maismehl", "Duenger"]
BRANCH = "NL-1"


def _period_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


def seed() -> None:
    db = SessionLocal()
    try:
        # 1) Regeln: Raps Toleranz -200, Maismehl -100
        if db.query(PosPositionRule).filter(PosPositionRule.tenant_id == TENANT_ID).count() == 0:
            for scope_id, neg_tol in [("Raps", -200), ("Maismehl", -100)]:
                db.add(
                    PosPositionRule(
                        rule_id=uuid7(),
                        scope_type="ARTICLE",
                        scope_id=scope_id,
                        neg_tolerance_qty=Decimal(str(neg_tol)),
                        max_short_days=14,
                        yellow_threshold=Decimal("-50"),
                        red_threshold=Decimal(str(neg_tol)),
                        approval_required=True,
                        approval_role="teamleiter",
                        tenant_id=TENANT_ID,
                        created_by="seed_commodity_positions",
                        updated_by="seed_commodity_positions",
                    )
                )
            db.flush()

        # 2) Kontrakte Apr–Jul 2026: je Artikel 5 EK + 5 VK mit Teilabrufen
        base = datetime(2026, 4, 1)
        existing = db.query(KonContract).filter(
            KonContract.tenant_id == TENANT_ID,
            KonContract.contract_no.like("POS-SEED-%"),
        ).count()
        if existing >= 5:
            print("seed_commodity_positions: contracts already present")
            db.commit()
            return

        for art in ARTICLES:
            for month_off in range(4):
                valid_from = datetime(2026, 4 + month_off, 1)
                valid_to = datetime(2026, 4 + month_off, 28)
                # Einkauf: 300 t
                cid_ek = uuid7()
                db.add(
                    KonContract(
                        contract_id=cid_ek,
                        contract_no=f"POS-SEED-EK-{art[:3]}-{month_off+1:02d}",
                        contract_type="EINKAUF",
                        branch_id=BRANCH,
                        party_id="LIEF-001",
                        contract_date=valid_from,
                        valid_from=valid_from,
                        valid_to=valid_to,
                        quantity_type="GESAMTKONTRAKT",
                        total_quantity=Decimal("300"),
                        unit="t",
                        status="OFFEN",
                        tenant_id=TENANT_ID,
                        created_by="seed_commodity_positions",
                        updated_by="seed_commodity_positions",
                    )
                )
                db.flush()
                lid = uuid7()
                db.add(
                    KonContractLine(
                        line_id=lid,
                        contract_id=cid_ek,
                        position_no=1,
                        article_id=art,
                        description1=art,
                        qty_contract=Decimal("300"),
                        price_unit="t",
                        tenant_id=TENANT_ID,
                        created_by="seed_commodity_positions",
                        updated_by="seed_commodity_positions",
                    )
                )
                # Teilabruf 100 t
                db.add(
                    KonContractMovement(
                        movement_id=uuid7(),
                        contract_id=cid_ek,
                        line_id=lid,
                        movement_date=valid_from,
                        quantity=Decimal("100"),
                        tenant_id=TENANT_ID,
                        created_by="seed_commodity_positions",
                    )
                )
                # Verkauf: variabel um Ziel-Netto zu treffen
                if art == "Raps" and month_off == 1:
                    sell_qty = Decimal("700")  # Mai: 200 EK - 700 VK = -500 (Rot)
                elif art == "Maismehl" and month_off == 1:
                    sell_qty = Decimal("220")  # Mai: 200 EK - 220 VK = -20 (Gelb)
                elif art == "Sojaschrot":
                    sell_qty = Decimal("50") if month_off == 0 else Decimal("0")  # Apr: 200-50=150, Summe +450
                else:
                    sell_qty = Decimal("150")
                cid_vk = uuid7()
                db.add(
                    KonContract(
                        contract_id=cid_vk,
                        contract_no=f"POS-SEED-VK-{art[:3]}-{month_off+1:02d}",
                        contract_type="VERKAUF",
                        branch_id=BRANCH,
                        party_id="KUND-001",
                        contract_date=valid_from,
                        valid_from=valid_from,
                        valid_to=valid_to,
                        quantity_type="GESAMTKONTRAKT",
                        total_quantity=sell_qty,
                        unit="t",
                        status="OFFEN",
                        tenant_id=TENANT_ID,
                        created_by="seed_commodity_positions",
                        updated_by="seed_commodity_positions",
                    )
                )
                db.flush()
                lid_vk = uuid7()
                db.add(
                    KonContractLine(
                        line_id=lid_vk,
                        contract_id=cid_vk,
                        position_no=1,
                        article_id=art,
                        description1=art,
                        qty_contract=sell_qty,
                        price_unit="t",
                        tenant_id=TENANT_ID,
                        created_by="seed_commodity_positions",
                        updated_by="seed_commodity_positions",
                    )
                )
                if sell_qty > 0 and art == "Raps" and month_off == 1:
                    db.add(
                        KonContractMovement(
                            movement_id=uuid7(),
                            contract_id=cid_vk,
                            line_id=lid_vk,
                            movement_date=valid_from,
                            quantity=Decimal("50"),
                            tenant_id=TENANT_ID,
                            created_by="seed_commodity_positions",
                        )
                    )

        # 3) Ein Override (Requested) für Raps / 2026-05
        if db.query(PosPositionOverride).filter(PosPositionOverride.tenant_id == TENANT_ID).count() == 0:
            db.add(
                PosPositionOverride(
                    override_id=uuid7(),
                    tenant_id=TENANT_ID,
                    branch_id=BRANCH,
                    article_id="Raps",
                    period_key="2026-05",
                    requested_by="seed_user",
                    reason="Seed: Freigabe angefordert für Raps Mai",
                    status="REQUESTED",
                    tenant_id=TENANT_ID,
                    created_by="seed_commodity_positions",
                    updated_by="seed_commodity_positions",
                )
            )
        db.commit()
        print("seed_commodity_positions: done")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
