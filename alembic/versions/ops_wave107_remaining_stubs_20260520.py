"""ops_wave107_remaining_stubs — DB tables for critical in-memory stores

Revision ID: ops_wave107_remaining_stubs_20260520
Revises: 31b00be545af
Create Date: 2026-05-20

Covered:
- domain_ops.agent_contexts
- domain_agrar.ernte_kampagnen
- domain_ops.reklamationen
- domain_ops.betriebs_kennzahlen
- domain_agrar.silo_zellen
- domain_agrar.silo_bewegungen
- domain_ops.pricing_sources
- domain_agrar.saatgut_partien  (saatzucht.py fallback table)
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "ops_wave107_remaining_stubs_20260520"
down_revision = "31b00be545af"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── agent_contexts ────────────────────────────────────────────────────────
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_ops")
    op.create_table(
        "agent_contexts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("context_id", sa.String(120), nullable=False, unique=True),
        sa.Column("agent_id", sa.String(120), nullable=False),
        sa.Column("tenant_id", sa.String(120), nullable=False),
        sa.Column("delegated_roles", JSONB, nullable=True),
        sa.Column("context_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("widerrufen", sa.Boolean, default=False),
        sa.Column("erstellt_am", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_ops",
    )
    op.create_index("ix_agent_contexts_tenant", "agent_contexts", ["tenant_id"], schema="domain_ops")
    op.create_index("ix_agent_contexts_agent", "agent_contexts", ["agent_id"], schema="domain_ops")

    # ── ernte_kampagnen ───────────────────────────────────────────────────────
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")
    op.create_table(
        "ernte_kampagnen",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("kampagne_id", sa.String(120), nullable=False, unique=True),
        sa.Column("tenant_id", sa.String(120), nullable=False),
        sa.Column("wirtschaftsjahr", sa.Integer, nullable=False),
        sa.Column("ernte_art", sa.String(40), nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("status", sa.String(30), default="geplant"),
        sa.Column("schlag_ziele", JSONB, nullable=True),
        sa.Column("erstellt_am", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_agrar",
    )
    op.create_index("ix_ernte_kampagnen_tenant", "ernte_kampagnen", ["tenant_id"], schema="domain_agrar")

    # ── reklamationen ─────────────────────────────────────────────────────────
    op.create_table(
        "reklamationen",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("reklamation_id", sa.String(120), nullable=False, unique=True),
        sa.Column("tenant_id", sa.String(120), nullable=False),
        sa.Column("lieferant_id", sa.String(120), nullable=False),
        sa.Column("typ", sa.String(60), nullable=False),
        sa.Column("positionen", JSONB, nullable=True),
        sa.Column("zustaendiger", sa.String(255), nullable=False),
        sa.Column("frist_datum", sa.Date, nullable=False),
        sa.Column("kontrakt_id", sa.String(120), nullable=True),
        sa.Column("status", sa.String(30), default="offen"),
        sa.Column("crm_referenz", JSONB, nullable=True),
        sa.Column("dms_referenzen", JSONB, nullable=True),
        sa.Column("gobd_beleg_id", sa.String(120), nullable=True),
        sa.Column("audit_trail", JSONB, nullable=True),
        sa.Column("erstellt_am", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_ops",
    )
    op.create_index("ix_reklamationen_tenant", "reklamationen", ["tenant_id"], schema="domain_ops")
    op.create_index("ix_reklamationen_lieferant", "reklamationen", ["lieferant_id"], schema="domain_ops")

    # ── betriebs_kennzahlen ───────────────────────────────────────────────────
    op.create_table(
        "betriebs_kennzahlen",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("kz_id", sa.String(120), nullable=False, unique=True),
        sa.Column("tenant_id", sa.String(120), nullable=False),
        sa.Column("kz_name", sa.String(120), nullable=False),
        sa.Column("einheit", sa.String(30), nullable=False),
        sa.Column("wert", sa.DECIMAL(18, 4), nullable=False),
        sa.Column("periode", sa.String(20), nullable=False),
        sa.Column("berechnet_am", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_ops",
    )
    op.create_index("ix_betriebs_kennzahlen_tenant", "betriebs_kennzahlen", ["tenant_id"], schema="domain_ops")
    op.create_index("ix_betriebs_kennzahlen_periode", "betriebs_kennzahlen", ["periode"], schema="domain_ops")

    # ── silo_zellen ───────────────────────────────────────────────────────────
    op.create_table(
        "silo_zellen",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("silo_id", sa.String(120), nullable=False, unique=True),
        sa.Column("tenant_id", sa.String(120), nullable=False),
        sa.Column("bezeichnung", sa.String(255), nullable=False),
        sa.Column("kapazitaet_t", sa.DECIMAL(14, 3), nullable=False),
        sa.Column("bestand_t", sa.DECIMAL(14, 3), nullable=False, default=0),
        sa.Column("sorte", sa.String(120), nullable=True),
        sa.Column("gesperrt", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_agrar",
    )
    op.create_index("ix_silo_zellen_tenant", "silo_zellen", ["tenant_id"], schema="domain_agrar")

    # ── silo_bewegungen ───────────────────────────────────────────────────────
    op.create_table(
        "silo_bewegungen",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("bewegung_id", sa.String(120), nullable=False, unique=True),
        sa.Column("silo_id", sa.String(120), sa.ForeignKey("domain_agrar.silo_zellen.silo_id"), nullable=False),
        sa.Column("typ", sa.String(20), nullable=False),
        sa.Column("menge_t", sa.DECIMAL(14, 3), nullable=False),
        sa.Column("sorte", sa.String(120), nullable=True),
        sa.Column("beleg_nr", sa.String(120), nullable=True),
        sa.Column("zeitpunkt", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_agrar",
    )
    op.create_index("ix_silo_bewegungen_silo", "silo_bewegungen", ["silo_id"], schema="domain_agrar")

    # ── pricing_sources ───────────────────────────────────────────────────────
    op.create_table(
        "pricing_sources",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("source_id", sa.String(120), nullable=False),
        sa.Column("tenant_id", sa.String(120), nullable=False),
        sa.Column("source_data", JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_ops",
    )
    op.create_index("ix_pricing_sources_tenant", "pricing_sources", ["tenant_id"], schema="domain_ops")

    # ── saatgut_partien (saatzucht.py fallback) ───────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_agrar.saatgut_partien (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            partie_nr TEXT NOT NULL,
            sorte_bezeichnung TEXT NOT NULL,
            art_code TEXT NOT NULL,
            z_stufe TEXT NOT NULL,
            vermehrungsbetrieb TEXT NOT NULL,
            anbauflaeche_ha NUMERIC(10,4) NOT NULL,
            saatgutmenge_kg NUMERIC(14,3) NOT NULL,
            keimfaehigkeit_prozent NUMERIC(5,2),
            sortenreinheit_prozent NUMERIC(5,2),
            tkg_gramm NUMERIC(8,2),
            anerkennungsnr TEXT,
            anerkennungsdatum DATE,
            status TEXT NOT NULL DEFAULT 'ANBAU',
            erstellt_am TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_saatgut_partien_tenant ON domain_agrar.saatgut_partien(tenant_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_agrar.saatgut_partien")
    op.execute("DROP TABLE IF EXISTS domain_agrar.silo_bewegungen")
    op.execute("DROP TABLE IF EXISTS domain_agrar.silo_zellen")
    op.execute("DROP TABLE IF EXISTS domain_agrar.ernte_kampagnen")
    op.execute("DROP TABLE IF EXISTS domain_ops.pricing_sources")
    op.execute("DROP TABLE IF EXISTS domain_ops.betriebs_kennzahlen")
    op.execute("DROP TABLE IF EXISTS domain_ops.reklamationen")
    op.execute("DROP TABLE IF EXISTS domain_ops.agent_contexts")
