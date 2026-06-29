"""Unit tests for paginate_tab_items sort/whitelist logic (Phase 022)."""
import pytest
from app.core.mask_screen_summary_common import paginate_tab_items

ITEMS = [
    {"id": "1", "name": "Ziegler", "amount": 300},
    {"id": "2", "name": "Arndt", "amount": 100},
    {"id": "3", "name": "Müller", "amount": 200},
]


def test_sort_asc_no_whitelist():
    result, total = paginate_tab_items(ITEMS, sort="name", sort_dir="asc")
    assert total == 3
    assert [r["name"] for r in result] == ["Arndt", "Müller", "Ziegler"]


def test_sort_desc_no_whitelist():
    result, _ = paginate_tab_items(ITEMS, sort="name", sort_dir="desc")
    assert [r["name"] for r in result] == ["Ziegler", "Müller", "Arndt"]


def test_sort_blocked_by_whitelist():
    """Column not in whitelist → sort silently ignored, original order kept."""
    result, _ = paginate_tab_items(
        ITEMS, sort="name", sort_dir="asc", allowed_sort_columns=frozenset({"amount"})
    )
    assert [r["name"] for r in result] == ["Ziegler", "Arndt", "Müller"]


def test_sort_allowed_by_whitelist():
    result, _ = paginate_tab_items(
        ITEMS, sort="amount", sort_dir="asc", allowed_sort_columns=frozenset({"amount"})
    )
    assert [r["amount"] for r in result] == [100, 200, 300]


def test_sort_numeric_asc():
    result, _ = paginate_tab_items(ITEMS, sort="amount", sort_dir="asc")
    assert [r["amount"] for r in result] == [100, 200, 300]


def test_sort_with_none_values_stable():
    items = [{"id": "1", "name": None}, {"id": "2", "name": "Arndt"}]
    result, _ = paginate_tab_items(items, sort="name", sort_dir="asc")
    # None sorts last
    assert result[0]["name"] == "Arndt"
    assert result[1]["name"] is None


def test_no_sort_preserves_order():
    result, total = paginate_tab_items(ITEMS)
    assert total == 3
    assert result == ITEMS


def test_sort_with_pagination():
    result, total = paginate_tab_items(
        ITEMS, sort="amount", sort_dir="asc", page=2, limit=2
    )
    assert total == 3
    assert len(result) == 1
    assert result[0]["amount"] == 300


def test_q_filter_then_sort():
    result, total = paginate_tab_items(ITEMS, q="ü", sort="amount", sort_dir="asc")
    assert total == 1
    assert result[0]["name"] == "Müller"


# FilterPlan tests (Phase 023)

def test_filter_plan_eq():
    result, total = paginate_tab_items(ITEMS, filter_plan={"name": {"op": "eq", "value": "Arndt"}})
    assert total == 1
    assert result[0]["name"] == "Arndt"


def test_filter_plan_neq():
    result, total = paginate_tab_items(ITEMS, filter_plan={"name": {"op": "neq", "value": "Arndt"}})
    assert total == 2


def test_filter_plan_contains():
    result, total = paginate_tab_items(ITEMS, filter_plan={"name": {"op": "contains", "value": "ül"}})
    assert total == 1
    assert result[0]["name"] == "Müller"


def test_filter_plan_gt():
    result, total = paginate_tab_items(ITEMS, filter_plan={"amount": {"op": "gt", "value": 150}})
    assert total == 2
    assert all(r["amount"] > 150 for r in result)


def test_filter_plan_between():
    result, total = paginate_tab_items(
        ITEMS, filter_plan={"amount": {"op": "between", "value": [100, 200]}}
    )
    assert total == 2


def test_filter_plan_in():
    result, total = paginate_tab_items(
        ITEMS, filter_plan={"name": {"op": "in", "value": ["Arndt", "Ziegler"]}}
    )
    assert total == 2


def test_filter_plan_unknown_op_ignored():
    result, total = paginate_tab_items(ITEMS, filter_plan={"name": {"op": "regex", "value": ".*"}})
    assert total == 3


def test_filter_plan_combined_with_sort():
    result, total = paginate_tab_items(
        ITEMS,
        filter_plan={"amount": {"op": "gte", "value": 200}},
        sort="amount", sort_dir="desc",
    )
    assert total == 2
    assert result[0]["amount"] == 300
