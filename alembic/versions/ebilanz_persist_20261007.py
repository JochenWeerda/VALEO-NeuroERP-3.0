"""Own the existing eBilanz draft schema; requests never create tables."""
from alembic import op

revision = "ebilanz_persist_20261007"
down_revision = "lead_pdf_archive_20261007"
branch_labels = None
depends_on = None


def upgrade():
    # IF NOT EXISTS adopts the former development-only request table without
    # deleting or rewriting anyone else's historical export records.
    op.execute("""CREATE TABLE IF NOT EXISTS domain_finance.ebilanz_exports (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, wirtschaftsjahr INT,
        bilanzart TEXT, berichtsperiode_von TEXT, berichtsperiode_bis TEXT,
        steuernummer TEXT, finanzamt_nr TEXT, status TEXT DEFAULT 'ERSTELLT',
        taxonomie_version TEXT DEFAULT '6.7', xbrl_paketgroesse_kb INT DEFAULT 0,
        elster_transfer_ticket TEXT, uebertragen_am TIMESTAMP,
        erstellt_am TIMESTAMP DEFAULT NOW()
    )""")
    op.execute("ALTER TABLE domain_finance.ebilanz_exports ALTER COLUMN xbrl_paketgroesse_kb SET DEFAULT 0")
    op.execute("CREATE INDEX IF NOT EXISTS ix_ebilanz_exports_tenant_created ON domain_finance.ebilanz_exports (tenant_id, erstellt_am, id)")


def downgrade():
    op.execute("DROP INDEX IF EXISTS domain_finance.ix_ebilanz_exports_tenant_created")
    op.execute("DROP TABLE domain_finance.ebilanz_exports")
