"""Wave 106: Operations CRUD — Versicherungen, Wartung/Anlagen, Tankstelle/Zapfungen,
Verladung, Projekte, E2E-Ketten, EDI-Nachrichten, Price-Hedges, Zertifikate-API

Revision ID: ops_wave106_operations_crud_20260519
Revises: warehouse_wms_structure_20260517
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "ops_wave106_operations_crud_20260519"
down_revision = "warehouse_wms_structure_20260517"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Schema sicherstellen ──────────────────────────────────────────────────
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_ops")

    # ── Versicherungen ────────────────────────────────────────────────────────
    op.create_table(
        "ops_versicherungen",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("art", sa.String(120), nullable=False),
        sa.Column("versicherer", sa.String(255), nullable=False),
        sa.Column("vertragsnummer", sa.String(120), nullable=False),
        sa.Column("praemie", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("waehrung", sa.String(10), server_default="EUR"),
        sa.Column("zahlungsweise", sa.String(30), server_default="jaehrlich"),
        sa.Column("ablauf", sa.DateTime(timezone=True), nullable=True),
        sa.Column("beginn", sa.DateTime(timezone=True), nullable=True),
        sa.Column("selbstbehalt", sa.Numeric(14, 2), nullable=True),
        sa.Column("versicherungssumme", sa.Numeric(14, 2), nullable=True),
        sa.Column("ansprechpartner", sa.String(255), nullable=True),
        sa.Column("telefon", sa.String(80), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("notiz", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), server_default="aktiv"),
        sa.Column("tenant_id", sa.String(120), nullable=False, server_default="default"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("updated_by", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vertragsnummer"),
        schema="domain_ops",
    )
    op.create_index("ix_ops_versicherungen_tenant", "ops_versicherungen", ["tenant_id"], schema="domain_ops")

    # ── Wartung / Anlagen ──────────────────────────────────────────────────────
    op.create_table(
        "ops_wartung_anlagen",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("typ", sa.String(120), nullable=False),
        sa.Column("standort", sa.String(255), nullable=False),
        sa.Column("hersteller", sa.String(255), nullable=True),
        sa.Column("seriennummer", sa.String(120), nullable=True),
        sa.Column("baujahr", sa.Integer(), nullable=True),
        sa.Column("letzte_wartung", sa.DateTime(timezone=True), nullable=True),
        sa.Column("naechste_wartung", sa.DateTime(timezone=True), nullable=True),
        sa.Column("wartungsintervall_monate", sa.Integer(), server_default="6"),
        sa.Column("verantwortlicher", sa.String(255), nullable=True),
        sa.Column("notiz", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), server_default="aktiv"),
        sa.Column("tenant_id", sa.String(120), nullable=False, server_default="default"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("updated_by", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_ops",
    )
    op.create_index("ix_ops_wartung_anlagen_tenant", "ops_wartung_anlagen", ["tenant_id"], schema="domain_ops")

    op.create_table(
        "ops_wartungs_protokolle",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("anlage_id", sa.String(), nullable=False),
        sa.Column("datum", sa.DateTime(timezone=True), nullable=False),
        sa.Column("art", sa.String(120), nullable=False),
        sa.Column("beschreibung", sa.Text(), nullable=True),
        sa.Column("techniker", sa.String(255), nullable=True),
        sa.Column("kosten", sa.Numeric(14, 2), nullable=True),
        sa.Column("naechste_faellig", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tenant_id", sa.String(120), nullable=False, server_default="default"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(["anlage_id"], ["domain_ops.ops_wartung_anlagen.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_ops",
    )
    op.create_index("ix_ops_wartungs_protokolle_anlage", "ops_wartungs_protokolle", ["anlage_id"], schema="domain_ops")

    # ── Tankstelle / Zapfungen ─────────────────────────────────────────────────
    op.create_table(
        "ops_zapfungen",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("kennzeichen", sa.String(30), nullable=False),
        sa.Column("fahrzeug_id", sa.String(), nullable=True),
        sa.Column("fahrer", sa.String(255), nullable=True),
        sa.Column("fahrer_id", sa.String(), nullable=True),
        sa.Column("artikel", sa.String(120), nullable=False),
        sa.Column("menge", sa.Float(), nullable=False),
        sa.Column("kilometer_stand", sa.Float(), nullable=True),
        sa.Column("zapfsaeule", sa.String(50), nullable=True),
        sa.Column("preis_liter", sa.Numeric(10, 4), nullable=True),
        sa.Column("gesamtpreis", sa.Numeric(14, 2), nullable=True),
        sa.Column("zeitstempel", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notiz", sa.Text(), nullable=True),
        sa.Column("tenant_id", sa.String(120), nullable=False, server_default="default"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_ops",
    )
    op.create_index("ix_ops_zapfungen_kennzeichen", "ops_zapfungen", ["kennzeichen"], schema="domain_ops")
    op.create_index("ix_ops_zapfungen_tenant", "ops_zapfungen", ["tenant_id"], schema="domain_ops")

    op.create_table(
        "ops_tank_bestand",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artikel", sa.String(120), nullable=False),
        sa.Column("bestand_liter", sa.Float(), nullable=False, server_default="0"),
        sa.Column("kapazitaet_liter", sa.Float(), nullable=False, server_default="0"),
        sa.Column("min_bestand", sa.Float(), server_default="0"),
        sa.Column("letzte_befuellung", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tenant_id", sa.String(120), nullable=False, server_default="default"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("artikel"),
        schema="domain_ops",
    )

    # ── Verladung ──────────────────────────────────────────────────────────────
    op.create_table(
        "ops_verladungen",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("kennzeichen", sa.String(30), nullable=False),
        sa.Column("fahrzeug_id", sa.String(), nullable=True),
        sa.Column("fahrer", sa.String(255), nullable=True),
        sa.Column("artikel", sa.String(255), nullable=False),
        sa.Column("artikel_id", sa.String(100), nullable=True),
        sa.Column("menge", sa.Float(), nullable=False),
        sa.Column("einheit", sa.String(20), server_default="t"),
        sa.Column("lieferschein_nr", sa.String(80), nullable=True),
        sa.Column("lieferschein_id", sa.String(100), nullable=True),
        sa.Column("kunde", sa.String(255), nullable=True),
        sa.Column("kunde_id", sa.String(100), nullable=True),
        sa.Column("ladeort", sa.String(255), nullable=True),
        sa.Column("zielort", sa.String(255), nullable=True),
        sa.Column("geplanter_zeitslot", sa.DateTime(timezone=True), nullable=True),
        sa.Column("beginn_verladung", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ende_verladung", sa.DateTime(timezone=True), nullable=True),
        sa.Column("datum", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(30), server_default="geplant"),
        sa.Column("notiz", sa.Text(), nullable=True),
        sa.Column("tenant_id", sa.String(120), nullable=False, server_default="default"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("updated_by", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_ops",
    )
    op.create_index("ix_ops_verladungen_lieferschein", "ops_verladungen", ["lieferschein_nr"], schema="domain_ops")
    op.create_index("ix_ops_verladungen_tenant", "ops_verladungen", ["tenant_id"], schema="domain_ops")

    # ── Projekte ───────────────────────────────────────────────────────────────
    op.create_table(
        "ops_projekte",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("beschreibung", sa.Text(), nullable=True),
        sa.Column("projektleiter", sa.String(255), nullable=True),
        sa.Column("kunde", sa.String(255), server_default="intern"),
        sa.Column("kunde_id", sa.String(100), nullable=True),
        sa.Column("startdatum", sa.DateTime(timezone=True), nullable=True),
        sa.Column("enddatum", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fortschritt", sa.Integer(), server_default="0"),
        sa.Column("budget", sa.Numeric(14, 2), server_default="0"),
        sa.Column("ausgaben", sa.Numeric(14, 2), server_default="0"),
        sa.Column("kostenstelle", sa.String(80), nullable=True),
        sa.Column("status", sa.String(30), server_default="geplant"),
        sa.Column("prioritaet", sa.String(20), server_default="normal"),
        sa.Column("notiz", sa.Text(), nullable=True),
        sa.Column("tenant_id", sa.String(120), nullable=False, server_default="default"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("updated_by", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_ops",
    )
    op.create_index("ix_ops_projekte_tenant", "ops_projekte", ["tenant_id"], schema="domain_ops")

    op.create_table(
        "ops_projekt_aufgaben",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("projekt_id", sa.String(), nullable=False),
        sa.Column("titel", sa.String(255), nullable=False),
        sa.Column("beschreibung", sa.Text(), nullable=True),
        sa.Column("verantwortlicher", sa.String(255), nullable=True),
        sa.Column("faellig_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column("erledigt_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(30), server_default="offen"),
        sa.Column("tenant_id", sa.String(120), nullable=False, server_default="default"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["projekt_id"], ["domain_ops.ops_projekte.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_ops",
    )
    op.create_index("ix_ops_projekt_aufgaben_projekt", "ops_projekt_aufgaben", ["projekt_id"], schema="domain_ops")

    # ── E2E-Prozessketten ─────────────────────────────────────────────────────
    op.create_table(
        "process_e2e_chains",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(120), nullable=False),
        sa.Column("ernte_annahme_id", sa.String(120), nullable=True),
        sa.Column("qualitaets_protokoll_id", sa.String(120), nullable=True),
        sa.Column("settlement_id", sa.String(120), nullable=True),
        sa.Column("contract_id", sa.String(120), nullable=True),
        sa.Column("lager_buchung_id", sa.String(120), nullable=True),
        sa.Column("ap_invoice_id", sa.String(120), nullable=True),
        sa.Column("chain_data", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("is_complete", sa.Boolean(), server_default="false"),
        sa.Column("completeness_pct", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_ops",
    )
    op.create_index("ix_process_e2e_chains_tenant", "process_e2e_chains", ["tenant_id"], schema="domain_ops")
    op.create_index("ix_process_e2e_chains_settlement", "process_e2e_chains", ["settlement_id"], schema="domain_ops")
    op.create_index("ix_process_e2e_chains_contract", "process_e2e_chains", ["contract_id"], schema="domain_ops")

    # ── EDI-Nachrichten und Partner ────────────────────────────────────────────
    op.create_table(
        "edi_nachrichten",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("nachricht_id", sa.String(120), nullable=False),
        sa.Column("typ", sa.String(50), nullable=False),
        sa.Column("absender_gln", sa.String(50), nullable=False),
        sa.Column("empfaenger_gln", sa.String(50), nullable=False),
        sa.Column("interchange_control_ref", sa.String(120), nullable=True),
        sa.Column("empfangen_am", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload_raw", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), server_default="verarbeitet"),
        sa.Column("fehler_beschreibung", sa.Text(), nullable=True),
        sa.Column("dokument_id", sa.String(120), nullable=True),
        sa.Column("tenant_id", sa.String(120), nullable=False, server_default="default"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nachricht_id"),
        schema="domain_ops",
    )
    op.create_index("ix_edi_nachrichten_tenant", "edi_nachrichten", ["tenant_id"], schema="domain_ops")

    op.create_table(
        "edi_partner",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("partner_id", sa.String(120), nullable=False),
        sa.Column("gln", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("tenant_id", sa.String(120), nullable=False),
        sa.Column("aktive_nachrichtentypen", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("partner_id"),
        sa.UniqueConstraint("gln"),
        schema="domain_ops",
    )
    op.create_index("ix_edi_partner_tenant", "edi_partner", ["tenant_id"], schema="domain_ops")

    # ── Price Hedges ───────────────────────────────────────────────────────────
    op.create_table(
        "price_hedges",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("hedge_id", sa.String(120), nullable=False),
        sa.Column("tenant_id", sa.String(120), nullable=False),
        sa.Column("kontrakt_id", sa.String(120), nullable=True),
        sa.Column("produkt", sa.String(50), nullable=False),
        sa.Column("typ", sa.String(30), nullable=False),
        sa.Column("menge_t", sa.Float(), nullable=False),
        sa.Column("basis_preis_eur_t", sa.Numeric(14, 4), nullable=False),
        sa.Column("aktueller_preis_eur_t", sa.Numeric(14, 4), nullable=True),
        sa.Column("verfall_datum", sa.DateTime(timezone=True), nullable=True),
        sa.Column("broker_referenz", sa.String(120), nullable=True),
        sa.Column("status", sa.String(30), server_default="aktiv"),
        sa.Column("pnl_eur", sa.Numeric(14, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hedge_id"),
        schema="domain_ops",
    )
    op.create_index("ix_price_hedges_tenant", "price_hedges", ["tenant_id"], schema="domain_ops")
    op.create_index("ix_price_hedges_kontrakt", "price_hedges", ["kontrakt_id"], schema="domain_ops")

    # ── Zertifikate API (Wave-9 Store) ─────────────────────────────────────────
    op.create_table(
        "ops_zertifikate_api",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("zertifikat_id", sa.String(120), nullable=False),
        sa.Column("tenant_id", sa.String(120), nullable=False),
        sa.Column("typ", sa.String(80), nullable=False),
        sa.Column("zertifizierungsstelle", sa.String(255), nullable=False),
        sa.Column("gueltig_von", sa.DateTime(timezone=True), nullable=False),
        sa.Column("gueltig_bis", sa.DateTime(timezone=True), nullable=False),
        sa.Column("zertifikatsnummer", sa.String(120), nullable=True),
        sa.Column("status", sa.String(30), server_default="gueltig"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("zertifikat_id"),
        schema="domain_ops",
    )
    op.create_index("ix_ops_zertifikate_api_tenant", "ops_zertifikate_api", ["tenant_id"], schema="domain_ops")


def downgrade() -> None:
    op.drop_table("ops_zertifikate_api", schema="domain_ops")
    op.drop_table("price_hedges", schema="domain_ops")
    op.drop_table("edi_partner", schema="domain_ops")
    op.drop_table("edi_nachrichten", schema="domain_ops")
    op.drop_table("process_e2e_chains", schema="domain_ops")
    op.drop_table("ops_projekt_aufgaben", schema="domain_ops")
    op.drop_table("ops_projekte", schema="domain_ops")
    op.drop_table("ops_verladungen", schema="domain_ops")
    op.drop_table("ops_tank_bestand", schema="domain_ops")
    op.drop_table("ops_zapfungen", schema="domain_ops")
    op.drop_table("ops_wartungs_protokolle", schema="domain_ops")
    op.drop_table("ops_wartung_anlagen", schema="domain_ops")
    op.drop_table("ops_versicherungen", schema="domain_ops")
