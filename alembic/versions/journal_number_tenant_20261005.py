"""Journal numbers identify entries within a tenant, never across tenants."""
from alembic import op
from sqlalchemy import inspect, text

revision = "journal_number_tenant_20261005"
down_revision = "kontrakt_disposition_20261005"
branch_labels = None
depends_on = None


def apply_contract(conn, schema="domain_erp"):
    quote = conn.dialect.identifier_preparer.quote
    table = f"{quote(schema)}.journal_entries"
    # Missing tenants cannot be repaired by inventing ownership.
    conn.execute(text(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET NOT NULL"))
    constraints = inspect(conn).get_unique_constraints("journal_entries", schema=schema)
    # Install the stronger tenant contract before removing the global constraint.
    if not any(c["column_names"] == ["tenant_id", "entry_number"] for c in constraints):
        conn.execute(text(f"ALTER TABLE {table} ADD CONSTRAINT uq_journal_tenant_number UNIQUE (tenant_id, entry_number)"))
    for constraint in constraints:
        if constraint["column_names"] == ["entry_number"]:
            conn.execute(text(f"ALTER TABLE {table} DROP CONSTRAINT {quote(constraint['name'])}"))


def upgrade():
    apply_contract(op.get_bind())


def downgrade():
    conn = op.get_bind()
    # A collision across tenants rejects rollback atomically; no data is deleted.
    conn.execute(text("ALTER TABLE domain_erp.journal_entries ADD CONSTRAINT journal_entries_entry_number_key UNIQUE (entry_number)"))
    conn.execute(text("ALTER TABLE domain_erp.journal_entries DROP CONSTRAINT uq_journal_tenant_number"))
    conn.execute(text("ALTER TABLE domain_erp.journal_entries ALTER COLUMN tenant_id DROP NOT NULL"))
