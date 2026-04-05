"""neuro_step_audit_trace + einkauf_bestellungen.tenant_id

Revision ID: neuro_step_audit_einkauf_tenant_20260405
Revises: crm_customers_business_partner_id_20260404
Create Date: 2026-04-05

- domain_shared.neuro_step_audit_trace: Kernel- und Broker-Schritt-Audit (NC-A7 / Action-Execute)
- public.einkauf_bestellungen.tenant_id: Mandanten-Spalte fuer Command-Mutation CreatePurchaseOrder
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision: str = "neuro_step_audit_einkauf_tenant_20260405"
down_revision: Union[str, None] = "crm_customers_business_partner_id_20260404"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS domain_shared.neuro_step_audit_trace (
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                tenant_id VARCHAR(120) NOT NULL,
                plan_id VARCHAR(255) NOT NULL,
                step_id VARCHAR(120) NOT NULL,
                step_order INTEGER NOT NULL DEFAULT 0,
                action VARCHAR(120) NOT NULL,
                step_type VARCHAR(80) NOT NULL,
                binding_kind VARCHAR(80) NOT NULL,
                binding_target VARCHAR(255) NOT NULL,
                step_status VARCHAR(80) NOT NULL,
                execution_detail TEXT,
                recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_neuro_step_audit_tenant
            ON domain_shared.neuro_step_audit_trace (tenant_id)
            """
        )
    )
    conn.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_neuro_step_audit_plan
            ON domain_shared.neuro_step_audit_trace (plan_id)
            """
        )
    )

    po = conn.execute(
        text("SELECT to_regclass('public.einkauf_bestellungen')")
    ).scalar()
    if po:
        col = conn.execute(
            text(
                """
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'einkauf_bestellungen'
                  AND column_name = 'tenant_id'
                """
            )
        ).fetchone()
        if not col:
            conn.execute(
                text(
                    """
                    ALTER TABLE public.einkauf_bestellungen
                    ADD COLUMN tenant_id VARCHAR(64) NOT NULL DEFAULT 'default'
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS ix_einkauf_bestellungen_tenant_id
                    ON public.einkauf_bestellungen (tenant_id)
                    """
                )
            )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("DROP TABLE IF EXISTS domain_shared.neuro_step_audit_trace"))
    po = conn.execute(
        text("SELECT to_regclass('public.einkauf_bestellungen')")
    ).scalar()
    if po:
        col = conn.execute(
            text(
                """
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'einkauf_bestellungen'
                  AND column_name = 'tenant_id'
                """
            )
        ).fetchone()
        if col:
            conn.execute(
                text("DROP INDEX IF EXISTS ix_einkauf_bestellungen_tenant_id")
            )
            op.drop_column("einkauf_bestellungen", "tenant_id", schema=None)
