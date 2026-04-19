"""Grundfutter-Laboranalysen: LUFA/VDLUFA-Prüfberichts-Schema (GfE-2023)

Revision ID: grundfutteranalysen_20260419
Revises: futtermittel_sorten_produktion_20260410
Create Date: 2026-04-19
"""
from alembic import op
import sqlalchemy as sa

revision = "grundfutteranalysen_20260419"
down_revision = "futtermittel_sorten_produktion_20260410"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")

    op.create_table(
        "grundfutter_analysen",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        # Metadaten
        sa.Column("labor", sa.String(255), nullable=True),
        sa.Column("probe_nr", sa.String(50), nullable=True),
        sa.Column("auftragsnummer", sa.String(50), nullable=True),
        sa.Column("kundennummer", sa.String(50), nullable=True),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("probenart", sa.String(100), nullable=True),
        sa.Column("erntetermin", sa.Date(), nullable=True),
        sa.Column("eingangsdatum", sa.Date(), nullable=True),
        sa.Column("analyse_datum", sa.Date(), nullable=True),
        sa.Column("probenahme_ort", sa.String(255), nullable=True),
        sa.Column("schnitt", sa.Integer(), nullable=True),
        sa.Column("quelle_datei", sa.String(500), nullable=True),
        # Sensorik
        sa.Column("aussehen", sa.String(100), nullable=True),
        sa.Column("geruch", sa.String(100), nullable=True),
        sa.Column("ph_wert", sa.DECIMAL(4, 2), nullable=True),
        # Grundnährstoffe
        sa.Column("trockensubstanz_os", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("rohprotein_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("rohfaser_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("rohfett_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("rohasche_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("gesamtzucker_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("sand_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("nfc_ts", sa.DECIMAL(6, 2), nullable=True),
        # Faseranalytik
        sa.Column("adfom_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("andfom_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("adl_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("hemicellulose_ts", sa.DECIMAL(6, 2), nullable=True),
        # Gasbildung / Verdaulichkeit
        sa.Column("gasbildung_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("omd_ts", sa.DECIMAL(6, 2), nullable=True),
        # Energie
        sa.Column("me_rind_gfe2008_ts", sa.DECIMAL(6, 3), nullable=True),
        sa.Column("nel_ts", sa.DECIMAL(6, 3), nullable=True),
        sa.Column("me_gfe2023_ts", sa.DECIMAL(6, 3), nullable=True),
        sa.Column("bruttoenergie_ts", sa.DECIMAL(6, 3), nullable=True),
        sa.Column("strukturwert_ts", sa.DECIMAL(5, 2), nullable=True),
        # Protein GfE
        sa.Column("nxp_ts", sa.DECIMAL(7, 1), nullable=True),
        sa.Column("nxp_udp_ts", sa.DECIMAL(7, 1), nullable=True),
        sa.Column("rnb_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("rnb_udp_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("reineiweis_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("anteil_reineiweis_ts", sa.DECIMAL(6, 2), nullable=True),
        # XP-Fraktionierung
        sa.Column("xp_fraktion_a_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("xp_fraktion_b1_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("xp_fraktion_b2_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("xp_fraktion_b3_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("xp_fraktion_c_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("udp2_ts", sa.DECIMAL(7, 1), nullable=True),
        sa.Column("udp5_ts", sa.DECIMAL(7, 1), nullable=True),
        sa.Column("udp8_ts", sa.DECIMAL(7, 1), nullable=True),
        # GfE 2023 sidAA
        sa.Column("sidp_ts", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("sidlys_ts", sa.DECIMAL(6, 3), nullable=True),
        sa.Column("sidmet_ts", sa.DECIMAL(6, 3), nullable=True),
        sa.Column("rmd_ts", sa.DECIMAL(6, 2), nullable=True),
        # CP-Abbau-Kinetik
        sa.Column("cp_abbau_a_ts", sa.DECIMAL(5, 1), nullable=True),
        sa.Column("cp_abbau_b_ts", sa.DECIMAL(5, 1), nullable=True),
        sa.Column("cp_abbau_c_ts", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("cp_abbau_lag_ts", sa.DECIMAL(5, 2), nullable=True),
        # Mineralstoffe
        sa.Column("calcium_ts", sa.DECIMAL(5, 3), nullable=True),
        sa.Column("phosphor_ts", sa.DECIMAL(5, 3), nullable=True),
        sa.Column("natrium_ts", sa.DECIMAL(5, 3), nullable=True),
        sa.Column("magnesium_ts", sa.DECIMAL(5, 3), nullable=True),
        sa.Column("kalium_ts", sa.DECIMAL(5, 3), nullable=True),
        # Verwaltung
        sa.Column("notizen", sa.Text(), nullable=True),
        sa.Column("verifiziert", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        schema="domain_shared",
    )
    op.create_index("ix_gfa_tenant", "grundfutter_analysen", ["tenant_id"], schema="domain_shared")
    op.create_index("ix_gfa_tenant_probe", "grundfutter_analysen", ["tenant_id", "probe_nr"], schema="domain_shared")


def downgrade() -> None:
    op.drop_index("ix_gfa_tenant_probe", table_name="grundfutter_analysen", schema="domain_shared")
    op.drop_index("ix_gfa_tenant", table_name="grundfutter_analysen", schema="domain_shared")
    op.drop_table("grundfutter_analysen", schema="domain_shared")
