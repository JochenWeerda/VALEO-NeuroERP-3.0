"""finance_followup_exports + optional unique (tenant_id, bestellnummer)

Revision ID: finance_followup_exports_einkauf_uq_20260406
Revises: neuro_step_audit_einkauf_tenant_20260405
Create Date: 2026-04-06

- domain_shared.finance_followup_exports: Metadaten fuer Finance-Follow-up-Downloads
- Unique-Index auf einkauf_bestellungen (tenant_id, bestellnummer) wenn keine Duplikate
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "finance_followup_exports_einkauf_uq_20260406"
down_revision: Union[str, None] = "neuro_step_audit_einkauf_tenant_20260405"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS domain_shared.finance_followup_exports (
                id UUID NOT NULL PRIMARY KEY,
                tenant_id VARCHAR(120) NOT NULL,
                kind VARCHAR(40) NOT NULL,
                run_id VARCHAR(120),
                record_count INTEGER NOT NULL DEFAULT 0,
                dms_document_id INTEGER,
                dms_view_url TEXT,
                params_json JSONB,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_finance_followup_exports_tenant
            ON domain_shared.finance_followup_exports (tenant_id)
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_finance_followup_exports_created
            ON domain_shared.finance_followup_exports (created_at)
            """
        )
    )

    # Unique (tenant_id, bestellnummer) nur wenn Tabelle existiert und keine Duplikate
    po = conn.execute(
        text("SELECT to_regclass('public.einkauf_bestellungen')")
    ).scalar()
    if po:
        dup = conn.execute(
            text(
                """
                SELECT 1 FROM (
                    SELECT tenant_id, bestellnummer, COUNT(*) AS c
                    FROM public.einkauf_bestellungen
                    GROUP BY tenant_id, bestellnummer
                    HAVING COUNT(*) > 1
                ) d LIMIT 1
                """
            )
        ).fetchone()
        if not dup:
            conn.execute(
                text(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS uq_einkauf_bestellungen_tenant_bestellnummer
                    ON public.einkauf_bestellungen (tenant_id, bestellnummer)
                    """
                )
            )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            "DROP INDEX IF EXISTS public.uq_einkauf_bestellungen_tenant_bestellnummer"
        )
    )
    conn.execute(
        text("DROP TABLE IF EXISTS domain_shared.finance_followup_exports")
    )
