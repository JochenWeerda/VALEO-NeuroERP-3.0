"""Append-only harvest rule, measurement, calculation and approval journal."""
from alembic import op

revision = "harvest_rule_store_20261015"
down_revision = "portal_lohndienst_persistenz_20261014"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE domain_inventory.harvest_control_events (
            event_no BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            id VARCHAR(36) NOT NULL UNIQUE,
            tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
            aggregate_id VARCHAR(150) NOT NULL,
            kind VARCHAR(40) NOT NULL CHECK (kind IN (
                'rule.created', 'rule.approved', 'rule.revoked', 'measurement.attested',
                'rule.bound', 'calculation.completed', 'calculation.approved', 'release.completed')),
            actor VARCHAR(255) NOT NULL CHECK (length(trim(actor)) > 0),
            idempotency_key VARCHAR(36) NOT NULL,
            request_hash CHAR(64) NOT NULL,
            payload JSONB NOT NULL CHECK (jsonb_typeof(payload) = 'object'),
            recorded_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
            UNIQUE (tenant_id, idempotency_key)
        );
        CREATE INDEX ix_harvest_control_aggregate
            ON domain_inventory.harvest_control_events (tenant_id, aggregate_id, kind, event_no DESC);
        CREATE FUNCTION domain_inventory.reject_harvest_control_mutation() RETURNS trigger
        LANGUAGE plpgsql AS $$ BEGIN
            RAISE EXCEPTION 'Harvest control evidence is append-only' USING ERRCODE = '23514';
        END $$;
        CREATE TRIGGER harvest_control_no_mutation BEFORE UPDATE OR DELETE
            ON domain_inventory.harvest_control_events FOR EACH ROW
            EXECUTE FUNCTION domain_inventory.reject_harvest_control_mutation();
        CREATE TRIGGER harvest_control_no_truncate BEFORE TRUNCATE
            ON domain_inventory.harvest_control_events FOR EACH STATEMENT
            EXECUTE FUNCTION domain_inventory.reject_harvest_control_mutation();
    """)


def downgrade():
    raise RuntimeError("Immutable business evidence requires an explicit retention/migration procedure.")
