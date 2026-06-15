from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_procurement_seed_uses_canonical_inventory_schema():
    text = (ROOT / "scripts" / "seed_demo_procurement.py").read_text(
        encoding="utf-8"
    )

    assert "domain_inventory.warehouses" in text
    assert "warehouse_code = :code AND tenant_id = :tenant" in text
    assert "domain_inventory.stock_locations" in text
    assert "warehouse_id = :warehouse_id AND location_code = :code" in text
    assert "public.inventory_warehouses" not in text
    assert "public.inventory_locations" not in text
