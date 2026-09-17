"""Kreditlimite und Freigaben je Kunde.

Die Kreditpruefung liest ``domain_crm.credit_limits`` und schreibt
``credit_overrides`` — **beide Tabellen gab es nicht**. Der Endpunkt fing den
Datenbankfehler ab und antwortete mit 503 „Datenbankfehler"; die Pruefung war
damit nie durchfuehrbar, obwohl sie an der Auftragsanlage haengt.

Ohne Eintrag greift weiterhin das Kreditlimit am Kundensatz — die Tabelle ist
die **Ausnahme vom Stammsatz**, nicht sein Ersatz. Darum keine Pflichtzeile je
Kunde und kein Vorbelegen: Eine leere Tabelle heisst „es gilt der Stamm".

Revision ID: crm_kreditlimite_20260917
Revises: mask_frontend_bridges_20260917
"""

from __future__ import annotations

from alembic import op

revision = "crm_kreditlimite_20260917"
down_revision = "mask_frontend_bridges_20260917"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_crm")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_crm.credit_limits (
          id VARCHAR PRIMARY KEY,
          tenant_id VARCHAR(120) NOT NULL,
          customer_id VARCHAR(120) NOT NULL,
          credit_limit_eur NUMERIC(18, 2) NOT NULL DEFAULT 0,
          -- Schwellen in Prozent des Limits: ab `warning` wird gewarnt, ab
          -- `block` gesperrt. Beide gehoeren zum Limit und nicht in den Code,
          -- weil sie je Haus und Kunde anders sind.
          warning_threshold_percent NUMERIC(5, 2) NOT NULL DEFAULT 80,
          block_threshold_percent NUMERIC(5, 2) NOT NULL DEFAULT 100,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_credit_limits_tenant_customer "
        "ON domain_crm.credit_limits (tenant_id, customer_id)"
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_crm.credit_overrides (
          id VARCHAR PRIMARY KEY,
          tenant_id VARCHAR(120) NOT NULL,
          customer_id VARCHAR(120) NOT NULL,
          -- Wer die Sperre aufhebt, steht im Beleg: Eine Freigabe ohne Namen
          -- und Grund ist keine.
          approved_by VARCHAR(255) NOT NULL,
          reason TEXT NOT NULL,
          valid_until DATE,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_credit_overrides_tenant_customer "
        "ON domain_crm.credit_overrides (tenant_id, customer_id)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_crm.credit_overrides")
    op.execute("DROP TABLE IF EXISTS domain_crm.credit_limits")
