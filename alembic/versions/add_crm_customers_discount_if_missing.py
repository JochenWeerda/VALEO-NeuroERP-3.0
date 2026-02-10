"""Add discount column to crm_core_customers if present (Rabatt-Vorbelegung)

Revision ID: add_crm_discount
Revises: 2012a7987e7f
Create Date: 2025-02-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "add_crm_discount"
down_revision: Union[str, None] = "2012a7987e7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    ***REMOVED*** The crm-core service owns this table in some deployments. In the monolith
    ***REMOVED*** DB it may not exist on a fresh install, so this migration must be safe.
    bind = op.get_bind()
    exists = bind.execute(sa.text("SELECT to_regclass(:name)"), {"name": "public.crm_core_customers"}).scalar()
    if not exists:
        return

    op.execute(
        """
        ALTER TABLE public.crm_core_customers
        ADD COLUMN IF NOT EXISTS discount DECIMAL(5, 2) DEFAULT 0
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    exists = bind.execute(sa.text("SELECT to_regclass(:name)"), {"name": "public.crm_core_customers"}).scalar()
    if not exists:
        return

    op.execute("ALTER TABLE public.crm_core_customers DROP COLUMN IF EXISTS discount")
