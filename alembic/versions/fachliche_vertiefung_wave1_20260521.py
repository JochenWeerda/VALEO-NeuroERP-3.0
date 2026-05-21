"""Fachliche Vertiefung Wave 1: Massebilanz, Zinsabrechnung, Hofliste, Folgeartikel

Revision ID: fachliche_vertiefung_wave1_20260521
Revises: ops_wave107_remaining_stubs_20260520
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "fachliche_vertiefung_wave1_20260521"
down_revision = "ops_wave107_remaining_stubs_20260520"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Massebilanz: Periodische Mengenbilanzierung für Rohware ---
    op.create_table(
        "rohware_massebilanzen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("periode", sa.String(7), nullable=False, comment="YYYY-MM"),
        sa.Column("artikel_id", sa.String, nullable=True),
        sa.Column("artikel_nr", sa.String(50), nullable=True),
        sa.Column("lager_id", sa.String, nullable=True),
        sa.Column("lager_nr", sa.String(50), nullable=True),
        sa.Column("anfangsbestand_kg", sa.Numeric(18, 3), default=0),
        sa.Column("zugaenge_kg", sa.Numeric(18, 3), default=0),
        sa.Column("abgaenge_kg", sa.Numeric(18, 3), default=0),
        sa.Column("endbestand_kg", sa.Numeric(18, 3), default=0),
        sa.Column("differenz_kg", sa.Numeric(18, 3), default=0),
        sa.Column("status", sa.String(20), default="offen",
                  comment="offen, festgeschrieben"),
        sa.Column("festgeschrieben_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column("festgeschrieben_von", sa.String(255), nullable=True),
        sa.Column("bemerkung", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_massebilanz_tenant_periode", "rohware_massebilanzen",
                    ["tenant_id", "periode"], schema="domain_shared")
    op.create_index("ix_massebilanz_tenant_status", "rohware_massebilanzen",
                    ["tenant_id", "status"], schema="domain_shared")

    # Massebilanz-Bewegungen (Einzelbuchungen innerhalb einer Massebilanz)
    op.create_table(
        "rohware_massebilanz_bewegungen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("massebilanz_id", sa.String, sa.ForeignKey("domain_shared.rohware_massebilanzen.id"), nullable=False),
        sa.Column("beleg_nr", sa.String(50), nullable=True),
        sa.Column("beleg_typ", sa.String(30), nullable=True,
                  comment="lieferschein, abschlag, finale, storno"),
        sa.Column("buchungsdatum", sa.Date, nullable=False),
        sa.Column("menge_kg", sa.Numeric(18, 3), nullable=False),
        sa.Column("vorzeichen", sa.String(1), default="+", comment="+ oder -"),
        sa.Column("kontrakt_nr", sa.String(50), nullable=True),
        sa.Column("lieferant_nr", sa.String(50), nullable=True),
        sa.Column("bemerkung", sa.Text, nullable=True),
        sa.Column("storniert", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_massebew_massebilanz", "rohware_massebilanz_bewegungen",
                    ["massebilanz_id"], schema="domain_shared")

    # --- Zinsabrechnung: Zinsen auf Rohware-Einlagerungskontrakte ---
    op.create_table(
        "kontrakt_zinsabrechnungen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("kontrakt_nr", sa.String(50), nullable=False),
        sa.Column("lieferant_nr", sa.String(50), nullable=False),
        sa.Column("lieferant_name", sa.String(255), nullable=True),
        sa.Column("zinssatz_prozent", sa.Numeric(6, 4), nullable=False,
                  comment="Jahreszinssatz in %"),
        sa.Column("basisbetrag_eur", sa.Numeric(18, 2), nullable=False,
                  comment="Abrechnungsgrundlage (Warenwert)"),
        sa.Column("von_datum", sa.Date, nullable=False),
        sa.Column("bis_datum", sa.Date, nullable=False),
        sa.Column("tage", sa.Integer, nullable=False),
        sa.Column("zinsbetrag_eur", sa.Numeric(18, 2), nullable=False),
        sa.Column("mwst_satz", sa.Numeric(5, 2), default=19.0),
        sa.Column("mwst_betrag_eur", sa.Numeric(18, 2), nullable=True),
        sa.Column("status", sa.String(20), default="offen",
                  comment="offen, gedruckt, gebucht, storniert"),
        sa.Column("beleg_nr", sa.String(50), nullable=True),
        sa.Column("buchungs_periode", sa.String(7), nullable=True),
        sa.Column("storno_von_id", sa.String, nullable=True),
        sa.Column("bemerkung", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_zinsabr_tenant_kontrakt", "kontrakt_zinsabrechnungen",
                    ["tenant_id", "kontrakt_nr"], schema="domain_shared")
    op.create_index("ix_zinsabr_tenant_status", "kontrakt_zinsabrechnungen",
                    ["tenant_id", "status"], schema="domain_shared")

    # --- Hofliste: Fahrzeugvormeldungen am Waagenterminal ---
    op.create_table(
        "waage_hofliste",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("standort_id", sa.String, nullable=True, comment="Waage/Lagerstandort"),
        sa.Column("kfz_kennzeichen", sa.String(20), nullable=False),
        sa.Column("fahrer_name", sa.String(255), nullable=True),
        sa.Column("lieferant_nr", sa.String(50), nullable=True),
        sa.Column("lieferant_name", sa.String(255), nullable=True),
        sa.Column("kontrakt_nr", sa.String(50), nullable=True),
        sa.Column("artikel_nr", sa.String(50), nullable=True),
        sa.Column("artikel_name", sa.String(255), nullable=True),
        sa.Column("geplante_menge_t", sa.Numeric(12, 3), nullable=True),
        sa.Column("status", sa.String(20), default="vorgemeldet",
                  comment="vorgemeldet, auf_hof, in_waegung, gewogen, abgefahren"),
        sa.Column("ankunft_zeit", sa.DateTime(timezone=True), nullable=True),
        sa.Column("wiegung_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("abfahrt_zeit", sa.DateTime(timezone=True), nullable=True),
        sa.Column("wiegeschein_id", sa.String, nullable=True),
        sa.Column("bemerkung", sa.Text, nullable=True),
        sa.Column("partievorerfassung", sa.Boolean, default=False,
                  comment="Partie bereits im System vorerfasst"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_hofliste_tenant_status", "waage_hofliste",
                    ["tenant_id", "status"], schema="domain_shared")
    op.create_index("ix_hofliste_tenant_kfz", "waage_hofliste",
                    ["tenant_id", "kfz_kennzeichen"], schema="domain_shared")

    # --- Folgeartikel: Artikelnachfolger-Verwaltung ---
    op.create_table(
        "artikel_folgeartikel",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("artikel_nr", sa.String(50), nullable=False, comment="Vorgänger-Artikel"),
        sa.Column("folge_artikel_nr", sa.String(50), nullable=False, comment="Nachfolger-Artikel"),
        sa.Column("gueltig_ab", sa.Date, nullable=True),
        sa.Column("gueltig_bis", sa.Date, nullable=True),
        sa.Column("grund", sa.String(255), nullable=True,
                  comment="Auslauf, Sortimentswechsel, Umbenennung"),
        sa.Column("automatisch_ersetzen", sa.Boolean, default=False,
                  comment="Automatisch bei Neuanlage von Vorgängen ersetzen"),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_folgeartikel_tenant_nr", "artikel_folgeartikel",
                    ["tenant_id", "artikel_nr"], schema="domain_shared")

    # --- Inventurgruppen: Gruppierung für Inventur ---
    op.create_table(
        "artikel_inventurgruppen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("gruppe_nr", sa.String(20), nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("inventur_zyklus", sa.String(20), nullable=True,
                  comment="jaehrlich, halbjaehrlich, quartalsweise, rollierend"),
        sa.Column("naechste_inventur", sa.Date, nullable=True),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_inventurgrp_tenant_nr", "artikel_inventurgruppen",
                    ["tenant_id", "gruppe_nr"], schema="domain_shared")

    # --- Wiegungs-Aggregation: Raffen und Aufteilen ---
    op.create_table(
        "waage_wiegungsgruppen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("gruppe_nr", sa.String(50), nullable=False),
        sa.Column("typ", sa.String(20), nullable=False,
                  comment="gerafft (aggregiert) oder aufgeteilt"),
        sa.Column("wiegeschein_ids", JSONB, nullable=True,
                  comment="Liste der zugehörigen Wiegeschein-IDs"),
        sa.Column("gesamt_netto_kg", sa.Numeric(18, 3), nullable=True),
        sa.Column("kontrakt_nr", sa.String(50), nullable=True),
        sa.Column("beleg_nr", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), default="offen",
                  comment="offen, abgerechnet"),
        sa.Column("bemerkung", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_wieggrp_tenant", "waage_wiegungsgruppen",
                    ["tenant_id"], schema="domain_shared")


def downgrade() -> None:
    op.drop_table("waage_wiegungsgruppen", schema="domain_shared")
    op.drop_table("artikel_inventurgruppen", schema="domain_shared")
    op.drop_table("artikel_folgeartikel", schema="domain_shared")
    op.drop_table("waage_hofliste", schema="domain_shared")
    op.drop_table("kontrakt_zinsabrechnungen", schema="domain_shared")
    op.drop_index("ix_massebew_massebilanz", "rohware_massebilanz_bewegungen", schema="domain_shared")
    op.drop_table("rohware_massebilanz_bewegungen", schema="domain_shared")
    op.drop_index("ix_massebilanz_tenant_status", "rohware_massebilanzen", schema="domain_shared")
    op.drop_index("ix_massebilanz_tenant_periode", "rohware_massebilanzen", schema="domain_shared")
    op.drop_table("rohware_massebilanzen", schema="domain_shared")
