"""Futtermittel-Stammdaten, Rezepte, Produktionsaufträge und Sortenregister

Revision ID: futtermittel_sorten_produktion_20260410
Revises:
Create Date: 2026-04-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "futtermittel_sorten_produktion_20260410"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")

    # -- Einzelfuttermittel --
    op.create_table(
        "futtermittel_einzelfutter",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("artikel_nummer", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("art", sa.String(100), nullable=False),
        sa.Column("herkunft", sa.String(100), nullable=True),
        sa.Column("lieferant", sa.String(255), nullable=True),
        sa.Column("protein", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("energie", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("faser", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("fett", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("asche", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("trockensubstanz", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("gvo_status", sa.String(50), nullable=True),
        sa.Column("qs_milch", sa.Boolean(), server_default="false"),
        sa.Column("gmp_plus", sa.Boolean(), server_default="false"),
        sa.Column("bio_zertifiziert", sa.Boolean(), server_default="false"),
        sa.Column("verfuegbar_t", sa.DECIMAL(12, 2), server_default="0"),
        sa.Column("einheit", sa.String(10), server_default="'t'"),
        sa.Column("min_bestand_t", sa.DECIMAL(12, 2), nullable=True),
        sa.Column("preis_pro_t", sa.DECIMAL(12, 2), nullable=True),
        sa.Column("aktiv", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "artikel_nummer", name="uq_ef_tenant_artikel"),
        schema="domain_shared",
    )
    op.create_index("ix_ef_tenant", "futtermittel_einzelfutter", ["tenant_id"], schema="domain_shared")
    op.create_index("ix_ef_tenant_artikel", "futtermittel_einzelfutter", ["tenant_id", "artikel_nummer"], schema="domain_shared")

    # -- Mischfuttermittel --
    op.create_table(
        "futtermittel_mischfutter",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("produkt_code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("tierart", sa.String(100), nullable=False),
        sa.Column("leistungsstufe", sa.String(100), nullable=True),
        sa.Column("protein", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("energie", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("beschreibung", sa.Text(), nullable=True),
        sa.Column("aktiv", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "produkt_code", name="uq_mf_tenant_code"),
        schema="domain_shared",
    )
    op.create_index("ix_mf_tenant", "futtermittel_mischfutter", ["tenant_id"], schema="domain_shared")
    op.create_index("ix_mf_tenant_code", "futtermittel_mischfutter", ["tenant_id", "produkt_code"], schema="domain_shared")

    # -- Rezepte --
    op.create_table(
        "futtermittel_rezepte",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("rezept_code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("tierart", sa.String(100), nullable=False),
        sa.Column("mischfutter_id", sa.String(), sa.ForeignKey("domain_shared.futtermittel_mischfutter.id"), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1"),
        sa.Column("protein_ziel", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("energie_ziel", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("bemerkung", sa.Text(), nullable=True),
        sa.Column("aktiv", sa.Boolean(), server_default="true"),
        sa.Column("gueltig_ab", sa.Date(), nullable=True),
        sa.Column("gueltig_bis", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "rezept_code", name="uq_rez_tenant_code"),
        schema="domain_shared",
    )
    op.create_index("ix_rez_tenant", "futtermittel_rezepte", ["tenant_id"], schema="domain_shared")
    op.create_index("ix_rez_tenant_code", "futtermittel_rezepte", ["tenant_id", "rezept_code"], schema="domain_shared")

    # -- Rezept-Komponenten --
    op.create_table(
        "futtermittel_rezept_komponenten",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("rezept_id", sa.String(), sa.ForeignKey("domain_shared.futtermittel_rezepte.id", ondelete="CASCADE"), nullable=False),
        sa.Column("einzelfutter_id", sa.String(), sa.ForeignKey("domain_shared.futtermittel_einzelfutter.id"), nullable=True),
        sa.Column("komponente_name", sa.String(255), nullable=False),
        sa.Column("anteil", sa.DECIMAL(6, 4), nullable=False),
        sa.Column("min_anteil", sa.DECIMAL(6, 4), nullable=True),
        sa.Column("max_anteil", sa.DECIMAL(6, 4), nullable=True),
        sa.Column("sortierung", sa.Integer(), server_default="0"),
        schema="domain_shared",
    )
    op.create_index("ix_rk_rezept", "futtermittel_rezept_komponenten", ["rezept_id"], schema="domain_shared")

    # -- Produktionsaufträge --
    op.create_table(
        "futtermittel_produktionsauftraege",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("chargen_id", sa.String(50), nullable=False),
        sa.Column("rezept_id", sa.String(), sa.ForeignKey("domain_shared.futtermittel_rezepte.id"), nullable=True),
        sa.Column("rezept_name", sa.String(255), nullable=False),
        sa.Column("menge_t", sa.DECIMAL(12, 3), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="'erstellt'"),
        sa.Column("bestands_abzug_erfolgt", sa.Boolean(), server_default="false"),
        sa.Column("erstellt_von", sa.String(255), nullable=True),
        sa.Column("freigegeben_von", sa.String(255), nullable=True),
        sa.Column("freigegeben_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fertig_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column("bemerkung", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_pa_tenant", "futtermittel_produktionsauftraege", ["tenant_id"], schema="domain_shared")
    op.create_index("ix_pa_tenant_status", "futtermittel_produktionsauftraege", ["tenant_id", "status"], schema="domain_shared")
    op.create_index("ix_pa_chargen", "futtermittel_produktionsauftraege", ["chargen_id"], schema="domain_shared")

    # -- Agrar Sorten --
    op.create_table(
        "agrar_sorten",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("variety_number", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("crop_type", sa.String(50), nullable=True),
        sa.Column("zuechter", sa.String(255), nullable=True),
        sa.Column("zulassungsjahr", sa.Integer(), nullable=True),
        sa.Column("reifezahl", sa.String(10), nullable=True),
        sa.Column("qualitaetsgruppe", sa.String(50), nullable=True),
        sa.Column("aktiv", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "variety_number", name="uq_as_tenant_varnr"),
        schema="domain_shared",
    )
    op.create_index("ix_as_tenant", "agrar_sorten", ["tenant_id"], schema="domain_shared")


def downgrade() -> None:
    op.drop_table("futtermittel_produktionsauftraege", schema="domain_shared")
    op.drop_table("futtermittel_rezept_komponenten", schema="domain_shared")
    op.drop_table("futtermittel_rezepte", schema="domain_shared")
    op.drop_table("futtermittel_mischfutter", schema="domain_shared")
    op.drop_table("futtermittel_einzelfutter", schema="domain_shared")
    op.drop_table("agrar_sorten", schema="domain_shared")
