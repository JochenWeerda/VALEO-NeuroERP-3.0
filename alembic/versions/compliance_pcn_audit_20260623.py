"""DOM-COMPLIANCE-004: compliance_pcn_meldungen, pcn_status_log, vvvo/sachkunde registers, artikel_sperre_audit

Revision ID: compliance_pcn_audit_20260623
Revises: agrar_partie_settlement_20260623
Create Date: 2026-06-23
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "compliance_pcn_audit_20260623"
down_revision = "agrar_partie_settlement_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_compliance")

    op.create_table(
        "compliance_pcn_meldungen",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("meldung_nummer", sa.String(60), nullable=False, unique=True),
        sa.Column("artikel_id", sa.String(64), nullable=True),
        sa.Column("meldungstyp", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), server_default="DRAFT"),
        sa.Column("bemerkung", sa.Text, nullable=True),
        sa.Column("eingereicht_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column("abgeschlossen_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        schema="domain_compliance",
    )
    op.create_index("ix_pcn_meldungen_tenant", "compliance_pcn_meldungen", ["tenant_id"], schema="domain_compliance")

    op.create_table(
        "compliance_pcn_status_log",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("meldung_id", sa.String(36), nullable=False),
        sa.Column("old_status", sa.String(20)),
        sa.Column("new_status", sa.String(20)),
        sa.Column("operator", sa.String(100)),
        sa.Column("reason", sa.Text),
        sa.Column("tenant_id", sa.String(36)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        schema="domain_compliance",
    )
    op.create_index("ix_pcn_status_log_meldung", "compliance_pcn_status_log", ["meldung_id"], schema="domain_compliance")

    op.create_table(
        "compliance_vvvo_register",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("betrieb_name", sa.String(255), nullable=False),
        sa.Column("vvvo_nummer", sa.String(50), nullable=False),
        sa.Column("letzte_pruefung_am", sa.Date, nullable=True),
        sa.Column("naechste_pruefung_am", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        schema="domain_compliance",
    )
    op.create_index("ix_vvvo_register_tenant", "compliance_vvvo_register", ["tenant_id"], schema="domain_compliance")

    op.create_table(
        "compliance_sachkunde_register",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("mitarbeiter_name", sa.String(255), nullable=False),
        sa.Column("zertifikat_art", sa.String(100), nullable=False),
        sa.Column("zertifikat_nummer", sa.String(100)),
        sa.Column("ablauf_datum", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        schema="domain_compliance",
    )
    op.create_index("ix_sachkunde_register_tenant", "compliance_sachkunde_register", ["tenant_id"], schema="domain_compliance")

    op.create_table(
        "compliance_artikel_sperre_audit",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("artikel_id", sa.String(64), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("aktion", sa.String(20), nullable=False),
        sa.Column("operator", sa.String(100)),
        sa.Column("grund", sa.Text),
        sa.Column("nachweis_ref", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        schema="domain_compliance",
    )
    op.create_index(
        "ix_sperre_audit_artikel_tenant",
        "compliance_artikel_sperre_audit",
        ["artikel_id", "tenant_id"],
        schema="domain_compliance",
    )


def downgrade() -> None:
    op.drop_table("compliance_artikel_sperre_audit", schema="domain_compliance")
    op.drop_table("compliance_sachkunde_register", schema="domain_compliance")
    op.drop_table("compliance_vvvo_register", schema="domain_compliance")
    op.drop_table("compliance_pcn_status_log", schema="domain_compliance")
    op.drop_table("compliance_pcn_meldungen", schema="domain_compliance")
