"""
Tests for Commodity Position Matrix: calculation, guard, override, severity, KPI, rules.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.position_service import (
    PositionCalculationService,
    _period_key,
    _periods_between,
    PERIOD_MODE_MONTH,
    SEVERITY_RED,
    SEVERITY_YELLOW,
    SEVERITY_GREEN,
)
from app.services.position_guard_service import PositionGuardService
from app.domains.operations.models import PosPositionRule, PosPositionOverride, KonContract, KonContractLine

try:
    from main import app
except ImportError:
    try:
        from app.main import app
    except ImportError:
        app = None

TENANT = "test-tenant-pos-001"
BRANCH = "NL-TEST"


@pytest.fixture
def db() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


class TestPeriodHelpers:
    def test_period_key_month(self):
        dt = datetime(2026, 5, 15)
        assert _period_key(dt, PERIOD_MODE_MONTH) == "2026-05"

    def test_period_key_none(self):
        assert _period_key(None, PERIOD_MODE_MONTH) is None

    def test_periods_between_month(self):
        out = _periods_between("2026-04", "2026-06", PERIOD_MODE_MONTH)
        assert out == ["2026-04", "2026-05", "2026-06"]


class TestPositionCalculationService:
    def test_calculate_matrix_empty(self, db: Session):
        svc = PositionCalculationService(db)
        result = svc.calculate_matrix(
            tenant_id=TENANT,
            branch_id=BRANCH,
            as_of_date=date(2026, 5, 1),
            period_mode=PERIOD_MODE_MONTH,
            period_from="2026-04",
            period_to="2026-05",
            article_ids=None,
        )
        assert result.period_keys == ["2026-04", "2026-05"]
        assert result.rows == []

    def test_net_calculation_per_period(self, db: Session):
        """With one EK (200 rest) and one VK (50 rest) in 2026-05, net = 150."""
        from app.core.uuid7 import uuid7
        cid_ek = uuid7()
        cid_vk = uuid7()
        lid_ek = uuid7()
        lid_vk = uuid7()
        db.add(
            KonContract(
                contract_id=cid_ek,
                contract_no="T-EK-001",
                contract_type="EINKAUF",
                branch_id=BRANCH,
                party_id="P1",
                contract_date=datetime(2026, 5, 1),
                valid_from=datetime(2026, 5, 1),
                valid_to=datetime(2026, 5, 31),
                quantity_type="GESAMTKONTRAKT",
                total_quantity=Decimal("200"),
                unit="t",
                status="OFFEN",
                tenant_id=TENANT,
                created_by="test",
                updated_by="test",
            )
        )
        db.add(
            KonContractLine(
                line_id=lid_ek,
                contract_id=cid_ek,
                position_no=1,
                article_id="Raps",
                qty_contract=Decimal("200"),
                tenant_id=TENANT,
                created_by="test",
                updated_by="test",
            )
        )
        db.add(
            KonContract(
                contract_id=cid_vk,
                contract_no="T-VK-001",
                contract_type="VERKAUF",
                branch_id=BRANCH,
                party_id="P2",
                contract_date=datetime(2026, 5, 1),
                valid_from=datetime(2026, 5, 1),
                valid_to=datetime(2026, 5, 31),
                quantity_type="GESAMTKONTRAKT",
                total_quantity=Decimal("100"),
                unit="t",
                status="OFFEN",
                tenant_id=TENANT,
                created_by="test",
                updated_by="test",
            )
        )
        db.add(
            KonContractLine(
                line_id=lid_vk,
                contract_id=cid_vk,
                position_no=1,
                article_id="Raps",
                qty_contract=Decimal("100"),
                tenant_id=TENANT,
                created_by="test",
                updated_by="test",
            )
        )
        from app.domains.operations.models import KonContractMovement
        db.add(
            KonContractMovement(
                movement_id=uuid7(),
                contract_id=cid_vk,
                line_id=lid_vk,
                movement_date=datetime(2026, 5, 1),
                quantity=Decimal("50"),
                tenant_id=TENANT,
                created_by="test",
            )
        )
        db.commit()

        svc = PositionCalculationService(db)
        result = svc.calculate_matrix(
            tenant_id=TENANT,
            branch_id=BRANCH,
            as_of_date=date(2026, 5, 15),
            period_mode=PERIOD_MODE_MONTH,
            period_from="2026-05",
            period_to="2026-05",
            article_ids=["Raps"],
        )
        assert len(result.rows) == 1
        row = result.rows[0]
        assert row.article_id == "Raps"
        assert row.sum_buy_open == Decimal("200")
        assert row.sum_sell_open == Decimal("50")
        assert row.sum_net == Decimal("150")
        assert len(row.cells) == 1
        assert row.cells[0].qty_net == Decimal("150")

    def test_view_mode_physisch_disponiert_only_open(self, db: Session):
        """Mit view_mode physisch_disponiert (Default) zählen nur OFFEN-Kontrakte."""
        from app.core.uuid7 import uuid7
        cid_open = uuid7()
        cid_erledigt = uuid7()
        lid_open = uuid7()
        lid_erledigt = uuid7()
        db.add(
            KonContract(
                contract_id=cid_open,
                contract_no="T-EK-OFFEN",
                contract_type="EINKAUF",
                branch_id=BRANCH,
                party_id="P1",
                contract_date=datetime(2026, 5, 1),
                valid_from=datetime(2026, 5, 1),
                valid_to=datetime(2026, 5, 31),
                quantity_type="GESAMTKONTRAKT",
                total_quantity=Decimal("100"),
                unit="t",
                status="OFFEN",
                tenant_id=TENANT,
                created_by="test",
                updated_by="test",
            )
        )
        db.add(
            KonContractLine(
                line_id=lid_open,
                contract_id=cid_open,
                position_no=1,
                article_id="Maismehl",
                qty_contract=Decimal("100"),
                tenant_id=TENANT,
                created_by="test",
                updated_by="test",
            )
        )
        db.add(
            KonContract(
                contract_id=cid_erledigt,
                contract_no="T-EK-ERLEDIGT",
                contract_type="EINKAUF",
                branch_id=BRANCH,
                party_id="P1",
                contract_date=datetime(2026, 5, 1),
                valid_from=datetime(2026, 5, 1),
                valid_to=datetime(2026, 5, 31),
                quantity_type="GESAMTKONTRAKT",
                total_quantity=Decimal("50"),
                unit="t",
                status="ERLEDIGT",
                tenant_id=TENANT,
                created_by="test",
                updated_by="test",
            )
        )
        db.add(
            KonContractLine(
                line_id=lid_erledigt,
                contract_id=cid_erledigt,
                position_no=1,
                article_id="Maismehl",
                qty_contract=Decimal("50"),
                tenant_id=TENANT,
                created_by="test",
                updated_by="test",
            )
        )
        db.commit()

        svc = PositionCalculationService(db)
        result_default = svc.calculate_matrix(
            tenant_id=TENANT,
            branch_id=BRANCH,
            as_of_date=date(2026, 5, 15),
            period_mode=PERIOD_MODE_MONTH,
            period_from="2026-05",
            period_to="2026-05",
            article_ids=["Maismehl"],
            view_mode="physisch_disponiert",
        )
        result_archiv = svc.calculate_matrix(
            tenant_id=TENANT,
            branch_id=BRANCH,
            as_of_date=date(2026, 5, 15),
            period_mode=PERIOD_MODE_MONTH,
            period_from="2026-05",
            period_to="2026-05",
            article_ids=["Maismehl"],
            view_mode="inkl_archiv",
        )
        assert len(result_default.rows) == 1
        assert len(result_archiv.rows) == 1
        assert result_default.rows[0].article_id == "Maismehl"
        assert result_archiv.rows[0].article_id == "Maismehl"
        assert result_default.rows[0].sum_buy_open == Decimal("100")
        assert result_archiv.rows[0].sum_buy_open == Decimal("150")


class TestSeverityClassification:
    def test_severity_green_without_rule(self, db: Session):
        svc = PositionCalculationService(db)
        rule = None
        assert svc._severity(Decimal("100"), rule) == SEVERITY_GREEN

    def test_severity_red_below_tolerance(self, db: Session):
        from app.core.uuid7 import uuid7
        r = PosPositionRule(
            rule_id=uuid7(),
            scope_type="ARTICLE",
            scope_id="Raps",
            neg_tolerance_qty=Decimal("-50"),
            red_threshold=Decimal("-100"),
            tenant_id=TENANT,
            created_by="test",
            updated_by="test",
        )
        db.add(r)
        db.commit()
        svc = PositionCalculationService(db)
        assert svc._severity(Decimal("-60"), r) == SEVERITY_RED
        assert svc._severity(Decimal("-30"), r) in (SEVERITY_YELLOW, SEVERITY_RED)


class TestPositionGuardService:
    def test_check_impact_allowed_above_tolerance(self, db: Session):
        guard = PositionGuardService(db)
        result = guard.check_impact(
            tenant_id=TENANT,
            branch_id=BRANCH,
            article_id="X",
            period_key="2026-05",
            delta_sell_qty=Decimal("10"),
            user_roles=["user"],
        )
        assert result.allowed is True

    def test_request_override(self, db: Session):
        guard = PositionGuardService(db)
        row = guard.request_override(
            tenant_id=TENANT,
            branch_id=BRANCH,
            article_id="Raps",
            period_key="2026-05",
            requested_by="test_user",
            reason="Test",
        )
        db.commit()
        assert row.override_id
        assert row.status == "REQUESTED"


@pytest.mark.skipif(app is None, reason="main app not importable")
class TestPositionsAPI:
    def test_get_matrix_requires_auth(self):
        client = TestClient(app)
        r = client.get("/api/v1/positions/matrix?period_from=2026-04&period_to=2026-05")
        assert r.status_code in (401, 403)

    def test_get_matrix_with_dev_token(self):
        client = TestClient(app)
        r = client.get(
            "/api/v1/positions/matrix?period_from=2026-04&period_to=2026-05",
            headers={"Authorization": "Bearer dev-token", "X-Tenant-ID": TENANT},
        )
        assert r.status_code == 200
        data = r.json()
        assert "period_keys" in data
        assert "rows" in data

    def test_get_kpi_with_dev_token(self):
        client = TestClient(app)
        r = client.get(
            "/api/v1/positions/kpi?period_from=2026-04&period_to=2026-05",
            headers={"Authorization": "Bearer dev-token", "X-Tenant-ID": TENANT},
        )
        assert r.status_code == 200
        data = r.json()
        assert "short_cell_count" in data
        assert "max_short_qty" in data

    def test_get_matrix_accepts_view_mode(self):
        client = TestClient(app)
        r = client.get(
            "/api/v1/positions/matrix?period_from=2026-04&period_to=2026-05&view_mode=inkl_archiv",
            headers={"Authorization": "Bearer dev-token", "X-Tenant-ID": TENANT},
        )
        assert r.status_code == 200
        data = r.json()
        assert "period_keys" in data
        assert "rows" in data
