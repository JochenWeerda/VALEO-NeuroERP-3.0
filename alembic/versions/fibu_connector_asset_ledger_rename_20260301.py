"""FIBU Connector: QUADRIGA → ASSET_LEDGER (geschützter Name entfernt)

Revision ID: fibu_connector_asset_ledger_20260301
Revises: fibu_connector_framework_20260301
Create Date: 2026-03-01

- connector_configs: connector_code QUADRIGA → ASSET_LEDGER
- fibu_connector_profiles / fibu_connector_runs: Check-Constraint erweitert auf ASSET_LEDGER
"""

from __future__ import annotations

from alembic import op


revision = "fibu_connector_asset_ledger_20260301"
down_revision = "fibu_connector_framework_20260301"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        UPDATE domain_erp.connector_configs
        SET connector_code = 'ASSET_LEDGER'
        WHERE connector_code = 'QUADRIGA'
    """)
    op.execute("ALTER TABLE domain_erp.fibu_connector_profiles DROP CONSTRAINT IF EXISTS chk_fibu_connector_profile_type")
    op.execute("ALTER TABLE domain_erp.fibu_connector_profiles ADD CONSTRAINT chk_fibu_connector_profile_type CHECK (connector_type IN ('PAYROLL', 'ASSET_LEDGER'))")
    op.execute("ALTER TABLE domain_erp.fibu_connector_runs DROP CONSTRAINT IF EXISTS chk_fibu_connector_run_type")
    op.execute("ALTER TABLE domain_erp.fibu_connector_runs ADD CONSTRAINT chk_fibu_connector_run_type CHECK (connector_type IN ('PAYROLL', 'ASSET_LEDGER'))")


def downgrade() -> None:
    op.execute("ALTER TABLE domain_erp.fibu_connector_runs DROP CONSTRAINT IF EXISTS chk_fibu_connector_run_type")
    op.execute("ALTER TABLE domain_erp.fibu_connector_runs ADD CONSTRAINT chk_fibu_connector_run_type CHECK (connector_type IN ('PAYROLL', 'QUADRIGA'))")
    op.execute("ALTER TABLE domain_erp.fibu_connector_profiles DROP CONSTRAINT IF EXISTS chk_fibu_connector_profile_type")
    op.execute("ALTER TABLE domain_erp.fibu_connector_profiles ADD CONSTRAINT chk_fibu_connector_profile_type CHECK (connector_type IN ('PAYROLL', 'QUADRIGA'))")
    op.execute("""
        UPDATE domain_erp.connector_configs
        SET connector_code = 'QUADRIGA'
        WHERE connector_code = 'ASSET_LEDGER'
    """)
