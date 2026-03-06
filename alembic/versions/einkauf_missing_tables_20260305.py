"""Einkauf: missing tables for RFQ, delivery advices, order confirmations, article groups, payment runs

Revision ID: einkauf_missing_20260305
Revises: sales_cn_ret_pl_20260305
Create Date: 2026-03-05
"""

from alembic import op
import sqlalchemy as sa

revision = "einkauf_missing_20260305"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # ---- Einkauf Angebote (supplier quotes / RFQ bids) ----
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS einkauf_angebote (
            id              VARCHAR(36) PRIMARY KEY,
            tenant_id       VARCHAR(64) NOT NULL DEFAULT 'default',
            anfrage_id      VARCHAR(36),
            lieferant_id    VARCHAR(36),
            lieferant_name  VARCHAR(200),
            angebotsnummer  VARCHAR(64),
            datum           DATE DEFAULT CURRENT_DATE,
            gueltig_bis     DATE,
            gesamtbetrag    NUMERIC(18,4) DEFAULT 0,
            waehrung        VARCHAR(3) DEFAULT 'EUR',
            status          VARCHAR(20) DEFAULT 'offen',
            notizen         TEXT,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        )
    """))
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS einkauf_angebote_positionen (
            id              VARCHAR(36) PRIMARY KEY,
            angebot_id      VARCHAR(36) NOT NULL REFERENCES einkauf_angebote(id) ON DELETE CASCADE,
            pos_nr          INT DEFAULT 1,
            artikel_nr      VARCHAR(80),
            bezeichnung     VARCHAR(500),
            menge           NUMERIC(18,4) DEFAULT 0,
            einheit         VARCHAR(20) DEFAULT 'Stk',
            einheitspreis   NUMERIC(18,4) DEFAULT 0,
            gesamtpreis     NUMERIC(18,4) DEFAULT 0,
            lieferzeit_tage INT
        )
    """))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_ea_tenant ON einkauf_angebote(tenant_id)"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_ea_anfrage ON einkauf_angebote(anfrage_id)"))

    # ---- Einkauf Anlieferavis (delivery advices) ----
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS einkauf_anlieferavis (
            id              VARCHAR(36) PRIMARY KEY,
            tenant_id       VARCHAR(64) NOT NULL DEFAULT 'default',
            lieferant_id    VARCHAR(36),
            lieferant_name  VARCHAR(200),
            avis_nummer     VARCHAR(64),
            bestell_nr      VARCHAR(64),
            erwartetes_datum DATE,
            status          VARCHAR(20) DEFAULT 'offen',
            notizen         TEXT,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        )
    """))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_eav_tenant ON einkauf_anlieferavis(tenant_id)"))

    # ---- Einkauf Auftragsbestätigungen (order confirmations from suppliers) ----
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS einkauf_auftragsbestaetigungen (
            id              VARCHAR(36) PRIMARY KEY,
            tenant_id       VARCHAR(64) NOT NULL DEFAULT 'default',
            lieferant_id    VARCHAR(36),
            lieferant_name  VARCHAR(200),
            ab_nummer       VARCHAR(64),
            bestell_nr      VARCHAR(64),
            datum           DATE DEFAULT CURRENT_DATE,
            lieferdatum     DATE,
            gesamtbetrag    NUMERIC(18,4) DEFAULT 0,
            waehrung        VARCHAR(3) DEFAULT 'EUR',
            status          VARCHAR(20) DEFAULT 'offen',
            abweichungen    TEXT,
            notizen         TEXT,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        )
    """))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_eab_tenant ON einkauf_auftragsbestaetigungen(tenant_id)"))

    # ---- Einkauf Warengruppen (article groups / categories) ----
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS einkauf_warengruppen (
            id              VARCHAR(36) PRIMARY KEY,
            tenant_id       VARCHAR(64) NOT NULL DEFAULT 'default',
            code            VARCHAR(20) NOT NULL,
            name            VARCHAR(200) NOT NULL,
            parent_id       VARCHAR(36),
            description     TEXT,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        )
    """))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_ewg_tenant ON einkauf_warengruppen(tenant_id)"))
    conn.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS idx_ewg_code ON einkauf_warengruppen(tenant_id, code)"))

    # ---- Einkauf Zahlungsläufe (payment runs) ----
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS einkauf_zahlungslaeufe (
            id              VARCHAR(36) PRIMARY KEY,
            tenant_id       VARCHAR(64) NOT NULL DEFAULT 'default',
            lauf_nummer     VARCHAR(64),
            datum           DATE DEFAULT CURRENT_DATE,
            faellig_bis     DATE,
            status          VARCHAR(20) DEFAULT 'entwurf',
            gesamtbetrag    NUMERIC(18,4) DEFAULT 0,
            waehrung        VARCHAR(3) DEFAULT 'EUR',
            anzahl_posten   INT DEFAULT 0,
            sepa_xml        TEXT,
            erstellt_von    VARCHAR(64),
            ausgefuehrt_am  TIMESTAMPTZ,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            updated_at      TIMESTAMPTZ DEFAULT NOW()
        )
    """))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_ezl_tenant ON einkauf_zahlungslaeufe(tenant_id)"))

    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS einkauf_zahlungslauf_posten (
            id              VARCHAR(36) PRIMARY KEY,
            zahlungslauf_id VARCHAR(36) NOT NULL REFERENCES einkauf_zahlungslaeufe(id) ON DELETE CASCADE,
            rechnung_id     VARCHAR(36),
            lieferant_id    VARCHAR(36),
            lieferant_name  VARCHAR(200),
            betrag          NUMERIC(18,4) DEFAULT 0,
            iban            VARCHAR(34),
            bic             VARCHAR(11),
            verwendungszweck VARCHAR(140),
            status          VARCHAR(20) DEFAULT 'offen'
        )
    """))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_ezlp_lauf ON einkauf_zahlungslauf_posten(zahlungslauf_id)"))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS einkauf_zahlungslauf_posten"))
    conn.execute(sa.text("DROP TABLE IF EXISTS einkauf_zahlungslaeufe"))
    conn.execute(sa.text("DROP TABLE IF EXISTS einkauf_warengruppen"))
    conn.execute(sa.text("DROP TABLE IF EXISTS einkauf_auftragsbestaetigungen"))
    conn.execute(sa.text("DROP TABLE IF EXISTS einkauf_anlieferavis"))
    conn.execute(sa.text("DROP TABLE IF EXISTS einkauf_angebote_positionen"))
    conn.execute(sa.text("DROP TABLE IF EXISTS einkauf_angebote"))
