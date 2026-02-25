"""Add Fuhrpark sub-tables and Speditionen Frachttarife

Revision ID: fuhrpark_tables_speditionen_20260225
Revises: sales_delivery_notes_branches_audit_20260216
Create Date: 2026-02-25

Tables added:
  domain_ops.ops_fuhrpark_terminarten
  domain_ops.ops_fuhrpark_rechnungen
  domain_ops.ops_fuhrpark_ausgehende_dokumente
  domain_ops.strecke_speditionen_frachttarife
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "fuhrpark_tables_speditionen_20260225"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def _table_exists(inspector, tablename: str, schema: str = "domain_ops") -> bool:
    return tablename in inspector.get_table_names(schema=schema)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Ensure schema exists (idempotent)
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_ops")

    # ── ops_fuhrpark_terminarten ──────────────────────────────────────────
    if not _table_exists(inspector, "ops_fuhrpark_terminarten"):
        op.create_table(
            "ops_fuhrpark_terminarten",
            sa.Column("id", sa.String, primary_key=True),
            sa.Column("terminart", sa.String(120), nullable=False, unique=True),
            sa.Column("intervall_monate", sa.Integer, nullable=False, server_default="0"),
            sa.Column("intervall_km", sa.Integer, nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            schema="domain_ops",
        )
        op.create_index(
            "ix_ops_fuhrpark_terminarten_terminart",
            "ops_fuhrpark_terminarten",
            ["terminart"],
            schema="domain_ops",
        )

    # ── ops_fuhrpark_rechnungen ───────────────────────────────────────────
    if not _table_exists(inspector, "ops_fuhrpark_rechnungen"):
        op.create_table(
            "ops_fuhrpark_rechnungen",
            sa.Column("id", sa.String, primary_key=True),
            sa.Column("rechnungs_nr", sa.String(80), nullable=False, unique=True),
            sa.Column("datum", sa.DateTime(timezone=True), nullable=False),
            sa.Column(
                "fahrzeug_id",
                sa.String,
                sa.ForeignKey("domain_ops.ops_fahrzeuge.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("fahrzeug_kennzeichen", sa.String(30), nullable=True),
            sa.Column("sachkonto", sa.String(40), nullable=True),
            sa.Column("kostenart", sa.String(120), nullable=True),
            sa.Column("betrag_eur", sa.Numeric(14, 2), nullable=False, server_default="0"),
            sa.Column("notiz", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            schema="domain_ops",
        )
        op.create_index(
            "ix_ops_fuhrpark_rechnungen_datum",
            "ops_fuhrpark_rechnungen",
            ["datum"],
            schema="domain_ops",
        )
        op.create_index(
            "ix_ops_fuhrpark_rechnungen_fahrzeug_id",
            "ops_fuhrpark_rechnungen",
            ["fahrzeug_id"],
            schema="domain_ops",
        )

    # ── ops_fuhrpark_ausgehende_dokumente ─────────────────────────────────
    if not _table_exists(inspector, "ops_fuhrpark_ausgehende_dokumente"):
        op.create_table(
            "ops_fuhrpark_ausgehende_dokumente",
            sa.Column("id", sa.String, primary_key=True),
            sa.Column("beleg_typ", sa.String(120), nullable=False),
            sa.Column("formular", sa.String(80), nullable=True),
            sa.Column("ziel_modul", sa.String(255), nullable=True),
            sa.Column("beschreibung", sa.Text, nullable=True),
            sa.Column("aktiv", sa.Boolean, nullable=False, server_default=sa.text("true")),
            sa.Column("letzter_druck", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            schema="domain_ops",
        )
        op.create_index(
            "ix_ops_fuhrpark_ausgehende_dokumente_beleg_typ",
            "ops_fuhrpark_ausgehende_dokumente",
            ["beleg_typ"],
            schema="domain_ops",
        )
        op.create_index(
            "ix_ops_fuhrpark_ausgehende_dokumente_aktiv",
            "ops_fuhrpark_ausgehende_dokumente",
            ["aktiv"],
            schema="domain_ops",
        )

    # ── strecke_speditionen_frachttarife ──────────────────────────────────
    if not _table_exists(inspector, "strecke_speditionen_frachttarife"):
        op.create_table(
            "strecke_speditionen_frachttarife",
            sa.Column("id", sa.String, primary_key=True),
            sa.Column("plz_von", sa.String(10), nullable=False),
            sa.Column("plz_bis", sa.String(10), nullable=False),
            sa.Column("spediteur", sa.String(255), nullable=False),
            sa.Column("preis_eur_t", sa.Numeric(10, 4), nullable=False, server_default="0"),
            sa.Column("aktiv", sa.Boolean, nullable=False, server_default=sa.text("true")),
            sa.Column("notiz", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("created_by", sa.String(100), nullable=True),
            sa.Column("updated_by", sa.String(100), nullable=True),
            schema="domain_ops",
        )
        op.create_index(
            "ix_strecke_frachttarife_plz",
            "strecke_speditionen_frachttarife",
            ["plz_von", "plz_bis"],
            schema="domain_ops",
        )
        op.create_index(
            "ix_strecke_frachttarife_spediteur",
            "strecke_speditionen_frachttarife",
            ["spediteur"],
            schema="domain_ops",
        )
        op.create_index(
            "ix_strecke_frachttarife_aktiv",
            "strecke_speditionen_frachttarife",
            ["aktiv"],
            schema="domain_ops",
        )


def downgrade() -> None:
    op.drop_table("strecke_speditionen_frachttarife", schema="domain_ops")
    op.drop_table("ops_fuhrpark_ausgehende_dokumente", schema="domain_ops")
    op.drop_table("ops_fuhrpark_rechnungen", schema="domain_ops")
    op.drop_table("ops_fuhrpark_terminarten", schema="domain_ops")
