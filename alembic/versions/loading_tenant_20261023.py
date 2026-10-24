"""Isolate legacy loading tours through their owning tenant.

Revision ID: loading_tenant_20261023
Revises: dms_inbox_tenant_20261022

Unattributed development rows remain unavailable as legacy-unassigned. Child
records inherit access through their tour; this migration invents no ownership.
"""

from alembic import op
import sqlalchemy as sa


revision = "loading_tenant_20261023"
down_revision = "dms_inbox_tenant_20261022"
branch_labels = None
depends_on = None

_SCHEMA = "domain_log"
_TABLE = "log_touren"
_SCOPED_UNIQUE = "uq_log_touren_tenant_tour_no"
_OLD_UNIQUE = "log_touren_tour_no_key"
_CHECK = "ck_log_touren_tenant_nonblank"


def _exists(conn) -> bool:
    return conn.execute(sa.text("SELECT to_regclass('domain_log.log_touren')")).scalar() is not None


def _unique_constraints(conn):
    return sa.inspect(conn).get_unique_constraints(_TABLE, schema=_SCHEMA)




def upgrade() -> None:
    conn = op.get_bind()
    if not _exists(conn):
        return
    op.execute("LOCK TABLE domain_log.log_touren IN ACCESS EXCLUSIVE MODE")
    columns = {column["name"]: column for column in sa.inspect(conn).get_columns(_TABLE, schema=_SCHEMA)}
    if "tenant_id" not in columns:
        op.add_column(_TABLE, sa.Column("tenant_id", sa.String(120), nullable=True), schema=_SCHEMA)
    else:
        column_type = columns["tenant_id"]["type"]
        if not isinstance(column_type, sa.String):
            raise RuntimeError("log_touren.tenant_id must be a character column; reconcile schema before migration")
        if conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM domain_log.log_touren WHERE length(tenant_id) > 120)")).scalar():
            raise RuntimeError("log_touren.tenant_id exceeds 120 characters; migration refuses truncation")
        op.alter_column(_TABLE, "tenant_id", type_=sa.String(120), schema=_SCHEMA)

    op.execute("UPDATE domain_log.log_touren SET tenant_id = 'legacy-unassigned' WHERE tenant_id IS NULL OR btrim(tenant_id) = ''")
    # New writers must explicitly provide trusted ownership, never a default.
    op.alter_column(_TABLE, "tenant_id", nullable=False, server_default=None, schema=_SCHEMA)
    checks = {item["name"] for item in sa.inspect(conn).get_check_constraints(_TABLE, schema=_SCHEMA)}
    if _CHECK not in checks:
        op.create_check_constraint(_CHECK, _TABLE, "btrim(tenant_id) <> ''", schema=_SCHEMA)

    constraints = _unique_constraints(conn)
    for constraint in constraints:
        if constraint["column_names"] == ["tour_no"]:
            if constraint["name"] != _OLD_UNIQUE:
                raise RuntimeError("Unexpected global tour number constraint; reconcile it explicitly before migration")
            op.drop_constraint(_OLD_UNIQUE, _TABLE, type_="unique", schema=_SCHEMA)
    scoped = next((item for item in constraints if item["name"] == _SCOPED_UNIQUE), None)
    if scoped is not None and scoped["column_names"] != ["tenant_id", "tour_no"]:
        raise RuntimeError("Unexpected definition of tenant tour number constraint")
    if scoped is None:
        op.create_unique_constraint(_SCOPED_UNIQUE, _TABLE, ["tenant_id", "tour_no"], schema=_SCHEMA)
    op.execute("CREATE INDEX IF NOT EXISTS ix_log_touren_tenant_date ON domain_log.log_touren (tenant_id, date)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_log_touren_tenant_status ON domain_log.log_touren (tenant_id, status)")


def downgrade() -> None:
    conn = op.get_bind()
    if not _exists(conn):
        return
    op.execute("LOCK TABLE domain_log.log_touren IN ACCESS EXCLUSIVE MODE")
    if conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM domain_log.log_touren GROUP BY tour_no HAVING count(*) > 1)")).scalar():
        raise RuntimeError("Cannot restore global tour number uniqueness: duplicate numbers exist; no rows were deleted")
    constraints = _unique_constraints(conn)
    old = next((item for item in constraints if item["name"] == _OLD_UNIQUE), None)
    if old is not None and old["column_names"] != ["tour_no"]:
        raise RuntimeError("Unexpected definition of legacy tour number constraint")
    if old is None:
        op.create_unique_constraint(_OLD_UNIQUE, _TABLE, ["tour_no"], schema=_SCHEMA)
    if any(item["name"] == _SCOPED_UNIQUE for item in constraints):
        op.drop_constraint(_SCOPED_UNIQUE, _TABLE, type_="unique", schema=_SCHEMA)
    op.execute("DROP INDEX IF EXISTS domain_log.ix_log_touren_tenant_status")
    op.execute("DROP INDEX IF EXISTS domain_log.ix_log_touren_tenant_date")
    columns = {column["name"] for column in sa.inspect(conn).get_columns(_TABLE, schema=_SCHEMA)}
    if "tenant_id" in columns:
        op.drop_column(_TABLE, "tenant_id", schema=_SCHEMA)
