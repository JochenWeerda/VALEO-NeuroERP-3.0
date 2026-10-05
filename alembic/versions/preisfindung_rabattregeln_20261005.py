"""Rollenrabatte als Tabelle — und ein Rabatt bleibt unter hundert Prozent.

`domain_pricing.discount_rules` existierte in keiner Datenbank. Die vierte Stufe
der Preiskaskade las sie, der Lesefehler lief in `except: db.rollback()`, und
heraus kam der volle Listenpreis mit `source: "base"` — ein plausibler, falscher
Preis. Ein Preis ist die Grundlage der Rechnung; ein verschluckter Rabatt ist ein
Abrechnungsfehler, der wie ein richtiger Preis aussieht.

Die Pruefbedingungen sind nicht Formsache: Ein Rabatt ueber hundert Prozent waere
ein negativer Preis, und ein Gueltigkeitsende vor dem Beginn eine Regel, die
nie gilt und trotzdem gepflegt aussieht.

Revision ID: preisfindung_rabattregeln_20261005
Revises: kontrakt_disposition_20261005
Create Date: 2026-10-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "preisfindung_rabattregeln_20261005"
down_revision = "kontrakt_disposition_20261005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_pricing")

    op.create_table(
        "discount_rules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        # Die Rolle, fuer die der Rabatt gilt (z. B. MITARBEITER, AUSSENDIENST).
        sa.Column("role", sa.String(60), nullable=False),
        sa.Column("discount_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("bezeichnung", sa.String(160), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "discount_percent >= 0 AND discount_percent <= 100",
            name="ck_rabattregel_prozent_bereich",
        ),
        sa.CheckConstraint(
            "valid_until IS NULL OR valid_from IS NULL OR valid_until >= valid_from",
            name="ck_rabattregel_zeitraum",
        ),
        schema="domain_pricing",
    )

    # Je Mandant und Rolle gilt eine Regel. Zwei aktive Regeln fuer dieselbe
    # Rolle hiessen, dass der Preis davon abhaengt, welche zuerst gelesen wird —
    # und `LIMIT 1` ohne Sortierung macht daraus eine Zufallsentscheidung.
    op.create_index(
        "ux_rabattregel_rolle",
        "discount_rules",
        ["tenant_id", "role"],
        unique=True,
        postgresql_where=sa.text("is_active"),
        schema="domain_pricing",
    )


def downgrade() -> None:
    verbindung = op.get_bind()
    anzahl = verbindung.execute(
        sa.text("SELECT COUNT(*) FROM domain_pricing.discount_rules")
    ).scalar()
    if anzahl:
        raise RuntimeError(
            f"domain_pricing.discount_rules fuehrt {anzahl} Regeln. Sie bestimmen "
            "Preise und werden nicht per Downgrade geloescht."
        )
    op.drop_index("ux_rabattregel_rolle", table_name="discount_rules", schema="domain_pricing")
    op.drop_table("discount_rules", schema="domain_pricing")
