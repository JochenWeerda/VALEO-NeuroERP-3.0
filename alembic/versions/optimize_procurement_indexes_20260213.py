"""
Optimize indexes for documents/procurement frequent query paths.
"""

from alembic import op

# Revision identifiers, used by Alembic.
revision = "optimize_procurement_indexes_20260213"
down_revision = "log_touren_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_documents_doc_type_created_at
        ON documents (doc_type, created_at DESC);
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_documents_doc_type_doc_number
        ON documents (doc_type, doc_number);
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_documents_tenant_id
        ON documents ((data->>'tenantId'));
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_documents_status
        ON documents ((data->>'status'));
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_documents_supplier_id
        ON documents ((data->>'supplierId'));
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_documents_purchase_order_id
        ON documents ((data->>'purchaseOrderId'));
        """
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('public.einkauf_lieferanten') IS NOT NULL THEN
                CREATE INDEX IF NOT EXISTS ix_einkauf_lieferanten_aktiv_name
                ON einkauf_lieferanten (aktiv, firmenname);
            END IF;
            IF to_regclass('public.einkauf_rechnungseingaenge') IS NOT NULL THEN
                CREATE INDEX IF NOT EXISTS ix_einkauf_rechnungseingaenge_status_created
                ON einkauf_rechnungseingaenge (status, created_at DESC);
            END IF;
            IF to_regclass('public.einkauf_retouren') IS NOT NULL THEN
                CREATE INDEX IF NOT EXISTS ix_einkauf_retouren_status_created
                ON einkauf_retouren (status, created_at DESC);
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_einkauf_retouren_status_created;")
    op.execute("DROP INDEX IF EXISTS ix_einkauf_rechnungseingaenge_status_created;")
    op.execute("DROP INDEX IF EXISTS ix_einkauf_lieferanten_aktiv_name;")
    op.execute("DROP INDEX IF EXISTS ix_documents_purchase_order_id;")
    op.execute("DROP INDEX IF EXISTS ix_documents_supplier_id;")
    op.execute("DROP INDEX IF EXISTS ix_documents_status;")
    op.execute("DROP INDEX IF EXISTS ix_documents_tenant_id;")
    op.execute("DROP INDEX IF EXISTS ix_documents_doc_type_doc_number;")
    op.execute("DROP INDEX IF EXISTS ix_documents_doc_type_created_at;")

