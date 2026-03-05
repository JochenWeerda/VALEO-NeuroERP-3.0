"""Agrar Maschinenpark — Tabelle agrar_maschinen in domain_agrar

Revision ID: agrar_maschinen_wetter_20260301
Revises: feldbuch_schlag_massnahme_20260226
Create Date: 2026-03-01
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "agrar_maschinen_wetter_20260301"
down_revision = "feldbuch_schlag_massnahme_20260226"
branch_labels = None
depends_on = None


def _table_exists(inspector, tablename: str, schema: str = "domain_agrar") -> bool:
    return tablename in inspector.get_table_names(schema=schema)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Schema sicherstellen (idempotent)
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")

    if not _table_exists(inspector, "agrar_maschinen"):
        op.create_table(
            "agrar_maschinen",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("tenant_id", sa.String(), nullable=False),
            sa.Column("customer_id", sa.String(), nullable=True),

            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("typ", sa.String(50), nullable=False),

            sa.Column("hersteller", sa.String(100), nullable=True),
            sa.Column("modell", sa.String(100), nullable=True),
            sa.Column("baujahr", sa.Integer(), nullable=True),
            sa.Column("kennzeichen", sa.String(20), nullable=True),
            sa.Column("fahrgestellnummer", sa.String(50), nullable=True),
            sa.Column("leistung_kw", sa.Float(), nullable=True),

            sa.Column("betriebsstunden", sa.Float(), nullable=False, server_default="0"),
            sa.Column("naechste_wartung_stunden", sa.Float(), nullable=True),
            sa.Column("naechste_wartung_datum", sa.DateTime(timezone=True), nullable=True),

            sa.Column("status", sa.String(20), nullable=False, server_default="verfuegbar"),
            sa.Column("standort", sa.String(100), nullable=True),
            sa.Column("notiz", sa.Text(), nullable=True),

            sa.Column("ist_aktiv", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),

            schema="domain_agrar",
        )
        op.create_index(
            "ix_agrar_maschinen_tenant_id",
            "agrar_maschinen",
            ["tenant_id"],
            schema="domain_agrar",
        )
        op.create_index(
            "ix_agrar_maschinen_customer_id",
            "agrar_maschinen",
            ["customer_id"],
            schema="domain_agrar",
        )
        op.create_index(
            "ix_agrar_maschinen_status",
            "agrar_maschinen",
            ["status"],
            schema="domain_agrar",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if _table_exists(inspector, "agrar_maschinen"):
        op.drop_index("ix_agrar_maschinen_status", table_name="agrar_maschinen", schema="domain_agrar")
        op.drop_index("ix_agrar_maschinen_customer_id", table_name="agrar_maschinen", schema="domain_agrar")
        op.drop_index("ix_agrar_maschinen_tenant_id", table_name="agrar_maschinen", schema="domain_agrar")
        op.drop_table("agrar_maschinen", schema="domain_agrar")
