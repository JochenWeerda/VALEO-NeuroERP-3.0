"""Add CRM sub-service seed tables with demo data."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision = "59b4fa8420f2"
down_revision = "34a9ed912cd7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text("CREATE SCHEMA IF NOT EXISTS crm_subdomains;"))

    _create_interaction_events(bind)
    _create_sales_opportunities(bind)
    _create_marketing_campaigns(bind)
    _create_service_tickets(bind)
    _create_analytics_scores(bind)
    _create_sync_mappings(bind)
    _create_ai_requests(bind)


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(sa.text("DROP SCHEMA IF EXISTS crm_subdomains CASCADE;"))


def _create_interaction_events(bind) -> None:
    op.create_table(
        "interaction_events",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("channel", sa.String(32), nullable=False),
        sa.Column("direction", sa.String(8), nullable=False),
        sa.Column("actor_type", sa.String(16), nullable=False),
        sa.Column("actor_id", sa.String(64), nullable=True),
        sa.Column("customer_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("tags", sa.ARRAY(sa.String), nullable=True),
        sa.Column("occurred_at", sa.DateTime, nullable=False, default=datetime.utcnow),
        schema="crm_subdomains",
    )
    tenant = "00000000-0000-0000-0000-000000000001"
    bind.execute(
        sa.text(
            """
            INSERT INTO crm_subdomains.interaction_events
            (id, tenant_id, channel, direction, actor_type, actor_id, customer_id, subject, body, tags, occurred_at)
            VALUES (:id, :tenant_id, :channel, :direction, :actor_type, :actor_id, :customer_id, :subject, :body, :tags, :occurred_at)
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {
            "id": str(uuid4()),
            "tenant_id": tenant,
            "channel": "email",
            "direction": "in",
            "actor_type": "user",
            "actor_id": "sales-demo",
            "customer_id": "cf9d8a61-f4a7-4847-91b6-0f08840957f7",
            "subject": "Anfrage Düngemittel 2026",
            "body": "Kunde bittet um aktualisierte Preislisten und Lieferfenster.",
            "tags": ["crm", "inquiry"],
            "occurred_at": datetime.utcnow() - timedelta(days=2),
        },
    )


def _create_sales_opportunities(bind) -> None:
    op.create_table(
        "sales_opportunities",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("stage", sa.String(32), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, default="EUR"),
        sa.Column("probability", sa.Integer, nullable=False),
        sa.Column("owner_id", sa.String(64), nullable=False),
        sa.Column("expected_close", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, default=datetime.utcnow),
        schema="crm_subdomains",
    )
    tenant = "00000000-0000-0000-0000-000000000001"
    bind.execute(
        sa.text(
            """
            INSERT INTO crm_subdomains.sales_opportunities
            (id, tenant_id, customer_id, name, stage, amount, currency, probability, owner_id, expected_close, created_at)
            VALUES (:id, :tenant_id, :customer_id, :name, :stage, :amount, :currency, :probability, :owner_id, :expected_close, :created_at)
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {
            "id": str(uuid4()),
            "tenant_id": tenant,
            "customer_id": "cf9d8a61-f4a7-4847-91b6-0f08840957f7",
            "name": "PSM SaaS Renewal 2026",
            "stage": "proposal",
            "amount": 125000.00,
            "currency": "EUR",
            "probability": 65,
            "owner_id": "sales-demo",
            "expected_close": datetime.utcnow() + timedelta(days=21),
            "created_at": datetime.utcnow() - timedelta(days=5),
        },
    )


def _create_marketing_campaigns(bind) -> None:
    op.create_table(
        "marketing_campaigns",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("channel", sa.String(32), nullable=False),
        sa.Column("budget", sa.Numeric(12, 2), nullable=True),
        sa.Column("starts_at", sa.DateTime, nullable=True),
        sa.Column("ends_at", sa.DateTime, nullable=True),
        schema="crm_subdomains",
    )
    tenant = "00000000-0000-0000-0000-000000000001"
    bind.execute(
        sa.text(
            """
            INSERT INTO crm_subdomains.marketing_campaigns
            (id, tenant_id, name, status, channel, budget, starts_at, ends_at)
            VALUES (:id, :tenant_id, :name, :status, :channel, :budget, :starts_at, :ends_at)
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {
            "id": str(uuid4()),
            "tenant_id": tenant,
            "name": "Smart Agrar Summit Nurture",
            "status": "active",
            "channel": "email",
            "budget": 15000,
            "starts_at": datetime.utcnow() - timedelta(days=3),
            "ends_at": datetime.utcnow() + timedelta(days=27),
        },
    )


def _create_service_tickets(bind) -> None:
    op.create_table(
        "service_tickets",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("priority", sa.String(16), nullable=False),
        sa.Column("opened_at", sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column("due_at", sa.DateTime, nullable=True),
        sa.Column("owner_id", sa.String(64), nullable=True),
        schema="crm_subdomains",
    )
    tenant = "00000000-0000-0000-0000-000000000001"
    bind.execute(
        sa.text(
            """
            INSERT INTO crm_subdomains.service_tickets
            (id, tenant_id, customer_id, title, status, priority, opened_at, due_at, owner_id)
            VALUES (:id, :tenant_id, :customer_id, :title, :status, :priority, :opened_at, :due_at, :owner_id)
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {
            "id": str(uuid4()),
            "tenant_id": tenant,
            "customer_id": "cf9d8a61-f4a7-4847-91b6-0f08840957f7",
            "title": "EDI-Schnittstelle liefert 500er Fehler",
            "status": "open",
            "priority": "high",
            "opened_at": datetime.utcnow() - timedelta(days=1),
            "due_at": datetime.utcnow() + timedelta(days=1),
            "owner_id": "service-demo",
        },
    )


def _create_analytics_scores(bind) -> None:
    op.create_table(
        "analytics_customer_scores",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_score", sa.Float, nullable=True),
        sa.Column("churn_score", sa.Float, nullable=True),
        sa.Column("calculated_at", sa.DateTime, nullable=False, default=datetime.utcnow),
        schema="crm_subdomains",
    )
    tenant = "00000000-0000-0000-0000-000000000001"
    bind.execute(
        sa.text(
            """
            INSERT INTO crm_subdomains.analytics_customer_scores
            (id, tenant_id, customer_id, lead_score, churn_score, calculated_at)
            VALUES (:id, :tenant_id, :customer_id, :lead_score, :churn_score, :calculated_at)
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {
            "id": str(uuid4()),
            "tenant_id": tenant,
            "customer_id": "cf9d8a61-f4a7-4847-91b6-0f08840957f7",
            "lead_score": 0.82,
            "churn_score": 0.12,
            "calculated_at": datetime.utcnow(),
        },
    )


def _create_sync_mappings(bind) -> None:
    op.create_table(
        "sync_legacy_mappings",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("legacy_system", sa.String(64), nullable=False),
        sa.Column("legacy_id", sa.String(64), nullable=False),
        sa.Column("crm_entity", sa.String(32), nullable=False),
        sa.Column("crm_id", sa.String(64), nullable=False),
        sa.Column("synced_at", sa.DateTime, nullable=False, default=datetime.utcnow),
        schema="crm_subdomains",
    )
    bind.execute(
        sa.text(
            """
            INSERT INTO crm_subdomains.sync_legacy_mappings
            (id, legacy_system, legacy_id, crm_entity, crm_id, synced_at)
            VALUES (:id, :legacy_system, :legacy_id, :crm_entity, :crm_id, :synced_at)
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {
            "id": str(uuid4()),
            "legacy_system": "navision",
            "legacy_id": "C-100045",
            "crm_entity": "customer",
            "crm_id": "cf9d8a61-f4a7-4847-91b6-0f08840957f7",
            "synced_at": datetime.utcnow() - timedelta(hours=4),
        },
    )


def _create_ai_requests(bind) -> None:
    op.create_table(
        "ai_assist_requests",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("request_type", sa.String(32), nullable=False),
        sa.Column("prompt_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, default=datetime.utcnow),
        schema="crm_subdomains",
    )
    tenant = "00000000-0000-0000-0000-000000000001"
    bind.execute(
        sa.text(
            """
            INSERT INTO crm_subdomains.ai_assist_requests
            (id, tenant_id, customer_id, request_type, prompt_hash, status, created_at)
            VALUES (:id, :tenant_id, :customer_id, :request_type, :prompt_hash, :status, :created_at)
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {
            "id": str(uuid4()),
            "tenant_id": tenant,
            "customer_id": "cf9d8a61-f4a7-4847-91b6-0f08840957f7",
            "request_type": "next-best-action",
            "prompt_hash": "nba-demo",
            "status": "completed",
            "created_at": datetime.utcnow() - timedelta(minutes=15),
        },
    )
