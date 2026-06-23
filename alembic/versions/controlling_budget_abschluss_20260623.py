"""DOM-CONTROLLING-004 — controlling_budgets, ist_werte, kst_abschluss.

Revision ID: controlling_budget_abschluss_20260623
Revises: proc_bestellung_wareneingang_20260623
Create Date: 2026-06-23
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "controlling_budget_abschluss_20260623"
down_revision = "proc_bestellung_wareneingang_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_controlling")

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_controlling.controlling_budgets (
            id                VARCHAR(36)    PRIMARY KEY,
            tenant_id         VARCHAR(100)   NOT NULL,
            kostenstelle_id   VARCHAR(100)   NOT NULL,
            periode           VARCHAR(20)    NOT NULL,
            plan_eur          NUMERIC(14,2)  NOT NULL,
            bezeichnung       TEXT,
            status            VARCHAR(30)    NOT NULL DEFAULT 'ENTWURF',
            freigabe_operator VARCHAR(100),
            created_at        TIMESTAMPTZ    NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_controlling.controlling_budget_status_log (
            id          VARCHAR(36)   PRIMARY KEY,
            budget_id   VARCHAR(36)   NOT NULL,
            tenant_id   VARCHAR(100)  NOT NULL,
            old_status  VARCHAR(30),
            new_status  VARCHAR(30)   NOT NULL,
            operator    VARCHAR(100),
            created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_controlling.controlling_ist_werte (
            id                VARCHAR(36)    PRIMARY KEY,
            tenant_id         VARCHAR(100)   NOT NULL,
            kostenstelle_id   VARCHAR(100)   NOT NULL,
            periode           VARCHAR(20)    NOT NULL,
            ist_eur           NUMERIC(14,2)  NOT NULL,
            buchungsref       VARCHAR(100),
            created_at        TIMESTAMPTZ    NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_controlling.controlling_kst_abschluss (
            id                VARCHAR(36)   PRIMARY KEY,
            tenant_id         VARCHAR(100)  NOT NULL,
            kostenstelle_id   VARCHAR(100)  NOT NULL,
            periode           VARCHAR(20)   NOT NULL,
            status            VARCHAR(30)   NOT NULL DEFAULT 'OFFEN',
            operator          VARCHAR(100),
            abgeschlossen_am  TIMESTAMPTZ,
            created_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
            UNIQUE (tenant_id, kostenstelle_id, periode)
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_controlling.controlling_kst_abschluss")
    op.execute("DROP TABLE IF EXISTS domain_controlling.controlling_ist_werte")
    op.execute("DROP TABLE IF EXISTS domain_controlling.controlling_budget_status_log")
    op.execute("DROP TABLE IF EXISTS domain_controlling.controlling_budgets")
