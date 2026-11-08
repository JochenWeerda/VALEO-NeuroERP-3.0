"""Row-level security for the CRM master data (RLS domain slice crm).

Separate policies per command, named like P3/P5/P6 (docs/architecture/rls-domaenen-entscheidungsmatrix.md,
§3): business partners, credit limits, segments, contacts, farm profiles, opportunities and the merge
and ownership logs belong to one tenant; no shared 'system' rows are readable.

The tables of the services under ``services/*`` (activities, customers, farm_profiles, leads,
crm_activities, crm_leads, crm_opportunities) are not part of this slice: those services do not
verify the token yet and follow after that.

Children hang under their parent over ``(parent key, tenant_id)``: FK checks bypass RLS, so only the
key stops a child under a parent of another tenant, also when re-parenting, and a parent with
children cannot change tenant. The sixteen ``business_partner_*`` detail tables, the consent history
and the segment members had no tenant; they take it from their parent (backfilled, NOT NULL, default
from the context). ON DELETE behaviour is kept. ``crm_contact_consents`` and ``supplier_tax_profiles``
are already under RLS (P5); they only get the key, their policies stay as they are.
``business_partner_communities`` has no tenant and no rows (class D); members reach it with a
single-column key as before.

Rows without a tenant or with a placeholder ('', 'default', 'system') and children under a parent of
another tenant block the migration.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_crm_20261027"
down_revision = "rls_domain_sales_20261027"
branch_labels = None
depends_on = None

PARTNERS = "domain_crm.business_partners"
CONSENTS, CONSENT_HISTORY = "domain_crm.crm_contact_consents", "domain_crm.crm_contact_consent_history"
SEGMENTS, SEGMENT_MEMBERS = "domain_crm.crm_segments", "domain_crm.crm_segment_members"
CONTACTS, FARM_PROFILES = "public.crm_contacts", "public.crm_betriebsprofile"
CANCEL_REASONS, OPPORTUNITY = "domain_crm.cancellation_reason", "domain_crm.opportunity"
SUPPLIER_TAX = "domain_crm.supplier_tax_profiles"

# Partnerdetails mit dem ON DELETE ihres bisherigen Schluessels.
PARTNER_CHILDREN = {
    "addresses": "NO ACTION", "billing_configs": "NO ACTION", "community_members": "CASCADE",
    "contacts": "NO ACTION", "cooperative_memberships": "CASCADE", "cpd_accounts": "NO ACTION",
    "discount_items": "NO ACTION", "dispatch_media": "CASCADE", "email_distributions": "CASCADE",
    "instructions": "NO ACTION", "interest_settings": "CASCADE", "interface_profiles": "CASCADE",
    "price_agreements": "NO ACTION", "pricing_rules": "CASCADE", "profiles": "CASCADE",
}

POLICY_TABLES = (
    PARTNERS, "domain_crm.credit_limits", SEGMENTS, CANCEL_REASONS, OPPORTUNITY, CONTACTS, FARM_PROFILES,
    "public.crm_merge_log", "public.crm_ownership_log", "public.opportunities",
    *(f"domain_crm.business_partner_{name}" for name in PARTNER_CHILDREN), CONSENT_HISTORY, SEGMENT_MEMBERS,
)
NEW_TENANT_COLUMN = (*(f"domain_crm.business_partner_{name}" for name in PARTNER_CHILDREN),
                     CONSENT_HISTORY, SEGMENT_MEMBERS)
NULLABLE_TENANT = (CANCEL_REASONS, OPPORTUNITY, "public.crm_merge_log", "public.crm_ownership_log",
                   "public.opportunities")
# child, column, parent, parent key, ON DELETE
LINKS = (
    *((f"domain_crm.business_partner_{name}", "partner_id", PARTNERS, "partner_id", on_delete)
      for name, on_delete in PARTNER_CHILDREN.items()),
    (SUPPLIER_TAX, "supplier_id", PARTNERS, "partner_id", "NO ACTION"),
    (CONSENT_HISTORY, "consent_id", CONSENTS, "id", "CASCADE"),
    (SEGMENT_MEMBERS, "segment_id", SEGMENTS, "id", "CASCADE"),
    (FARM_PROFILES, "contact_id", CONTACTS, "id", "NO ACTION"),
    (OPPORTUNITY, "cancel_reason_id", CANCEL_REASONS, "cancel_reason_id", "NO ACTION"),
)
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


def _exists(bind, table: str) -> bool:
    return bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


def _name(table: str) -> str:
    return table.split(".")[1]


def _tenant_type(bind, table: str) -> str:
    return bind.execute(sa.text(
        "SELECT format_type(atttypid, atttypmod) FROM pg_attribute "
        "WHERE attrelid = to_regclass(:t) AND attname = 'tenant_id' AND NOT attisdropped"), {"t": table}).scalar()


def _single_fk(bind, child: str, column: str, parent: str) -> str | None:
    return bind.execute(sa.text(
        "SELECT k.conname FROM pg_constraint k JOIN pg_attribute a ON a.attrelid = k.conrelid "
        "AND a.attnum = k.conkey[1] WHERE k.contype = 'f' AND k.conrelid = to_regclass(:c) "
        "AND k.confrelid = to_regclass(:p) AND cardinality(k.conkey) = 1 AND a.attname = :col"),
        {"c": child, "p": parent, "col": column}).scalar()


def _enable(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({OWN})")


def _disable(table: str) -> None:
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")


def upgrade() -> None:
    bind = op.get_bind()
    links = [l for l in LINKS if _exists(bind, l[0]) and _exists(bind, l[2])]
    present = [t for t in POLICY_TABLES if _exists(bind, t)]
    locked = sorted(set(present) | {l[0] for l in links} | {l[2] for l in links})
    op.execute(f"LOCK TABLE {', '.join(locked)} IN ACCESS EXCLUSIVE MODE")

    for child, column, parent, key, _ in links:
        if child in NEW_TENANT_COLUMN:
            op.execute(f"ALTER TABLE {child} ADD COLUMN tenant_id {_tenant_type(bind, parent)}")
            op.execute(f"UPDATE {child} c SET tenant_id = p.tenant_id FROM {parent} p WHERE p.{key} = c.{column}")

    for table in present:
        unclear = bind.execute(sa.text(
            f"SELECT count(*) FROM {table} WHERE tenant_id IS NULL OR tenant_id IN ('', 'default', 'system')"
        )).scalar()
        if unclear:
            raise RuntimeError(
                f"{table}: {unclear} Zeilen ohne eindeutigen Mandanten; Herkunft klaeren, "
                "nicht pauschal zuordnen (rls-domaenen-entscheidungsmatrix.md)"
            )
    for table in NEW_TENANT_COLUMN + NULLABLE_TENANT:
        if table in present:
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET NOT NULL")
    for table in NEW_TENANT_COLUMN:
        if table in present:
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()")

    for child, column, parent, key, _ in links:
        foreign = bind.execute(sa.text(
            f"SELECT count(*) FROM {child} c JOIN {parent} p ON p.{key} = c.{column} "
            "WHERE p.tenant_id IS DISTINCT FROM c.tenant_id")).scalar()
        if foreign:
            raise RuntimeError(f"{child}: {foreign} Zeilen haengen an einem Eltern eines anderen Mandanten")
    for parent, key in sorted({(l[2], l[3]) for l in links}):
        op.execute(f"ALTER TABLE {parent} ADD CONSTRAINT uq_{_name(parent)}_{key}_tenant UNIQUE ({key}, tenant_id)")
    for child, column, parent, key, on_delete in links:
        old = _single_fk(bind, child, column, parent)
        if old:
            op.execute(f"ALTER TABLE {child} DROP CONSTRAINT {old}")
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT fk_{_name(child)}_{column}_tenant FOREIGN KEY ({column}, tenant_id) "
            f"REFERENCES {parent} ({key}, tenant_id) ON DELETE {on_delete}"
        )

    for table in present:
        _enable(table)


def downgrade() -> None:
    bind = op.get_bind()
    for table in POLICY_TABLES:
        if _exists(bind, table):
            _disable(table)
    for child, column, parent, key, on_delete in LINKS:
        if not (_exists(bind, child) and _exists(bind, parent)):
            continue
        op.execute(f"ALTER TABLE {child} DROP CONSTRAINT IF EXISTS fk_{_name(child)}_{column}_tenant")
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT {_name(child)}_{column}_fkey FOREIGN KEY ({column}) "
            f"REFERENCES {parent} ({key}) ON DELETE {on_delete}"
        )
    for parent, key in sorted({(l[2], l[3]) for l in LINKS}):
        if _exists(bind, parent):
            op.execute(f"ALTER TABLE {parent} DROP CONSTRAINT IF EXISTS uq_{_name(parent)}_{key}_tenant")
    for table in NEW_TENANT_COLUMN:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS tenant_id")
    for table in NULLABLE_TENANT:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id DROP NOT NULL")
