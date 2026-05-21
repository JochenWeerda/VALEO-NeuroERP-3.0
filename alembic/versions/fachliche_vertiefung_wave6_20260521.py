"""Fachliche Vertiefung Wave 6: Mengeneinheitengruppen, Artikelverpackung/Gebinde, Zahlungsmeldungen

Revision ID: fachliche_vertiefung_wave6_20260521
Revises: fachliche_vertiefung_wave5_20260521
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa

revision = "fachliche_vertiefung_wave6_20260521"
down_revision = "fachliche_vertiefung_wave5_20260521"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Mengeneinheiten-Stamm: Basiseinheiten mit Umrechnungen ---
    op.create_table(
        "artikel_mengeneinheiten",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("einheit_kuerzel", sa.String(10), nullable=False,
                  comment="z.B. kg, t, l, Stk, Kar"),
        sa.Column("bezeichnung", sa.String(100), nullable=False),
        sa.Column("basis_einheit", sa.String(10), nullable=True,
                  comment="Basiseinheit für Umrechnung z.B. kg für t"),
        sa.Column("umrechnungsfaktor", sa.Numeric(18, 6), nullable=True,
                  comment="1 Einheit = Faktor * Basiseinheit (z.B. 1 t = 1000 kg)"),
        sa.Column("dezimalstellen", sa.Integer, default=3),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_mengeneinheit_tenant_kz", "artikel_mengeneinheiten",
                    ["tenant_id", "einheit_kuerzel"], unique=True, schema="domain_shared")

    # --- Mengeneinheitengruppen: EK/VK/Bestand-Einheiten je Artikel ---
    op.create_table(
        "artikel_mengeneinheitengruppen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("gruppe_nr", sa.String(20), nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("bestand_einheit", sa.String(10), nullable=False,
                  comment="Mengeneinheit für Bestandsführung"),
        sa.Column("ek_einheit", sa.String(10), nullable=True,
                  comment="Mengeneinheit im Einkauf"),
        sa.Column("vk_einheit", sa.String(10), nullable=True,
                  comment="Mengeneinheit im Verkauf"),
        sa.Column("preis_einheit", sa.String(10), nullable=True,
                  comment="Mengeneinheit für Preisfindung"),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_me_gruppe_tenant_nr", "artikel_mengeneinheitengruppen",
                    ["tenant_id", "gruppe_nr"], unique=True, schema="domain_shared")

    # --- Artikelverpackung [AVP]: Gebinde-Stamm (1-3 Ebenen) ---
    op.create_table(
        "artikel_verpackungen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("verpackungs_nr", sa.String(20), nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("stufen", sa.Integer, default=1,
                  comment="Anzahl Gebindestufen: 1, 2 oder 3 (SPA 591/592/593)"),
        # Stufe 1 — Einzelgebinde
        sa.Column("stufe1_bezeichnung", sa.String(100), nullable=True),
        sa.Column("stufe1_menge", sa.Numeric(12, 4), nullable=True,
                  comment="Inhalt Stufe 1 in Basiseinheit"),
        sa.Column("stufe1_einheit", sa.String(10), nullable=True),
        sa.Column("stufe1_gewicht_kg", sa.Numeric(10, 4), nullable=True),
        # Stufe 2 — Karton/Tray
        sa.Column("stufe2_bezeichnung", sa.String(100), nullable=True),
        sa.Column("stufe2_einheiten_pro_stufe2", sa.Integer, nullable=True,
                  comment="Anzahl Stufe-1-Einheiten pro Stufe-2-Einheit"),
        sa.Column("stufe2_gewicht_kg", sa.Numeric(10, 4), nullable=True),
        # Stufe 3 — Palette/Masterkarton
        sa.Column("stufe3_bezeichnung", sa.String(100), nullable=True),
        sa.Column("stufe3_einheiten_pro_stufe3", sa.Integer, nullable=True,
                  comment="Anzahl Stufe-2-Einheiten pro Stufe-3-Einheit"),
        sa.Column("stufe3_gewicht_kg", sa.Numeric(10, 4), nullable=True),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_artikelverp_tenant_nr", "artikel_verpackungen",
                    ["tenant_id", "verpackungs_nr"], unique=True, schema="domain_shared")

    # --- Zahlungsmeldungen [KASSZAME]: Eingehende Zahlungsanzeigen ---
    op.create_table(
        "fibu_zahlungsmeldungen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("meldungs_nr", sa.String(30), nullable=True,
                  comment="Externe Referenznummer der Zahlungsmeldung"),
        sa.Column("kunden_nr", sa.String(50), nullable=False),
        sa.Column("rechnungs_nr", sa.String(50), nullable=True),
        sa.Column("zahlungsdatum", sa.Date, nullable=False),
        sa.Column("zahlungsbetrag_eur", sa.Numeric(18, 2), nullable=False),
        sa.Column("skonto_betrag_eur", sa.Numeric(18, 2), default=0),
        sa.Column("skonto_erlaubt", sa.Boolean, default=False,
                  comment="Zusätzlicher Skonto aus Zahlungsvereinbarung erlaubt (EPA KASSZAME)"),
        sa.Column("teilzahlung", sa.Boolean, default=False,
                  comment="Teilzahlung — OP bleibt offen für Restbetrag"),
        sa.Column("aus_fibu", sa.Boolean, default=False,
                  comment="Ausgangsrechnung aus FIBU (nicht Warenwirtschaft)"),
        sa.Column("status", sa.String(20), default="eingegangen",
                  comment="eingegangen, verarbeitet, abgewiesen"),
        sa.Column("verarbeitet_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_zahlungsmeldung_tenant_kdnr", "fibu_zahlungsmeldungen",
                    ["tenant_id", "kunden_nr"], schema="domain_shared")


def downgrade() -> None:
    op.drop_index("ix_zahlungsmeldung_tenant_kdnr", "fibu_zahlungsmeldungen", schema="domain_shared")
    op.drop_table("fibu_zahlungsmeldungen", schema="domain_shared")
    op.drop_index("ix_artikelverp_tenant_nr", "artikel_verpackungen", schema="domain_shared")
    op.drop_table("artikel_verpackungen", schema="domain_shared")
    op.drop_index("ix_me_gruppe_tenant_nr", "artikel_mengeneinheitengruppen", schema="domain_shared")
    op.drop_table("artikel_mengeneinheitengruppen", schema="domain_shared")
    op.drop_index("ix_mengeneinheit_tenant_kz", "artikel_mengeneinheiten", schema="domain_shared")
    op.drop_table("artikel_mengeneinheiten", schema="domain_shared")
