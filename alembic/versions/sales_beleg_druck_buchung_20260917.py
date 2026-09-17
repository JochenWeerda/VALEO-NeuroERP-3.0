"""Druck- und Buchungsstand an Auftrag und Angebot.

Die Masken „Auftrag drucken und buchen" und „Angebot drucken und buchen" riefen
Endpunkte auf, die es nicht gab — und die Belege hatten auch nichts, worin sie
den Vorgang haetten festhalten koennen. Ein gedruckter Beleg, der nicht weiss,
dass er gedruckt wurde, laesst sich weder nachweisen noch gegen versehentlichen
Zweitdruck schuetzen.

``print_count`` statt eines Wahrheitswerts: Der zweite Druck ist im Landhandel
ein eigener Vorgang (Kunde hat den ersten nicht erhalten) und gehoert gezaehlt,
nicht ueberschrieben.

Revision ID: sales_beleg_druck_buchung_20260917
Revises: crm_consents_20260917
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "sales_beleg_druck_buchung_20260917"
down_revision = "crm_consents_20260917"
branch_labels = None
depends_on = None

_TABELLEN = (
    ("domain_crm", "sales_orders"),
    ("domain_crm", "sales_offers"),
)


def upgrade() -> None:
    for schema, tabelle in _TABELLEN:
        op.add_column(
            tabelle,
            sa.Column("printed_at", sa.DateTime(timezone=True), nullable=True),
            schema=schema,
        )
        op.add_column(
            tabelle,
            sa.Column(
                "print_count",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
            schema=schema,
        )
        op.add_column(
            tabelle,
            sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
            schema=schema,
        )


def downgrade() -> None:
    for schema, tabelle in _TABELLEN:
        op.drop_column(tabelle, "posted_at", schema=schema)
        op.drop_column(tabelle, "print_count", schema=schema)
        op.drop_column(tabelle, "printed_at", schema=schema)
