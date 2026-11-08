"""Versandwege: Anfragen mit Mandant, Mahnungen mit Versandweg.

Revision ID: versandwege_echt_20261008
Revises: fuhrpark_tenant_ce_20261009

``einkauf_anfragen`` wurde ohne ``tenant_id`` angelegt, jeder Zugriff filtert aber
danach (Liste, Laden, Anlegen, Versand). Auf einer frischen Datenbank scheiterte
deshalb jeder Aufruf; in der gewachsenen fehlte die Tabelle ganz. Weil das Anlegen
nie gelang, gibt es keine Zeile ohne Mandant: die Spalte kann gleich NOT NULL sein.
Die Anfragenummer ist je Mandant eindeutig, nicht systemweit.

``dunning_notices`` merkt sich, wie und an wen eine Mahnung ging (E-Mail oder Post).
"""

from alembic import op

revision = "versandwege_echt_20261008"
down_revision = "fuhrpark_tenant_ce_20261009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS einkauf_anfragen (
            id VARCHAR(36) PRIMARY KEY,
            anfrage_nummer VARCHAR(100) NOT NULL,
            typ VARCHAR(20) NOT NULL DEFAULT 'BANF',
            anforderer VARCHAR(100) NOT NULL,
            abteilung VARCHAR(100),
            datum DATE,
            prioritaet VARCHAR(50) NOT NULL DEFAULT 'normal',
            status VARCHAR(50) NOT NULL DEFAULT 'ENTWURF',
            begruendung TEXT,
            kostenstelle VARCHAR(100),
            projekt_id VARCHAR(36),
            artikel VARCHAR(255),
            menge NUMERIC(15, 3),
            einheit VARCHAR(20),
            budget NUMERIC(15, 2),
            notizen TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS einkauf_anfragen_positionen (
            id VARCHAR(36) PRIMARY KEY,
            anfrage_id VARCHAR(36) NOT NULL REFERENCES einkauf_anfragen (id),
            article_id VARCHAR(36),
            artikel VARCHAR(255),
            quantity NUMERIC(15, 3) NOT NULL,
            unit VARCHAR(20) NOT NULL,
            due_date DATE,
            notes TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_einkauf_anfragen_pos_req_id ON einkauf_anfragen_positionen (anfrage_id)")
    op.execute("ALTER TABLE einkauf_anfragen ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(36)")
    op.execute("ALTER TABLE einkauf_anfragen ALTER COLUMN tenant_id SET NOT NULL")
    op.execute("ALTER TABLE einkauf_anfragen DROP CONSTRAINT IF EXISTS uq_einkauf_anfragen_nummer")
    op.execute("ALTER TABLE einkauf_anfragen DROP CONSTRAINT IF EXISTS uq_einkauf_anfragen_mandant_nummer")
    op.execute(
        "ALTER TABLE einkauf_anfragen ADD CONSTRAINT uq_einkauf_anfragen_mandant_nummer "
        "UNIQUE (tenant_id, anfrage_nummer)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_einkauf_anfragen_tenant_status ON einkauf_anfragen (tenant_id, status)")

    op.execute("ALTER TABLE domain_erp.dunning_notices ADD COLUMN IF NOT EXISTS versand_art VARCHAR(10)")
    op.execute("ALTER TABLE domain_erp.dunning_notices ADD COLUMN IF NOT EXISTS empfaenger VARCHAR(320)")
    op.execute("ALTER TABLE domain_erp.dunning_notices DROP CONSTRAINT IF EXISTS ck_dunning_versand_art")
    op.execute(
        "ALTER TABLE domain_erp.dunning_notices ADD CONSTRAINT ck_dunning_versand_art "
        "CHECK (versand_art IS NULL OR versand_art IN ('email', 'post'))"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE domain_erp.dunning_notices DROP CONSTRAINT IF EXISTS ck_dunning_versand_art")
    op.execute("ALTER TABLE domain_erp.dunning_notices DROP COLUMN IF EXISTS empfaenger")
    op.execute("ALTER TABLE domain_erp.dunning_notices DROP COLUMN IF EXISTS versand_art")
    op.execute("DROP INDEX IF EXISTS ix_einkauf_anfragen_tenant_status")
    op.execute("ALTER TABLE einkauf_anfragen DROP CONSTRAINT IF EXISTS uq_einkauf_anfragen_mandant_nummer")
    op.execute(
        "ALTER TABLE einkauf_anfragen ADD CONSTRAINT uq_einkauf_anfragen_nummer UNIQUE (anfrage_nummer)"
    )
    op.execute("ALTER TABLE einkauf_anfragen DROP COLUMN IF EXISTS tenant_id")
