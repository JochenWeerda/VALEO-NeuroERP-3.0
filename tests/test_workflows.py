"""
Tests for LangGraph Workflows
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from app.agents.workflows.bestellvorschlag import build_bestellvorschlag_workflow
from app.agents.workflows.skonto_optimizer import optimize_skonto
from app.agents.workflows.compliance_copilot import check_compliance


@pytest.mark.asyncio
async def test_skonto_optimizer():
    """Test skonto optimization workflow."""
    result = await optimize_skonto(
        available_cash=Decimal("20000.00"),
        payment_date=datetime.now()
    )
    
    assert "payment_plan" in result
    assert "total_discount" in result
    assert "recommendations" in result
    assert isinstance(result["total_discount"], float)
    assert result["total_discount"] >= 0


@pytest.mark.asyncio
async def test_compliance_copilot_customer():
    """Test compliance checking for customer."""
    result = await check_compliance(
        entity_type="customer",
        entity_id="CUST-001",
        entity_data={
            "name": "Test GmbH",
            "psm_sachkundenachweis": False  # Missing!
        }
    )
    
    assert "violations" in result
    assert "risk_score" in result
    assert "recommendations" in result
    
    # Should have violation for missing PSM-Nachweis
    assert len(result["violations"]) > 0
    assert result["risk_score"] > 0


@pytest.mark.asyncio
async def test_compliance_copilot_no_violations():
    """Test compliance checking with compliant data."""
    result = await check_compliance(
        entity_type="customer",
        entity_id="CUST-002",
        entity_data={
            "name": "Compliant GmbH",
            "psm_sachkundenachweis": True  # OK!
        }
    )
    
    assert result["risk_score"] == 0.0
    assert len(result["violations"]) == 0


def test_bestellvorschlag_workflow_build():
    """Test that bestellvorschlag workflow can be built."""
    workflow = build_bestellvorschlag_workflow()
    
    assert workflow is not None
    # Workflow compiled successfully
    assert callable(workflow)

