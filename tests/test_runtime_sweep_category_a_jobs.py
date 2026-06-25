from pathlib import Path

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.endpoints import job_runner


class _FailingDb:
    rolled_back = False

    def execute(self, *_args, **_kwargs):
        raise SQLAlchemyError("relation domain_shared.jobs does not exist")

    def rollback(self):
        self.rolled_back = True


@pytest.mark.asyncio
async def test_job_runner_list_degrades_when_jobs_table_missing():
    db = _FailingDb()

    response = await job_runner.list_jobs(
        status=None,
        limit=50,
        db=db,
        tenant_id="tenant-1",
    )

    assert response == []
    assert db.rolled_back is True


def test_job_runner_repair_migration_is_chained_to_current_head():
    migration = Path("alembic/versions/job_runner_tables_repair_20260625.py").read_text()

    assert 'revision = "job_runner_tables_repair_20260625"' in migration
    assert 'down_revision = "hr_planning_tables_20260625"' in migration
    assert "CREATE TABLE IF NOT EXISTS domain_shared.jobs" in migration
    assert "CREATE TABLE IF NOT EXISTS domain_shared.job_artifacts" in migration
