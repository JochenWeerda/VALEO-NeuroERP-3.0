"""DOM-MEL-004 — Meldewesen Lifecycle Tabellen (Intrastat/ELSTER/ATLAS)

Revision ID: meldewesen_lifecycle_20260623
Revises: hrm_zeiterfassung_abwesenheit_20260623
Create Date: 2026-06-23
"""
from alembic import op
import sqlalchemy as sa

revision = "meldewesen_lifecycle_20260623"
down_revision = "hrm_zeiterfassung_abwesenheit_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_meldewesen")

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_meldewesen.meldungen (
            id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            tenant_id           TEXT NOT NULL,
            meldung_typ         TEXT NOT NULL,
            periode             TEXT NOT NULL,
            betrag_eur          NUMERIC(14,2) NOT NULL,
            waehrung            TEXT NOT NULL DEFAULT 'EUR',
            anzahl_positionen   INT NOT NULL DEFAULT 0,
            status              TEXT NOT NULL DEFAULT 'ENTWURF',
            fehler_grund        TEXT NOT NULL DEFAULT '',
            externe_referenz    TEXT,
            operator            TEXT NOT NULL DEFAULT 'system',
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_meldewesen.meldung_log (
            id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            meldung_id      UUID NOT NULL,
            tenant_id       TEXT NOT NULL,
            old_status      TEXT NOT NULL DEFAULT '',
            new_status      TEXT NOT NULL,
            operator        TEXT NOT NULL DEFAULT 'system',
            fehler_grund    TEXT NOT NULL DEFAULT '',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_meldewesen.meldung_log")
    op.execute("DROP TABLE IF EXISTS domain_meldewesen.meldungen")
