"""Daily worker for enabled, contract-gated herd-data connections."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.rations_herd_data_sync_service import HerdDataSyncService, connection_from_row

logger = logging.getLogger(__name__)


async def run_herd_data_syncs() -> dict[str, Any]:
    db = SessionLocal()
    completed = 0
    failed = 0
    imported = 0
    try:
        rows = db.execute(text("""SELECT * FROM domain_agrar.herd_data_connections
          WHERE enabled=TRUE AND live_enabled=TRUE ORDER BY tenant_id,provider,herd_id""")).mappings().all()
        service = HerdDataSyncService(db)
        for row in rows:
            connection = connection_from_row(dict(row))
            try:
                result = await service.sync(connection)
                completed += 1
                imported += int(result["imported_count"])
            except Exception as exc:  # connection isolation: one farm must not block the rest
                failed += 1
                logger.error("Herd-Data-Sync %s/%s failed: %s", connection.provider, connection.herd_id, exc)
        return {"success": failed == 0, "connections": len(rows), "completed": completed,
                "failed": failed, "imported_count": imported}
    finally:
        db.close()


def execute_herd_data_syncs() -> dict[str, Any]:
    return asyncio.run(run_herd_data_syncs())


if __name__ == "__main__":
    print(execute_herd_data_syncs())
