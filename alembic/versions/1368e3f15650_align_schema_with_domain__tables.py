"""align schema with domain_* tables

Revision ID: 1368e3f15650
Revises: 001
Create Date: 2025-10-12 13:01:03.132240

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1368e3f15650'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Move policy_rules table into the domain_erp schema
    op.execute("ALTER TABLE policy_rules SET SCHEMA domain_erp")


def downgrade() -> None:
    op.execute("ALTER TABLE domain_erp.policy_rules SET SCHEMA public")
