"""Ingestion-Service für InfraStat-Daten."""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Iterable, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.etl.validator import InfrastatValidator
from app.integration.event_bus import EventBus
from app.metrics import VALIDATION_FAILURE_TOTAL, VALIDATION_SUCCESS_TOTAL
from app.schemas.declaration import DeclarationBatchCreate, DeclarationLineCreate, ETLJobResult

logger = logging.getLogger(__name__)


class InfrastatIngestionService:
    """Kapselt ETL/Validierungslogik."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def ingest_and_validate(
        self,
        payload: DeclarationBatchCreate,
        validator: InfrastatValidator,
        *,
        tenant_id: str,
        event_bus: EventBus | None = None,
        warnings: list[str] | None = None,
    ) -> tuple[models.DeclarationBatch, ETLJobResult]:
        """Umfasst Ingestion, Validierung und Statusmanagement in einem Schritt."""

        started = time.perf_counter()
        batch = await self.ingest_batch(payload)
        await self.update_status(batch, models.DeclarationStatus.VALIDATING)

        validation_errors, valid_lines = validator.validate_lines(payload.lines)
        error_count = await self.record_validation_errors(batch, tenant_id, validation_errors)

        if error_count > 0:
            await self.update_status(batch, models.DeclarationStatus.ERROR)
            VALIDATION_FAILURE_TOTAL.inc()
            if event_bus:
                await event_bus.publish(
                    event_type="intrastat.validation.failed",
                    tenant=tenant_id,
                    data={
                        "batch_id": str(batch.id),
                        "reference_period": batch.reference_period.isoformat(),
                        "error_count": error_count,
                    },
                )
        else:
            await self.update_status(batch, models.DeclarationStatus.READY)
            VALIDATION_SUCCESS_TOTAL.inc()
            if event_bus:
                await event_bus.publish(
                    event_type="intrastat.validation.completed",
                    tenant=tenant_id,
                    data={"batch_id": str(batch.id), "reference_period": batch.reference_period.isoformat()},
                )

        duration_seconds = time.perf_counter() - started
        result = await self.build_etl_result(
            batch=batch,
            tenant_id=tenant_id,
            ingested=len(valid_lines),
            skipped=len(payload.lines) - len(valid_lines),
            validation_errors=error_count,
            warnings=warnings or [],
            duration_seconds=duration_seconds,
        )
        return batch, result

    async def ingest_batch(self, payload: DeclarationBatchCreate) -> models.DeclarationBatch:
        batch = models.DeclarationBatch(
            tenant_id=payload.tenant_id,
            flow_type=payload.flow_type,
            reference_period=payload.reference_period,
            metadata=payload.metadata,
            status=models.DeclarationStatus.COLLECTING,
            item_count=len(payload.lines),
        )
        self._session.add(batch)
        await self._session.flush()

        line_models = [
            models.DeclarationLine(
                batch_id=batch.id,
                tenant_id=payload.tenant_id,
                sequence_no=line.sequence_no,
                commodity_code=line.commodity_code,
                country_of_origin=line.country_of_origin,
                country_of_destination=line.country_of_destination,
                net_mass_kg=line.net_mass_kg,
                supplementary_units=line.supplementary_units,
                invoice_value_eur=line.invoice_value_eur,
                statistical_value_eur=line.statistical_value_eur,
                nature_of_transaction=line.nature_of_transaction,
                transport_mode=line.transport_mode,
                delivery_terms=line.delivery_terms,
                line_data=line.line_data,
            )
            for line in payload.lines
        ]
        self._session.add_all(line_models)
        await self._session.flush()

        await self._update_batch_totals(batch, line_models)
        return batch

    async def _update_batch_totals(
        self,
        batch: models.DeclarationBatch,
        lines: Sequence[models.DeclarationLine],
    ) -> None:
        value_sum = sum((line.invoice_value_eur or 0) for line in lines)
        weight_sum = sum((line.net_mass_kg or 0) for line in lines)
        batch.total_value_eur = value_sum
        batch.total_weight_kg = weight_sum
        batch.updated_at = datetime.utcnow()
        await self._session.flush()

    async def update_status(self, batch: models.DeclarationBatch, status: models.DeclarationStatus) -> None:
        batch.status = status
        batch.updated_at = datetime.utcnow()
        await self._session.flush()

    async def record_validation_errors(
        self,
        batch: models.DeclarationBatch,
        tenant_id: str,
        errors: Iterable[dict],
    ) -> int:
        error_models = [
            models.ValidationError(
                batch_id=batch.id,
                tenant_id=tenant_id,
                line_id=error.get("line_id"),
                code=error["code"],
                severity=error["severity"],
                message=error["message"],
                details=error.get("details", {}),
            )
            for error in errors
        ]
        if not error_models:
            return 0
        self._session.add_all(error_models)
        await self._session.flush()
        return len(error_models)

    async def build_etl_result(
        self,
        batch: models.DeclarationBatch,
        tenant_id: str,
        ingested: int,
        skipped: int,
        validation_errors: int,
        warnings: list[str] | None = None,
        duration_seconds: float = 0.0,
    ) -> ETLJobResult:
        return ETLJobResult(
            batch_id=batch.id,
            tenant_id=tenant_id,
            ingested_lines=ingested,
            skipped_lines=skipped,
            validation_error_count=validation_errors,
            warnings=warnings or [],
            duration_seconds=duration_seconds,
        )

