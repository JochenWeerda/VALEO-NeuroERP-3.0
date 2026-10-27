"""Row-level security for the evidence room (RLS domain slice nachweisraum).

Separate policies per command, named like the corrected P3/P5/P6 policies
(docs/architecture/rls-domaenen-entscheidungsmatrix.md, §3): SELECT, UPDATE and DELETE
see only rows of the transaction's tenant, INSERT and the result of UPDATE must belong to
it. Evidence documents and GoBD exports belong to one tenant: no shared 'system' rows.

The document audit log (already under P5 policies) had no key to its document. It gets a
foreign key over ``(dokument_id, tenant_id)``: FK checks bypass RLS, so only the key stops
audit rows under a document of another tenant. NO ACTION: a document with audit history
cannot vanish silently.

Rows without a tenant or with a placeholder ('', 'default', 'system'), audit rows without
their document and audit rows under a document of another tenant block the migration.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_nachweisraum_20261027"
down_revision = "rls_domain_audit_compliance_20261027"
branch_labels = None
depends_on = None

DOCUMENTS = "domain_nachweisraum.nachweisraum_dokumente"
EXPORTS = "domain_nachweisraum.gobd_exporte"
AUDIT = "domain_nachweisraum.nachweisraum_audit_log"
TABLES = (DOCUMENTS, EXPORTS)
UNIQUE = "uq_nachweisraum_dokumente_id_tenant"
AUDIT_FK = "fk_nachweisraum_audit_log_dokument_tenant"
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


def _exists(bind, table: str) -> bool:
    return bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


def _enable_tenant_policies(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({OWN})")


def _disable_tenant_policies(table: str) -> None:
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")


def upgrade() -> None:
    bind = op.get_bind()
    present = [t for t in TABLES if _exists(bind, t)]
    link = DOCUMENTS in present and _exists(bind, AUDIT)
    op.execute(f"LOCK TABLE {', '.join(present + ([AUDIT] if link else []))} IN ACCESS EXCLUSIVE MODE")

    for table in present:
        unclear = bind.execute(sa.text(
            f"SELECT count(*) FROM {table} WHERE tenant_id IS NULL OR tenant_id IN ('', 'default', 'system')"
        )).scalar()
        if unclear:
            raise RuntimeError(
                f"{table}: {unclear} Zeilen ohne eindeutigen Mandanten; Herkunft klaeren, "
                "nicht pauschal zuordnen (rls-domaenen-entscheidungsmatrix.md)"
            )
    if link:
        unmatched = bind.execute(sa.text(
            f"SELECT count(*) FROM {AUDIT} a LEFT JOIN {DOCUMENTS} d ON d.id = a.dokument_id "
            "WHERE d.id IS NULL OR d.tenant_id IS DISTINCT FROM a.tenant_id"
        )).scalar()
        if unmatched:
            raise RuntimeError(f"{AUDIT}: {unmatched} Zeilen ohne Dokument oder unter dem Dokument eines anderen Mandanten")
        op.execute(f"ALTER TABLE {DOCUMENTS} ADD CONSTRAINT {UNIQUE} UNIQUE (id, tenant_id)")
        op.execute(
            f"ALTER TABLE {AUDIT} ADD CONSTRAINT {AUDIT_FK} FOREIGN KEY (dokument_id, tenant_id) "
            f"REFERENCES {DOCUMENTS} (id, tenant_id)"
        )

    for table in present:
        _enable_tenant_policies(table)


def downgrade() -> None:
    bind = op.get_bind()
    for table in TABLES:
        if _exists(bind, table):
            _disable_tenant_policies(table)
    if _exists(bind, AUDIT):
        op.execute(f"ALTER TABLE {AUDIT} DROP CONSTRAINT IF EXISTS {AUDIT_FK}")
    if _exists(bind, DOCUMENTS):
        op.execute(f"ALTER TABLE {DOCUMENTS} DROP CONSTRAINT IF EXISTS {UNIQUE}")
