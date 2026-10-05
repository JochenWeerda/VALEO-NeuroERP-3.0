"""Persist the audit contract already used by native mask commands.

Revision ID: mask_action_audit_20260921
Revises: einkauf_bestellung_fuehrend_20260918
"""
from alembic import op

revision = "mask_action_audit_20260921"
down_revision = "einkauf_bestellung_fuehrend_20260918"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_crm")
    op.execute("""
        CREATE TABLE domain_crm.crm_action_audit_log (
            id VARCHAR(36) PRIMARY KEY,
            tenant_id VARCHAR(100) NOT NULL,
            action_key VARCHAR(200) NOT NULL,
            entity_type VARCHAR(200) NOT NULL,
            entity_id VARCHAR(200) NOT NULL,
            idempotency_key VARCHAR(200),
            audit_reason TEXT,
            performed_at TIMESTAMPTZ NOT NULL,
            result_summary TEXT NOT NULL
        )
    """)
    op.execute("""
        CREATE INDEX ix_mask_action_audit_tenant_entity
        ON domain_crm.crm_action_audit_log (tenant_id, entity_type, entity_id, performed_at)
    """)


def downgrade():
    # Never silently destroy the audit trail when rolling application code back.
    raise RuntimeError("Audit records must be retained; roll back application code without dropping this table")
