"""DOM-HRM-004 — HRM Zeiterfassung, Abwesenheit, Arbeitszeitkonto

Revision ID: hrm_zeiterfassung_abwesenheit_20260623
Revises: doc_nachweisraum_lifecycle_20260623
Create Date: 2026-06-23
"""
from alembic import op
import sqlalchemy as sa

revision = "hrm_zeiterfassung_abwesenheit_20260623"
down_revision = "doc_nachweisraum_lifecycle_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_hrm")

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_hrm.hrm_zeitbuchungen (
            id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            tenant_id           TEXT NOT NULL,
            mitarbeiter_id      TEXT NOT NULL,
            datum               TEXT NOT NULL,
            von_zeit            TEXT NOT NULL,
            bis_zeit            TEXT NOT NULL,
            stunden             NUMERIC(5,2) NOT NULL,
            taetigkeit          TEXT NOT NULL DEFAULT '',
            kostenstelle_id     TEXT NOT NULL DEFAULT '',
            status              TEXT NOT NULL DEFAULT 'OFFEN',
            korrektur_grund     TEXT NOT NULL DEFAULT '',
            operator            TEXT NOT NULL DEFAULT 'system',
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_hrm.hrm_mitarbeiter_konten (
            id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            tenant_id               TEXT NOT NULL,
            mitarbeiter_id          TEXT NOT NULL,
            soll_stunden_monat      NUMERIC(6,2) NOT NULL DEFAULT 168.0,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (tenant_id, mitarbeiter_id)
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_hrm.hrm_abwesenheiten (
            id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            tenant_id           TEXT NOT NULL,
            mitarbeiter_id      TEXT NOT NULL,
            abwesenheit_typ     TEXT NOT NULL,
            von_datum           TEXT NOT NULL,
            bis_datum           TEXT NOT NULL,
            arbeitstage         INT NOT NULL,
            kommentar           TEXT NOT NULL DEFAULT '',
            status              TEXT NOT NULL DEFAULT 'BEANTRAGT',
            ablehnungs_grund    TEXT NOT NULL DEFAULT '',
            operator            TEXT NOT NULL DEFAULT 'system',
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_hrm.hrm_abwesenheiten")
    op.execute("DROP TABLE IF EXISTS domain_hrm.hrm_mitarbeiter_konten")
    op.execute("DROP TABLE IF EXISTS domain_hrm.hrm_zeitbuchungen")
