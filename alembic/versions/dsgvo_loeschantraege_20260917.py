"""Loeschantraege nach Art. 17 DSGVO bekommen ihre Tabelle.

``domain_compliance.data_erasure_requests`` wurde von den Endpunkten gelesen
und beschrieben, aber nie angelegt. Jeder Loeschantrag scheiterte deshalb schon
beim Anlegen mit 503 — ein Betroffenenrecht, das im Haus schlicht keinen Ort
hatte.

Revision ID: dsgvo_loeschantraege_20260917
Revises: crm_kreditlimite_20260917
Create Date: 2026-09-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "dsgvo_loeschantraege_20260917"
down_revision = "crm_kreditlimite_20260917"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_compliance")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_compliance.data_erasure_requests (
            id               VARCHAR(64)  PRIMARY KEY,
            requester_name   VARCHAR(200) NOT NULL,
            requester_email  VARCHAR(320) NOT NULL,
            subject_id       VARCHAR(64)  NOT NULL,
            subject_type     VARCHAR(32)  NOT NULL,
            request_date     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            completion_date  TIMESTAMPTZ,
            status           VARCHAR(32)  NOT NULL DEFAULT 'EINGEGANGEN',
            deletion_log     JSONB        NOT NULL DEFAULT '[]'::jsonb,
            tenant_id        VARCHAR(64)  NOT NULL,
            created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at       TIMESTAMPTZ
        )
        """
    )
    # Die Fristenfrage („welcher Antrag laeuft seit wann?") ist die, die hier
    # wirklich gestellt wird — Art. 12 Abs. 3 DSGVO gibt einen Monat.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_data_erasure_requests_tenant_status "
        "ON domain_compliance.data_erasure_requests (tenant_id, status, request_date DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_data_erasure_requests_subject "
        "ON domain_compliance.data_erasure_requests (tenant_id, subject_type, subject_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_compliance.ix_data_erasure_requests_subject")
    op.execute("DROP INDEX IF EXISTS domain_compliance.ix_data_erasure_requests_tenant_status")
    op.execute("DROP TABLE IF EXISTS domain_compliance.data_erasure_requests")
