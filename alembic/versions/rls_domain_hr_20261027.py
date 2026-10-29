"""Row-level security for domain_hr master data (RLS domain slice hr).

Separate policies per command, named like the corrected P3/P5/P6 policies
(docs/architecture/rls-domaenen-entscheidungsmatrix.md, §3): SELECT, UPDATE and DELETE
see only rows of the transaction's tenant, INSERT and the result of UPDATE must belong to
it. HR data is personal data of one tenant: no shared 'system' rows are readable.

Children that point at these tables (onboarding runs, training assignments, employments)
get a foreign key over ``(parent, tenant_id)``: FK checks bypass RLS, so only the key
stops a row from hanging under a checklist, course or person of another tenant, also
when it is re-parented. The children's own policies (P5) are not touched.

``person``/``employment`` had a nullable tenant; they become NOT NULL. Rows without a
tenant or with a placeholder ('', 'default', 'system') block the migration: their origin
has to be settled first. Tables missing on a database (person/employment exist only on
fresh installations) are skipped.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_hr_20261027"
down_revision = "rls_domain_pricing_20261027"
branch_labels = None
depends_on = None

TABLES = (
    "domain_hr.onboarding_checklists",
    "domain_hr.training_courses",
    "domain_hr.work_plan_assignments",
    "domain_hr.person",
    "domain_hr.employment",
)
NULLABLE_TENANT = ("domain_hr.person", "domain_hr.employment")
# child, child column, parent, parent key, old FK, parent UNIQUE, new FK, ON DELETE
LINKS = (
    ("domain_hr.onboarding_runs", "checklist_id", "domain_hr.onboarding_checklists", "id",
     "fk_hr_onboarding_runs_checklist", "uq_hr_onboarding_checklists_id_tenant",
     "fk_hr_onboarding_runs_checklist_tenant", "CASCADE"),
    ("domain_hr.training_assignments", "course_id", "domain_hr.training_courses", "id",
     "fk_hr_training_assignments_course", "uq_hr_training_courses_id_tenant",
     "fk_hr_training_assignments_course_tenant", "CASCADE"),
    ("domain_hr.employment", "person_id", "domain_hr.person", "person_id",
     "employment_person_id_fkey", "uq_hr_person_person_id_tenant",
     "fk_hr_employment_person_tenant", "NO ACTION"),
)
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
    links = [link for link in LINKS if _exists(bind, link[0]) and _exists(bind, link[2])]
    locked = sorted(set(present) | {link[0] for link in links})
    op.execute(f"LOCK TABLE {', '.join(locked)} IN ACCESS EXCLUSIVE MODE")

    for table in present:
        unclear = bind.execute(sa.text(
            f"SELECT count(*) FROM {table} WHERE tenant_id IS NULL OR tenant_id IN ('', 'default', 'system')"
        )).scalar()
        if unclear:
            raise RuntimeError(
                f"{table}: {unclear} Zeilen ohne eindeutigen Mandanten; Herkunft klaeren, "
                "nicht pauschal zuordnen (rls-domaenen-entscheidungsmatrix.md)"
            )
    for table in NULLABLE_TENANT:
        if table in present:
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET NOT NULL")

    for child, column, parent, key, old_fk, unique, new_fk, on_delete in links:
        foreign = bind.execute(sa.text(
            f"SELECT count(*) FROM {child} c JOIN {parent} p ON p.{key} = c.{column} "
            "WHERE p.tenant_id IS DISTINCT FROM c.tenant_id"
        )).scalar()
        if foreign:
            raise RuntimeError(f"{child}: {foreign} Zeilen haengen an einem Elternsatz eines anderen Mandanten")
        op.execute(f"ALTER TABLE {parent} ADD CONSTRAINT {unique} UNIQUE ({key}, tenant_id)")
        op.execute(f"ALTER TABLE {child} DROP CONSTRAINT IF EXISTS {old_fk}")
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT {new_fk} FOREIGN KEY ({column}, tenant_id) "
            f"REFERENCES {parent} ({key}, tenant_id) ON DELETE {on_delete}"
        )

    for table in present:
        _enable_tenant_policies(table)


def downgrade() -> None:
    bind = op.get_bind()
    for table in TABLES:
        if _exists(bind, table):
            _disable_tenant_policies(table)
    for child, column, parent, key, old_fk, unique, new_fk, on_delete in LINKS:
        if not (_exists(bind, child) and _exists(bind, parent)):
            continue
        op.execute(f"ALTER TABLE {child} DROP CONSTRAINT IF EXISTS {new_fk}")
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT {old_fk} FOREIGN KEY ({column}) "
            f"REFERENCES {parent} ({key}) ON DELETE {on_delete}"
        )
        op.execute(f"ALTER TABLE {parent} DROP CONSTRAINT IF EXISTS {unique}")
    for table in NULLABLE_TENANT:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id DROP NOT NULL")
