"""M4-PM: Charge-Rückkopplung und Löschschutz (ohne Live-DB)."""

from __future__ import annotations

import inspect
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.api.v1.endpoints import produktion_rezepturgruppen as schnelle
from app.api.v1.endpoints import quality_lot_binding as qlb
from app.domains.operations.models import ChargeStatus
from app.domains.operations.repository import ChargeRepository


def test_release_decision_aktualisiert_ops_chargen_nur_im_mandanten():
    src = inspect.getsource(qlb.create_release_decision)
    assert "WHERE chargen_id = :cid AND tenant_id = :tid" in src


def test_schnellerfassung_legt_auftrag_als_erstellt_an():
    src = inspect.getsource(schnelle.buche_schnellerfassung)
    assert ", 'erstellt'," in src
    assert "status\": \"erstellt\"" in src or "\"status\": \"erstellt\"" in src


def test_charge_delete_blockiert_freigegebene():
    db = MagicMock()
    repo = ChargeRepository(db, "haus-a")
    charge = SimpleNamespace(
        id="CH-1",
        chargen_id="LOT-1",
        status=ChargeStatus.FREIGEGEBEN.value,
        qualitaetsstatus="erfasst",
    )
    repo.get_by_id = MagicMock(return_value=charge)  # type: ignore[method-assign]
    with pytest.raises(ValueError, match="Freigegebene"):
        repo.delete("CH-1")
    db.delete.assert_not_called()


def test_charge_delete_blockiert_produktionsbezug():
    db = MagicMock()
    db.execute.return_value.first.return_value = (1,)
    repo = ChargeRepository(db, "haus-a")
    charge = SimpleNamespace(
        id="CH-2",
        chargen_id="LOT-2",
        status=ChargeStatus.ERFASST.value,
        qualitaetsstatus="erfasst",
    )
    repo.get_by_id = MagicMock(return_value=charge)  # type: ignore[method-assign]
    with pytest.raises(ValueError, match="Produktionsauftrag"):
        repo.delete("CH-2")
    db.delete.assert_not_called()


def test_charge_delete_erlaubt_ohne_bindung():
    db = MagicMock()
    db.execute.return_value.first.return_value = None
    repo = ChargeRepository(db, "haus-a")
    charge = SimpleNamespace(
        id="CH-3",
        chargen_id="LOT-3",
        status=ChargeStatus.ERFASST.value,
        qualitaetsstatus="erfasst",
    )
    repo.get_by_id = MagicMock(return_value=charge)  # type: ignore[method-assign]
    assert repo.delete("CH-3") is True
    db.delete.assert_called_once_with(charge)
    db.commit.assert_called_once()
