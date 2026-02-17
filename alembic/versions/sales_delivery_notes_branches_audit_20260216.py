"""Add sales delivery notes, branches, and audit attestations tables.

Revision ID: sales_delivery_notes_branches_audit_20260216
Revises: hr_personal_time_tracking_20260215
Create Date: 2026-02-16
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "sales_delivery_notes_branches_audit_20260216"
down_revision = "admin_report_permissions_20260215"
branch_labels = None
depends_on = None

DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    # Create schemas if they don't exist
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS domain_sales"))
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS domain_audit"))
    
    # 1. Niederlassungen (Branches) - domain_shared.branches
    op.create_table(
        "branches",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("branch_number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "branch_number", name="uq_branches_tenant_branch_number"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_branches_tenant_id",
        "branches",
        ["tenant_id"],
        unique=False,
        schema="domain_shared",
    )
    op.create_index(
        "ix_branches_branch_number",
        "branches",
        ["branch_number"],
        unique=False,
        schema="domain_shared",
    )
    
    # 2. Lieferscheine (Delivery Notes) - domain_sales.delivery_notes
    op.create_table(
        "delivery_notes",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("delivery_note_number", sa.String(length=50), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("sales_rep_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("operator_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("delivery_date", sa.Date(), nullable=False),
        sa.Column("delivery_time", sa.Time(), nullable=True),
        sa.Column("cost_center_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("truck_number", sa.Integer(), nullable=True),
        sa.Column("is_credit_note", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("is_self_pickup", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("is_early_payment", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("reference_invoice_number", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("is_printed", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("is_delivered", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("invoice_number", sa.String(length=50), nullable=True),
        sa.Column("totals", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["customer_id"], ["domain_crm.customers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["branch_id"], ["domain_shared.branches.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sales_rep_id"], ["domain_shared.users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["operator_id"], ["domain_shared.users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "delivery_note_number", name="uq_delivery_notes_tenant_number"),
        sa.CheckConstraint(
            "status IN ('draft', 'printed', 'delivered', 'invoiced', 'cancelled')",
            name="ck_delivery_notes_status",
        ),
        schema="domain_sales",
    )
    op.create_index(
        "ix_delivery_notes_tenant_id",
        "delivery_notes",
        ["tenant_id"],
        unique=False,
        schema="domain_sales",
    )
    op.create_index(
        "ix_delivery_notes_customer_id",
        "delivery_notes",
        ["customer_id"],
        unique=False,
        schema="domain_sales",
    )
    op.create_index(
        "ix_delivery_notes_delivery_note_number",
        "delivery_notes",
        ["delivery_note_number"],
        unique=False,
        schema="domain_sales",
    )
    op.create_index(
        "ix_delivery_notes_delivery_date",
        "delivery_notes",
        ["delivery_date"],
        unique=False,
        schema="domain_sales",
    )
    op.create_index(
        "ix_delivery_notes_status",
        "delivery_notes",
        ["status"],
        unique=False,
        schema="domain_sales",
    )
    
    # 3. Lieferschein-Positionen (Delivery Note Positions) - domain_sales.delivery_note_positions
    op.create_table(
        "delivery_note_positions",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("delivery_note_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("pos_nr", sa.Integer(), nullable=False),
        sa.Column("artikel_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("artikel_nr", sa.String(length=50), nullable=True),
        sa.Column("bezeichnung", sa.String(length=255), nullable=True),
        sa.Column("bezeichnung2", sa.String(length=255), nullable=True),
        sa.Column("menge", sa.Numeric(14, 3), nullable=False),
        sa.Column("einheit", sa.String(length=20), nullable=True),
        sa.Column("listenpreis", sa.Numeric(14, 4), nullable=True),
        sa.Column("rabatt", sa.Numeric(5, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("art", sa.String(length=50), nullable=True),
        sa.Column("netto_preis", sa.Numeric(14, 4), nullable=True),
        sa.Column("netto_betrag", sa.Numeric(14, 2), nullable=True),
        sa.Column("niederlassung", sa.Integer(), nullable=True),
        sa.Column("lagerhalle", sa.String(length=80), nullable=True),
        sa.Column("lagerfach", sa.String(length=80), nullable=True),
        sa.Column("charge", sa.String(length=80), nullable=True),
        sa.Column("serien_nr", sa.String(length=80), nullable=True),
        sa.Column("erloskonto", sa.String(length=20), nullable=True),
        sa.Column("mwst_prozent", sa.Numeric(5, 2), nullable=False, server_default=sa.text("19")),
        sa.Column("kontrakt_nr", sa.String(length=50), nullable=True),
        sa.Column("skontierf", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("fremdware", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ["delivery_note_id"],
            ["domain_sales.delivery_notes.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["artikel_id"],
            ["domain_inventory.articles.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("delivery_note_id", "pos_nr", name="uq_delivery_note_positions_pos_nr"),
        schema="domain_sales",
    )
    op.create_index(
        "ix_delivery_note_positions_delivery_note",
        "delivery_note_positions",
        ["delivery_note_id"],
        unique=False,
        schema="domain_sales",
    )
    op.create_index(
        "ix_delivery_note_positions_artikel",
        "delivery_note_positions",
        ["artikel_id"],
        unique=False,
        schema="domain_sales",
    )
    op.create_index(
        "ix_delivery_note_positions_artikel_nr",
        "delivery_note_positions",
        ["artikel_nr"],
        unique=False,
        schema="domain_sales",
    )
    
    # 4. Attestierungen (Audit Attestations) - domain_audit.attestations
    op.create_table(
        "attestations",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("changes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["domain_shared.users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["approved_by"], ["domain_shared.users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "action IN ('print', 'modify', 'cancel', 'post', 'reopen')",
            name="ck_attestations_action",
        ),
        schema="domain_audit",
    )
    op.create_index(
        "ix_attestations_entity",
        "attestations",
        ["entity_type", "entity_id"],
        unique=False,
        schema="domain_audit",
    )
    op.create_index(
        "ix_attestations_tenant_id",
        "attestations",
        ["tenant_id"],
        unique=False,
        schema="domain_audit",
    )
    op.create_index(
        "ix_attestations_created_at",
        "attestations",
        ["created_at"],
        unique=False,
        schema="domain_audit",
    )


def downgrade() -> None:
    op.drop_index("ix_attestations_created_at", table_name="attestations", schema="domain_audit")
    op.drop_index("ix_attestations_tenant_id", table_name="attestations", schema="domain_audit")
    op.drop_index("ix_attestations_entity", table_name="attestations", schema="domain_audit")
    op.drop_table("attestations", schema="domain_audit")
    
    op.drop_index("ix_delivery_note_positions_artikel_nr", table_name="delivery_note_positions", schema="domain_sales")
    op.drop_index("ix_delivery_note_positions_artikel", table_name="delivery_note_positions", schema="domain_sales")
    op.drop_index("ix_delivery_note_positions_delivery_note", table_name="delivery_note_positions", schema="domain_sales")
    op.drop_table("delivery_note_positions", schema="domain_sales")
    
    op.drop_index("ix_delivery_notes_status", table_name="delivery_notes", schema="domain_sales")
    op.drop_index("ix_delivery_notes_delivery_date", table_name="delivery_notes", schema="domain_sales")
    op.drop_index("ix_delivery_notes_delivery_note_number", table_name="delivery_notes", schema="domain_sales")
    op.drop_index("ix_delivery_notes_customer_id", table_name="delivery_notes", schema="domain_sales")
    op.drop_index("ix_delivery_notes_tenant_id", table_name="delivery_notes", schema="domain_sales")
    op.drop_table("delivery_notes", schema="domain_sales")
    
    op.drop_index("ix_branches_branch_number", table_name="branches", schema="domain_shared")
    op.drop_index("ix_branches_tenant_id", table_name="branches", schema="domain_shared")
    op.drop_table("branches", schema="domain_shared")

