"""Add leads, activities, and farm profiles tables."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from psycopg2.extras import Json

revision = "20251114_02_expand_crm_entities"
down_revision = "20251114_01_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crm_core_leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_core_customers.id"), nullable=True),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("contact_person", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(50)),
        sa.Column("status", sa.String(32), nullable=False, server_default="new"),
        sa.Column("priority", sa.String(16), nullable=False, server_default="medium"),
        sa.Column("source", sa.String(64)),
        sa.Column("estimated_value", sa.Float),
        sa.Column("assigned_to", sa.String(64)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime),
    )

    op.create_table(
        "crm_core_activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_core_customers.id"), nullable=True),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_core_contacts.id"), nullable=True),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="planned"),
        sa.Column("assigned_to", sa.String(64)),
        sa.Column("scheduled_at", sa.DateTime),
        sa.Column("description", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime),
    )

    op.create_table(
        "crm_core_farm_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_core_customers.id"), nullable=True),
        sa.Column("farm_name", sa.String(255), nullable=False),
        sa.Column("owner", sa.String(150), nullable=False),
        sa.Column("total_area", sa.Float, nullable=False),
        sa.Column("crops", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("livestock", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("location", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("certifications", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime),
    )

    _seed_records()


def downgrade() -> None:
    op.drop_table("crm_core_farm_profiles")
    op.drop_table("crm_core_activities")
    op.drop_table("crm_core_leads")


def _seed_records() -> None:
    bind = op.get_bind()
    customer_row = bind.execute(
        sa.text("SELECT id, display_name FROM crm_core_customers ORDER BY created_at LIMIT 1")
    ).first()
    if not customer_row:
        return
    customer_id = customer_row.id
    contact_row = bind.execute(
        sa.text("SELECT id FROM crm_core_contacts WHERE customer_id = :cid ORDER BY created_at LIMIT 1"),
        {"cid": customer_id},
    ).first()
    contact_id = contact_row.id if contact_row else None
    tenant_id = bind.execute(
        sa.text("SELECT tenant_id FROM crm_core_customers WHERE id = :cid"),
        {"cid": customer_id},
    ).scalar()

    lead_id = uuid4()
    bind.execute(
        sa.text(
            """
            INSERT INTO crm_core_leads
            (id, tenant_id, customer_id, company_name, contact_person, email, phone, status, priority, source, estimated_value, assigned_to, notes, created_at)
            VALUES (:id, :tenant_id, :customer_id, :company_name, :contact_person, :email, :phone, :status, :priority, :source, :estimated_value, :assigned_to, :notes, :created_at)
            """
        ),
        {
            "id": str(lead_id),
            "tenant_id": tenant_id,
            "customer_id": str(customer_id),
            "company_name": customer_row.display_name,
            "contact_person": "Carla Muster",
            "email": "carla.muster@valeo-demo.example",
            "phone": "+49-89-1234-101",
            "status": "qualified",
            "priority": "high",
            "source": "demo",
            "estimated_value": 125000,
            "assigned_to": "sales-demo",
            "notes": "Demo seed lead for CRM wiring.",
            "created_at": datetime.utcnow() - timedelta(days=3),
        },
    )

    bind.execute(
        sa.text(
            """
            INSERT INTO crm_core_activities
            (id, tenant_id, customer_id, contact_id, type, title, status, assigned_to, scheduled_at, description, created_at)
            VALUES (:id, :tenant_id, :customer_id, :contact_id, :type, :title, :status, :assigned_to, :scheduled_at, :description, :created_at)
            """
        ),
        {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "customer_id": str(customer_id),
            "contact_id": str(contact_id) if contact_id else None,
            "type": "call",
            "title": "Quarterly Check-in",
            "status": "planned",
            "assigned_to": "service-demo",
            "scheduled_at": datetime.utcnow() + timedelta(days=2),
            "description": "Seed record for timeline demos.",
            "created_at": datetime.utcnow() - timedelta(days=1),
        },
    )

    bind.execute(
        sa.text(
            """
            INSERT INTO crm_core_farm_profiles
            (id, tenant_id, customer_id, farm_name, owner, total_area, crops, livestock, location, certifications, notes, created_at)
            VALUES (:id, :tenant_id, :customer_id, :farm_name, :owner, :total_area, :crops, :livestock, :location, :certifications, :notes, :created_at)
            """
        ),
        {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "customer_id": str(customer_id),
            "farm_name": "Demo Hof Muster",
            "owner": "Familie Muster",
            "total_area": 450.0,
            "crops": Json(
                [
                    {"crop": "Weizen", "area": 120},
                    {"crop": "Mais", "area": 80},
                ]
            ),
            "livestock": Json([{"type": "Rind", "count": 150}]),
            "location": Json({"address": "Bayern", "latitude": 48.137, "longitude": 11.575}),
            "certifications": Json(["Bioland", "DLG"]),
            "notes": "Seed profile for CRM farm module.",
            "created_at": datetime.utcnow() - timedelta(days=7),
        },
    )
