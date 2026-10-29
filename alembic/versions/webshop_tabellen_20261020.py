"""Webshop-Anbindung: Konfigurationen, Bestellungen und Synchronisationsprotokoll als Tabellen.

Revision ID: webshop_tabellen_20261020
Revises: audit_evidence_20261020

``app/services/webshop_integration_service.py`` las und schrieb ``domain_shared.webshop_configs``,
``webshop_bestellungen`` und ``webshop_sync_log``; keine Migration legte sie an. Auf jeder frischen Installation
fielen Konfigurationen und importierte Bestellungen in einen Arbeitsspeicher-Ersatz und gingen beim Neustart
verloren (20.10.2026).
"""
from alembic import op

revision = "webshop_tabellen_20261020"
down_revision = "audit_evidence_20261020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.webshop_configs (
            id                     VARCHAR(64)  PRIMARY KEY,
            tenant_id              VARCHAR(80)  NOT NULL,
            shop_url               VARCHAR(500) NOT NULL,
            api_key_masked         VARCHAR(32)  NOT NULL DEFAULT '****',
            shop_system            VARCHAR(40)  NOT NULL,
            sync_interval_minutes  INTEGER      NOT NULL DEFAULT 15,
            is_active              BOOLEAN      NOT NULL DEFAULT TRUE,
            created_at             TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_webshop_configs_tenant ON domain_shared.webshop_configs (tenant_id)")
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.webshop_bestellungen (
            id                   VARCHAR(64)   PRIMARY KEY,
            tenant_id            VARCHAR(80)   NOT NULL,
            externe_bestellnr    VARCHAR(120)  NOT NULL,
            shop_system          VARCHAR(40)   NOT NULL DEFAULT 'CUSTOM',
            kunde_email          VARCHAR(255)  NOT NULL DEFAULT '',
            kunde_name           VARCHAR(255)  NOT NULL DEFAULT '',
            artikel_positionen   JSONB         NOT NULL DEFAULT '[]'::jsonb,
            gesamtbetrag_brutto  NUMERIC(14, 2) NOT NULL DEFAULT 0,
            bestelldatum         VARCHAR(32)   NOT NULL DEFAULT '',
            status               VARCHAR(20)   NOT NULL DEFAULT 'NEU',
            blockers             JSONB         NOT NULL DEFAULT '[]'::jsonb,
            imported_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
            erp_order_number     VARCHAR(64),
            processed_at         TIMESTAMPTZ,
            CONSTRAINT uq_webshop_bestellung UNIQUE (tenant_id, externe_bestellnr)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.webshop_sync_log (
            id           VARCHAR(64)  PRIMARY KEY,
            tenant_id    VARCHAR(80)  NOT NULL,
            shop_system  VARCHAR(40)  NOT NULL DEFAULT 'CUSTOM',
            ereignis     VARCHAR(40)  NOT NULL,
            details      TEXT         NOT NULL DEFAULT '',
            erfolgreich  BOOLEAN      NOT NULL DEFAULT TRUE,
            zeitpunkt    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_webshop_sync_log_tenant "
               "ON domain_shared.webshop_sync_log (tenant_id, zeitpunkt DESC)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_shared.webshop_sync_log")
    op.execute("DROP TABLE IF EXISTS domain_shared.webshop_bestellungen")
    op.execute("DROP TABLE IF EXISTS domain_shared.webshop_configs")
