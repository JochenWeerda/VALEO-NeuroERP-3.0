"""crm_ownership_log — Übergabe-/Zuordnungs-Audit (DOM-CRM-004.3)

Append-only Protokoll der Owner-Änderungen (Außendienst/Innendienst) je Kunde.

Revision ID: crm_ownership_log_20260610
Revises: crm_merge_20260610
Create Date: 2026-06-10
"""

from __future__ import annotations

from alembic import op

revision = "crm_ownership_log_20260610"
down_revision = "crm_merge_20260610"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.crm_ownership_log (
            id          UUID PRIMARY KEY,
            tenant_id   TEXT,
            kunden_nr   VARCHAR(32) NOT NULL,
            feld        VARCHAR(16) NOT NULL,   -- sales_rep | dispatcher
            alt         VARCHAR(64),
            neu         VARCHAR(64),
            grund       TEXT,
            bediener    VARCHAR(64),
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_crm_ownership_log_kunde "
        "ON public.crm_ownership_log (kunden_nr, created_at DESC)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS public.ix_crm_ownership_log_kunde")
    op.execute("DROP TABLE IF EXISTS public.crm_ownership_log")
