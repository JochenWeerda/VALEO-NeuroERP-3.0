"""merge_all_heads

Revision ID: 6c69769c28cb
Revises: add_article_extended_fields_20260219, add_business_partners_tenant_id_20260219, gobd_compliance_20260220, add_sched_cfg_20260218, add_vat_codes_20260220
Create Date: 2026-02-20 09:03:27.472096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c69769c28cb'
down_revision: Union[str, None] = ('add_article_extended_fields_20260219', 'add_business_partners_tenant_id_20260219', 'gobd_compliance_20260220', 'add_sched_cfg_20260218', 'add_vat_codes_20260220')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
