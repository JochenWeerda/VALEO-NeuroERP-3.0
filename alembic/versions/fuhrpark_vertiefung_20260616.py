"""Fuhrpark Vertiefung: Statushistorie, Schaeden, Bussgeld

Revision ID: fuhrpark_vertiefung_20260616
Revises: einkauf_3wm_invoice_verification_20260613
Create Date: 2026-06-16

Tables added:
  domain_ops.ops_fahrzeug_status_historie
  domain_ops.ops_fahrzeug_schaeden
  domain_ops.ops_fahrzeug_bussgeld
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "fuhrpark_vertiefung_20260616"
down_revision = "einkauf_3wm_invoice_verification_20260613"
branch_labels = None
depends_on = None


def _table_exists(inspector, tablename: str, schema: str = "domain_ops") -> bool:
    return tablename in inspector.get_table_names(schema=schema)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    op.execute("CREATE SCHEMA IF NOT EXISTS domain_ops")

    # ── ops_fahrzeug_status_historie ─────────────────────────────────────────
    if not _table_exists(inspector, "ops_fahrzeug_status_historie"):
        op.create_table(
            "ops_fahrzeug_status_historie",
            sa.Column("id", sa.String, primary_key=True),
            sa.Column(
                "fahrzeug_id",
                sa.String,
                sa.ForeignKey("domain_ops.ops_fahrzeuge.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("von_status", sa.String(30), nullable=True),
            sa.Column("zu_status", sa.String(30), nullable=False),
            sa.Column("grund", sa.Text, nullable=True),
            sa.Column("benutzer", sa.String(120), nullable=True),
            sa.Column("km_stand", sa.Numeric(12, 1), nullable=True),
            sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            schema="domain_ops",
        )
        op.create_index(
            "ix_fahrzeug_status_historie_fahrzeug_id",
            "ops_fahrzeug_status_historie",
            ["fahrzeug_id"],
            schema="domain_ops",
        )
        op.create_index(
            "ix_fahrzeug_status_historie_timestamp",
            "ops_fahrzeug_status_historie",
            ["timestamp"],
            schema="domain_ops",
        )

    # ── ops_fahrzeug_schaeden ────────────────────────────────────────────────
    if not _table_exists(inspector, "ops_fahrzeug_schaeden"):
        op.create_table(
            "ops_fahrzeug_schaeden",
            sa.Column("id", sa.String, primary_key=True),
            sa.Column(
                "fahrzeug_id",
                sa.String,
                sa.ForeignKey("domain_ops.ops_fahrzeuge.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("datum", sa.DateTime(timezone=True), nullable=False),
            sa.Column("ort", sa.String(255), nullable=False),
            sa.Column("beschreibung", sa.Text, nullable=False),
            sa.Column("schadenhoehe_eur", sa.Numeric(14, 2), nullable=True),
            sa.Column("versicherung_gemeldet", sa.Boolean, nullable=False, server_default=sa.text("false")),
            sa.Column("versicherungs_nr", sa.String(120), nullable=True),
            sa.Column("gegner_kennzeichen", sa.String(30), nullable=True),
            sa.Column("polizei_aktenzeichen", sa.String(120), nullable=True),
            sa.Column(
                "status",
                sa.String(30),
                nullable=False,
                server_default="'offen'",
            ),  # offen | bearbeitung | abgeschlossen
            sa.Column("abgeschlossen_am", sa.DateTime(timezone=True), nullable=True),
            sa.Column("erstellt_von", sa.String(120), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            schema="domain_ops",
        )
        op.create_index(
            "ix_fahrzeug_schaeden_fahrzeug_id",
            "ops_fahrzeug_schaeden",
            ["fahrzeug_id"],
            schema="domain_ops",
        )
        op.create_index(
            "ix_fahrzeug_schaeden_datum",
            "ops_fahrzeug_schaeden",
            ["datum"],
            schema="domain_ops",
        )

    # ── ops_fahrzeug_bussgeld ────────────────────────────────────────────────
    if not _table_exists(inspector, "ops_fahrzeug_bussgeld"):
        op.create_table(
            "ops_fahrzeug_bussgeld",
            sa.Column("id", sa.String, primary_key=True),
            sa.Column(
                "fahrzeug_id",
                sa.String,
                sa.ForeignKey("domain_ops.ops_fahrzeuge.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("fahrer_id", sa.String, nullable=True),
            sa.Column("datum", sa.DateTime(timezone=True), nullable=False),
            sa.Column("ort", sa.String(255), nullable=True),
            sa.Column("tatbestand", sa.String(255), nullable=False),
            sa.Column("betrag_eur", sa.Numeric(10, 2), nullable=False, server_default="0"),
            sa.Column("faellig_am", sa.DateTime(timezone=True), nullable=True),
            sa.Column("bezahlt_am", sa.DateTime(timezone=True), nullable=True),
            sa.Column("aktenzeichen", sa.String(120), nullable=True),
            sa.Column(
                "status",
                sa.String(20),
                nullable=False,
                server_default="'offen'",
            ),  # offen | bezahlt | einspruch | verjährt
            sa.Column("notiz", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            schema="domain_ops",
        )
        op.create_index(
            "ix_fahrzeug_bussgeld_fahrzeug_id",
            "ops_fahrzeug_bussgeld",
            ["fahrzeug_id"],
            schema="domain_ops",
        )
        op.create_index(
            "ix_fahrzeug_bussgeld_status",
            "ops_fahrzeug_bussgeld",
            ["status"],
            schema="domain_ops",
        )


def downgrade() -> None:
    op.drop_table("ops_fahrzeug_bussgeld", schema="domain_ops")
    op.drop_table("ops_fahrzeug_schaeden", schema="domain_ops")
    op.drop_table("ops_fahrzeug_status_historie", schema="domain_ops")
