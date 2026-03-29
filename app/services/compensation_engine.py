"""
Compensation Engine — NC-006
Fehlerbehandlung: Retry, Rollback, Alternative Pfade, Eskalation.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class CompensationStrategy(str, Enum):
    RETRY_LINEAR = "retry_linear"
    RETRY_EXPONENTIAL = "retry_exponential"
    ROLLBACK = "rollback"
    ALTERNATIVE_PATH = "alternative_path"
    ESCALATE = "escalate"


class CompensationStatus(str, Enum):
    PENDING = "pending"
    RETRYING = "retrying"
    ROLLED_BACK = "rolled_back"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    FAILED = "failed"


@dataclass
class CompensationRun:
    run_id: str = field(default_factory=lambda: str(uuid4()))
    strategy: CompensationStrategy = CompensationStrategy.RETRY_LINEAR
    status: CompensationStatus = CompensationStatus.PENDING
    attempts: int = 0
    max_retries: int = 3
    error: str = ""
    actions_log: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id, "strategy": self.strategy.value,
            "status": self.status.value, "attempts": self.attempts,
            "max_retries": self.max_retries, "error": self.error,
            "actions_log": self.actions_log, "created_at": self.created_at,
        }


_runs: dict[str, CompensationRun] = {}


async def compensate(
    error_context: dict,
    strategy: str = "retry_linear",
    action_fn: Optional[Callable] = None,
    rollback_steps: Optional[list[dict]] = None,
) -> CompensationRun:
    strat = CompensationStrategy(strategy)
    run = CompensationRun(strategy=strat, error=error_context.get("error", "unknown"))

    if strat in (CompensationStrategy.RETRY_LINEAR, CompensationStrategy.RETRY_EXPONENTIAL):
        run.max_retries = 5 if strat == CompensationStrategy.RETRY_EXPONENTIAL else 3
        run.status = CompensationStatus.RETRYING

        for attempt in range(1, run.max_retries + 1):
            run.attempts = attempt
            delay = attempt if strat == CompensationStrategy.RETRY_LINEAR else 2 ** (attempt - 1)
            run.actions_log.append(f"Retry {attempt}/{run.max_retries} nach {delay}s")
            await asyncio.sleep(min(delay, 5))

            if action_fn:
                try:
                    await action_fn()
                    run.status = CompensationStatus.RESOLVED
                    run.actions_log.append(f"Retry {attempt} erfolgreich")
                    break
                except Exception as exc:
                    run.actions_log.append(f"Retry {attempt} fehlgeschlagen: {exc}")
            else:
                run.actions_log.append("Kein action_fn — Retry simuliert")
                run.status = CompensationStatus.RESOLVED
                break

        if run.status != CompensationStatus.RESOLVED:
            run.status = CompensationStatus.FAILED
            run.actions_log.append("Max Retries erreicht — Eskalation empfohlen")

    elif strat == CompensationStrategy.ROLLBACK:
        run.status = CompensationStatus.ROLLED_BACK
        for step in (rollback_steps or []):
            run.actions_log.append(f"Rollback: {step.get('description', 'Schritt')}")
        run.actions_log.append("Rollback abgeschlossen")

    elif strat == CompensationStrategy.ESCALATE:
        run.status = CompensationStatus.ESCALATED
        run.actions_log.append("An manuellen Bearbeiter eskaliert")

    elif strat == CompensationStrategy.ALTERNATIVE_PATH:
        run.status = CompensationStatus.RESOLVED
        run.actions_log.append("Alternativer Pfad gestartet")

    _runs[run.run_id] = run
    return run


def get_compensation_run(run_id: str) -> Optional[CompensationRun]:
    return _runs.get(run_id)
