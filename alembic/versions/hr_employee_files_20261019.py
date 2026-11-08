"""Canonical tenant-bound personal file metadata; no pilot persistence."""
from alembic import op

revision = "hr_employee_files_20261019"
down_revision = "harvest_rule_store_20261015"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE domain_hr.employee_file_documents (
            id VARCHAR PRIMARY KEY,
            tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
            employee_ref VARCHAR NOT NULL CHECK (length(trim(employee_ref)) > 0),
            document_type VARCHAR(80) NOT NULL,
            title VARCHAR(180) NOT NULL CHECK (length(trim(title)) > 0),
            status VARCHAR(40) NOT NULL DEFAULT 'active',
            visibility VARCHAR(20) NOT NULL CHECK (visibility IN ('employee','manager','hr','payroll')),
            issued_at DATE,
            valid_until DATE,
            retention_until DATE NOT NULL,
            dms_document_id VARCHAR(160),
            audit_ref VARCHAR(100) NOT NULL,
            notes VARCHAR(500),
            created_by VARCHAR NOT NULL CHECK (length(trim(created_by)) > 0),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (tenant_id, audit_ref)
        );
        CREATE INDEX ix_employee_file_documents_tenant_employee
        ON domain_hr.employee_file_documents (tenant_id, employee_ref, issued_at DESC, created_at DESC);
    """)


def downgrade():
    op.execute("DROP TABLE domain_hr.employee_file_documents")
