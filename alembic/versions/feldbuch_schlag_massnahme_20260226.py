"""Add feldbuch_schlaege and feldbuch_massnahmen to domain_agrar

Revision ID: feldbuch_schlag_massnahme_20260226
Revises: sales_angebot_auftrag_tables_20260225
Create Date: 2026-02-26
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB


revision = "feldbuch_schlag_massnahme_20260226"
down_revision = "sales_angebot_auftrag_tables_20260225"
branch_labels = None
depends_on = None


def _table_exists(inspector, tablename: str, schema: str = "domain_agrar") -> bool:
    return tablename in inspector.get_table_names(schema=schema)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Sicherstellen dass domain_agrar schema existiert (idempotent)
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")

    # ── domain_agrar.feldbuch_schlaege ────────────────────────────────────
    if not _table_exists(inspector, "feldbuch_schlaege"):
        op.create_table(
            "feldbuch_schlaege",
            sa.Column("id", sa.String, primary_key=True),
            sa.Column("tenant_id", sa.String, nullable=False),
            sa.Column("customer_id", sa.String, nullable=False),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("flik", sa.String(20), nullable=True),
            sa.Column("flaeche", sa.Float, nullable=False),
            sa.Column("kultur", sa.String(100), nullable=True),
            sa.Column("vorkultur", sa.String(100), nullable=True),
            sa.Column("gemeinde", sa.String(100), nullable=True),
            sa.Column("gemarkung", sa.String(100), nullable=True),
            sa.Column("bodenart", sa.String(50), nullable=True),
            sa.Column("ackerzahl", sa.Float, nullable=True),
            sa.Column("status", sa.String(20), server_default="aktiv"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_by", sa.String(200), nullable=True),
            schema="domain_agrar",
        )
        op.create_index(
            "ix_feldbuch_schlaege_tenant_customer",
            "feldbuch_schlaege",
            ["tenant_id", "customer_id"],
            schema="domain_agrar",
        )
        op.create_index(
            "ix_feldbuch_schlaege_tenant",
            "feldbuch_schlaege",
            ["tenant_id"],
            schema="domain_agrar",
        )
        op.create_index(
            "ix_feldbuch_schlaege_customer",
            "feldbuch_schlaege",
            ["customer_id"],
            schema="domain_agrar",
        )

    # ── domain_agrar.feldbuch_massnahmen ──────────────────────────────────
    if not _table_exists(inspector, "feldbuch_massnahmen"):
        op.create_table(
            "feldbuch_massnahmen",
            sa.Column("id", sa.String, primary_key=True),
            sa.Column("tenant_id", sa.String, nullable=False),
            sa.Column("schlag_id", sa.String, nullable=True),
            sa.Column("customer_id", sa.String, nullable=False),
            sa.Column("datum", sa.DateTime(timezone=True), nullable=False),
            sa.Column("uhrzeit", sa.String(10), nullable=True),
            sa.Column("typ", sa.String(30), nullable=False),
            sa.Column("bezeichnung", sa.String(300), nullable=True),
            sa.Column("mittel", sa.String(200), nullable=True),
            sa.Column("mittel_id", sa.String, nullable=True),
            sa.Column("mittel_typ", sa.String(30), nullable=True),
            sa.Column("menge", sa.Float, nullable=True),
            sa.Column("einheit", sa.String(20), nullable=True),
            sa.Column("flaeche", sa.Float, nullable=True),
            sa.Column("anwender", sa.String(200), nullable=True),
            sa.Column("quelle", sa.String(20), nullable=False, server_default="portal"),
            sa.Column("lieferschein_id", sa.String, nullable=True),
            sa.Column("auflagen", JSONB, nullable=True),
            sa.Column("wartezeit_tage", sa.Integer, nullable=True),
            sa.Column("windgeschwindigkeit", sa.Float, nullable=True),
            sa.Column("temperatur", sa.Float, nullable=True),
            sa.Column("compliant", sa.Boolean, server_default=sa.text("true")),
            sa.Column("exportiert", sa.Boolean, server_default=sa.text("false")),
            sa.Column("exportiert_am", sa.DateTime(timezone=True), nullable=True),
            sa.Column("bemerkung", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(
                ["schlag_id"],
                ["domain_agrar.feldbuch_schlaege.id"],
                name="fk_feldbuch_massnahmen_schlag",
            ),
            schema="domain_agrar",
        )
        op.create_index(
            "ix_feldbuch_massnahmen_tenant_customer",
            "feldbuch_massnahmen",
            ["tenant_id", "customer_id"],
            schema="domain_agrar",
        )
        op.create_index(
            "ix_feldbuch_massnahmen_schlag_datum",
            "feldbuch_massnahmen",
            ["schlag_id", "datum"],
            schema="domain_agrar",
        )
        op.create_index(
            "ix_feldbuch_massnahmen_lieferschein",
            "feldbuch_massnahmen",
            ["lieferschein_id"],
            schema="domain_agrar",
        )
        op.create_index(
            "ix_feldbuch_massnahmen_tenant",
            "feldbuch_massnahmen",
            ["tenant_id"],
            schema="domain_agrar",
        )
        op.create_index(
            "ix_feldbuch_massnahmen_customer",
            "feldbuch_massnahmen",
            ["customer_id"],
            schema="domain_agrar",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if _table_exists(inspector, "feldbuch_massnahmen"):
        op.drop_table("feldbuch_massnahmen", schema="domain_agrar")

    if _table_exists(inspector, "feldbuch_schlaege"):
        op.drop_table("feldbuch_schlaege", schema="domain_agrar")
