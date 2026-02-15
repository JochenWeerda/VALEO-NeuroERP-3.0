"""Extend offene_posten with L3 fields for full CRUD.

Revision ID: offene_posten_fields_crud_20260214
Revises: business_partner_tab_23_24_25_20260214
Create Date: 2026-02-14
"""

from alembic import op
import sqlalchemy as sa


revision = "offene_posten_fields_crud_20260214"
down_revision = "business_partner_tab_23_24_25_20260214"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offene_posten", sa.Column("konto_nr", sa.String(length=40), nullable=True))
    op.add_column("offene_posten", sa.Column("konto_name", sa.String(length=255), nullable=True))
    op.add_column("offene_posten", sa.Column("konto_typ", sa.String(length=20), nullable=False, server_default="debitoren"))
    op.add_column("offene_posten", sa.Column("op_status", sa.String(length=20), nullable=False, server_default="offen"))
    op.add_column("offene_posten", sa.Column("rechnungsdatum", sa.Date(), nullable=True))
    op.add_column("offene_posten", sa.Column("valuta", sa.Date(), nullable=True))
    op.add_column("offene_posten", sa.Column("op_betrag", sa.Numeric(14, 2), nullable=True))
    op.add_column("offene_posten", sa.Column("saldo", sa.Numeric(14, 2), nullable=True))
    op.add_column("offene_posten", sa.Column("op_text", sa.String(length=255), nullable=True))
    op.add_column("offene_posten", sa.Column("waehrung", sa.String(length=3), nullable=False, server_default="EUR"))
    op.add_column("offene_posten", sa.Column("letzte_bewegung_am", sa.Date(), nullable=True))
    op.add_column("offene_posten", sa.Column("kredit_limit", sa.Numeric(14, 2), nullable=True))
    op.add_column("offene_posten", sa.Column("kv_limit", sa.Numeric(14, 2), nullable=True))
    op.add_column("offene_posten", sa.Column("sperre_grund", sa.String(length=255), nullable=True))

    op.execute("UPDATE offene_posten SET rechnungsdatum = COALESCE(rechnungsdatum, datum)")
    op.execute("UPDATE offene_posten SET op_betrag = COALESCE(op_betrag, betrag)")
    op.execute("UPDATE offene_posten SET saldo = COALESCE(saldo, 0)")
    op.execute("UPDATE offene_posten SET konto_typ = COALESCE(konto_typ, 'debitoren')")
    op.execute("UPDATE offene_posten SET op_status = COALESCE(op_status, 'offen')")
    op.execute("UPDATE offene_posten SET waehrung = COALESCE(waehrung, 'EUR')")

    op.create_index("ix_offene_posten_konto_nr", "offene_posten", ["konto_nr"], unique=False)
    op.create_index("ix_offene_posten_konto_typ", "offene_posten", ["konto_typ"], unique=False)
    op.create_index("ix_offene_posten_op_status", "offene_posten", ["op_status"], unique=False)
    op.create_index("ix_offene_posten_faelligkeit_status", "offene_posten", ["faelligkeit", "op_status"], unique=False)

    op.create_check_constraint(
        "ck_offene_posten_konto_typ",
        "offene_posten",
        "konto_typ IN ('debitoren','kreditoren')",
    )
    op.create_check_constraint(
        "ck_offene_posten_op_status",
        "offene_posten",
        "op_status IN ('offen','teilweise','geschlossen','storniert')",
    )
    op.create_check_constraint(
        "ck_offene_posten_amounts_nonnegative",
        "offene_posten",
        "betrag >= 0 AND offen >= 0 AND (op_betrag IS NULL OR op_betrag >= 0)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_offene_posten_amounts_nonnegative", "offene_posten", type_="check")
    op.drop_constraint("ck_offene_posten_op_status", "offene_posten", type_="check")
    op.drop_constraint("ck_offene_posten_konto_typ", "offene_posten", type_="check")

    op.drop_index("ix_offene_posten_faelligkeit_status", table_name="offene_posten")
    op.drop_index("ix_offene_posten_op_status", table_name="offene_posten")
    op.drop_index("ix_offene_posten_konto_typ", table_name="offene_posten")
    op.drop_index("ix_offene_posten_konto_nr", table_name="offene_posten")

    op.drop_column("offene_posten", "sperre_grund")
    op.drop_column("offene_posten", "kv_limit")
    op.drop_column("offene_posten", "kredit_limit")
    op.drop_column("offene_posten", "letzte_bewegung_am")
    op.drop_column("offene_posten", "waehrung")
    op.drop_column("offene_posten", "op_text")
    op.drop_column("offene_posten", "saldo")
    op.drop_column("offene_posten", "op_betrag")
    op.drop_column("offene_posten", "valuta")
    op.drop_column("offene_posten", "rechnungsdatum")
    op.drop_column("offene_posten", "op_status")
    op.drop_column("offene_posten", "konto_typ")
    op.drop_column("offene_posten", "konto_name")
    op.drop_column("offene_posten", "konto_nr")
