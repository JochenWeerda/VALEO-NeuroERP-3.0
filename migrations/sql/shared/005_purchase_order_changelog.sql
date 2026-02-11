-- Purchase Order Change Log
-- GoBD-compliant audit trail for all PO modifications
-- Immutable: INSERT only, no UPDATE/DELETE allowed

CREATE TABLE IF NOT EXISTS purchase_order_changelog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purchase_order_id UUID NOT NULL REFERENCES purchase_orders(id),
    purchase_order_number VARCHAR(50) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    change_type VARCHAR(50) NOT NULL CHECK (change_type IN (
        'CREATED', 'STATUS_CHANGED', 'ITEMS_MODIFIED', 'HEADER_MODIFIED',
        'APPROVED', 'ORDERED', 'PARTIALLY_DELIVERED', 'DELIVERED',
        'CANCELLED', 'REVERTED'
    )),
    version INTEGER NOT NULL DEFAULT 1,
    user_id VARCHAR(128) NOT NULL,
    user_name VARCHAR(256),
    reason TEXT,
    field_changes JSONB NOT NULL DEFAULT '[]',
    snapshot JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_po_changelog_po_id ON purchase_order_changelog(purchase_order_id);
CREATE INDEX IF NOT EXISTS idx_po_changelog_tenant ON purchase_order_changelog(tenant_id);
CREATE INDEX IF NOT EXISTS idx_po_changelog_created ON purchase_order_changelog(created_at);
CREATE INDEX IF NOT EXISTS idx_po_changelog_change_type ON purchase_order_changelog(change_type);

-- Prevent any UPDATE or DELETE on changelog (GoBD compliance)
CREATE OR REPLACE FUNCTION prevent_changelog_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Change log entries are immutable (GoBD compliance). UPDATE/DELETE not allowed.';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_prevent_changelog_update ON purchase_order_changelog;
CREATE TRIGGER trg_prevent_changelog_update
    BEFORE UPDATE OR DELETE ON purchase_order_changelog
    FOR EACH ROW
    EXECUTE FUNCTION prevent_changelog_modification();

COMMENT ON TABLE purchase_order_changelog IS 'GoBD-compliant immutable change log for purchase orders';

