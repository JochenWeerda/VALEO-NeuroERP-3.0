"""Close 8.3 article master-data field gaps.

Revision ID: articles_master_fields_gap_83_20260215
Revises: business_partner_gap_811_normalized_20260214
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "articles_master_fields_gap_83_20260215"
down_revision = "business_partner_gap_811_normalized_20260214"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("articles", sa.Column("suchbegriff", sa.String(length=100), nullable=True), schema="domain_inventory")
    op.add_column("articles", sa.Column("hersteller", sa.String(length=120), nullable=True), schema="domain_inventory")
    op.add_column("articles", sa.Column("herkunftsland", sa.String(length=2), nullable=True), schema="domain_inventory")
    op.add_column("articles", sa.Column("naehrwertangaben", sa.Text(), nullable=True), schema="domain_inventory")
    op.add_column(
        "articles",
        sa.Column("mhd_erforderlich", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        schema="domain_inventory",
    )
    op.add_column(
        "articles",
        sa.Column("lagerartikel", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        schema="domain_inventory",
    )
    op.add_column(
        "articles",
        sa.Column("mehrwertsteuer_prozent", sa.Numeric(5, 2), nullable=True),
        schema="domain_inventory",
    )
    op.add_column("articles", sa.Column("warengruppe", sa.String(length=80), nullable=True), schema="domain_inventory")
    op.add_column("articles", sa.Column("gefahrgutklasse", sa.String(length=40), nullable=True), schema="domain_inventory")
    op.add_column(
        "articles",
        sa.Column("lagerorte", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        schema="domain_inventory",
    )
    op.add_column(
        "articles",
        sa.Column("chargenpflicht", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        schema="domain_inventory",
    )
    op.add_column(
        "articles",
        sa.Column("qs_pruefung_erforderlich", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        schema="domain_inventory",
    )
    op.add_column("articles", sa.Column("zolltarifnummer", sa.String(length=30), nullable=True), schema="domain_inventory")
    op.add_column(
        "articles",
        sa.Column("bio_kennzeichnung", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        schema="domain_inventory",
    )
    op.add_column(
        "articles",
        sa.Column("gmp_plus_relevanz", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        schema="domain_inventory",
    )
    op.add_column("articles", sa.Column("lieferantennummer", sa.String(length=50), nullable=True), schema="domain_inventory")

    op.execute(
        """
        UPDATE domain_inventory.articles
        SET
          warengruppe = COALESCE(warengruppe, category),
          lieferantennummer = COALESCE(lieferantennummer, supplier_number),
          mehrwertsteuer_prozent = COALESCE(mehrwertsteuer_prozent, 19.00)
        """
    )

    op.create_check_constraint(
        "ck_articles_mehrwertsteuer_range",
        "articles",
        "mehrwertsteuer_prozent IS NULL OR (mehrwertsteuer_prozent >= 0 AND mehrwertsteuer_prozent <= 100)",
        schema="domain_inventory",
    )
    op.create_index("ix_articles_suchbegriff", "articles", ["suchbegriff"], unique=False, schema="domain_inventory")
    op.create_index("ix_articles_warengruppe", "articles", ["warengruppe"], unique=False, schema="domain_inventory")


def downgrade() -> None:
    op.drop_index("ix_articles_warengruppe", table_name="articles", schema="domain_inventory")
    op.drop_index("ix_articles_suchbegriff", table_name="articles", schema="domain_inventory")
    op.drop_constraint("ck_articles_mehrwertsteuer_range", "articles", schema="domain_inventory", type_="check")

    op.drop_column("articles", "lieferantennummer", schema="domain_inventory")
    op.drop_column("articles", "gmp_plus_relevanz", schema="domain_inventory")
    op.drop_column("articles", "bio_kennzeichnung", schema="domain_inventory")
    op.drop_column("articles", "zolltarifnummer", schema="domain_inventory")
    op.drop_column("articles", "qs_pruefung_erforderlich", schema="domain_inventory")
    op.drop_column("articles", "chargenpflicht", schema="domain_inventory")
    op.drop_column("articles", "lagerorte", schema="domain_inventory")
    op.drop_column("articles", "gefahrgutklasse", schema="domain_inventory")
    op.drop_column("articles", "warengruppe", schema="domain_inventory")
    op.drop_column("articles", "mehrwertsteuer_prozent", schema="domain_inventory")
    op.drop_column("articles", "lagerartikel", schema="domain_inventory")
    op.drop_column("articles", "mhd_erforderlich", schema="domain_inventory")
    op.drop_column("articles", "naehrwertangaben", schema="domain_inventory")
    op.drop_column("articles", "herkunftsland", schema="domain_inventory")
    op.drop_column("articles", "hersteller", schema="domain_inventory")
    op.drop_column("articles", "suchbegriff", schema="domain_inventory")
