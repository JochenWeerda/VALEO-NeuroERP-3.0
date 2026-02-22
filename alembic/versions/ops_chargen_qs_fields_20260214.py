"""add qs fields to ops_chargen

Revision ID: ops_chargen_qs_fields_20260214
Revises: agrar_settlements_initial_20260213
Create Date: 2026-02-14 11:45:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "ops_chargen_qs_fields_20260214"
down_revision = "agrar_settlements_initial_20260213"
branch_labels = None
depends_on = None


def _existing_columns() -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = inspector.get_columns("ops_chargen", schema="domain_ops")
    return {c["name"] for c in cols}


def upgrade() -> None:
    existing = _existing_columns()

    if "losnummer" not in existing:
        op.add_column("ops_chargen", sa.Column("losnummer", sa.String(length=50), nullable=True), schema="domain_ops")
    if "produktbezeichnung" not in existing:
        op.add_column("ops_chargen", sa.Column("produktbezeichnung", sa.String(length=255), nullable=True), schema="domain_ops")
    if "herstellungsdatum" not in existing:
        op.add_column("ops_chargen", sa.Column("herstellungsdatum", sa.DateTime(timezone=True), nullable=True), schema="domain_ops")
    if "rueckverfolgbar_bis_stunden" not in existing:
        op.add_column(
            "ops_chargen",
            sa.Column("rueckverfolgbar_bis_stunden", sa.Integer(), nullable=True, server_default="4"),
            schema="domain_ops",
        )
    if "rohstoffe" not in existing:
        op.add_column("ops_chargen", sa.Column("rohstoffe", postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema="domain_ops")
    if "lieferant_info" not in existing:
        op.add_column("ops_chargen", sa.Column("lieferant_info", postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema="domain_ops")
    if "kunden_info" not in existing:
        op.add_column("ops_chargen", sa.Column("kunden_info", postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema="domain_ops")
    if "produktionsprozess" not in existing:
        op.add_column(
            "ops_chargen",
            sa.Column("produktionsprozess", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            schema="domain_ops",
        )
    if "digitales_mischbuch" not in existing:
        op.add_column(
            "ops_chargen",
            sa.Column("digitales_mischbuch", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            schema="domain_ops",
        )
    if "haccp_system" not in existing:
        op.add_column("ops_chargen", sa.Column("haccp_system", postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema="domain_ops")
    if "eigenkontrollen" not in existing:
        op.add_column("ops_chargen", sa.Column("eigenkontrollen", postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema="domain_ops")
    if "warentrennung_qs_nicht_qs" not in existing:
        op.add_column(
            "ops_chargen",
            sa.Column("warentrennung_qs_nicht_qs", sa.Boolean(), nullable=True, server_default=sa.text("false")),
            schema="domain_ops",
        )
    if "krisenmanagement" not in existing:
        op.add_column("ops_chargen", sa.Column("krisenmanagement", postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema="domain_ops")
    if "futtermittelmonitoring" not in existing:
        op.add_column(
            "ops_chargen",
            sa.Column("futtermittelmonitoring", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            schema="domain_ops",
        )
    if "qualitaetspersonal" not in existing:
        op.add_column(
            "ops_chargen",
            sa.Column("qualitaetspersonal", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            schema="domain_ops",
        )
    if "qs_datenbank" not in existing:
        op.add_column("ops_chargen", sa.Column("qs_datenbank", postgresql.JSONB(astext_type=sa.Text()), nullable=True), schema="domain_ops")


def downgrade() -> None:
    existing = _existing_columns()

    for name in [
        "qs_datenbank",
        "qualitaetspersonal",
        "futtermittelmonitoring",
        "krisenmanagement",
        "warentrennung_qs_nicht_qs",
        "eigenkontrollen",
        "haccp_system",
        "digitales_mischbuch",
        "produktionsprozess",
        "kunden_info",
        "lieferant_info",
        "rohstoffe",
        "rueckverfolgbar_bis_stunden",
        "herstellungsdatum",
        "produktbezeichnung",
        "losnummer",
    ]:
        if name in existing:
            op.drop_column("ops_chargen", name, schema="domain_ops")
