"""
Operations Domain Models Migration
Creates tables for Waage, Wiegung, Fahrzeug, Fahrer, FahrzeugTour, and Dokumente
"""

from typing import Optional
from alembic import op
import sqlalchemy as sa
from app.core.uuid7 import uuid7

# Revision identifiers
revision = "ops_domain_initial"
down_revision = "1368e3f15650"  # Update with your current revision
branch_labels = None
depends_on = None


def generate_uuid() -> str:
    return uuid7()


def upgrade():
    # Create domain_ops schema
    op.execute('CREATE SCHEMA IF NOT EXISTS domain_ops')
    
    # Create enum types if they don't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE waage_status AS ENUM ('aktiv', 'inaktiv', 'wartung', 'defekt');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE fahrzeug_status AS ENUM ('verfuegbar', 'unterwegs', 'wartung', 'ausgeschieden');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $body$ BEGIN
            CREATE TYPE fahrer_status AS ENUM ('verfuegbar', 'unterwegs', 'pause', 'urlaub', 'krank');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $body$;
    """)
    
    op.execute("""
        DO $body$ BEGIN
            CREATE TYPE dokument_status AS ENUM ('aktiv', 'geloescht', 'archiviert');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $body$;
    """)
    
    # Create ops_waagen table
    op.create_table(
        "ops_waagen",
        sa.Column("id", sa.String, primary_key=True, default=lambda: f"W-{uuid7()[:8].upper()}"),
        sa.Column("standort", sa.String(100), nullable=False),
        sa.Column("typ", sa.String(50), nullable=False),
        sa.Column("max_kapazitaet", sa.Float, nullable=False),
        sa.Column("letzte_eichung", sa.DateTime(timezone=True)),
        sa.Column("naechste_eichung", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20), default="aktiv"),
        sa.Column("hersteller", sa.String(100)),
        sa.Column("seriennummer", sa.String(50)),
        sa.Column("installiert_am", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("created_by", sa.String(100)),
        sa.Column("updated_by", sa.String(100)),
        schema="domain_ops"
    )
    
    # Create ops_wiegungen table
    op.create_table(
        "ops_wiegungen",
        sa.Column("id", sa.String, primary_key=True, default=lambda: f"WG-{uuid7()[:8].upper()}"),
        sa.Column("kennzeichen", sa.String(20), nullable=False),
        sa.Column("fahrer_name", sa.String(100)),
        sa.Column("artikel", sa.String(100), nullable=False),
        sa.Column("brutto", sa.Float, nullable=False),
        sa.Column("tara", sa.Float, nullable=False),
        sa.Column("netto", sa.Float, nullable=False),
        sa.Column("chargennummer", sa.String(50)),
        sa.Column("lieferant", sa.String(100)),
        sa.Column("kunde", sa.String(100)),
        sa.Column("zeitstempel", sa.DateTime(timezone=True), nullable=False),
        sa.Column("waage_id", sa.String, sa.ForeignKey("domain_ops.ops_waagen.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("created_by", sa.String(100)),
        schema="domain_ops"
    )
    
    # Create ops_fahrzeuge table
    op.create_table(
        "ops_fahrzeuge",
        sa.Column("id", sa.String, primary_key=True, default=lambda: f"F-{uuid7()[:8].upper()}"),
        sa.Column("kennzeichen", sa.String(20), nullable=False, unique=True),
        sa.Column("typ", sa.String(50), nullable=False),
        sa.Column("marke", sa.String(50)),
        sa.Column("modell", sa.String(50)),
        sa.Column("baujahr", sa.Integer),
        sa.Column("kilometerstand", sa.Float, default=0),
        sa.Column("versicherung", sa.String(100)),
        sa.Column("naechste_pruefung", sa.DateTime(timezone=True)),
        sa.Column("naechste_inspektion", sa.DateTime(timezone=True)),
        sa.Column("letzte_inspektion", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20), default="verfuegbar"),
        sa.Column("tank_groesse", sa.Float),
        sa.Column("aktueller_tank", sa.Float, default=0),
        sa.Column("zulassungsdatum", sa.DateTime(timezone=True)),
        sa.Column("abmeldedatum", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("created_by", sa.String(100)),
        sa.Column("updated_by", sa.String(100)),
        schema="domain_ops"
    )
    
    # Create ops_fahrer table
    op.create_table(
        "ops_fahrer",
        sa.Column("id", sa.String, primary_key=True, default=lambda: f"DR-{uuid7()[:8].upper()}"),
        sa.Column("personalnummer", sa.String(20), unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("vorname", sa.String(100)),
        sa.Column("geburtsdatum", sa.DateTime(timezone=True)),
        sa.Column("telefon", sa.String(50)),
        sa.Column("email", sa.String(200)),
        sa.Column("fuehrerschein", sa.String(10), nullable=False),
        sa.Column("fuehrerschein_gueltig_bis", sa.DateTime(timezone=True)),
        sa.Column("adr_bescheinigung", sa.Boolean, default=False),
        sa.Column("adr_gueltig_bis", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20), default="verfuegbar"),
        sa.Column("aktuelles_fahrzeug_id", sa.String, sa.ForeignKey("domain_ops.ops_fahrzeuge.id", ondelete="SET NULL")),
        sa.Column("touren_heute", sa.Integer, default=0),
        sa.Column("touren_woche", sa.Integer, default=0),
        sa.Column("kilometer_heute", sa.Float, default=0),
        sa.Column("verfuegbar_ab", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("created_by", sa.String(100)),
        sa.Column("updated_by", sa.String(100)),
        schema="domain_ops"
    )
    
    # Create ops_fahrzeug_touren table
    op.create_table(
        "ops_fahrzeug_touren",
        sa.Column("id", sa.String, primary_key=True, default=lambda: f"TOUR-{uuid7()[:8].upper()}"),
        sa.Column("fahrzeug_id", sa.String, sa.ForeignKey("domain_ops.ops_fahrzeuge.id", ondelete="CASCADE")),
        sa.Column("fahrer_id", sa.String, sa.ForeignKey("domain_ops.ops_fahrer.id", ondelete="SET NULL")),
        sa.Column("tour_nummer", sa.String(50)),
        sa.Column("start_zeit", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ende_zeit", sa.DateTime(timezone=True)),
        sa.Column("start_adresse", sa.Text),
        sa.Column("ziel_adresse", sa.Text),
        sa.Column("kilometer", sa.Float, default=0),
        sa.Column("status", sa.String(20), default="geplant"),
        sa.Column("artikel", sa.String(100)),
        sa.Column("menge", sa.Float),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("created_by", sa.String(100)),
        schema="domain_ops"
    )
    
    # Create indexes
    op.create_index("ix_ops_waagen_status", "ops_waagen", ["status"], schema="domain_ops")
    op.create_index("ix_ops_wiegungen_waage_id", "ops_wiegungen", ["waage_id"], schema="domain_ops")
    op.create_index("ix_ops_wiegungen_zeitstempel", "ops_wiegungen", ["zeitstempel"], schema="domain_ops")
    op.create_index("ix_ops_fahrzeuge_status", "ops_fahrzeuge", ["status"], schema="domain_ops")
    op.create_index("ix_ops_fahrzeuge_kennzeichen", "ops_fahrzeuge", ["kennzeichen"], schema="domain_ops")
    op.create_index("ix_ops_fahrer_status", "ops_fahrer", ["status"], schema="domain_ops")
    op.create_index("ix_ops_fahrer_fahrzeug_id", "ops_fahrer", ["aktuelles_fahrzeug_id"], schema="domain_ops")
    op.create_index("ix_ops_touren_fahrzeug_id", "ops_fahrzeug_touren", ["fahrzeug_id"], schema="domain_ops")
    op.create_index("ix_ops_touren_fahrer_id", "ops_fahrzeug_touren", ["fahrer_id"], schema="domain_ops")
    
    # Create ops_dokumente table
    op.create_table(
        "ops_dokumente",
        sa.Column("id", sa.String, primary_key=True, default=lambda: f"DOC-{uuid7()[:8].upper()}"),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("typ", sa.String(20), nullable=False),
        sa.Column("kategorie", sa.String(100), nullable=False),
        sa.Column("groesse", sa.Integer, default=0),
        sa.Column("speicherpfad", sa.String(500)),
        sa.Column("mime_type", sa.String(100)),
        sa.Column("beschreibung", sa.Text),
        sa.Column("schlagwoerter", sa.String(500)),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("referenz_typ", sa.String(50)),
        sa.Column("referenz_id", sa.String(100)),
        sa.Column("status", sa.String(20), default="aktiv"),
        sa.Column("hochgeladen_am", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("hochgeladen_von", sa.String(100)),
        sa.Column("geloescht_am", sa.DateTime(timezone=True)),
        sa.Column("geloescht_von", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("created_by", sa.String(100)),
        sa.Column("updated_by", sa.String(100)),
        schema="domain_ops"
    )
    
    # Create ops_dokument_versionen table
    op.create_table(
        "ops_dokument_versionen",
        sa.Column("id", sa.String, primary_key=True, default=lambda: f"VER-{uuid7()[:8].upper()}"),
        sa.Column("dokument_id", sa.String, sa.ForeignKey("domain_ops.ops_dokumente.id", ondelete="CASCADE")),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("groesse", sa.Integer, default=0),
        sa.Column("speicherpfad", sa.String(500)),
        sa.Column("aenderungsbemerkung", sa.Text),
        sa.Column("erstellt_am", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("erstellt_von", sa.String(100)),
        schema="domain_ops"
    )
    
    # Create Dokument indexes
    op.create_index("ix_ops_dokumente_status", "ops_dokumente", ["status"], schema="domain_ops")
    op.create_index("ix_ops_dokumente_kategorie", "ops_dokumente", ["kategorie"], schema="domain_ops")
    op.create_index("ix_ops_dokumente_typ", "ops_dokumente", ["typ"], schema="domain_ops")
    op.create_index("ix_ops_dokumente_referenz", "ops_dokumente", ["referenz_typ", "referenz_id"], schema="domain_ops")
    op.create_index("ix_ops_versionen_dokument_id", "ops_dokument_versionen", ["dokument_id"], schema="domain_ops")

    # Create ops_chargen table
    op.create_table(
        "ops_chargen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("chargen_id", sa.String(50), nullable=False, unique=True),
        sa.Column("artikel", sa.String(100), nullable=False),
        sa.Column("artikel_id", sa.String(100), nullable=False),
        sa.Column("menge", sa.Float, nullable=False),
        sa.Column("lagerort", sa.String(100), nullable=False),
        sa.Column("eingang", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), server_default="erfasst"),
        sa.Column("qualitaetsstatus", sa.String(30), server_default="in-pruefung"),
        sa.Column("freigabe_datum", sa.DateTime(timezone=True)),
        sa.Column("herkunft", sa.String(255)),
        sa.Column("bemerkungen", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("created_by", sa.String(100)),
        sa.Column("updated_by", sa.String(100)),
        schema="domain_ops",
    )
    op.create_index("ix_ops_chargen_status", "ops_chargen", ["status"], schema="domain_ops")
    op.create_index("ix_ops_chargen_lagerort", "ops_chargen", ["lagerort"], schema="domain_ops")

    # Create ops_bankkonten table
    op.create_table(
        "ops_bankkonten",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("iban", sa.String(50), nullable=False, unique=True),
        sa.Column("bic", sa.String(20), nullable=False),
        sa.Column("bank", sa.String(255), nullable=False),
        sa.Column("kontoart", sa.String(100), nullable=False),
        sa.Column("saldo", sa.Numeric(14, 2), server_default="0"),
        sa.Column("waehrung", sa.String(10), server_default="EUR"),
        sa.Column("status", sa.String(20), server_default="aktiv"),
        sa.Column("ist_aktiv", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("created_by", sa.String(100)),
        sa.Column("updated_by", sa.String(100)),
        schema="domain_ops",
    )
    op.create_index("ix_ops_bankkonten_status", "ops_bankkonten", ["status"], schema="domain_ops")
    op.create_index("ix_ops_bankkonten_kontoart", "ops_bankkonten", ["kontoart"], schema="domain_ops")

    # Create ops_rahmenvertraege table
    op.create_table(
        "ops_rahmenvertraege",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("nummer", sa.String(50), nullable=False, unique=True),
        sa.Column("partner", sa.String(255), nullable=False),
        sa.Column("partner_id", sa.String(100), nullable=False),
        sa.Column("typ", sa.String(50), nullable=False),
        sa.Column("artikel", sa.String(100), nullable=False),
        sa.Column("artikel_id", sa.String(100), nullable=False),
        sa.Column("menge", sa.Float, nullable=False),
        sa.Column("restmenge", sa.Float, nullable=False),
        sa.Column("preis", sa.Numeric(14, 2), nullable=False),
        sa.Column("laufzeit_bis", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(30), server_default="aktiv"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("created_by", sa.String(100)),
        sa.Column("updated_by", sa.String(100)),
        schema="domain_ops",
    )
    op.create_index("ix_ops_rahmenvertraege_status", "ops_rahmenvertraege", ["status"], schema="domain_ops")
    op.create_index("ix_ops_rahmenvertraege_typ", "ops_rahmenvertraege", ["typ"], schema="domain_ops")


def downgrade():
    # Drop tables in reverse order
    op.drop_table("ops_rahmenvertraege", schema="domain_ops")
    op.drop_table("ops_bankkonten", schema="domain_ops")
    op.drop_table("ops_chargen", schema="domain_ops")
    op.drop_table("ops_dokument_versionen", schema="domain_ops")
    op.drop_table("ops_dokumente", schema="domain_ops")
    op.drop_table("ops_fahrzeug_touren", schema="domain_ops")
    op.drop_table("ops_fahrer", schema="domain_ops")
    op.drop_table("ops_fahrzeuge", schema="domain_ops")
    op.drop_table("ops_wiegungen", schema="domain_ops")
    op.drop_table("ops_waagen", schema="domain_ops")
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS dokument_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS fahrer_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS fahrzeug_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS waage_status CASCADE;")
