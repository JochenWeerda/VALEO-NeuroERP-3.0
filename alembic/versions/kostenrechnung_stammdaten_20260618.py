"""Kostenrechnung: Kostenstellen-Stammdaten + Kostenarten

Revision ID: kostenrechnung_stammdaten_20260618
Revises: fuhrpark_vertiefung_20260616
Create Date: 2026-06-18

Tables added:
  domain_finance.kostenstellen
  domain_finance.kostenarten
  domain_finance.kostenstellen_buchungen
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "kostenrechnung_stammdaten_20260618"
down_revision = "fuhrpark_vertiefung_20260616"
branch_labels = None
depends_on = None


def _table_exists(inspector, tablename: str, schema: str = "domain_finance") -> bool:
    return tablename in inspector.get_table_names(schema=schema)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    op.execute("CREATE SCHEMA IF NOT EXISTS domain_finance")

    # ── kostenstellen ─────────────────────────────────────────────────────────
    if not _table_exists(inspector, "kostenstellen"):
        op.create_table(
            "kostenstellen",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), nullable=False),
            sa.Column("nummer", sa.String(20), nullable=False),
            sa.Column("bezeichnung", sa.String(200), nullable=False),
            sa.Column(
                "kostenstelle_art",
                sa.String(50),
                nullable=False,
                server_default="'KOSTENSTELLE'",
            ),  # KOSTENSTELLE | KOSTENTRAEGER | PROJEKT | ABTEILUNG
            sa.Column("uebergeordnet", sa.String(36), nullable=True),
            sa.Column("verantwortlicher", sa.String(100), nullable=True),
            sa.Column("budget", sa.Numeric(16, 2), nullable=True),
            sa.Column("budget_periode", sa.String(20), nullable=True),  # MONAT|QUARTAL|JAHR
            sa.Column("aktiv", sa.Boolean, nullable=False, server_default=sa.text("true")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            schema="domain_finance",
        )
        op.create_index("ix_kostenstellen_tenant_id", "kostenstellen", ["tenant_id"], schema="domain_finance")
        op.create_index("ix_kostenstellen_nummer", "kostenstellen", ["tenant_id", "nummer"], unique=True, schema="domain_finance")

    # ── kostenarten ───────────────────────────────────────────────────────────
    if not _table_exists(inspector, "kostenarten"):
        op.create_table(
            "kostenarten",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), nullable=False),
            sa.Column("nummer", sa.String(20), nullable=False),
            sa.Column("bezeichnung", sa.String(200), nullable=False),
            sa.Column(
                "kostenart_gruppe",
                sa.String(50),
                nullable=False,
                server_default="'SONSTIGE'",
            ),  # PERSONAL | MATERIAL | ABSCHREIBUNG | FREMDLEISTUNG | ENERGIE | SONSTIGE
            sa.Column("konto_nr", sa.String(20), nullable=True),  # FiBu-Gegenkonto
            sa.Column("aktiv", sa.Boolean, nullable=False, server_default=sa.text("true")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            schema="domain_finance",
        )
        op.create_index("ix_kostenarten_tenant_id", "kostenarten", ["tenant_id"], schema="domain_finance")
        op.create_index("ix_kostenarten_nummer", "kostenarten", ["tenant_id", "nummer"], unique=True, schema="domain_finance")

    # ── kostenstellen_buchungen ───────────────────────────────────────────────
    if not _table_exists(inspector, "kostenstellen_buchungen"):
        op.create_table(
            "kostenstellen_buchungen",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), nullable=False),
            sa.Column(
                "kostenstelle_id",
                sa.String(36),
                sa.ForeignKey("domain_finance.kostenstellen.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("kostenart_id", sa.String(36), nullable=True),
            sa.Column("buchungsdatum", sa.Date, nullable=False),
            sa.Column("betrag_eur", sa.Numeric(16, 2), nullable=False),
            sa.Column("buchungstext", sa.String(255), nullable=True),
            sa.Column("belegnummer", sa.String(50), nullable=True),
            sa.Column("periode", sa.String(7), nullable=False),  # "2026-06"
            sa.Column("erstellt_von", sa.String(120), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            schema="domain_finance",
        )
        op.create_index("ix_kst_buchungen_kostenstelle", "kostenstellen_buchungen", ["kostenstelle_id"], schema="domain_finance")
        op.create_index("ix_kst_buchungen_periode", "kostenstellen_buchungen", ["tenant_id", "periode"], schema="domain_finance")
        op.create_index("ix_kst_buchungen_datum", "kostenstellen_buchungen", ["buchungsdatum"], schema="domain_finance")


def downgrade() -> None:
    op.drop_table("kostenstellen_buchungen", schema="domain_finance")
    op.drop_table("kostenarten", schema="domain_finance")
    op.drop_table("kostenstellen", schema="domain_finance")
