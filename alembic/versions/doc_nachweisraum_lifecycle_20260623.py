"""DOM-DOC-004 — Nachweisraum Dokument-Lifecycle + GoBD-Export Tabellen

Revision ID: doc_nachweisraum_lifecycle_20260623
Revises: pos_tagesabschluss_lifecycle_20260623
Create Date: 2026-06-23
"""
from alembic import op
import sqlalchemy as sa

revision = "doc_nachweisraum_lifecycle_20260623"
down_revision = "pos_tagesabschluss_lifecycle_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_nachweisraum")

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_nachweisraum.nachweisraum_dokumente (
            id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            tenant_id           TEXT NOT NULL,
            dokument_typ        TEXT NOT NULL,
            bezeichnung         TEXT NOT NULL DEFAULT '',
            referenz_id         TEXT NOT NULL,
            referenz_typ        TEXT NOT NULL,
            datei_pfad          TEXT NOT NULL DEFAULT '',
            version             INT NOT NULL DEFAULT 1,
            status              TEXT NOT NULL DEFAULT 'EINGEGANGEN',
            wiedervorlage_datum TEXT,
            operator            TEXT NOT NULL DEFAULT 'system',
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_nachweisraum.nachweisraum_audit_log (
            id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            dokument_id     UUID NOT NULL,
            tenant_id       TEXT NOT NULL,
            old_status      TEXT NOT NULL DEFAULT '',
            new_status      TEXT NOT NULL,
            operator        TEXT NOT NULL DEFAULT 'system',
            kommentar       TEXT NOT NULL DEFAULT '',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_nachweisraum.gobd_exporte (
            id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            tenant_id           TEXT NOT NULL,
            periode             TEXT NOT NULL,
            anzahl_dokumente    INT NOT NULL DEFAULT 0,
            status              TEXT NOT NULL DEFAULT 'OFFEN',
            export_pfad         TEXT,
            fehler_grund        TEXT,
            operator            TEXT NOT NULL DEFAULT 'system',
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_nachweisraum.gobd_exporte")
    op.execute("DROP TABLE IF EXISTS domain_nachweisraum.nachweisraum_audit_log")
    op.execute("DROP TABLE IF EXISTS domain_nachweisraum.nachweisraum_dokumente")
