"""UStVA Voranmeldungen Tabelle (§ 18 UStG ELSTER-Übertragung).

Revision ID: ustva_voranmeldungen_20260527
Revises: gis_geojson_schlag_20260527
Create Date: 2026-05-27

Speichert UStVA-Übermittlungen mit Kennzahlen, Zahllast und ELSTER-Ticket.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "ustva_voranmeldungen_20260527"
down_revision = "gis_geojson_schlag_20260527"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ustva_voranmeldungen",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("tenant_id", sa.String, nullable=False, index=True),
        sa.Column("steuernummer", sa.String(20), nullable=False),
        sa.Column("finanzamt_nr", sa.String(10), nullable=False),
        sa.Column("voranmeldungszeitraum", sa.String(20), nullable=False),
        sa.Column("zahllast_eur", sa.Numeric(15, 2), nullable=True),
        sa.Column("erstattung_eur", sa.Numeric(15, 2), nullable=True),
        sa.Column("elster_status", sa.String(20), nullable=True),
        sa.Column("transfer_ticket", sa.String(50), nullable=True),
        sa.Column("payload_json", postgresql.JSONB, nullable=True),
        sa.Column("erstellt_am", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="domain_finance",
    )
    op.create_index(
        "ix_ustva_tenant_zeitraum",
        "ustva_voranmeldungen",
        ["tenant_id", "voranmeldungszeitraum"],
        schema="domain_finance",
    )


def downgrade() -> None:
    op.drop_index("ix_ustva_tenant_zeitraum", table_name="ustva_voranmeldungen", schema="domain_finance")
    op.drop_table("ustva_voranmeldungen", schema="domain_finance")
