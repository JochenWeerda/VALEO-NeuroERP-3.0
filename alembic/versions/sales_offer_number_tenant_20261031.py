"""Scope active offer numbers to their tenant without changing historical data.

Revision ID: sales_offer_number_tenant_20261031
Revises: waage_tenant_20261030
"""
from alembic import op
import sqlalchemy as sa

revision = "sales_offer_number_tenant_20261031"
down_revision = "waage_tenant_20261030"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    # Build the stronger active-record invariant before removing the legacy
    # global namespace. No tenant, offer or historical row is rewritten.
    indexes = inspector.get_indexes("sales_offers", schema="domain_crm")
    name = "uq_sales_offers_active_tenant_number"
    if not any(index["name"] == name for index in indexes):
        op.create_index(name, "sales_offers", ["tenant_id", "offer_number"],
                        unique=True, schema="domain_crm",
                        postgresql_where=sa.text("deleted_at IS NULL"))
    for constraint in inspector.get_unique_constraints("sales_offers", schema="domain_crm"):
        if constraint["column_names"] in (["offer_number"], ["tenant_id", "offer_number"]):
            op.drop_constraint(constraint["name"], "sales_offers", schema="domain_crm", type_="unique")


def downgrade():
    # Restoring the old global namespace could reject valid cross-tenant data.
    # Refuse that destructive semantic downgrade explicitly.
    raise RuntimeError("Offer number tenant scoping requires a reviewed data-aware downgrade")
