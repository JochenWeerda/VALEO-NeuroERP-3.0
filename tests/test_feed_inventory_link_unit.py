"""Unit-Tests für FeedInventoryLinkService (FEED-CHAIN-004, COV-RATCHET)."""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.feed_inventory_link_service import (
    FeedInventoryLinkError,
    FeedInventoryLinkService,
    _movement_reference,
)


class TestMovementReference:
    def test_reference_max_length(self):
        ref = _movement_reference(
            "019ef36f-755b-75e3-897a-1d2687a48b8e",
            "IT-EF1-53b3b710",
            "out",
        )
        assert len(ref) <= 50
        assert ref.endswith("O")

    def test_in_suffix(self):
        ref = _movement_reference("prod-1", "ef-2", "in")
        assert ref.endswith("I")


def _mock_execute_db(responses: list):
  """Sequential db.execute() results; each item is .first() return or list for mappings."""
  db = MagicMock()
  it = iter(responses)

  def side_effect(stmt, params=None):
    m = MagicMock()
    try:
      val = next(it)
    except StopIteration:
      m.first.return_value = None
      m.mappings.return_value.first.return_value = None
      m.mappings.return_value.all.return_value = []
      return m
    if isinstance(val, list):
      m.mappings.return_value.all.return_value = val
      m.mappings.return_value.first.return_value = val[0] if val else None
    else:
      m.first.return_value = val
      m.mappings.return_value.first.return_value = val
    return m

  db.execute.side_effect = side_effect
  return db


class TestFeedInventoryLinkService:
    TENANT = "00000000-0000-0000-0000-000000000001"

    def test_resolve_warehouse_id_none_without_row(self):
        db = _mock_execute_db([None])
        svc = FeedInventoryLinkService(db, self.TENANT)
        assert svc.resolve_warehouse_id() is None

    def test_resolve_warehouse_id_returns_string(self):
        db = _mock_execute_db([("wh-1",)])
        svc = FeedInventoryLinkService(db, self.TENANT)
        assert svc.resolve_warehouse_id() == "wh-1"

    def test_book_snapshot_fail_soft_without_warehouse(self):
        db = _mock_execute_db([None])
        svc = FeedInventoryLinkService(db, self.TENANT)
        result = svc.book_snapshot_movements(
            snapshot=[{"einzelfutter_id": "ef-1", "menge_t": 1.0, "name": "Weizen"}],
            direction=-1,
            production_order_id="prod-1",
            booked_by="test",
        )
        assert result["ok"] is False
        assert result["reason"] == "no_warehouse"

    def test_list_links_counts_mapped(self):
        rows = [
            {"id": "ef-1", "inventory_article_id": "a-1", "artikel_nummer": "E1", "name": "A", "verfuegbar_t": 10},
            {"id": "ef-2", "inventory_article_id": None, "artikel_nummer": "E2", "name": "B", "verfuegbar_t": 5},
        ]
        db = _mock_execute_db([rows])
        svc = FeedInventoryLinkService(db, self.TENANT)
        out = svc.list_links(limit=10)
        assert out["total"] == 2
        assert out["mapped_count"] == 1
        assert out["unmapped_count"] == 1

    def test_ensure_article_link_already_mapped(self):
        ef = SimpleNamespace(
            id="ef-1",
            artikel_nummer="EF-1",
            name="Weizen",
            art="Energiefutter",
            inventory_article_id="art-existing",
        )
        db = MagicMock()
        db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = ef
        svc = FeedInventoryLinkService(db, self.TENANT)
        result = svc.ensure_article_link("ef-1")
        assert result == {"ok": True, "created": False, "article_id": "art-existing"}

    def test_ensure_article_link_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = None
        svc = FeedInventoryLinkService(db, self.TENANT)
        with pytest.raises(FeedInventoryLinkError, match="nicht gefunden"):
            svc.ensure_article_link("missing")

    def test_book_snapshot_skips_zero_quantity(self):
        ef = SimpleNamespace(
            id="ef-1",
            artikel_nummer="EF-1",
            name="Weizen",
            art="Energiefutter",
            inventory_article_id="art-1",
        )
        db = MagicMock()
        db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = ef
        db.execute.return_value.first.side_effect = [
            ("wh-1",),  # resolve warehouse
            None,  # idempotency check
        ]
        svc = FeedInventoryLinkService(db, self.TENANT)
        result = svc.book_snapshot_movements(
            snapshot=[{"einzelfutter_id": "ef-1", "menge_t": 0, "name": "Weizen"}],
            direction=-1,
            production_order_id="prod-1",
            booked_by="test",
            warehouse_id="wh-1",
        )
        assert result["ok"] is True
        assert result["movements"] == []

    def test_get_link_raises_when_missing(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        svc = FeedInventoryLinkService(db, self.TENANT)
        with pytest.raises(FeedInventoryLinkError):
            svc.get_link("nope")

    def test_get_link_with_article(self):
        ef = SimpleNamespace(
            id="ef-1",
            artikel_nummer="EF-1",
            name="Weizen",
            inventory_article_id="art-1",
            verfuegbar_t=Decimal("12.5"),
        )
        article_row = {"id": "art-1", "article_number": "EF-1", "name": "Weizen"}
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = ef
        db.execute.return_value.mappings.return_value.first.return_value = article_row
        svc = FeedInventoryLinkService(db, self.TENANT)
        link = svc.get_link("ef-1")
        assert link["inventory_article_id"] == "art-1"
        assert link["article"]["article_number"] == "EF-1"
        assert link["verfuegbar_t"] == pytest.approx(12.5)
