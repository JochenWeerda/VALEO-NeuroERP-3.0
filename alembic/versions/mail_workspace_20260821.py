"""Role based ERP mail workspace.

Revision ID: mail_workspace_20260821
Revises: team_calendar_20260821
"""

from alembic import op

revision = "mail_workspace_20260821"
down_revision = "team_calendar_20260821"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      CREATE SCHEMA IF NOT EXISTS domain_crm;
      CREATE TABLE IF NOT EXISTS domain_crm.mail_workspace_messages (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, role_key TEXT NOT NULL,
        message_id TEXT NOT NULL, direction TEXT NOT NULL, status TEXT NOT NULL,
        from_address TEXT, to_addresses JSONB NOT NULL DEFAULT '[]'::jsonb,
        subject TEXT, body_text TEXT, contact_id TEXT, document_type TEXT,
        document_ref TEXT, document_route TEXT, assigned_to TEXT,
        provider_ref TEXT, error_message TEXT,
        received_at TIMESTAMPTZ, sent_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (tenant_id,message_id),
        CHECK (direction IN ('incoming','outgoing')),
        CHECK (status IN ('received','draft','queued','sent','error','archived'))
      );
      CREATE INDEX IF NOT EXISTS ix_mail_workspace_role_inbox
        ON domain_crm.mail_workspace_messages (tenant_id,role_key,status,received_at,created_at);
      CREATE TABLE IF NOT EXISTS domain_crm.mail_workspace_attachments (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, message_id TEXT NOT NULL
          REFERENCES domain_crm.mail_workspace_messages(id),
        filename TEXT NOT NULL, mime_type TEXT, size_bytes INTEGER NOT NULL,
        sha256 TEXT NOT NULL, content BYTEA, transfer_status TEXT NOT NULL DEFAULT 'available',
        dms_document_id TEXT, transferred_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (tenant_id,message_id,filename,sha256),
        CHECK (transfer_status IN ('available','transferred','rejected'))
      );
      CREATE TABLE IF NOT EXISTS domain_crm.mail_workspace_audit (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, message_id TEXT,
        action TEXT NOT NULL, actor TEXT NOT NULL, reason TEXT NOT NULL,
        payload_hash TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
      CREATE INDEX IF NOT EXISTS ix_mail_workspace_audit
        ON domain_crm.mail_workspace_audit (tenant_id,message_id,created_at);
    """)


def downgrade() -> None:
    op.execute("""
      DROP TABLE IF EXISTS domain_crm.mail_workspace_audit;
      DROP TABLE IF EXISTS domain_crm.mail_workspace_attachments;
      DROP TABLE IF EXISTS domain_crm.mail_workspace_messages;
    """)
