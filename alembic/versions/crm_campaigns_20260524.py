"""CRM: campaign_templates, campaigns, campaign_recipients

Revision ID: crm_campaigns_20260524
Revises: None
Create Date: 2026-05-24
"""

from alembic import op

revision = "crm_campaigns_20260524"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_crm")

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_crm.crm_campaign_templates (
            id              VARCHAR PRIMARY KEY,
            tenant_id       VARCHAR NOT NULL,
            name            VARCHAR(255) NOT NULL,
            description     TEXT,
            campaign_type   VARCHAR(50) NOT NULL DEFAULT 'email',
            subject_line    VARCHAR(500),
            message_body    TEXT,
            is_active       BOOLEAN NOT NULL DEFAULT TRUE,
            created_by      VARCHAR,
            meta            JSONB DEFAULT '{}',
            created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_crm_campaign_templates_tenant
        ON domain_crm.crm_campaign_templates (tenant_id)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_crm_campaign_templates_active
        ON domain_crm.crm_campaign_templates (tenant_id, is_active)
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_crm.crm_campaigns (
            id                   VARCHAR PRIMARY KEY,
            tenant_id            VARCHAR NOT NULL,
            name                 VARCHAR(255) NOT NULL,
            description          TEXT,
            state                VARCHAR(20) NOT NULL DEFAULT 'draft',
            campaign_type        VARCHAR(50) NOT NULL DEFAULT 'email',
            template_id          VARCHAR REFERENCES domain_crm.crm_campaign_templates(id) ON DELETE SET NULL,
            segment_id           VARCHAR,
            start_date           TIMESTAMP WITH TIME ZONE,
            end_date             TIMESTAMP WITH TIME ZONE,
            budget               NUMERIC(12,2),
            owner_id             VARCHAR,
            total_sent           INTEGER NOT NULL DEFAULT 0,
            total_delivered      INTEGER NOT NULL DEFAULT 0,
            total_bounced        INTEGER NOT NULL DEFAULT 0,
            total_opens          INTEGER NOT NULL DEFAULT 0,
            total_clicks         INTEGER NOT NULL DEFAULT 0,
            total_conversions    INTEGER NOT NULL DEFAULT 0,
            revenue_generated    NUMERIC(12,2) NOT NULL DEFAULT 0,
            activated_at         TIMESTAMP WITH TIME ZONE,
            paused_at            TIMESTAMP WITH TIME ZONE,
            completed_at         TIMESTAMP WITH TIME ZONE,
            campaign_channel     VARCHAR(50),
            target_customer_type VARCHAR(50),
            seasonal_context     VARCHAR(50),
            meta                 JSONB DEFAULT '{}',
            created_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_crm_campaigns_tenant
        ON domain_crm.crm_campaigns (tenant_id)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_crm_campaigns_state
        ON domain_crm.crm_campaigns (tenant_id, state)
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_crm.crm_campaign_recipients (
            id             VARCHAR PRIMARY KEY,
            tenant_id      VARCHAR NOT NULL,
            campaign_id    VARCHAR NOT NULL REFERENCES domain_crm.crm_campaigns(id) ON DELETE CASCADE,
            recipient_id   VARCHAR NOT NULL,
            recipient_type VARCHAR(50) NOT NULL DEFAULT 'contact',
            status         VARCHAR(20) NOT NULL DEFAULT 'queued',
            sent_at        TIMESTAMP WITH TIME ZONE,
            opened_at      TIMESTAMP WITH TIME ZONE,
            clicked_at     TIMESTAMP WITH TIME ZONE,
            converted_at   TIMESTAMP WITH TIME ZONE,
            bounce_reason  VARCHAR(255),
            meta           JSONB DEFAULT '{}',
            created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_crm_campaign_recipients_campaign
        ON domain_crm.crm_campaign_recipients (campaign_id, tenant_id)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_crm_campaign_recipients_recipient
        ON domain_crm.crm_campaign_recipients (recipient_id, tenant_id)
    """)

    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_crm_campaign_recipients_unique
        ON domain_crm.crm_campaign_recipients (campaign_id, recipient_id)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_crm.crm_campaign_recipients")
    op.execute("DROP TABLE IF EXISTS domain_crm.crm_campaigns")
    op.execute("DROP TABLE IF EXISTS domain_crm.crm_campaign_templates")
