"""Lead qualification reference and persistent PDF content in PostgreSQL."""
from alembic import op
import sqlalchemy as sa

revision = "lead_pdf_archive_20261007"
down_revision = "mandant_finanz_crm_20261007"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("crm_leads", sa.Column("qualified_opportunity_id", sa.String(64)), schema="public")
    op.add_column("document_artifacts", sa.Column("content_bytes", sa.LargeBinary()), schema="domain_docflow")
    op.execute("""
        CREATE FUNCTION domain_docflow.guard_archived_content() RETURNS trigger AS $$
        BEGIN
            IF OLD.content_bytes IS NOT NULL THEN
                IF TG_OP = 'DELETE' THEN
                    RAISE EXCEPTION 'Archived content cannot be deleted';
                END IF;
                IF ROW(NEW.content_bytes, NEW.content_hash_sha256, NEW.tenant_id, NEW.header_id, NEW.storage_key)
                   IS DISTINCT FROM ROW(OLD.content_bytes, OLD.content_hash_sha256, OLD.tenant_id, OLD.header_id, OLD.storage_key) THEN
                    RAISE EXCEPTION 'Archived content and identity cannot be changed';
                END IF;
            END IF;
            IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER guard_archived_content BEFORE UPDATE OR DELETE
        ON domain_docflow.document_artifacts FOR EACH ROW
        EXECUTE FUNCTION domain_docflow.guard_archived_content();
    """)


def downgrade():
    op.execute("DROP TRIGGER guard_archived_content ON domain_docflow.document_artifacts")
    op.execute("DROP FUNCTION domain_docflow.guard_archived_content()")
    op.drop_column("document_artifacts", "content_bytes", schema="domain_docflow")
    op.drop_column("crm_leads", "qualified_opportunity_id", schema="public")
