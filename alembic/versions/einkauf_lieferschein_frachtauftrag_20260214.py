"""Add procurement delivery note and freight order tables.

Revision ID: einkauf_lieferschein_frachtauftrag_20260214
Revises: offene_posten_fields_crud_20260214
Create Date: 2026-02-14
"""

from alembic import op
import sqlalchemy as sa


revision = "einkauf_lieferschein_frachtauftrag_20260214"
down_revision = "offene_posten_fields_crud_20260214"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "einkauf_lieferscheine",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("lieferschein_nr", sa.String(length=64), nullable=False),
        sa.Column("lieferschein_datum", sa.Date(), nullable=False),
        sa.Column("niederlassung", sa.String(length=120), nullable=True),
        sa.Column("lieferant_id", sa.String(length=36), nullable=True),
        sa.Column("lieferant_name", sa.String(length=255), nullable=True),
        sa.Column("zahlungsbedingung", sa.String(length=120), nullable=True),
        sa.Column("texte", sa.Text(), nullable=True),
        sa.Column("zwischenhaendler", sa.String(length=255), nullable=True),
        sa.Column("wie_vom_ls", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("lieferanten_stamm", sa.String(length=255), nullable=True),
        sa.Column("liefer_termin", sa.Date(), nullable=True),
        sa.Column("lieferdatum", sa.Date(), nullable=True),
        sa.Column("liefer_nr", sa.String(length=80), nullable=True),
        sa.Column("bediener", sa.String(length=120), nullable=True),
        sa.Column("erledigt", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("verfuegbarer_bestand", sa.Numeric(14, 3), nullable=True),
        sa.Column("summe_gewicht", sa.Numeric(14, 3), nullable=True),
        sa.Column("mwst_betrag", sa.Numeric(14, 2), nullable=True),
        sa.Column("netto_betrag", sa.Numeric(14, 2), nullable=True),
        sa.Column("brutto_betrag", sa.Numeric(14, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "lieferschein_nr", name="uq_einkauf_lieferschein_nr_tenant"),
    )
    op.create_index("ix_einkauf_lieferscheine_tenant_id", "einkauf_lieferscheine", ["tenant_id"], unique=False)
    op.create_index("ix_einkauf_lieferscheine_lieferant", "einkauf_lieferscheine", ["lieferant_id"], unique=False)
    op.create_index("ix_einkauf_lieferscheine_datum", "einkauf_lieferscheine", ["lieferschein_datum"], unique=False)

    op.create_table(
        "einkauf_lieferschein_positionen",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("lieferschein_id", sa.String(length=36), nullable=False),
        sa.Column("pos_nr", sa.Integer(), nullable=False),
        sa.Column("artikel_nr", sa.String(length=64), nullable=True),
        sa.Column("lieferant_artikel_nr", sa.String(length=64), nullable=True),
        sa.Column("bezeichnung", sa.String(length=255), nullable=True),
        sa.Column("gebinde_nr", sa.String(length=64), nullable=True),
        sa.Column("gebinde", sa.Numeric(14, 3), nullable=True),
        sa.Column("menge", sa.Numeric(14, 3), nullable=False),
        sa.Column("einheit", sa.String(length=20), nullable=True),
        sa.Column("einzelpreis", sa.Numeric(14, 4), nullable=True),
        sa.Column("nettobetrag", sa.Numeric(14, 2), nullable=True),
        sa.Column("lagerhalle", sa.String(length=80), nullable=True),
        sa.Column("lagerfach", sa.String(length=80), nullable=True),
        sa.Column("charge", sa.String(length=80), nullable=True),
        sa.Column("serien_nr", sa.String(length=80), nullable=True),
        sa.Column("kontakt", sa.String(length=120), nullable=True),
        sa.Column("prozent", sa.Numeric(7, 3), nullable=True),
        sa.Column("master_nr", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["lieferschein_id"], ["einkauf_lieferscheine.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lieferschein_id", "pos_nr", name="uq_einkauf_ls_pos_nr"),
    )
    op.create_index("ix_einkauf_lieferschein_positionen_lieferschein", "einkauf_lieferschein_positionen", ["lieferschein_id"], unique=False)
    op.create_index("ix_einkauf_lieferschein_positionen_artikel", "einkauf_lieferschein_positionen", ["artikel_nr"], unique=False)

    op.create_table(
        "einkauf_frachtauftraege",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("frachtauftrag_nr", sa.String(length=64), nullable=False),
        sa.Column("frachtauftrag_erzeugt", sa.DateTime(timezone=True), nullable=True),
        sa.Column("niederlassung", sa.String(length=120), nullable=True),
        sa.Column("liefertermin", sa.Date(), nullable=True),
        sa.Column("spediteur_nr", sa.String(length=64), nullable=True),
        sa.Column("spediteur_name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("telefon", sa.String(length=60), nullable=True),
        sa.Column("belegnummer", sa.String(length=64), nullable=True),
        sa.Column("lade_datum", sa.Date(), nullable=True),
        sa.Column("kunde_id", sa.String(length=36), nullable=True),
        sa.Column("kunde_name", sa.String(length=255), nullable=True),
        sa.Column("debitoren_filter", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "frachtauftrag_nr", name="uq_einkauf_frachtauftrag_nr_tenant"),
    )
    op.create_index("ix_einkauf_frachtauftraege_tenant_id", "einkauf_frachtauftraege", ["tenant_id"], unique=False)
    op.create_index("ix_einkauf_frachtauftraege_spediteur", "einkauf_frachtauftraege", ["spediteur_nr"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_einkauf_frachtauftraege_spediteur", table_name="einkauf_frachtauftraege")
    op.drop_index("ix_einkauf_frachtauftraege_tenant_id", table_name="einkauf_frachtauftraege")
    op.drop_table("einkauf_frachtauftraege")

    op.drop_index("ix_einkauf_lieferschein_positionen_artikel", table_name="einkauf_lieferschein_positionen")
    op.drop_index("ix_einkauf_lieferschein_positionen_lieferschein", table_name="einkauf_lieferschein_positionen")
    op.drop_table("einkauf_lieferschein_positionen")

    op.drop_index("ix_einkauf_lieferscheine_datum", table_name="einkauf_lieferscheine")
    op.drop_index("ix_einkauf_lieferscheine_lieferant", table_name="einkauf_lieferscheine")
    op.drop_index("ix_einkauf_lieferscheine_tenant_id", table_name="einkauf_lieferscheine")
    op.drop_table("einkauf_lieferscheine")
