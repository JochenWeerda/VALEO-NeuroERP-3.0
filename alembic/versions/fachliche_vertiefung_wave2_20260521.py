"""Fachliche Vertiefung Wave 2: Kontraktmengenzeitraum, Zu-Abschlaege, Rezepturgruppen

Revision ID: fachliche_vertiefung_wave2_20260521
Revises: fachliche_vertiefung_wave1_20260521
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa

revision = "fachliche_vertiefung_wave2_20260521"
down_revision = "fachliche_vertiefung_wave1_20260521"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Kontraktmengenzeitraum: Ratierliche Lieferpläne je Kontrakt ---
    op.create_table(
        "kontrakt_mengenzeitraeume",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("kontrakt_nr", sa.String(50), nullable=False),
        sa.Column("zeitraum_von", sa.Date, nullable=False),
        sa.Column("zeitraum_bis", sa.Date, nullable=False),
        sa.Column("menge_t", sa.Numeric(18, 3), nullable=False,
                  comment="Sollmenge in diesem Zeitraum in Tonnen"),
        sa.Column("menge_bereits_geliefert_t", sa.Numeric(18, 3), default=0),
        sa.Column("menge_restmenge_t", sa.Numeric(18, 3), nullable=True),
        sa.Column("variante", sa.String(50), nullable=True,
                  comment="z.B. monatl. lin. Abnahme, quartalsweise"),
        sa.Column("status", sa.String(20), default="offen",
                  comment="offen, erfuellt, teilerfuellt, ueberschritten"),
        sa.Column("bemerkung", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_ktrmengen_tenant_kontrakt", "kontrakt_mengenzeitraeume",
                    ["tenant_id", "kontrakt_nr"], schema="domain_shared")

    # --- Kontrakt Zu-/Abschlagsgruppen ---
    op.create_table(
        "kontrakt_zuabschlagsgruppen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("gruppe_nr", sa.String(20), nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("typ", sa.String(10), nullable=False,
                  comment="zuschlag oder abschlag"),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_ktrza_tenant_nr", "kontrakt_zuabschlagsgruppen",
                    ["tenant_id", "gruppe_nr"], schema="domain_shared")

    # Einzelne Zu-/Abschläge einer Gruppe
    op.create_table(
        "kontrakt_zuabschlaege",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("gruppe_id", sa.String,
                  sa.ForeignKey("domain_shared.kontrakt_zuabschlagsgruppen.id"),
                  nullable=False),
        sa.Column("kontrakt_nr", sa.String(50), nullable=True,
                  comment="NULL = gilt für alle Kontrakte der Gruppe"),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("betrag_eur", sa.Numeric(12, 4), nullable=True,
                  comment="Festbetrag in EUR/t"),
        sa.Column("prozent", sa.Numeric(8, 4), nullable=True,
                  comment="Prozentualer Zu-/Abschlag"),
        sa.Column("einheit", sa.String(10), default="t"),
        sa.Column("gueltig_ab", sa.Date, nullable=True),
        sa.Column("gueltig_bis", sa.Date, nullable=True),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_ktrza_gruppe", "kontrakt_zuabschlaege",
                    ["gruppe_id"], schema="domain_shared")

    # --- Rezepturgruppen für Mischfutter ---
    op.create_table(
        "futtermittel_rezepturgruppen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("gruppe_nr", sa.String(20), nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("tierart", sa.String(100), nullable=True,
                  comment="Rind, Schwein, Geflügel, Schaf, etc."),
        sa.Column("nutzungsrichtung", sa.String(100), nullable=True,
                  comment="Milch, Mast, Zucht, Aufzucht"),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_rezgrp_tenant_nr", "futtermittel_rezepturgruppen",
                    ["tenant_id", "gruppe_nr"], schema="domain_shared")

    # --- Produktions-Schnellerfassung: Wiederholungsbuchungen ---
    op.create_table(
        "futtermittel_schnellerfassung",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False,
                  comment="Name der Schnellerfassungsvorlage"),
        sa.Column("rezept_id", sa.String, nullable=True),
        sa.Column("rezept_name", sa.String(255), nullable=True),
        sa.Column("standard_menge_t", sa.Numeric(12, 3), nullable=True),
        sa.Column("ziel_lager_id", sa.String, nullable=True),
        sa.Column("abteilung", sa.String(100), nullable=True),
        sa.Column("letzter_einsatz", sa.DateTime(timezone=True), nullable=True),
        sa.Column("anzahl_auftraege", sa.Integer, default=0),
        sa.Column("aktiv", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_shared",
    )
    op.create_index("ix_schnell_tenant", "futtermittel_schnellerfassung",
                    ["tenant_id"], schema="domain_shared")


def downgrade() -> None:
    op.drop_table("futtermittel_schnellerfassung", schema="domain_shared")
    op.drop_index("ix_rezgrp_tenant_nr", "futtermittel_rezepturgruppen", schema="domain_shared")
    op.drop_table("futtermittel_rezepturgruppen", schema="domain_shared")
    op.drop_table("kontrakt_zuabschlaege", schema="domain_shared")
    op.drop_index("ix_ktrza_tenant_nr", "kontrakt_zuabschlagsgruppen", schema="domain_shared")
    op.drop_table("kontrakt_zuabschlagsgruppen", schema="domain_shared")
    op.drop_index("ix_ktrmengen_tenant_kontrakt", "kontrakt_mengenzeitraeume", schema="domain_shared")
    op.drop_table("kontrakt_mengenzeitraeume", schema="domain_shared")
