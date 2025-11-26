"""Erzeugt IDEV-konforme Meldungen und protokolliert die Einreichung."""

from __future__ import annotations

import asyncio
import hashlib
import logging
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import models
from app.integration.event_bus import EventBus
from app.metrics import (
    SUBMISSION_ATTEMPTS_TOTAL,
    SUBMISSION_FAILURE_RATIO,
    SUBMISSION_FAILURE_TOTAL,
    SUBMISSION_SUCCESS_TOTAL,
)
from app.services.idev_client import IdevClient
from app.schemas.submission import SubmissionRequest, SubmissionResponse
from app.xml import DatMLRawBuilder, DatMLResBuilder

logger = logging.getLogger(__name__)

_submission_attempt_cache = 0
_submission_failure_cache = 0


class SubmissionService:
    """Kapselt XML-Generierung und (optionale) IDEV-Übertragung."""

    def __init__(self, session: AsyncSession, *, event_bus: EventBus | None = None, idev_client: IdevClient | None = None) -> None:
        self._session = session
        self._event_bus = event_bus
        self._idev_client = idev_client or IdevClient.from_settings(settings)

    async def submit(self, batch: models.DeclarationBatch, request: SubmissionRequest) -> SubmissionResponse:
        global _submission_attempt_cache, _submission_failure_cache

        payload = await self._build_payload(batch)
        payload_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        submission = models.SubmissionLog(
            id=uuid4(),
            batch_id=batch.id,
            tenant_id=batch.tenant_id,
            submission_channel="idev",
            payload_hash=payload_hash,
            status="generated",
            success=False,
            submitted_at=datetime.utcnow(),
            response_payload={"dry_run": request.dry_run},
            reference_number=request.override_reference,
        )
        self._session.add(submission)

        if request.dry_run or not settings.SUBMISSION_ENABLED:
            datml_res = DatMLResBuilder(str(submission.id), batch).build(errors=None)
            batch.status = models.DeclarationStatus.READY
            await self._session.flush()
            return SubmissionResponse(
                batch_id=batch.id,
                status=batch.status.value,
                submission_id=submission.id,
                payload_hash=payload_hash,
                success=False,
                endpoint=settings.SUBMISSION_BASE_URL,
                datml_res=datml_res,
                dry_run=True,
            )

        SUBMISSION_ATTEMPTS_TOTAL.inc()
        _submission_attempt_cache += 1
        if self._event_bus:
            await self._event_bus.publish(
                event_type="intrastat.submission.started",
                tenant=batch.tenant_id,
                data={"batch_id": str(batch.id), "submission_id": str(submission.id)},
            )

        response = await self._transmit_with_retry(payload, submission.id)
        errors = response.get("errors") if isinstance(response, dict) else None
        res_xml = DatMLResBuilder(str(submission.id), batch).build(errors=errors)
        submission.response_payload = {
            "raw": response,
            "res_xml": res_xml,
        }
        submission.status = response.get("status", "queued") if isinstance(response, dict) else "queued"
        submission.success = response.get("success", False) if isinstance(response, dict) else False
        submission.reference_number = response.get("reference_number") if isinstance(response, dict) else None

        if submission.success:
            batch.status = models.DeclarationStatus.SUBMITTED
            SUBMISSION_SUCCESS_TOTAL.inc()
        else:
            batch.status = models.DeclarationStatus.ERROR
            SUBMISSION_FAILURE_TOTAL.inc()
            _submission_failure_cache += 1

        if _submission_attempt_cache:
            SUBMISSION_FAILURE_RATIO.set(_submission_failure_cache / _submission_attempt_cache)

        if submission.success:
            if self._event_bus:
                await self._event_bus.publish(
                    event_type="intrastat.submission.completed",
                    tenant=batch.tenant_id,
                    data={
                        "batch_id": str(batch.id),
                        "submission_id": str(submission.id),
                        "reference_period": batch.reference_period.isoformat(),
                        "reference_number": submission.reference_number,
                        "datml_res": res_xml,
                    },
                )
        else:
            if self._event_bus:
                await self._event_bus.publish(
                    event_type="intrastat.submission.failed",
                    tenant=batch.tenant_id,
                    data={
                        "batch_id": str(batch.id),
                        "submission_id": str(submission.id),
                        "reference_period": batch.reference_period.isoformat(),
                        "message": response.get("message") if isinstance(response, dict) else None,
                        "datml_res": res_xml,
                    },
                )

        batch.updated_at = datetime.utcnow()
        await self._session.flush()

        return SubmissionResponse(
            batch_id=batch.id,
            status=batch.status.value,
            submission_id=submission.id,
            payload_hash=payload_hash,
            success=submission.success,
            endpoint=settings.SUBMISSION_BASE_URL,
            reference_number=submission.reference_number,
            datml_res=res_xml,
            dry_run=False,
        )

    async def _build_payload(self, batch: models.DeclarationBatch) -> str:
        builder = DatMLRawBuilder(batch)
        return builder.build()

    async def _transmit_with_retry(self, payload: str, submission_id: UUID) -> dict:
        attempts = settings.SUBMISSION_RETRY_ATTEMPTS
        delay = settings.SUBMISSION_RETRY_DELAY_SECONDS

        last_error: dict[str, str] | None = None
        for attempt in range(1, attempts + 1):
            try:
                response = await self._idev_client.upload(payload, submission_id=str(submission_id))
                return response
            except Exception as exc:  # noqa: BLE001
                logger.error("IDEV Submission Versuch %s fehlgeschlagen: %s", attempt, exc, exc_info=True)
                last_error = {"status": "error", "success": False, "message": str(exc)}
                if attempt < attempts:
                    await asyncio.sleep(delay)

        assert last_error is not None
        return last_error

