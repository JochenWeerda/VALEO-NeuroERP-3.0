"""merge heads sales_orders_items_shipping and consignment_storage_fee_engine

Revision ID: merge_sales_orders_and_consignment_20260215
Revises: sales_orders_items_shipping_20260215, consignment_storage_fee_engine_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations


revision = "merge_sales_orders_and_consignment_20260215"
down_revision = ("sales_orders_items_shipping_20260215", "consignment_storage_fee_engine_20260215")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
