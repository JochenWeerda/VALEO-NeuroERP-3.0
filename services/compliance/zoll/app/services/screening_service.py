"""Service für Sanktionslistenscreening."""

from __future__ import annotations

import logging
from typing import Iterable, List

from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter

from app.config import settings
from app.db import models
from app.integrations.event_bus import EventBus
from app.integrations.sanctions_provider import SanctionsProvider
from app.schemas.screening import ScreeningRequest, ScreeningResponse, ScreeningResult

logger = logging.getLogger(__name__)

SCREENING_STATUS_COUNTER = Counter(
    "zoll_screening_status_total",
    "Aggregated screening outcomes",
    labelnames=["status"],
)


class ScreeningService:
    """Berechnet Matches gegen Sanktionslisten und publiziert Events."""

    def __init__(
        self,
        session: AsyncSession,
        provider: SanctionsProvider | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self._session = session
        self.threshold_block = settings.SCREENING_THRESHOLD_BLOCK
        self.threshold_review = settings.SCREENING_THRESHOLD_REVIEW
        self._provider = provider or SanctionsProvider()
        self._event_bus = event_bus

    async def screen_subject(self, payload: ScreeningRequest) -> ScreeningResponse:
        matches: List[ScreeningResult] = []
        subject_name = payload.subject.name.lower()
        for entry in self._provider.matches():
            candidate = entry.get("name", "").lower()
            score = self._fuzzy_score(subject_name, candidate)
            if score <= 0:
                continue
            matches.append(
                ScreeningResult(
                    list_name=entry.get("list", "unknown"),
                    entry_id=entry.get("id", "n/a"),
                    score=score,
                    matched_fields={"name": entry.get("name", "")},
                )
            )

        await self._persist_matches(payload.tenant_id, payload.subject.name, matches)
        status_flag = self._derive_overall_status(matches)
        await self._publish_event(payload.tenant_id, payload.subject.name, status_flag)
        return ScreeningResponse(status=status_flag, matches=matches)

    async def refresh(self) -> None:
        await self._provider.refresh()

    @staticmethod
    def _fuzzy_score(subject: str, candidate: str) -> float:
        if not subject or not candidate:
            return 0.0
        overlap = len(set(subject.split()) & set(candidate.split()))
        total = max(len(subject.split()), len(candidate.split()))
        return round(overlap / total, 2) if total else 0.0

    async def _persist_matches(
        self,
        tenant_id: str,
        subject_name: str,
        matches: Iterable[ScreeningResult],
    ) -> None:
        to_store = [
            models.ScreeningMatch(
                tenant_id=tenant_id,
                subject_name=subject_name,
                subject_type="entity",
                list_name=match.list_name,
                score=match.score,
                status=self._derive_status(match.score),
                metadata=match.matched_fields,
            )
            for match in matches
        ]
        if to_store:
            self._session.add_all(to_store)
            await self._session.flush()

    def _derive_status(self, score: float) -> models.ScreeningStatus:
        if score >= self.threshold_block:
            return models.ScreeningStatus.BLOCKED
        if score >= self.threshold_review:
            return models.ScreeningStatus.REVIEW
        return models.ScreeningStatus.CLEAR

    def _derive_overall_status(self, matches: List[ScreeningResult]) -> str:
        if not matches:
            return "clear"
        highest = max(matches, key=lambda match: match.score)
        if highest.score >= self.threshold_block:
            return "blocked"
        if highest.score >= self.threshold_review:
            return "review"
        return "clear"

    async def _publish_event(self, tenant_id: str, subject_name: str, status: str) -> None:
        SCREENING_STATUS_COUNTER.labels(status=status).inc()
        if not self._event_bus:
            return
        event_map = {
            "blocked": "export.screening.failed",
            "review": "export.screening.review",
            "clear": "export.screening.cleared",
        }
        event_type = event_map.get(status)
        if not event_type:
            return
        await self._event_bus.publish(
            event_type=event_type,
            tenant=tenant_id,
            data={"subject": subject_name, "status": status},
        )
