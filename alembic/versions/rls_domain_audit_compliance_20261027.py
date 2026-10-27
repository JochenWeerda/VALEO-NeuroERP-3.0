"""Row-level security for audit attestations and compliance records (RLS domain slice).

Separate policies per command, named like the corrected P3/P5/P6 policies
(docs/architecture/rls-domaenen-entscheidungsmatrix.md, §3): SELECT, UPDATE and DELETE
see only rows of the transaction's tenant, INSERT and the result of UPDATE must belong to
it. Attestations, erasure requests (Art. 17 GDPR), Intrastat declarations and the PCN
status history are records of one tenant: no shared 'system' rows are readable.

The PCN status log had a nullable tenant and no key to its declaration. It becomes
NOT NULL and gets a foreign key over ``(meldung_id, tenant_id)`` to
``compliance_pcn_meldungen`` (FK checks bypass RLS, so only the key stops history rows
under a declaration of another tenant; NO ACTION, so a declaration with history cannot
vanish silently). The declaration table keeps its P5 policies.

Rows without a tenant or with a placeholder ('', 'default', 'system'), log rows without
their declaration and log rows under a declaration of another tenant block the migration:
their origin has to be settled first.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_audit_compliance_20261027"
down_revision = "rls_domain_hr_20261027"
branch_labels = None
depends_on = None

TABLES = (
    "domain_audit.attestations",
    "domain_compliance.compliance_pcn_status_log",
    "domain_compliance.data_erasure_requests",
    "domain_compliance.intrastat_meldungen",
)
LOG = "domain_compliance.compliance_pcn_status_log"
DECLARATIONS = "domain_compliance.compliance_pcn_meldungen"
UNIQUE = "uq_compliance_pcn_meldungen_id_tenant"
LOG_FK = "fk_compliance_pcn_status_log_meldung_tenant"
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
    link = LOG in present and _exists(bind, DECLARATIONS)
    op.execute(f"LOCK TABLE {', '.join(sorted(set(present) | ({DECLARATIONS} if link else set())))} "
               "IN ACCESS EXCLUSIVE MODE")

    for table in present:
        unclear = bind.execute(sa.text(
            f"SELECT count(*) FROM {table} WHERE tenant_id IS NULL OR tenant_id IN ('', 'default', 'system')"
        )).scalar()
        if unclear:
            raise RuntimeError(
                f"{table}: {unclear} Zeilen ohne eindeutigen Mandanten; Herkunft klaeren, "
                "nicht pauschal zuordnen (rls-domaenen-entscheidungsmatrix.md)"
            )

    if LOG in present:
        op.execute(f"ALTER TABLE {LOG} ALTER COLUMN tenant_id SET NOT NULL")
    if link:
        unmatched = bind.execute(sa.text(
            f"SELECT count(*) FROM {LOG} l LEFT JOIN {DECLARATIONS} m ON m.id = l.meldung_id "
            "WHERE m.id IS NULL OR m.tenant_id IS DISTINCT FROM l.tenant_id"
        )).scalar()
        if unmatched:
            raise RuntimeError(f"{LOG}: {unmatched} Zeilen ohne Meldung oder unter der Meldung eines anderen Mandanten")
        op.execute(f"ALTER TABLE {DECLARATIONS} ADD CONSTRAINT {UNIQUE} UNIQUE (id, tenant_id)")
        op.execute(
            f"ALTER TABLE {LOG} ADD CONSTRAINT {LOG_FK} FOREIGN KEY (meldung_id, tenant_id) "
            f"REFERENCES {DECLARATIONS} (id, tenant_id)"  # Verlauf ueberlebt keine stille Loeschung
        )

    for table in present:
        _enable_tenant_policies(table)


def downgrade() -> None:
    bind = op.get_bind()
    for table in TABLES:
        if _exists(bind, table):
            _disable_tenant_policies(table)
    if _exists(bind, LOG):
        op.execute(f"ALTER TABLE {LOG} DROP CONSTRAINT IF EXISTS {LOG_FK}")
        op.execute(f"ALTER TABLE {LOG} ALTER COLUMN tenant_id DROP NOT NULL")
    if _exists(bind, DECLARATIONS):
        op.execute(f"ALTER TABLE {DECLARATIONS} DROP CONSTRAINT IF EXISTS {UNIQUE}")
