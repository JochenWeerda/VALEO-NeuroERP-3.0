"""vat_codes entfaellt: Steuerschluessel kommen allein aus domain_erp.tax_keys.

Revision ID: vat_codes_entfernt_20261012
Revises: steuerschluessel_einheit_20261012

``vat_codes`` und ``vat_codes_audit`` (angelegt mit ``add_vat_codes_20260220``) hatten Pflegewege,
aber keinen Verbraucher: keine Maske, kein Beleg, keine Auswertung las daraus. Massgeblich ist
``domain_erp.tax_keys`` — die Tabelle hinter der Maske „Steuerschluessel“, aus der Eingangsrechnung,
Umsatzsteuer-Voranmeldung und Gutschrift lesen. Entscheidung des Auftraggebers vom 12.10.2026: loeschen.

Mit den Tabellen gehen die zehn Vorgabezeilen (``DE_19`` …) und, wo vorhanden, Aenderungen daran
verloren. Der Rueckweg legt die leeren Tabellen wieder an, nicht ihren Inhalt.
"""

from alembic import op

revision = "vat_codes_entfernt_20261012"
down_revision = "steuerschluessel_einheit_20261012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS vat_codes_audit")
    op.execute("DROP TABLE IF EXISTS vat_codes")
    op.execute("DROP TYPE IF EXISTS vatcodecategory")


def downgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE vatcodecategory AS ENUM
                ('DE_INLAND', 'DE_AGR_PAUSCHAL', 'DE_FORST', 'EU_IGL', 'EU_ERWERB', 'EU_OSS', 'EXPORT', 'EXEMPT');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS vat_codes (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            name_long VARCHAR(500),
            category vatcodecategory NOT NULL,
            rate DOUBLE PRECISION NOT NULL,
            skr03_account VARCHAR(10),
            skr04_account VARCHAR(10),
            valid_from TIMESTAMP NOT NULL DEFAULT now(),
            valid_to TIMESTAMP,
            is_active BOOLEAN,
            legal_basis VARCHAR(200),
            legal_note TEXT,
            is_standard BOOLEAN,
            is_reduced BOOLEAN,
            is_zero BOOLEAN,
            is_reverse_charge BOOLEAN,
            is_agricultural BOOLEAN,
            paragraph_24 BOOLEAN,
            tenant_id VARCHAR(50),
            created_at TIMESTAMP DEFAULT now(),
            created_by VARCHAR(100),
            updated_at TIMESTAMP DEFAULT now(),
            updated_by VARCHAR(100)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS vat_codes_audit (
            id VARCHAR(50) PRIMARY KEY,
            vat_code_id VARCHAR(50) NOT NULL,
            action VARCHAR(20) NOT NULL,
            change_type VARCHAR(50),
            old_value TEXT,
            new_value TEXT,
            changed_by VARCHAR(100) NOT NULL,
            changed_at TIMESTAMP DEFAULT now(),
            reason TEXT,
            legal_reference VARCHAR(200),
            tenant_id VARCHAR(50)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_vat_codes_category ON vat_codes (category)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_vat_codes_tenant ON vat_codes (tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_vat_codes_is_active ON vat_codes (is_active)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_vat_codes_audit_vat_code ON vat_codes_audit (vat_code_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_vat_codes_audit_changed_at ON vat_codes_audit (changed_at)")
