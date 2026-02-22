"""seed default tenant for foreign-key constrained domain tables

Revision ID: seed_default_tenant_20260214
Revises: articles_model_alignment_20260214
Create Date: 2026-02-14 11:45:00.000000
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "seed_default_tenant_20260214"
down_revision: Union[str, Sequence[str], None] = "articles_model_alignment_20260214"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    op.execute(
        f"""
        INSERT INTO domain_shared.tenants (id, name, domain, settings, is_active)
        VALUES ('{DEFAULT_TENANT_ID}', 'Default Tenant', 'default.local', '{{}}', TRUE)
        ON CONFLICT (id) DO NOTHING;
        """
    )


def downgrade() -> None:
    op.execute(
        f"""
        DELETE FROM domain_shared.tenants
        WHERE id = '{DEFAULT_TENANT_ID}'
          AND NOT EXISTS (
              SELECT 1
              FROM domain_inventory.articles a
              WHERE a.tenant_id = '{DEFAULT_TENANT_ID}'
          );
        """
    )
