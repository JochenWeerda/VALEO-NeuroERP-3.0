"""OCR-Demo-Stammdaten: Pseudonym-Plan idempotent / re-runbar (pure + optional DB)."""

from __future__ import annotations

from scripts.ocr_demo_stammdaten_catalog import (
    FIXTURE_SUPPLIER_KEY,
    SUPPLIER_PSEUDONYMS,
    build_demo_seed_plan,
)
from scripts.seed_ocr_demo_stammdaten import (
    inbox_demo_item_id,
    inbox_demo_legacy_double_id,
)


def test_pseudonym_map_covers_korpus_and_avoids_real_names():
    plan = build_demo_seed_plan()
    assert len(plan["suppliers"]) >= 11
    mapping = plan["pseudonym_map"]
    assert "Bröring / Broering" in mapping or any("Bröring" in k or "Broering" in k for k in mapping)
    # Keine 1:1-Realnamen als Demo-Firmenname
    names = {s["firmenname"].casefold() for s in plan["suppliers"]}
    assert not any("bröring" in n or "broering" in n for n in names)
    assert not any("telekom" in n for n in names)
    assert not any("webfleet" in n for n in names)
    assert all(s["lieferantennummer"].startswith("DEMO-") for s in plan["suppliers"])


def test_articles_from_fixtures_have_demo_prefix_and_defaults():
    plan = build_demo_seed_plan()
    assert len(plan["articles"]) >= 10
    for art in plan["articles"]:
        assert art["article_number"].startswith("DEMO-")
        assert art["unit"]
        assert art["category"]
        assert float(art["sales_price"]) >= 0
        assert len(art["name"]) <= 100


def test_seed_plan_is_stable_on_rerun():
    a = build_demo_seed_plan()
    b = build_demo_seed_plan()
    assert {s["lieferantennummer"] for s in a["suppliers"]} == {
        s["lieferantennummer"] for s in b["suppliers"]
    }
    assert {x["article_number"] for x in a["articles"]} == {
        x["article_number"] for x in b["articles"]
    }


def test_fixture_supplier_keys_point_to_catalog():
    for fixture, key in FIXTURE_SUPPLIER_KEY.items():
        assert key in SUPPLIER_PSEUDONYMS, fixture
        assert SUPPLIER_PSEUDONYMS[key]["lieferantennummer"].startswith("DEMO-")


def test_inbox_samples_use_pseudonym_supplier():
    plan = build_demo_seed_plan()
    assert plan["inbox_samples"]
    for sample in plan["inbox_samples"]:
        assert sample["supplier_nr"].startswith("DEMO-")
        assert "Broering" not in sample["supplier_name"]
        assert "Telekom" not in sample["supplier_name"]
        assert sample["positionen"]


def test_inbox_demo_item_id_avoids_double_demo_prefix():
    assert inbox_demo_item_id("DEMO-LF-NWF") == "INBOX-DEMO-LF-NWF"
    assert inbox_demo_item_id("DEMO-LF-WAH") == "INBOX-DEMO-LF-WAH"
    assert "DEMO-DEMO" not in inbox_demo_item_id("DEMO-LF-NWF")
    # Legacy-Bug-Form (nur Cleanup)
    assert inbox_demo_legacy_double_id("DEMO-LF-NWF") == "INBOX-DEMO-DEMO-LF-NWF"
    plan = build_demo_seed_plan()
    for sample in plan["inbox_samples"][:2]:
        item_id = inbox_demo_item_id(sample["supplier_nr"])
        assert item_id.startswith("INBOX-DEMO-")
        assert "INBOX-DEMO-DEMO-" not in item_id
        assert item_id == f"INBOX-{sample['supplier_nr']}"
