from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_procurement_match_and_seed_share_canonical_goods_receipt_schema():
    service = (
        ROOT / "app" / "services" / "procurement_match_service.py"
    ).read_text(encoding="utf-8")
    seed = (ROOT / "scripts" / "seed_demo_procurement.py").read_text(
        encoding="utf-8"
    )
    combined = service + seed

    assert "einkauf_wareneingaenge" in service
    assert "einkauf_wareneingang_positionen" in service
    assert "b.tenant_id = :t" in service
    assert "bp.id::text = l.purchase_order_item_id" in service
    assert "einkauf_wareneingaenge" in seed
    assert "purchase_order_item_id" in seed
    assert "public.inventory_goods_receipts" not in combined
    assert "public.inventory_goods_receipt_lines" not in combined
