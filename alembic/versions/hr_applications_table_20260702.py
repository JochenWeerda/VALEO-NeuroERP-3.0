"""hr: applications-Tabelle für Bewerbungs-Pipeline

Die Endpoints /api/v1/personal/applications (GET/POST/PATCH stage) existieren
seit Wave-104, die zugrunde liegende Tabelle domain_hr.applications wurde aber
nie migriert — alle Aufrufe liefen in den 503-Fallback ("applications table
not available"). Spaltensatz exakt nach dem Endpoint-Vertrag in
app/api/v1/endpoints/personal.py (INSERT + Stage-PATCH: status, applied_at,
last_updated, notes).

Revision ID: hr_applications_table_20260702
Revises: 42e0e183bd0c
Create Date: 2026-07-02
"""

from __future__ import annotations

from alembic import op

revision = "hr_applications_table_20260702"
down_revision = "42e0e183bd0c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_hr")
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_hr.applications (
            id              VARCHAR(36)  PRIMARY KEY,
            tenant_id       VARCHAR(64)  NOT NULL,
            applicant_name  VARCHAR(200) NOT NULL,
            applicant_email VARCHAR(200) NOT NULL,
            position_id     VARCHAR(36),
            position_title  VARCHAR(200),
            source          VARCHAR(80),
            documents_ref   TEXT,
            status          VARCHAR(32)  NOT NULL DEFAULT 'EINGANG',
            notes           TEXT,
            applied_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            last_updated    TIMESTAMPTZ
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_hr_applications_tenant_status
            ON domain_hr.applications (tenant_id, status)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_hr.applications")
