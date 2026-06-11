from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEGACY_TABLE = "domain_inventory.stock_movements"
CANONICAL_TABLE = "domain_inventory.inventory_stock_movements"


def test_articles_position_context_uses_canonical_stock_movements():
    source = (ROOT / "app/api/v1/endpoints/articles.py").read_text(encoding="utf-8")
    assert LEGACY_TABLE not in source
    assert CANONICAL_TABLE in source
    assert "charge AS batch_number" in source


def test_pos_retoure_writes_canonical_stock_movements():
    source = (ROOT / "app/api/v1/endpoints/pos_retoure.py").read_text(encoding="utf-8")
    assert LEGACY_TABLE not in source
    assert CANONICAL_TABLE in source
    assert "source_document_type" in source
    assert "'pos_retoure'" in source


def test_app_endpoints_have_no_legacy_stock_movements_table():
    endpoints = ROOT / "app/api/v1/endpoints"
    offenders = []
    for path in endpoints.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if LEGACY_TABLE in text:
            offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []
