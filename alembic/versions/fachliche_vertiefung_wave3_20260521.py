"""Fachliche Vertiefung Wave 3: Kundenbanken, PIV, Stoffstromanteil, Skonto-Auszifferung

Revision ID: fachliche_vertiefung_wave3_20260521
Revises: fachliche_vertiefung_wave2_20260521
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa

revision = "fachliche_vertiefung_wave3_20260521"
down_revision = "fachliche_vertiefung_wave2_20260521"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Kundenbanken: IBAN/BIC-Verbindungen je Kunde ---
    op.create_table(
        "kunden_bankverbindungen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("kunden_nr", sa.String(50), nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=True,
                  comment="Kurzbezeichnung z.B. 'Hauptkonto', 'Saisonkonto'"),
        sa.Column("iban", sa.String(34), nullable=False),
        sa.Column("bic", sa.String(11), nullable=True),
        sa.Column("bank_name", sa.String(255), nullable=True),
        sa.Column("kontoinhaber", sa.String(255), nullable=True),
        sa.Column("sepa_mandat_ref", sa.String(50), nullable=True,
                  comment="SEPA-Lastschriftmandat Referenz"),
        sa.Column("sepa_mandat_datum", sa.Date, nullable=True),
        sa.Column("standard", sa.Boolean, default=False,
                  comment="Standard-Bankverbindung für Zahlungsverkehr"),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_kundenbank_tenant_nr", "kunden_bankverbindungen",
                    ["tenant_id", "kunden_nr"], schema="domain_shared")
    op.create_index("ix_kundenbank_iban", "kunden_bankverbindungen",
                    ["tenant_id", "iban"], schema="domain_shared")

    # --- Permanente Inventur (PIV): Rollierender Bestandsabschluss ---
    op.create_table(
        "inventur_piv_abschluesse",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("abschluss_datum", sa.Date, nullable=False),
        sa.Column("inventurgruppe_nr", sa.String(20), nullable=True),
        sa.Column("lager_nr", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), default="offen",
                  comment="offen, laufend, abgeschlossen, ignoriert"),
        sa.Column("erfasst_von", sa.String(255), nullable=True),
        sa.Column("abgeschlossen_von", sa.String(255), nullable=True),
        sa.Column("abgeschlossen_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column("anzahl_positionen", sa.Integer, default=0),
        sa.Column("differenzwert_eur", sa.Numeric(18, 2), nullable=True),
        sa.Column("bemerkung", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_piv_tenant_datum", "inventur_piv_abschluesse",
                    ["tenant_id", "abschluss_datum"], schema="domain_shared")

    # PIV-Positionen (einzelne Artikel/Lagerplatz-Zählungen)
    op.create_table(
        "inventur_piv_positionen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("abschluss_id", sa.String,
                  sa.ForeignKey("domain_shared.inventur_piv_abschluesse.id"),
                  nullable=False),
        sa.Column("artikel_nr", sa.String(50), nullable=False),
        sa.Column("lagerplatz", sa.String(50), nullable=True),
        sa.Column("buchbestand", sa.Numeric(18, 3), nullable=False,
                  comment="Buchbestand laut System"),
        sa.Column("zaehlmenge", sa.Numeric(18, 3), nullable=True,
                  comment="Gezählte physische Menge"),
        sa.Column("differenz", sa.Numeric(18, 3), nullable=True,
                  comment="Zählmenge - Buchbestand"),
        sa.Column("bewertungspreis_eur", sa.Numeric(12, 4), nullable=True),
        sa.Column("differenzwert_eur", sa.Numeric(18, 2), nullable=True),
        sa.Column("erfasst", sa.Boolean, default=False),
        sa.Column("ignoriert", sa.Boolean, default=False,
                  comment="PIV-Belege Partien ignorieren (SPA-gesteuertes Verhalten)"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_pivpos_abschluss", "inventur_piv_positionen",
                    ["abschluss_id"], schema="domain_shared")

    # --- Skonto-Auszifferung: Protokoll der OP-Ausgleiche mit Skonto ---
    op.create_table(
        "op_auszifferungen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("op_id", sa.String, nullable=False),
        sa.Column("rechnungsnr", sa.String(50), nullable=True),
        sa.Column("zahlungsdatum", sa.Date, nullable=False),
        sa.Column("zahlungsbetrag_eur", sa.Numeric(18, 2), nullable=False),
        sa.Column("skonto_betrag_eur", sa.Numeric(18, 2), default=0,
                  comment="Skontoabzug in EUR"),
        sa.Column("skonto_prozent", sa.Numeric(5, 2), nullable=True),
        sa.Column("gesamtbetrag_eur", sa.Numeric(18, 2), nullable=False,
                  comment="Zahlung + Skonto = Rechnungsbetrag"),
        sa.Column("zahlungsart", sa.String(30), nullable=True,
                  comment="ueberweisung, lastschrift, bar, scheck"),
        sa.Column("buchungstext", sa.String(255), nullable=True),
        sa.Column("fibu_konto", sa.String(20), nullable=True),
        sa.Column("skonto_konto", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), default="gebucht"),
        sa.Column("storniert", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_opausziffer_tenant_op", "op_auszifferungen",
                    ["tenant_id", "op_id"], schema="domain_shared")

    # --- Stoffstromanteil: THG/CO2-Bewertung je Artikel ---
    op.create_table(
        "artikel_stoffstrom",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("artikel_nr", sa.String(50), nullable=False),
        sa.Column("anbauland", sa.String(50), nullable=True,
                  comment="ISO 3166-2 Ländercode"),
        sa.Column("rohstoff_kategorie", sa.String(100), nullable=True,
                  comment="z.B. Getreide, Ölsaat, Zucker"),
        sa.Column("co2_aequivalent_kg_per_t", sa.Numeric(12, 4), nullable=True,
                  comment="kg CO2-Äquivalent pro Tonne"),
        sa.Column("thg_wert", sa.Numeric(12, 4), nullable=True,
                  comment="THG-Treibhausgasemissionswert (gCO2eq/MJ)"),
        sa.Column("nachhaltig", sa.Boolean, default=True),
        sa.Column("iscc_zertifiziert", sa.Boolean, default=False),
        sa.Column("red_konform", sa.Boolean, default=False,
                  comment="EU Renewable Energy Directive konform"),
        sa.Column("gueltig_ab", sa.Date, nullable=True),
        sa.Column("gueltig_bis", sa.Date, nullable=True),
        sa.Column("bemerkung", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_stoffstrom_tenant_artikel", "artikel_stoffstrom",
                    ["tenant_id", "artikel_nr"], schema="domain_shared")


def downgrade() -> None:
    op.drop_index("ix_stoffstrom_tenant_artikel", "artikel_stoffstrom", schema="domain_shared")
    op.drop_table("artikel_stoffstrom", schema="domain_shared")
    op.drop_index("ix_opausziffer_tenant_op", "op_auszifferungen", schema="domain_shared")
    op.drop_table("op_auszifferungen", schema="domain_shared")
    op.drop_table("inventur_piv_positionen", schema="domain_shared")
    op.drop_index("ix_piv_tenant_datum", "inventur_piv_abschluesse", schema="domain_shared")
    op.drop_table("inventur_piv_abschluesse", schema="domain_shared")
    op.drop_index("ix_kundenbank_iban", "kunden_bankverbindungen", schema="domain_shared")
    op.drop_index("ix_kundenbank_tenant_nr", "kunden_bankverbindungen", schema="domain_shared")
    op.drop_table("kunden_bankverbindungen", schema="domain_shared")
