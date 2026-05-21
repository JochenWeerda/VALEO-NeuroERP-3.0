"""Fachliche Vertiefung Wave 4: Rabattgruppen/klassen, Hausbankenstamm, Bestandteile, Frachttabellen

Revision ID: fachliche_vertiefung_wave4_20260521
Revises: fachliche_vertiefung_wave3_20260521
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa

revision = "fachliche_vertiefung_wave4_20260521"
down_revision = "fachliche_vertiefung_wave3_20260521"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Rabattgruppen: Artikel-Gruppierung für Rabattpflege ---
    op.create_table(
        "preis_rabattgruppen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("gruppe_nr", sa.String(20), nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("richtung", sa.String(2), nullable=False,
                  comment="EK=Einkauf, VK=Verkauf"),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_rabattgruppe_tenant_nr", "preis_rabattgruppen",
                    ["tenant_id", "gruppe_nr", "richtung"], unique=True, schema="domain_shared")

    # --- Rabattklassen: Kunden/Lieferanten-Gruppierung für Rabattpflege ---
    op.create_table(
        "preis_rabattklassen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("klasse_nr", sa.String(20), nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("richtung", sa.String(2), nullable=False,
                  comment="EK=Einkauf, VK=Verkauf"),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_rabattklasse_tenant_nr", "preis_rabattklassen",
                    ["tenant_id", "klasse_nr", "richtung"], unique=True, schema="domain_shared")

    # --- Rabattsätze: Konkrete Rabatte je Gruppe x Klasse ---
    op.create_table(
        "preis_rabattsaetze",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("rabattgruppe_nr", sa.String(20), nullable=False,
                  comment="Artikel-Rabattgruppe"),
        sa.Column("rabattklasse_nr", sa.String(20), nullable=False,
                  comment="Kunden-/Lieferanten-Rabattklasse"),
        sa.Column("richtung", sa.String(2), nullable=False, comment="EK oder VK"),
        sa.Column("rabatt_prozent", sa.Numeric(6, 3), nullable=False,
                  comment="Rabattsatz in Prozent"),
        sa.Column("ab_menge", sa.Numeric(18, 3), nullable=True,
                  comment="Staffelmenge ab der dieser Satz gilt"),
        sa.Column("gueltig_ab", sa.Date, nullable=True),
        sa.Column("gueltig_bis", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_rabattsatz_tenant_grp_kl", "preis_rabattsaetze",
                    ["tenant_id", "rabattgruppe_nr", "rabattklasse_nr", "richtung"],
                    schema="domain_shared")

    # --- Hausbankenstamm: Eigene Bankverbindungen des Mandanten ---
    op.create_table(
        "hausbankenstamm",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("bank_nr", sa.String(20), nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("iban", sa.String(34), nullable=False),
        sa.Column("bic", sa.String(11), nullable=True),
        sa.Column("bank_name", sa.String(255), nullable=True),
        sa.Column("kontonummer", sa.String(30), nullable=True),
        sa.Column("blz", sa.String(10), nullable=True),
        sa.Column("waehrung", sa.String(3), default="EUR",
                  comment="ISO 4217 Währungscode"),
        sa.Column("erechnung_aktiv", sa.Boolean, default=False,
                  comment="Hausbank in eRechnungen verwenden (BNKH eRechnung-Flag)"),
        sa.Column("sepa_glaeubiger_id", sa.String(35), nullable=True,
                  comment="SEPA Gläubiger-ID für Lastschriftmandate"),
        sa.Column("standard", sa.Boolean, default=False),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_hausbank_tenant_nr", "hausbankenstamm",
                    ["tenant_id", "bank_nr"], unique=True, schema="domain_shared")

    # --- Artikel-Bestandteile: Qualitätsmerkmale/Inhaltsstoffe je Artikel ---
    op.create_table(
        "artikel_bestandteile_def",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("bestandteil_nr", sa.String(20), nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("einheit", sa.String(20), nullable=True,
                  comment="Mengeneinheit z.B. %, mg/kg, g/kg"),
        sa.Column("grenzwert_min", sa.Numeric(12, 4), nullable=True),
        sa.Column("grenzwert_max", sa.Numeric(12, 4), nullable=True),
        sa.Column("nutzung", sa.String(30), nullable=True,
                  comment="egal, qualitaetsdaten, ackerschlagkartei, partieartikelanalyse"),
        sa.Column("typ_schad_naehr", sa.String(20), nullable=True,
                  comment="beides, schadstoff, naehrstoff, keins"),
        sa.Column("waage_qualitaet_nr", sa.Integer, nullable=True,
                  comment="Feldnummer für Waagenqualitäts-Übernahme"),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_bestandteil_tenant_nr", "artikel_bestandteile_def",
                    ["tenant_id", "bestandteil_nr"], unique=True, schema="domain_shared")

    # --- Artikel-Bestandteil-Zuordnung: Welche Bestandteile hat ein Artikel ---
    op.create_table(
        "artikel_bestandteile_zuordnung",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("artikel_nr", sa.String(50), nullable=False),
        sa.Column("bestandteil_nr", sa.String(20), nullable=False),
        sa.Column("sollwert", sa.Numeric(12, 4), nullable=True,
                  comment="Sollwert/Standardwert für Analyse"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_bestandteil_zuord_artikel", "artikel_bestandteile_zuordnung",
                    ["tenant_id", "artikel_nr"], schema="domain_shared")

    # --- Frachttabellen: Frachtkosten-Stamm ---
    op.create_table(
        "logistik_frachttabellen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("tabelle_nr", sa.String(20), nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("einheit", sa.String(20), nullable=True,
                  comment="t, km, Palette, Stück"),
        sa.Column("waehrung", sa.String(3), default="EUR"),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_frachttabelle_tenant_nr", "logistik_frachttabellen",
                    ["tenant_id", "tabelle_nr"], unique=True, schema="domain_shared")

    # --- Frachttabellen-Positionen: Staffelwerte ---
    op.create_table(
        "logistik_frachttabellen_positionen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("tabelle_nr", sa.String(20), nullable=False),
        sa.Column("ab_menge", sa.Numeric(18, 3), nullable=False,
                  comment="Menge ab der dieser Frachtsatz gilt"),
        sa.Column("frachtsatz_eur", sa.Numeric(12, 4), nullable=False,
                  comment="Frachtsatz in EUR je Einheit"),
        sa.Column("mindestfracht_eur", sa.Numeric(12, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_frachttabellenpos_tabelle", "logistik_frachttabellen_positionen",
                    ["tenant_id", "tabelle_nr"], schema="domain_shared")

    # --- Frachttabellen-Zuordnungen: Frachtklasse x Frachtgruppe x Versandart ---
    op.create_table(
        "logistik_frachttabellen_zuordnung",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("frachtklasse", sa.String(20), nullable=False,
                  comment="Frachtklasse aus Kundenstamm"),
        sa.Column("frachtgruppe", sa.String(20), nullable=False,
                  comment="Frachtgruppe aus Artikelstamm"),
        sa.Column("versandart", sa.String(30), nullable=True),
        sa.Column("tabelle_nr", sa.String(20), nullable=False),
        sa.Column("sperre", sa.Boolean, default=False),
        sa.Column("gueltig_ab", sa.Date, nullable=True),
        sa.Column("gueltig_bis", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_frachtzuord_tenant", "logistik_frachttabellen_zuordnung",
                    ["tenant_id", "frachtklasse", "frachtgruppe"], schema="domain_shared")


def downgrade() -> None:
    op.drop_index("ix_frachtzuord_tenant", "logistik_frachttabellen_zuordnung", schema="domain_shared")
    op.drop_table("logistik_frachttabellen_zuordnung", schema="domain_shared")
    op.drop_index("ix_frachttabellenpos_tabelle", "logistik_frachttabellen_positionen", schema="domain_shared")
    op.drop_table("logistik_frachttabellen_positionen", schema="domain_shared")
    op.drop_index("ix_frachttabelle_tenant_nr", "logistik_frachttabellen", schema="domain_shared")
    op.drop_table("logistik_frachttabellen", schema="domain_shared")
    op.drop_index("ix_bestandteil_zuord_artikel", "artikel_bestandteile_zuordnung", schema="domain_shared")
    op.drop_table("artikel_bestandteile_zuordnung", schema="domain_shared")
    op.drop_index("ix_bestandteil_tenant_nr", "artikel_bestandteile_def", schema="domain_shared")
    op.drop_table("artikel_bestandteile_def", schema="domain_shared")
    op.drop_index("ix_hausbank_tenant_nr", "hausbankenstamm", schema="domain_shared")
    op.drop_table("hausbankenstamm", schema="domain_shared")
    op.drop_index("ix_rabattsatz_tenant_grp_kl", "preis_rabattsaetze", schema="domain_shared")
    op.drop_table("preis_rabattsaetze", schema="domain_shared")
    op.drop_index("ix_rabattklasse_tenant_nr", "preis_rabattklassen", schema="domain_shared")
    op.drop_table("preis_rabattklassen", schema="domain_shared")
    op.drop_index("ix_rabattgruppe_tenant_nr", "preis_rabattgruppen", schema="domain_shared")
    op.drop_table("preis_rabattgruppen", schema="domain_shared")
