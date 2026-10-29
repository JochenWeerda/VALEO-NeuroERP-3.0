"""Row-level security for the AI domain: agent proposals, tool executions, knowledge versions.

Separate policies per command, named like P3/P5/P6 (docs/architecture/rls-domaenen-entscheidungsmatrix.md,
§3). Agent proposals and MCP tool executions (idempotency records with results) belong to one
tenant: no shared 'system' rows are readable. The services already filter on the verified
tenant (mcp_execution_service, sales_credit_notes, agent_proposal_repository).

Knowledge versions had no tenant; the tenant came only from their knowledge object. They now
carry the tenant of their object (backfilled, NOT NULL, default from the context) with a key over
``(knowledge_id, tenant_id)``: a version cannot hang under an object of another tenant, also not by
re-pointing it, and an object with versions cannot change tenant. Versions belong to the same
family as the objects: shared product knowledge ('system') is readable for every tenant
(docs/admin/rls-exceptions.json -> system_lesbar), changing it stays with central maintenance.

Rows without a tenant or with a placeholder ('', 'default'; for the two tenant-owned tables
also 'system') block the migration.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_ki_20261027"
down_revision = "rls_verified_agrar_20261027"
branch_labels = None
depends_on = None

PROPOSALS = "public.agent_proposals"
EXECUTIONS = "public.mcp_tool_executions"
OBJECTS = "domain_shared.knowledge_objects"
VERSIONS = "domain_shared.knowledge_versions"
OWN = "tenant_id::text = public.rls_current_tenant()"
SHARED = f"{OWN} OR (tenant_id::text = 'system' AND public.rls_current_tenant() IS NOT NULL)"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


def _exists(bind, table: str) -> bool:
    return bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


def _policies(table: str, select_using: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({select_using})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({OWN})")


def _drop_policies(table: str) -> None:
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")


def _unclear(bind, table: str, placeholders: str) -> int:
    return bind.execute(sa.text(
        f"SELECT count(*) FROM {table} WHERE tenant_id IS NULL OR tenant_id::text IN ({placeholders})")).scalar()


def upgrade() -> None:
    bind = op.get_bind()
    owned = [t for t in (PROPOSALS, EXECUTIONS) if _exists(bind, t)]
    versions = _exists(bind, VERSIONS) and _exists(bind, OBJECTS)
    locked = owned + ([OBJECTS, VERSIONS] if versions else [])
    if locked:
        op.execute(f"LOCK TABLE {', '.join(locked)} IN ACCESS EXCLUSIVE MODE")

    for table in owned:
        if _unclear(bind, table, "'', 'default', 'system'"):
            raise RuntimeError(f"{table}: Zeilen ohne eindeutigen Mandanten; Herkunft klaeren, nicht pauschal zuordnen")
        _policies(table, OWN)

    if versions:
        if _unclear(bind, OBJECTS, "'', 'default'"):
            raise RuntimeError(f"{OBJECTS}: Zeilen ohne eindeutigen Mandanten")
        op.execute(f"ALTER TABLE {VERSIONS} ADD COLUMN tenant_id character varying")
        op.execute(f"UPDATE {VERSIONS} v SET tenant_id = o.tenant_id FROM {OBJECTS} o WHERE o.knowledge_id = v.knowledge_id")
        orphans = bind.execute(sa.text(f"SELECT count(*) FROM {VERSIONS} WHERE tenant_id IS NULL")).scalar()
        if orphans:
            raise RuntimeError(f"{VERSIONS}: {orphans} Versionen ohne Wissensobjekt")
        op.execute(f"ALTER TABLE {VERSIONS} ALTER COLUMN tenant_id SET NOT NULL")
        op.execute(f"ALTER TABLE {VERSIONS} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()")
        op.execute(f"ALTER TABLE {OBJECTS} ADD CONSTRAINT uq_knowledge_objects_id_tenant UNIQUE (knowledge_id, tenant_id)")
        old = bind.execute(sa.text(
            "SELECT conname FROM pg_constraint WHERE contype = 'f' AND conrelid = to_regclass(:c) "
            "AND confrelid = to_regclass(:p) AND cardinality(conkey) = 1"), {"c": VERSIONS, "p": OBJECTS}).scalar()
        if old:
            op.execute(f"ALTER TABLE {VERSIONS} DROP CONSTRAINT {old}")
        op.execute(
            f"ALTER TABLE {VERSIONS} ADD CONSTRAINT fk_knowledge_versions_knowledge_tenant "
            f"FOREIGN KEY (knowledge_id, tenant_id) REFERENCES {OBJECTS} (knowledge_id, tenant_id) ON DELETE CASCADE"
        )
        _policies(VERSIONS, SHARED)


def downgrade() -> None:
    bind = op.get_bind()
    if _exists(bind, VERSIONS) and _exists(bind, OBJECTS):
        _drop_policies(VERSIONS)
        op.execute(f"ALTER TABLE {VERSIONS} DROP CONSTRAINT IF EXISTS fk_knowledge_versions_knowledge_tenant")
        op.execute(
            f"ALTER TABLE {VERSIONS} ADD CONSTRAINT knowledge_versions_knowledge_id_fkey "
            f"FOREIGN KEY (knowledge_id) REFERENCES {OBJECTS} (knowledge_id) ON DELETE CASCADE"
        )
        op.execute(f"ALTER TABLE {OBJECTS} DROP CONSTRAINT IF EXISTS uq_knowledge_objects_id_tenant")
        op.execute(f"ALTER TABLE {VERSIONS} DROP COLUMN IF EXISTS tenant_id")
    for table in (PROPOSALS, EXECUTIONS):
        if _exists(bind, table):
            _drop_policies(table)
