from __future__ import annotations

import asyncio
from decimal import Decimal

from app.agents.genxais_service import GENXAISService


def test_genxais_service_lists_productive_capabilities():
    service = GENXAISService()

    capabilities = service.list_capabilities(productive_only=True)

    assert [cap.capability_key for cap in capabilities] == [
        "bestellvorschlag_assistant",
        "finance_skonto_assistant",
        "compliance_copilot",
    ]


def test_genxais_service_runs_skonto_assistant():
    service = GENXAISService()

    result = asyncio.run(service.run_skonto_assistant(available_cash=Decimal("10000.00")))

    assert result["capability_key"] == "finance_skonto_assistant"
    assert "recommendations" in result


def test_genxais_service_runs_compliance_copilot():
    service = GENXAISService()

    result = asyncio.run(
        service.run_compliance_copilot(
            entity_type="customer",
            entity_id="C-1",
            entity_data={"name": "Demo Kunde", "psm_sachkundenachweis": False},
        )
    )

    assert result["capability_key"] == "compliance_copilot"
    assert result["entity_id"] == "C-1"
    assert result["violations"]
