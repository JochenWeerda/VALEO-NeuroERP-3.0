"""Activate scheduled ration versions once their feeding start is due."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import text

from app.agrar.rations.lifecycle import RationStatus
from app.core.database import SessionLocal
from app.services.rations_lifecycle_service import RationLifecycleService

logger = logging.getLogger(__name__)


def execute_due_ration_activations() -> dict[str, Any]:
    db = SessionLocal()
    activated = 0
    failed = 0
    try:
        due = db.execute(text("""
          SELECT tenant_id,version_id,feeding_start
          FROM domain_agrar.ration_version_lifecycle
          WHERE status='scheduled' AND feeding_start<=now()
          ORDER BY feeding_start,version_id
        """)).mappings().all()
        for item in due:
            try:
                RationLifecycleService(db, str(item["tenant_id"]), "system:ration-scheduler").transition(
                    version_id=str(item["version_id"]),
                    target=RationStatus.ACTIVE,
                    expected_status=RationStatus.SCHEDULED,
                    reason="Geplanter Fuetterungsbeginn erreicht.",
                    feeding_start=item["feeding_start"],
                )
                activated += 1
            except Exception as exc:
                db.rollback()
                failed += 1
                logger.error("Scheduled ration activation %s failed: %s", item["version_id"], exc)
        return {"success": failed == 0, "due": len(due), "activated": activated, "failed": failed}
    finally:
        db.close()


if __name__ == "__main__":
    print(execute_due_ration_activations())

