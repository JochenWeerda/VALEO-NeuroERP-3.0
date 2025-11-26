"""Initial CRM core tables.

Revision ID: 20251114_01_initial
Revises: 
Create Date: 2025-11-14 11:25:00
"""

import uuid
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20251114_01_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _ensure_enum(name: str, values: Sequence[str]) -> None:
    """Create the Postgres ENUM iff it is not present yet."""
    values_sql = ", ".join(f"''{value}''" for value in values)
    op.execute(
        sa.text(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{name}') THEN
                    EXECUTE 'CREATE TYPE {name} AS ENUM ({values_sql})';
                END IF;
            END
            $$;
            """
        )
    )


def upgrade() -> None:
    customer_type_values = ("company", "person")
    customer_status_values = ("prospect", "active", "dormant", "former", "blacklisted")

    _ensure_enum("crm_core_customer_type", customer_type_values)
    _ensure_enum("crm_core_customer_status", customer_status_values)
    op.execute("DROP INDEX IF EXISTS ix_crm_core_customers_tenant_id;")
    op.execute("DROP TABLE IF EXISTS crm_core_contacts CASCADE;")
    op.execute("DROP TABLE IF EXISTS crm_core_customers CASCADE;")

    op.create_table(
        "crm_core_customers",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("legal_name", sa.String(255)),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(50)),
        sa.Column("industry", sa.String(128)),
        sa.Column("region", sa.String(64)),
        sa.Column("lead_score", sa.Float),
        sa.Column("churn_score", sa.Float),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime),
        sa.Index("ix_crm_core_customers_tenant_id", "tenant_id"),
    )
    op.execute(
        """
        ALTER TABLE crm_core_customers
        ALTER COLUMN type TYPE crm_core_customer_type
        USING type::crm_core_customer_type
        """
    )
    op.execute(
        """
        ALTER TABLE crm_core_customers
        ALTER COLUMN status TYPE crm_core_customer_status
        USING status::crm_core_customer_status
        """
    )

    op.create_table(
        "crm_core_contacts",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "customer_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("crm_core_customers.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(50)),
        sa.Column("job_title", sa.String(150)),
        sa.Column("department", sa.String(150)),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime),
    )

    customers_table = sa.table(
        "crm_core_customers",
        sa.column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.column("tenant_id", sa.String(64)),
        sa.column("type", sa.String(32)),
        sa.column("display_name", sa.String(255)),
        sa.column("legal_name", sa.String(255)),
        sa.column("status", sa.String(32)),
        sa.column("email", sa.String(255)),
        sa.column("phone", sa.String(50)),
        sa.column("industry", sa.String(128)),
        sa.column("region", sa.String(64)),
        sa.column("lead_score", sa.Float),
        sa.column("churn_score", sa.Float),
        sa.column("notes", sa.Text),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    contacts_table = sa.table(
        "crm_core_contacts",
        sa.column("id", sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.column("customer_id", sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.column("first_name", sa.String(100)),
        sa.column("last_name", sa.String(100)),
        sa.column("email", sa.String(255)),
        sa.column("phone", sa.String(50)),
        sa.column("job_title", sa.String(150)),
        sa.column("department", sa.String(150)),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    demo_customer_id = uuid.uuid4()
    default_tenant_id = "00000000-0000-0000-0000-000000000001"
    now = datetime.utcnow()
    op.bulk_insert(
        customers_table,
        [
            {
                "id": demo_customer_id,
                "tenant_id": default_tenant_id,
                "type": "company",
                "display_name": "Valeo Demo GmbH",
                "legal_name": "Valeo Demo GmbH",
                "status": "active",
                "email": "contact@valeo-demo.example",
                "phone": "+49-89-1234-0",
                "industry": "Manufacturing",
                "region": "DE-BY",
                "lead_score": 0.82,
                "churn_score": 0.12,
                "notes": "Seeded record so UI and Playwright flows have data.",
                "created_at": now,
                "updated_at": now,
            }
        ],
    )
    op.bulk_insert(
        contacts_table,
        [
            {
                "id": uuid.uuid4(),
                "customer_id": demo_customer_id,
                "first_name": "Carla",
                "last_name": "Muster",
                "email": "carla.muster@valeo-demo.example",
                "phone": "+49-89-1234-101",
                "job_title": "Head of Procurement",
                "department": "Purchasing",
                "created_at": now,
                "updated_at": now,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("crm_core_contacts")
    op.drop_table("crm_core_customers")
    op.execute("DROP TYPE IF EXISTS crm_core_customer_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS crm_core_customer_type CASCADE;")
