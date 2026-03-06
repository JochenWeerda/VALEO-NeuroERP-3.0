"""CRM: consent, segments and segment_members tables

Revision ID: crm_consent_seg_001
Revises: None
Create Date: 2026-03-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "crm_consent_seg_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_crm")

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_crm.crm_consents (
            id VARCHAR PRIMARY KEY,
            tenant_id VARCHAR NOT NULL,
            partner_id VARCHAR NOT NULL,
            channel VARCHAR(50) NOT NULL,
            purpose VARCHAR(200) NOT NULL,
            granted BOOLEAN NOT NULL DEFAULT TRUE,
            source VARCHAR(100) DEFAULT 'manual',
            ip_address VARCHAR(50),
            notes TEXT,
            granted_at TIMESTAMP,
            revoked_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_crm_consents_partner
        ON domain_crm.crm_consents (partner_id, tenant_id)
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_crm.crm_segments (
            id VARCHAR PRIMARY KEY,
            tenant_id VARCHAR NOT NULL,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            criteria JSONB DEFAULT '{}',
            segment_type VARCHAR(50) DEFAULT 'static',
            member_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_crm_segments_tenant
        ON domain_crm.crm_segments (tenant_id)
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_crm.crm_segment_members (
            id VARCHAR PRIMARY KEY,
            segment_id VARCHAR NOT NULL REFERENCES domain_crm.crm_segments(id) ON DELETE CASCADE,
            partner_id VARCHAR NOT NULL,
            added_at TIMESTAMP DEFAULT NOW(),
            UNIQUE (segment_id, partner_id)
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_crm_segment_members_seg
        ON domain_crm.crm_segment_members (segment_id)
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_crm.crm_opportunities (
            id VARCHAR PRIMARY KEY,
            tenant_id VARCHAR NOT NULL,
            customer_id VARCHAR NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            product_category VARCHAR(100),
            estimated_value DECIMAL(12,2),
            estimated_quantity DECIMAL(10,2),
            currency VARCHAR(3) DEFAULT 'EUR',
            stage VARCHAR(50) DEFAULT 'prospecting',
            probability INTEGER DEFAULT 0,
            expected_close_date TIMESTAMP,
            assigned_to VARCHAR NOT NULL DEFAULT 'unassigned',
            source VARCHAR(100),
            status VARCHAR(20) DEFAULT 'aktiv',
            is_active BOOLEAN DEFAULT TRUE,
            competitors JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_crm_opportunities_tenant
        ON domain_crm.crm_opportunities (tenant_id, is_active)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_crm.crm_segment_members")
    op.execute("DROP TABLE IF EXISTS domain_crm.crm_segments")
    op.execute("DROP TABLE IF EXISTS domain_crm.crm_consents")
    op.execute("DROP TABLE IF EXISTS domain_crm.crm_opportunities")
