"""EINKAUF-LS-REPAIR-001: Einkauf-Lieferschein + Opportunities Repair-Migration.

Tabellengruppen aus Parallel-Alembic-Branches idempotent in der Hauptkette anlegen:
  - einkauf_lieferscheine           (public, aus einkauf_lieferschein_frachtauftrag_20260214)
  - einkauf_lieferschein_positionen (public)
  - einkauf_frachtauftraege         (public)
  - opportunities                   (public, aus crm_phase4_opportunity_links_20260305 / crm-sales)

Revision ID: einkauf_ls_opportunities_repair_20260626
Revises: admin_mobile_repair_20260626
Create Date: 2026-06-26
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text


revision = "einkauf_ls_opportunities_repair_20260626"
down_revision = "admin_mobile_repair_20260626"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # ── einkauf_lieferscheine (public schema) ───────────────────────────────
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS einkauf_lieferscheine (
            id                  VARCHAR(36)     NOT NULL PRIMARY KEY,
            tenant_id           VARCHAR(36)     NOT NULL,
            lieferschein_nr     VARCHAR(64)     NOT NULL,
            lieferschein_datum  DATE            NOT NULL,
            niederlassung       VARCHAR(120),
            lieferant_id        VARCHAR(36),
            lieferant_name      VARCHAR(255),
            zahlungsbedingung   VARCHAR(120),
            texte               TEXT,
            zwischenhaendler    VARCHAR(255),
            wie_vom_ls          BOOLEAN         NOT NULL DEFAULT FALSE,
            lieferanten_stamm   VARCHAR(255),
            liefer_termin       DATE,
            lieferdatum         DATE,
            liefer_nr           VARCHAR(80),
            bediener            VARCHAR(120),
            erledigt            BOOLEAN         NOT NULL DEFAULT FALSE,
            verfuegbarer_bestand NUMERIC(14,3),
            summe_gewicht       NUMERIC(14,3),
            mwst_betrag         NUMERIC(14,2),
            netto_betrag        NUMERIC(14,2),
            brutto_betrag       NUMERIC(14,2),
            created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_einkauf_lieferschein_nr_tenant UNIQUE (tenant_id, lieferschein_nr)
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_einkauf_lieferscheine_tenant_id
            ON einkauf_lieferscheine (tenant_id)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_einkauf_lieferscheine_lieferant
            ON einkauf_lieferscheine (lieferant_id)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_einkauf_lieferscheine_datum
            ON einkauf_lieferscheine (lieferschein_datum)
    """))

    # ── einkauf_lieferschein_positionen (public schema) ─────────────────────
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS einkauf_lieferschein_positionen (
            id                  VARCHAR(36)     NOT NULL PRIMARY KEY,
            lieferschein_id     VARCHAR(36)     NOT NULL
                REFERENCES einkauf_lieferscheine (id) ON DELETE CASCADE,
            pos_nr              INTEGER         NOT NULL,
            artikel_nr          VARCHAR(64),
            lieferant_artikel_nr VARCHAR(64),
            bezeichnung         VARCHAR(255),
            gebinde_nr          VARCHAR(64),
            gebinde             NUMERIC(14,3),
            menge               NUMERIC(14,3)   NOT NULL,
            einheit             VARCHAR(20),
            einzelpreis         NUMERIC(14,4),
            nettobetrag         NUMERIC(14,2),
            lagerhalle          VARCHAR(80),
            lagerfach           VARCHAR(80),
            charge              VARCHAR(80),
            serien_nr           VARCHAR(80),
            kontakt             VARCHAR(120),
            prozent             NUMERIC(7,3),
            master_nr           VARCHAR(80),
            created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_einkauf_ls_pos_nr UNIQUE (lieferschein_id, pos_nr)
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_einkauf_lieferschein_positionen_lieferschein
            ON einkauf_lieferschein_positionen (lieferschein_id)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_einkauf_lieferschein_positionen_artikel
            ON einkauf_lieferschein_positionen (artikel_nr)
    """))

    # ── einkauf_frachtauftraege (public schema) ──────────────────────────────
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS einkauf_frachtauftraege (
            id                  VARCHAR(36)     NOT NULL PRIMARY KEY,
            tenant_id           VARCHAR(36)     NOT NULL,
            frachtauftrag_nr    VARCHAR(64)     NOT NULL,
            frachtauftrag_erzeugt TIMESTAMPTZ,
            niederlassung       VARCHAR(120),
            liefertermin        DATE,
            spediteur_nr        VARCHAR(64),
            spediteur_name      VARCHAR(255),
            email               VARCHAR(255),
            telefon             VARCHAR(60),
            belegnummer         VARCHAR(64),
            lade_datum          DATE,
            kunde_id            VARCHAR(36),
            kunde_name          VARCHAR(255),
            debitoren_filter    VARCHAR(120),
            created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_einkauf_frachtauftrag_nr_tenant UNIQUE (tenant_id, frachtauftrag_nr)
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_einkauf_frachtauftraege_tenant_id
            ON einkauf_frachtauftraege (tenant_id)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_einkauf_frachtauftraege_spediteur
            ON einkauf_frachtauftraege (spediteur_nr)
    """))

    # ── opportunities (public schema — CRM-Sales) ────────────────────────────
    # Der Endpoint /crm/opportunities/pipeline und /crm-sales/opportunities
    # lesen direkt aus public.opportunities. Die Originalmigration liegt in
    # crm_phase4_opportunity_links_20260305 (Parallel-Branch).
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id                  VARCHAR(64)     NOT NULL PRIMARY KEY,
            tenant_id           VARCHAR(64),
            title               VARCHAR(255)    NOT NULL,
            stage               TEXT            NOT NULL DEFAULT 'LEAD',
            probability         FLOAT           DEFAULT 25,
            expected_close_date DATE,
            amount              NUMERIC,
            stage_history       JSONB           NOT NULL DEFAULT '[]'::jsonb,
            customer_id         VARCHAR(64),
            customer_name       VARCHAR(255),
            assigned_to         VARCHAR(120),
            notes               TEXT,
            created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
        )
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_opportunities_tenant_stage
            ON opportunities (tenant_id, stage)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_opportunities_customer
            ON opportunities (customer_id)
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_opportunities_assigned
            ON opportunities (assigned_to)
    """))


def downgrade() -> None:
    # Repair-Migrations werden nicht rueckgaengig gemacht (IF NOT EXISTS Pattern)
    pass
