"""Service für Präferenzkalkulationen."""

from __future__ import annotations

from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.schemas.preference import PreferenceCalculationRequest, PreferenceCalculationResponse


class PreferenceService:
    """Berechnet Ursprungseigenschaften auf Basis der Stückliste."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def calculate(self, payload: PreferenceCalculationRequest) -> PreferenceCalculationResponse:
        originating_value, total_value = self._aggregate(payload)
        ratio = (originating_value / total_value * 100) if total_value else 0
        qualifies = ratio >= 50  # Platzhalterregel
        remarks = "qualifiziert" if qualifies else "keine Präferenz"

        record = models.PreferenceCalculation(
            tenant_id=payload.tenant_id,
            bill_of_materials_id=payload.bill_of_materials_id,
            agreement_code=payload.agreement_code,
            qualifies=qualifies,
            originating_value_percent=ratio,
            remarks=remarks,
            calculation_details={
                "originating_value": originating_value,
                "total_value": total_value,
                "ruleset": payload.ruleset_override or "default",
            },
        )
        self._session.add(record)
        await self._session.flush()

        return PreferenceCalculationResponse(
            qualifies=qualifies,
            originating_value_percent=ratio,
            remarks=remarks,
            calculation_details=record.calculation_details,
        )

    @staticmethod
    def _aggregate(payload: PreferenceCalculationRequest) -> Tuple[float, float]:
        total = sum(component.value for component in payload.components)
        originating = sum(component.value for component in payload.components if component.originating)
        return originating, total
