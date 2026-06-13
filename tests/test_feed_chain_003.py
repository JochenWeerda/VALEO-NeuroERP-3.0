"""FEED-CHAIN-003 — quality_lot_binding DB-Persistenz + Charge-Rückkopplung.

Prüft die Kern-Logik des rewritten Endpoints ohne echte DB:
1. _ensure_tables wirft 503 wenn Tabelle nicht existiert
2. create_lot schreibt INSERT ON CONFLICT
3. release-decision approve → qualitaetsstatus freigegeben auf ops_chargen
4. release-decision reject → qualitaetsstatus gesperrt
5. 404 wenn Lot nicht gefunden
"""

from __future__ import annotations

from unittest.mock import MagicMock, AsyncMock, patch
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.core.quality_lot_binding import LotQualityProfile, QualityReleaseDecision


TENANT = "00000000-0000-0000-0000-000000000001"


def _mock_db(tables_ready: bool = True, lot_row=None) -> MagicMock:
    db = MagicMock()

    def execute_side(sql, params=None):
        sql_str = str(sql) if not isinstance(sql, str) else sql
        mock_result = MagicMock()
        if "information_schema.tables" in sql_str:
            mock_result.scalar.return_value = 1 if tables_ready else 0
        elif "quality_lot_profiles" in sql_str and "SELECT" in sql_str:
            mock_result.fetchone.return_value = lot_row
            mock_result.fetchall.return_value = [lot_row] if lot_row else []
        else:
            mock_result.fetchone.return_value = None
            mock_result.fetchall.return_value = []
        return mock_result

    db.execute.side_effect = execute_side
    return db


def _make_lot(lot_id: str = "LOT-001") -> LotQualityProfile:
    return LotQualityProfile(
        lot_id=lot_id, tenant_id=TENANT, moisture_pct=14.5,
        protein_pct=12.0, approval_status="pending",
    )


def _make_lot_row(lot_id: str = "LOT-001"):
    row = MagicMock()
    row._mapping = {
        "lot_id": lot_id, "tenant_id": TENANT, "acceptance_id": None,
        "contract_id": None, "protocol_id": None, "moisture_pct": Decimal("14.5"),
        "impurities_pct": None, "protein_pct": Decimal("12.0"), "hl_weight": None,
        "overall_grade": None, "price_deduction_pct": Decimal("0"),
        "approval_status": "pending",
    }
    return row


class TestEnsureTables:
    def test_raises_503_wenn_tabelle_fehlt(self):
        from app.api.v1.endpoints.quality_lot_binding import _ensure_tables
        db = _mock_db(tables_ready=False)
        with pytest.raises(HTTPException) as exc_info:
            _ensure_tables(db)
        assert exc_info.value.status_code == 503

    def test_kein_fehler_wenn_tabelle_vorhanden(self):
        from app.api.v1.endpoints.quality_lot_binding import _ensure_tables
        db = _mock_db(tables_ready=True)
        _ensure_tables(db)  # kein Fehler


class TestRowToProfile:
    def test_konvertiert_db_row_korrekt(self):
        from app.api.v1.endpoints.quality_lot_binding import _row_to_profile
        row = _make_lot_row()
        profile = _row_to_profile(row)
        assert profile.lot_id == "LOT-001"
        assert profile.moisture_pct == pytest.approx(14.5)
        assert profile.approval_status == "pending"


@pytest.mark.asyncio
class TestCreateLot:
    async def test_upsert_aufgerufen(self):
        from app.api.v1.endpoints.quality_lot_binding import create_lot
        db = _mock_db()
        profile = _make_lot()
        result = await create_lot(profile=profile, tenant_id=TENANT, db=db)
        assert result.lot_id == "LOT-001"
        assert result.tenant_id == TENANT
        # INSERT ON CONFLICT muss ausgeführt worden sein
        insert_calls = [str(c.args[0]) for c in db.execute.call_args_list]
        assert any("INSERT INTO domain_ops.quality_lot_profiles" in s for s in insert_calls)
        db.commit.assert_called_once()


@pytest.mark.asyncio
class TestReleaseDecision:
    async def test_approve_setzt_freigegeben_auf_chargen(self):
        from app.api.v1.endpoints.quality_lot_binding import create_release_decision
        lot_row = _make_lot_row("MF-CHARGE-001")
        db = _mock_db(lot_row=lot_row)
        decision = QualityReleaseDecision(
            lot_id="MF-CHARGE-001", protocol_id="PROTO-1",
            decision="approve", decided_by="qa-user",
            decided_at="2026-06-13T10:00:00",
        )
        await create_release_decision(
            lot_id="MF-CHARGE-001", decision=decision, tenant_id=TENANT, db=db
        )
        update_calls = [str(c.args[0]) for c in db.execute.call_args_list]
        assert any(
            "ops_chargen" in s and "freigegeben" in str(c.args[1] or {})
            for c, s in zip(db.execute.call_args_list, update_calls)
        ), "Charge-Update auf freigegeben fehlt"

    async def test_reject_setzt_gesperrt_auf_chargen(self):
        from app.api.v1.endpoints.quality_lot_binding import create_release_decision
        lot_row = _make_lot_row("MF-CHARGE-002")
        db = _mock_db(lot_row=lot_row)
        decision = QualityReleaseDecision(
            lot_id="MF-CHARGE-002", protocol_id="PROTO-2",
            decision="reject", decided_by="qa-user",
            decided_at="2026-06-13T10:00:00",
            reason="Mykotoxin-Grenzwert überschritten",
        )
        await create_release_decision(
            lot_id="MF-CHARGE-002", decision=decision, tenant_id=TENANT, db=db
        )
        all_args = [str(c.args) for c in db.execute.call_args_list]
        assert any("gesperrt" in s for s in all_args), "Charge-Update auf gesperrt fehlt"

    async def test_404_wenn_lot_nicht_gefunden(self):
        from app.api.v1.endpoints.quality_lot_binding import create_release_decision
        db = _mock_db(lot_row=None)
        decision = QualityReleaseDecision(
            lot_id="MISSING", protocol_id="P1",
            decision="approve", decided_by="u", decided_at="2026-06-13T10:00:00",
        )
        with pytest.raises(HTTPException) as exc_info:
            await create_release_decision(lot_id="MISSING", decision=decision, tenant_id=TENANT, db=db)
        assert exc_info.value.status_code == 404
