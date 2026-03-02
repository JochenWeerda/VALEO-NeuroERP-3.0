"""GoBD: domain_finance.aufbewahrungsfristen (operative Fristentabelle)

Revision ID: gobd_aufbewahrungsfristen_20260301
Revises: gobd_archiv_erechnung_20260301
Create Date: 2026-03-01

- Erstellt Schema domain_finance (IF NOT EXISTS)
- Erstellt Tabelle aufbewahrungsfristen mit operativen Spalten
- Seed: 5 gesetzliche Standard-Dokumenttypen
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from datetime import date, datetime
import uuid


revision = "gobd_aufbewahrungsfristen_20260301"
down_revision = "gobd_archiv_erechnung_20260301"
branch_labels = None
depends_on = None

_SEED_ROWS = [
    {
        "dokument_typ": "Buchungsbelege",
        "gesetzliche_grundlage": "§147 AO",
        "aufbewahrungs_jahre": 10,
    },
    {
        "dokument_typ": "Jahresabschlüsse",
        "gesetzliche_grundlage": "§147 AO",
        "aufbewahrungs_jahre": 10,
    },
    {
        "dokument_typ": "Geschäftsbriefe",
        "gesetzliche_grundlage": "§257 HGB",
        "aufbewahrungs_jahre": 6,
    },
    {
        "dokument_typ": "Rechnungen",
        "gesetzliche_grundlage": "§147 AO",
        "aufbewahrungs_jahre": 10,
    },
    {
        "dokument_typ": "Lohnunterlagen",
        "gesetzliche_grundlage": "§147 AO",
        "aufbewahrungs_jahre": 10,
    },
]


def upgrade() -> None:
    # Schema anlegen falls noch nicht vorhanden
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_finance")

    op.create_table(
        "aufbewahrungsfristen",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("dokument_typ", sa.String(length=100), nullable=False),
        sa.Column("gesetzliche_grundlage", sa.String(length=100), nullable=True),
        sa.Column("aufbewahrungs_jahre", sa.Integer(), nullable=False),
        sa.Column("aeltestes_dokument_datum", sa.Date(), nullable=True),
        sa.Column("anzahl_dokumente", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("ablauf_datum", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True, server_default="AKTIV"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_finance",
    )

    op.create_index(
        "ix_aufbewahrungs_tenant",
        "aufbewahrungsfristen",
        ["tenant_id"],
        unique=False,
        schema="domain_finance",
    )

    # Seed: Standardtypen mit Platzhalter-Tenant "SYSTEM"
    now = datetime.utcnow()
    conn = op.get_bind()
    for row in _SEED_ROWS:
        conn.execute(
            sa.text(
                """
                INSERT INTO domain_finance.aufbewahrungsfristen
                    (id, tenant_id, dokument_typ, gesetzliche_grundlage,
                     aufbewahrungs_jahre, status, created_at, updated_at)
                VALUES
                    (:id, :tenant_id, :dokument_typ, :gesetzliche_grundlage,
                     :aufbewahrungs_jahre, 'AKTIV', :created_at, :updated_at)
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "id": str(uuid.uuid4()),
                "tenant_id": "SYSTEM",
                "dokument_typ": row["dokument_typ"],
                "gesetzliche_grundlage": row["gesetzliche_grundlage"],
                "aufbewahrungs_jahre": row["aufbewahrungs_jahre"],
                "created_at": now,
                "updated_at": now,
            },
        )


def downgrade() -> None:
    op.drop_index("ix_aufbewahrungs_tenant", table_name="aufbewahrungsfristen", schema="domain_finance")
    op.drop_table("aufbewahrungsfristen", schema="domain_finance")
