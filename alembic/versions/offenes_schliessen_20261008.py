"""Bestellkommunikation mit Inhalt; Bankkonten im Mandanten.

Revision ID: offenes_schliessen_20261008
Revises: lagercode_mandant_20261008

* ``domain_einkauf.bestellung_kommunikation``: ``nachricht``, ``erfasst_am``,
  ``erfasst_von`` — die Bestellmaske zeigt die Kommunikation aus dieser Tabelle;
  bis 08.10.2026 landeten Eintraege stattdessen im Dokumentspeicher, und nur
  fuer Altbelege.
* ``domain_erp.bank_accounts``: Kontonummer je Mandant statt systemweit eindeutig.
* ``domain_ops.ops_bankkonten`` hatte **keine** ``tenant_id``: ``/banken/konten``
  zeigte und aenderte die Bankkonten aller Mandanten. Jetzt ``tenant_id NOT NULL``
  mit Fremdschluessel und IBAN je Mandant eindeutig. Gibt es bereits Zeilen,
  bricht die Migration ab — ihr Mandant laesst sich nicht erraten.
"""

from alembic import op
from sqlalchemy import text

revision = "offenes_schliessen_20261008"
down_revision = "lagercode_mandant_20261008"
branch_labels = None
depends_on = None


def _constraint_dazu(tabelle: str, name: str, definition: str) -> None:
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = '{name}' AND conrelid = '{tabelle}'::regclass
            ) THEN
                ALTER TABLE {tabelle} ADD CONSTRAINT {name} {definition};
            END IF;
        END $$;
        """
    )


def upgrade() -> None:
    verbindung = op.get_bind()

    op.execute(
        "ALTER TABLE domain_einkauf.bestellung_kommunikation "
        "ADD COLUMN IF NOT EXISTS nachricht TEXT, "
        "ADD COLUMN IF NOT EXISTS erfasst_am TIMESTAMPTZ NOT NULL DEFAULT now(), "
        "ADD COLUMN IF NOT EXISTS erfasst_von VARCHAR(100)"
    )

    dubletten = verbindung.execute(text(
        "SELECT tenant_id, account_number FROM domain_erp.bank_accounts "
        "GROUP BY tenant_id, account_number HAVING count(*) > 1 LIMIT 5"
    )).all()
    if dubletten:
        raise RuntimeError(f"Doppelte Bankkontonummern je Mandant, bitte zuerst bereinigen: {dubletten}")
    op.execute("ALTER TABLE domain_erp.bank_accounts DROP CONSTRAINT IF EXISTS bank_accounts_account_number_key")
    _constraint_dazu("domain_erp.bank_accounts", "uq_bank_accounts_mandant_nummer",
                     "UNIQUE NULLS NOT DISTINCT (tenant_id, account_number)")

    op.execute("ALTER TABLE domain_ops.ops_bankkonten ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(64)")
    ohne = verbindung.execute(text("SELECT count(*) FROM domain_ops.ops_bankkonten WHERE tenant_id IS NULL")).scalar()
    if ohne:
        raise RuntimeError(
            f"{ohne} Bankkonten in domain_ops.ops_bankkonten ohne Mandant: bitte tenant_id setzen, dann erneut migrieren."
        )
    op.execute("ALTER TABLE domain_ops.ops_bankkonten ALTER COLUMN tenant_id SET NOT NULL")
    _constraint_dazu("domain_ops.ops_bankkonten", "fk_ops_bankkonten_tenant",
                     "FOREIGN KEY (tenant_id) REFERENCES domain_shared.tenants(id)")
    op.execute("ALTER TABLE domain_ops.ops_bankkonten DROP CONSTRAINT IF EXISTS ops_bankkonten_iban_key")
    _constraint_dazu("domain_ops.ops_bankkonten", "uq_ops_bankkonten_mandant_iban", "UNIQUE (tenant_id, iban)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_ops_bankkonten_tenant ON domain_ops.ops_bankkonten (tenant_id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_ops.ix_ops_bankkonten_tenant")
    op.execute("ALTER TABLE domain_ops.ops_bankkonten DROP CONSTRAINT IF EXISTS uq_ops_bankkonten_mandant_iban")
    op.execute("ALTER TABLE domain_ops.ops_bankkonten DROP CONSTRAINT IF EXISTS fk_ops_bankkonten_tenant")
    op.execute("ALTER TABLE domain_ops.ops_bankkonten DROP COLUMN IF EXISTS tenant_id")
    op.execute("ALTER TABLE domain_erp.bank_accounts DROP CONSTRAINT IF EXISTS uq_bank_accounts_mandant_nummer")
    op.execute(
        "ALTER TABLE domain_einkauf.bestellung_kommunikation "
        "DROP COLUMN IF EXISTS erfasst_von, DROP COLUMN IF EXISTS erfasst_am, DROP COLUMN IF EXISTS nachricht"
    )
