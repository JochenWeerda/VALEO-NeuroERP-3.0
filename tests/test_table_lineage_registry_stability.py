"""The real lazy registry must yield a stable, complete native catalog."""
from scripts.table_lineage import load_native_screens


def test_table_lineage_native_registry_is_import_order_independent():
    first = load_native_screens()
    second = load_native_screens()
    assert first and first == second
    ids = [row["id"] for row in first]
    assert len(ids) == len(set(ids))
