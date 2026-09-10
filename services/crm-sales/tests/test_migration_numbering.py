"""Run with python -m unittest discover -s tests in the CRM-Sales container."""
import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import MagicMock

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


class MigrationNumberingTest(unittest.IsolatedAsyncioTestCase):
    async def test_numbers_existing_rows_without_overwriting_references(self):
        migration_path = Path(__file__).resolve().parents[1] / "alembic/versions/002_extend_opportunities.py"
        spec = importlib.util.spec_from_file_location("crm_numbering_migration", migration_path)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        migration.op = MagicMock()
        migration.upgrade()
        statements = [str(call.args[0]) for call in migration.op.execute.call_args_list]
        numbering = next(sql for sql in statements if "ROW_NUMBER()" in sql)
        engine = create_async_engine(os.environ["DATABASE_URL"])
        try:
            async with engine.connect() as connection:
                transaction = await connection.begin()
                try:
                    # The temporary table shadows the service table on this connection.
                    await connection.execute(text("CREATE TEMP TABLE crm_sales_opportunities (id TEXT PRIMARY KEY, created_at TIMESTAMP, number TEXT UNIQUE) ON COMMIT DROP"))
                    await connection.execute(text("INSERT INTO crm_sales_opportunities VALUES ('b', '2026-01-01', NULL), ('a', '2026-01-01', NULL), ('c', '2025-01-01', 'EXISTING')"))
                    await connection.execute(text(numbering))
                    rows = (await connection.execute(text("SELECT id, number FROM crm_sales_opportunities ORDER BY id"))).all()
                    self.assertEqual(rows, [('a', 'OPP-000001'), ('b', 'OPP-000002'), ('c', 'EXISTING')])
                    await connection.execute(text(numbering))
                    repeated = (await connection.execute(text("SELECT id, number FROM crm_sales_opportunities ORDER BY id"))).all()
                    self.assertEqual(repeated, rows)
                finally:
                    await transaction.rollback()
        finally:
            await engine.dispose()
