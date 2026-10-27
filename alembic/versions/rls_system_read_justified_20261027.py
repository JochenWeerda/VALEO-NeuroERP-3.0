"""Shared 'system' rows readable only where justified (RLS, system-wide).

P3/P5/P6 (corrected in 943ba2bb0) let every tenant read rows of the shared tenant 'system'
on all 501 tables they cover. The finding of 27.10.2026 (docs/admin/rls-system-read.json,
scripts/rls_system_read.py) shows that no code path reads 'system' rows of these tables:
every reader filters on its own tenant. 'system' rows exist only in
``domain_erp.booking_templates`` (70 templates, grown database, unused by the code),
``domain_finance.aufbewahrungsfristen`` (5 seeds of a fresh install; the GoBD view seeds
per tenant) and ``domain_erp.journal_entries`` (one integration-test posting).

So ``tenant_isolation_select`` becomes ``tenant_id = rls_current_tenant()`` on these tables,
except where docs/admin/rls-exceptions.json -> ``system_lesbar`` gives a reason
(``KEEP_SYSTEM_READ``, empty at the time of writing). Insert, update and delete policies
are unchanged. No row is changed or deleted; 'system' rows stay where they are, unseen by
tenants and readable for the owner and valeo_system.

The table lists are those of the three migrations, read from their files on purpose: they
are frozen there, and the downgrade must restore exactly what they created.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import sqlalchemy as sa

from alembic import op

revision = "rls_system_read_justified_20261027"
down_revision = "rls_domain_nachweisraum_20261027"
branch_labels = None
depends_on = None

SOURCES = (
    ("rls_pilot_finance_20261026", "PILOT_TABLES"),
    ("rls_rollout_20261026", "ROLLOUT_TABLES"),
    ("rls_system_role_20261026", "SYSTEM_ROLE_TABLES"),
)
# Tables whose readers need shared 'system' rows; each needs a reason in
# docs/admin/rls-exceptions.json -> system_lesbar.
KEEP_SYSTEM_READ: tuple[str, ...] = ()


def _covered_tables() -> list[str]:
    tables: list[str] = []
    for name, constant in SOURCES:
        path = Path(__file__).with_name(f"{name}.py")
        spec = importlib.util.spec_from_file_location(f"_rls_source_{name}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        tables.extend(getattr(module, constant))
    return [t for t in dict.fromkeys(tables) if t not in KEEP_SYSTEM_READ]


def _column(bind, table: str) -> str | None:
    schema, name = table.split(".")
    data_type = bind.execute(sa.text(
        "SELECT data_type FROM information_schema.columns "
        "WHERE table_schema = :s AND table_name = :n AND column_name = 'tenant_id'"), {"s": schema, "n": name}).scalar()
    if data_type is None:
        return None
    return "tenant_id::text" if data_type == "uuid" else "tenant_id"


def _replace_select(read_system: bool) -> None:
    bind = op.get_bind()
    for table in _covered_tables():
        if bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is None:
            continue
        column = _column(bind, table)
        if column is None:
            continue
        owned = f"{column} = public.rls_current_tenant()"
        using = f"{owned} OR ({column} = 'system' AND public.rls_current_tenant() IS NOT NULL)" if read_system else owned
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_select ON {table}")
        op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({using})")


def upgrade() -> None:
    _replace_select(read_system=False)


def downgrade() -> None:
    _replace_select(read_system=True)
