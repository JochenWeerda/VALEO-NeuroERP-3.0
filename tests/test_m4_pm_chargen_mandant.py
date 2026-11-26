"""M4-PM: Charge-Rückkopplung, Löschschutz, Schnellerfassung-Status (ohne Live-DB)."""

from __future__ import annotations

import asyncio
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import produktion_rezepturgruppen as schnelle
from app.api.v1.endpoints import quality_lot_binding as qlb
from app.api.v1.endpoints.charges import delete_charge
from app.core.quality_lot_binding import QualityReleaseDecision
from app.domains.operations.models import ChargeStatus
from app.domains.operations.repository import ChargeRepository


TENANT = "haus-a"


def test_charge_delete_fehlt_liefert_false():
    db = MagicMock()
    repo = ChargeRepository(db, TENANT)
    repo.get_by_id = MagicMock(return_value=None)  # type: ignore[method-assign]
    assert repo.delete("missing") is False
    db.delete.assert_not_called()


def test_charge_delete_blockiert_freigegebene():
    db = MagicMock()
    repo = ChargeRepository(db, TENANT)
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


def test_charge_delete_blockiert_qualitaetsstatus_freigegeben():
    db = MagicMock()
    repo = ChargeRepository(db, TENANT)
    charge = SimpleNamespace(
        id="CH-1b",
        chargen_id="LOT-1b",
        status=ChargeStatus.ERFASST.value,
        qualitaetsstatus=ChargeStatus.FREIGEGEBEN.value,
    )
    repo.get_by_id = MagicMock(return_value=charge)  # type: ignore[method-assign]
    with pytest.raises(ValueError, match="Freigegebene"):
        repo.delete("CH-1b")
    db.delete.assert_not_called()


def test_charge_delete_blockiert_produktionsbezug():
    db = MagicMock()
    db.execute.return_value.first.return_value = (1,)
    repo = ChargeRepository(db, TENANT)
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
    repo = ChargeRepository(db, TENANT)
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


def test_delete_charge_endpoint_409_bei_loeschschutz():
    db = MagicMock()
    with patch("app.api.v1.endpoints.charges.ChargeRepository") as repo_cls:
        repo_cls.return_value.delete.side_effect = ValueError(
            "Freigegebene Charge darf nicht gelöscht werden."
        )
        with pytest.raises(HTTPException) as exc:
            asyncio.run(delete_charge("CH-1", db=db, tenant_id=TENANT))
    assert exc.value.status_code == 409
    assert "Freigegebene" in str(exc.value.detail)


def test_delete_charge_endpoint_404_wenn_fehlt():
    db = MagicMock()
    with patch("app.api.v1.endpoints.charges.ChargeRepository") as repo_cls:
        repo_cls.return_value.delete.return_value = False
        with pytest.raises(HTTPException) as exc:
            asyncio.run(delete_charge("CH-missing", db=db, tenant_id=TENANT))
    assert exc.value.status_code == 404


def test_delete_charge_endpoint_ok():
    db = MagicMock()
    with patch("app.api.v1.endpoints.charges.ChargeRepository") as repo_cls:
        repo_cls.return_value.delete.return_value = True
        result = asyncio.run(delete_charge("CH-ok", db=db, tenant_id=TENANT))
    assert result is None


def test_release_decision_aktualisiert_ops_chargen_nur_im_mandanten():
    lot_row = MagicMock()
    lot_row._mapping = {
        "lot_id": "LOT-M4",
        "tenant_id": TENANT,
        "acceptance_id": None,
        "contract_id": None,
        "protocol_id": None,
        "moisture_pct": Decimal("14.5"),
        "impurities_pct": None,
        "protein_pct": Decimal("12.0"),
        "hl_weight": None,
        "overall_grade": None,
        "price_deduction_pct": Decimal("0"),
        "approval_status": "pending",
    }
    db = MagicMock()

    def execute_side(sql, params=None):
        sql_str = str(sql)
        result = MagicMock()
        if "information_schema.tables" in sql_str:
            result.scalar.return_value = 1
        elif "quality_lot_profiles" in sql_str and "SELECT" in sql_str:
            result.fetchone.return_value = lot_row
        else:
            result.fetchone.return_value = None
        return result

    db.execute.side_effect = execute_side
    decision = QualityReleaseDecision(
        lot_id="LOT-M4",
        protocol_id="PROTO-M4",
        decision="approve",
        decided_by="qa",
        decided_at="2026-06-13T10:00:00",
    )
    asyncio.run(
        qlb.create_release_decision(
            lot_id="LOT-M4", decision=decision, tenant_id=TENANT, db=db
        )
    )
    chargen_updates = [
        (str(c.args[0]), c.args[1] if len(c.args) > 1 else {})
        for c in db.execute.call_args_list
        if "ops_chargen" in str(c.args[0])
    ]
    assert chargen_updates, "ops_chargen-Update fehlt"
    sql, params = chargen_updates[-1]
    assert "tenant_id = :tid" in sql
    assert params.get("tid") == TENANT
    assert params.get("cid") == "LOT-M4"
    assert params.get("qs") == "freigegeben"


def test_schnellerfassung_legt_auftrag_als_erstellt_an():
    vorlage = MagicMock()
    vorlage._mapping = {
        "id": "VORL-1",
        "bezeichnung": "Standard-Mix",
        "rezept_id": "RZ-1",
        "rezept_name": "Milchvieh 18",
        "standard_menge_t": Decimal("2.5"),
        "ziel_lager_id": None,
        "abteilung": None,
        "anzahl_auftraege": 0,
        "aktiv": True,
    }
    db = MagicMock()
    select_result = MagicMock()
    select_result.fetchone.return_value = vorlage
    db.execute.return_value = select_result

    payload = schnelle.SchnellerfassungBuchenPayload(
        menge_t=Decimal("3.0"), chargen_id="CH-SCHNELL-1"
    )
    with patch.object(schnelle, "uuid7", return_value="AUF-1"):
        result = schnelle.buche_schnellerfassung(
            vorlage_id="VORL-1", payload=payload, db=db, tenant_id=TENANT
        )

    assert result["status"] == "erstellt"
    assert "Freigabe" in result["hinweis"]
    insert_sqls = [str(c.args[0]) for c in db.execute.call_args_list]
    assert any(
        "'erstellt'" in s and "futtermittel_produktionsauftraege" in s for s in insert_sqls
    )
    db.commit.assert_called_once()
