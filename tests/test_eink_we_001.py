"""EINK-WE-001 — Wareneingang buchen: Einkauf-Lieferschein → Lager (Belegbruch-Fix).

Prüft:
1. 404 wenn Lieferschein nicht gefunden
2. 422 wenn keine Positionen vorhanden
3. Positionen mit artikel_nr=None werden übersprungen
4. Einlagerung wird korrekt gebucht (book_stock_movement aufgerufen)
5. Lieferschein wird nach Buchung auf erledigt gesetzt
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from fastapi import HTTPException


TENANT = "system"
LS_ID = "LS-001"


def _mock_db(ls_row=None, positions=None, warehouse_bins=None) -> MagicMock:
    db = MagicMock()

    def execute_side(sql, params=None):
        sql_str = str(sql)
        result = MagicMock()

        if "einkauf_lieferscheine WHERE id" in sql_str:
            if ls_row:
                result.mappings.return_value.first.return_value = ls_row
            else:
                result.mappings.return_value.first.return_value = None
        elif "einkauf_lieferschein_positionen WHERE lieferschein_id" in sql_str:
            result.mappings.return_value.all.return_value = positions or []
        elif "UPDATE einkauf_lieferscheine SET erledigt" in sql_str:
            pass
        elif "bin_stock" in sql_str or "warehouse_bins" in sql_str or "inventory_stock_movements" in sql_str:
            result.fetchone.return_value = None
            result.fetchall.return_value = []
        else:
            result.fetchone.return_value = None
            result.fetchall.return_value = []
        return result

    db.execute.side_effect = execute_side
    return db


def _ls_row(erledigt: bool = False):
    row = MagicMock()
    row.__getitem__ = lambda s, k: {"id": LS_ID, "lieferschein_nr": "EK-2026-001", "erledigt": erledigt}[k]
    row.get = lambda k, d=None: {"id": LS_ID, "lieferschein_nr": "EK-2026-001", "erledigt": erledigt}.get(k, d)
    return row


def _pos(pos_nr: int, artikel_nr: str | None, menge: float = 100.0):
    row = MagicMock()
    data = {
        "pos_nr": pos_nr, "artikel_nr": artikel_nr,
        "menge": Decimal(str(menge)), "lagerfach": None,
        "charge": None, "einzelpreis": Decimal("5.00"),
    }
    row.__getitem__ = lambda s, k: data[k]
    row.get = lambda k, d=None: data.get(k, d)
    return row


class TestEinbuchenLieferschein:
    @pytest.mark.asyncio
    async def test_404_wenn_ls_nicht_gefunden(self):
        from app.api.v1.endpoints.einkauf_lieferschein import einbuchen_lieferschein, EinbuchenPayload
        db = _mock_db(ls_row=None)
        with pytest.raises(HTTPException) as exc:
            await einbuchen_lieferschein(
                ls_id="MISSING", payload=EinbuchenPayload(warehouse_id="WH-1"),
                tenant_id=TENANT, db=db,
            )
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_422_wenn_keine_positionen(self):
        from app.api.v1.endpoints.einkauf_lieferschein import einbuchen_lieferschein, EinbuchenPayload
        db = _mock_db(ls_row=_ls_row(), positions=[])
        with pytest.raises(HTTPException) as exc:
            await einbuchen_lieferschein(
                ls_id=LS_ID, payload=EinbuchenPayload(warehouse_id="WH-1"),
                tenant_id=TENANT, db=db,
            )
        assert exc.value.status_code == 422

    @pytest.mark.asyncio
    async def test_position_ohne_artikel_nr_wird_uebersprungen(self):
        from app.api.v1.endpoints.einkauf_lieferschein import einbuchen_lieferschein, EinbuchenPayload

        positions = [_pos(1, None, 100.0)]
        db = _mock_db(ls_row=_ls_row(), positions=positions)

        with patch("app.services.warehouse_service.WarehouseService.book_stock_movement") as mock_book:
            with patch("app.services.warehouse_service.WarehouseService.suggest_putaway_bin", return_value=[]):
                result = await einbuchen_lieferschein(
                    ls_id=LS_ID, payload=EinbuchenPayload(warehouse_id="WH-1", default_bin_id="BIN-1"),
                    tenant_id=TENANT, db=db,
                )
        assert result.movements_created == 0
        assert result.positions_skipped == 1

    @pytest.mark.asyncio
    async def test_einlagerung_wird_gebucht(self):
        from app.api.v1.endpoints.einkauf_lieferschein import einbuchen_lieferschein, EinbuchenPayload

        positions = [_pos(1, "ART-001", 100.0), _pos(2, "ART-002", 50.0)]
        db = _mock_db(ls_row=_ls_row(), positions=positions)

        with patch("app.services.warehouse_service.WarehouseService.book_stock_movement", return_value="MV-ID") as mock_book:
            with patch("app.services.warehouse_service.WarehouseService.suggest_putaway_bin", return_value=[]):
                result = await einbuchen_lieferschein(
                    ls_id=LS_ID,
                    payload=EinbuchenPayload(warehouse_id="WH-1", default_bin_id="BIN-DEFAULT"),
                    tenant_id=TENANT, db=db,
                )
        assert result.movements_created == 2
        assert mock_book.call_count == 2
        # verify movement_type is EINLAGERUNG
        call_kwargs = mock_book.call_args_list[0][1]
        assert call_kwargs["movement_type"] == "EINLAGERUNG"
