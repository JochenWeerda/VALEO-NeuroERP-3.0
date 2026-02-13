"""align schema with domain_* tables

Revision ID: 1368e3f15650
Revises: 001
Create Date: 2025-10-12 13:01:03.132240

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '1368e3f15650'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Move policy_rules table into the domain_erp schema (only if it exists)
    bind = op.get_bind()
    result = bind.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'policy_rules'
        )
    """))
    if result.scalar():
        op.execute("ALTER TABLE policy_rules SET SCHEMA domain_erp")


def downgrade() -> None:
    op.execute("ALTER TABLE domain_erp.policy_rules SET SCHEMA public")
