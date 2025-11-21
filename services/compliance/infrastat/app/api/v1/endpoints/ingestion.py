"""ETL-Ingestion-Endpunkte."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import date
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session, get_event_bus, get_validator
from app.etl.loader import IterableSourceLoader
from app.etl.transformer import InfrastatTransformer
from app.schemas.declaration import ETLJobResult
from app.services.ingestion_service import InfrastatIngestionService
from app.integration.event_bus import EventBus


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/batch", response_model=ETLJobResult, status_code=status.HTTP_201_CREATED)
async def ingest_batch(
    payload: Dict[str, Any],
    tenant_id: str,
    reference_period: date,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    event_bus: EventBus | None = Depends(get_event_bus),
) -> ETLJobResult:
    """Nimmt rohe Belegdaten entgegen und startet ETL + Validierung."""

    ingestion_service = InfrastatIngestionService(session)
    validator = get_validator()

    loader = IterableSourceLoader()
    raw_records = list(loader.load(payload.get("records", [])))
    transformer = InfrastatTransformer(reference_period=reference_period, tenant_id=tenant_id, flow_type=payload.get("flow_type"))
    batch_payload, warnings = transformer.transform(raw_records)
    metadata = payload.get("metadata", {}) or {}
    if payload.get("sender"):
        metadata.setdefault("sender", payload["sender"])
    if payload.get("receiver"):
        metadata.setdefault("receiver", payload["receiver"])
    batch_payload.metadata.update(metadata)

    start_ts = time.perf_counter()

    async with session.begin():
        batch, result = await ingestion_service.ingest_and_validate(
            batch_payload,
            validator,
            tenant_id=tenant_id,
            event_bus=event_bus,
            warnings=warnings,
        )

    duration = time.perf_counter() - start_ts
    result = result.model_copy(update={"duration_seconds": duration})

    # Trigger async Folgeprozesse (z. B. Validierungen, Aggregationen)
    background_tasks.add_task(_start_validation_pipeline, batch.id, tenant_id)

    if result.ingested_lines == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Keine gültigen Datensätze importiert.",
        )

    return result


async def _start_validation_pipeline(batch_id: Any, tenant_id: str) -> None:
    logger.info("Starte asynchrone Validierung für Batch %s (%s)", batch_id, tenant_id)
    await asyncio.sleep(0)  # Platzhalter für zukünftige async Tasks

