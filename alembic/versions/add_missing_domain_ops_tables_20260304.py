"""add missing domain_ops tables (compliance, enni, qs, zulassungen, sachkunde, saatgut, vvvo, disposition, foerderantraege, labor, marketing, zertifikate)

Revision ID: missing_ops_20260304
Revises: pos_commodity_20260304
Create Date: 2026-03-04

Adds all domain_ops tables that have models but were not yet in migrations:
ops_compliance_items, ops_enni_meldungen, ops_qs_checks, ops_zulassungen_register,
ops_sachkunde_register, ops_saatgut_nachbau, ops_vvvo_register, ops_disposition,
ops_foerderantraege, ops_labor_proben, ops_labor_auftraege, ops_marketing_kampagnen, ops_zertifikate.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision: str = "missing_ops_20260304"
down_revision: Union[str, None] = "pos_commodity_20260304"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(conn, schema: str, table: str) -> bool:
    r = conn.execute(
        text(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = :schema AND table_name = :table"
        ),
        {"schema": schema, "table": table},
    )
    return r.scalar() is not None


def upgrade() -> None:
    conn = op.get_bind()
    if _table_exists(conn, "domain_ops", "ops_compliance_items"):
        return

    op.execute("CREATE SCHEMA IF NOT EXISTS domain_ops")

    op.create_table(
        "ops_compliance_items",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("bereich", sa.String(120), nullable=False),
        sa.Column("anforderung", sa.String(255), nullable=False),
        sa.Column("erfuellt", sa.Boolean(), server_default=sa.false()),
        sa.Column("nachweis", sa.String(255), server_default=""),
        sa.Column("frist", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_ops_compliance_items"),
        schema="domain_ops",
    )

    op.create_table(
        "ops_enni_meldungen",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("typ", sa.String(20), nullable=False),
        sa.Column("betrieb", sa.String(255), nullable=False),
        sa.Column("vvvo", sa.String(50), nullable=False),
        sa.Column("datum", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(30), server_default="entwurf"),
        sa.Column("naehrstoff_n", sa.Float(), server_default=sa.text("0")),
        sa.Column("naehrstoff_p", sa.Float(), server_default=sa.text("0")),
        sa.Column("naehrstoff_k", sa.Float(), server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_ops_enni_meldungen"),
        schema="domain_ops",
    )

    op.create_table(
        "ops_qs_checks",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("bereich", sa.String(120), nullable=False),
        sa.Column("pruefpunkt", sa.String(255), nullable=False),
        sa.Column("erfuellt", sa.Boolean(), server_default=sa.false()),
        sa.Column("bemerkung", sa.String(500), server_default=""),
        sa.Column("geprueft_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_ops_qs_checks"),
        schema="domain_ops",
    )

    op.create_table(
        "ops_zulassungen_register",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("produkt", sa.String(255), nullable=False),
        sa.Column("typ", sa.String(50), nullable=False),
        sa.Column("nummer", sa.String(80), nullable=False),
        sa.Column("behoerde", sa.String(120), nullable=False),
        sa.Column("gueltig_bis", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(30), server_default="aktiv"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_ops_zulassungen_register"),
        schema="domain_ops",
    )

    op.create_table(
        "ops_sachkunde_register",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("kunde", sa.String(255), nullable=False),
        sa.Column("kundennr", sa.String(80), nullable=False),
        sa.Column("nachweis_nr", sa.String(120), nullable=False),
        sa.Column("ausstellungsdatum", sa.DateTime(timezone=True), nullable=True),
        sa.Column("gueltig_bis", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ausstellende_stelle", sa.String(255), nullable=True),
        sa.Column("status", sa.String(30), server_default="gueltig"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_ops_sachkunde_register"),
        schema="domain_ops",
    )

    op.create_table(
        "ops_saatgut_nachbau",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("betrieb", sa.String(255), nullable=False),
        sa.Column("sorte", sa.String(120), nullable=False),
        sa.Column("kultur", sa.String(120), nullable=False),
        sa.Column("flaeche", sa.Float(), server_default=sa.text("0")),
        sa.Column("erntejahr", sa.Integer(), nullable=False),
        sa.Column("gebuehr", sa.DECIMAL(14, 2), server_default=sa.text("0")),
        sa.Column("status", sa.String(30), server_default="offen"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_ops_saatgut_nachbau"),
        schema="domain_ops",
    )

    op.create_table(
        "ops_vvvo_register",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("betriebsname", sa.String(255), nullable=False),
        sa.Column("vvvo", sa.String(50), nullable=False),
        sa.Column("bundesland", sa.String(80), nullable=True),
        sa.Column("tierart", sa.String(120), nullable=True),
        sa.Column("status", sa.String(30), server_default="aktiv"),
        sa.Column("letzte_aktualisierung", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_ops_vvvo_register"),
        schema="domain_ops",
    )

    op.create_table(
        "ops_disposition",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artikel", sa.String(255), nullable=False),
        sa.Column("artikel_id", sa.String(100), nullable=False),
        sa.Column("bestand", sa.Float(), server_default=sa.text("0")),
        sa.Column("mindestbestand", sa.Float(), server_default=sa.text("0")),
        sa.Column("bedarf", sa.Float(), server_default=sa.text("0")),
        sa.Column("empfehlung", sa.String(255), server_default=""),
        sa.Column("prioritaet", sa.String(20), server_default="niedrig"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_ops_disposition"),
        schema="domain_ops",
    )

    op.create_table(
        "ops_foerderantraege",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("nummer", sa.String(80), nullable=False),
        sa.Column("programm", sa.String(120), nullable=False),
        sa.Column("antragsdatum", sa.DateTime(timezone=True), nullable=True),
        sa.Column("flaeche", sa.Float(), server_default=sa.text("0")),
        sa.Column("betrag", sa.DECIMAL(14, 2), server_default=sa.text("0")),
        sa.Column("status", sa.String(30), server_default="entwurf"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_ops_foerderantraege"),
        schema="domain_ops",
    )

    op.create_table(
        "ops_labor_proben",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("probennummer", sa.String(80), nullable=False),
        sa.Column("typ", sa.String(80), nullable=False),
        sa.Column("artikel", sa.String(255), nullable=False),
        sa.Column("datum", sa.DateTime(timezone=True), nullable=True),
        sa.Column("labor", sa.String(255), nullable=False),
        sa.Column("status", sa.String(30), server_default="ausstehend"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_ops_labor_proben"),
        schema="domain_ops",
    )

    op.create_table(
        "ops_labor_auftraege",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("chargen_id", sa.String(80), nullable=False),
        sa.Column("labor", sa.String(255), nullable=False),
        sa.Column("analysen", sa.Integer(), server_default=sa.text("0")),
        sa.Column("auftragsdatum", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(30), server_default="offen"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_ops_labor_auftraege"),
        schema="domain_ops",
    )

    op.create_table(
        "ops_marketing_kampagnen",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("typ", sa.String(80), nullable=False),
        sa.Column("zielgruppe", sa.String(120), nullable=True),
        sa.Column("startdatum", sa.DateTime(timezone=True), nullable=True),
        sa.Column("enddatum", sa.DateTime(timezone=True), nullable=True),
        sa.Column("budget", sa.DECIMAL(14, 2), server_default=sa.text("0")),
        sa.Column("status", sa.String(30), server_default="geplant"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_ops_marketing_kampagnen"),
        schema="domain_ops",
    )

    op.create_table(
        "ops_zertifikate",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("art", sa.String(120), nullable=False),
        sa.Column("standard", sa.String(120), nullable=False),
        sa.Column("nummer", sa.String(120), nullable=False),
        sa.Column("gueltig_bis", sa.DateTime(timezone=True), nullable=True),
        sa.Column("audit", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(30), server_default="gueltig"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name="pk_ops_zertifikate"),
        schema="domain_ops",
    )

    for tbl in [
        "ops_compliance_items",
        "ops_enni_meldungen",
        "ops_qs_checks",
        "ops_zulassungen_register",
        "ops_sachkunde_register",
        "ops_saatgut_nachbau",
        "ops_vvvo_register",
        "ops_disposition",
        "ops_foerderantraege",
        "ops_labor_proben",
        "ops_labor_auftraege",
        "ops_marketing_kampagnen",
        "ops_zertifikate",
    ]:
        op.create_index(
            f"ix_{tbl}_created_at",
            tbl,
            ["created_at"],
            unique=False,
            schema="domain_ops",
        )


def downgrade() -> None:
    for tbl in [
        "ops_zertifikate",
        "ops_marketing_kampagnen",
        "ops_labor_auftraege",
        "ops_labor_proben",
        "ops_foerderantraege",
        "ops_disposition",
        "ops_vvvo_register",
        "ops_saatgut_nachbau",
        "ops_sachkunde_register",
        "ops_zulassungen_register",
        "ops_qs_checks",
        "ops_enni_meldungen",
        "ops_compliance_items",
    ]:
        op.drop_table(tbl, schema="domain_ops")
