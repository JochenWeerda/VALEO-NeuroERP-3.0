"""Zahlarten und Kassenaktionen bekommen eine Migration.

``domain_pos.payment_methods`` und ``domain_pos.promotions`` wurden von keiner
Migration angelegt, sondern zur Laufzeit vom Endpunkt selbst
(``pos_payments.py``, ``_ensure_tables``). Auf einer frischen Installation gab
es sie erst, nachdem jemand die Kasse geoeffnet hatte.

Die Form stammt woertlich aus dieser Laufzeit-DDL — sie ist nicht erfunden,
sondern uebernommen. Ergaenzt sind nur die beiden Dinge, die eine Tabelle
braucht, um benutzbar zu sein: Zeitstempel und ein Index auf die Frage, die
der Kasse gestellt wird ("welche Zahlarten hat *mein* Haus, die aktiv sind?").

Beide Tabellen tragen bereits ``tenant_id``, und der Endpunkt filtert in jeder
Abfrage danach — anders als bei den Hinweisgebermeldungen gab es hier kein
Mandantenproblem.

Revision ID: pos_zahlarten_aktionen_20260930
Revises: whistleblower_eine_tabelle_20260930
"""

from __future__ import annotations

from alembic import op

revision = "pos_zahlarten_aktionen_20260930"
down_revision = "whistleblower_eine_tabelle_20260930"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_pos")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_pos.payment_methods (
            id          VARCHAR(64)  PRIMARY KEY,
            tenant_id   VARCHAR(64)  NOT NULL,
            method_code VARCHAR(32)  NOT NULL,
            name        VARCHAR(128) NOT NULL,
            is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
            created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_pos.promotions (
            id             VARCHAR(64)  PRIMARY KEY,
            tenant_id      VARCHAR(64)  NOT NULL,
            name           VARCHAR(128) NOT NULL,
            promo_type     VARCHAR(32)  NOT NULL,
            article_id     VARCHAR(64),
            article_group  VARCHAR(64),
            discount_value NUMERIC(12, 4),
            min_quantity   NUMERIC(12, 3) NOT NULL DEFAULT 1,
            valid_from     DATE,
            valid_to       DATE,
            is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
            created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )
        """
    )

    # Fuer eine Installation, auf der die Laufzeitfassung schon steht.
    op.execute(
        """
        ALTER TABLE domain_pos.payment_methods
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        """
    )
    op.execute(
        """
        ALTER TABLE domain_pos.promotions
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        """
    )

    # Eine Zahlart je Haus und Kuerzel — zweimal 'BAR' im selben Haus waere
    # eine Fehlbedienung, keine Konfiguration.
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_pos_payment_methods_tenant_code "
        "ON domain_pos.payment_methods (tenant_id, method_code)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_pos_promotions_tenant_aktiv "
        "ON domain_pos.promotions (tenant_id, is_active, valid_to)"
    )


def downgrade() -> None:
    # Kein DROP TABLE: Die Tabellen tragen die Kassenkonfiguration eines
    # Hauses. Zurueckgenommen wird nur, was diese Migration hinzugefuegt hat.
    op.execute("DROP INDEX IF EXISTS domain_pos.ux_pos_payment_methods_tenant_code")
    op.execute("DROP INDEX IF EXISTS domain_pos.ix_pos_promotions_tenant_aktiv")
