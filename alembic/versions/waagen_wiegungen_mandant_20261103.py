"""Waagen und Alt-Wiegungen im selben Mandantenmuster wie die uebrigen domain_ops-Tabellen.

Revision ID: waagen_wiegungen_mandant_20261103
Revises: rls_domain_ops_teil2_20261028

``waage_tenant_20261030`` hat ``ops_waagen`` eine Mandantenspalte gegeben, sie aber nullable gelassen (NOT-VALID-Check),
damit Altzeilen unbekannter Herkunft nicht geraten werden. ``ops_wiegungen`` blieb ohne Mandant; ihre Wege antworten
seit der Abloesung durch die Wiegescheine mit 410. Nutzerauftrag 03.11.2026: Waage homogen zu den uebrigen ops-Tabellen
(RLS-Domain ops Teil 1/2).

- ``ops_waagen.tenant_id``: NOT NULL, Vorgabe aus dem Kontext, Pruefbedingung validiert, ``(id, tenant_id)`` eindeutig.
- ``ops_wiegungen.tenant_id``: aus der Waage nachgezogen, NOT NULL, Verbundschluessel ``(waage_id, tenant_id)`` zur
  Waage (FK-Pruefungen umgehen RLS; nur der Schluessel verhindert den Verweis auf eine fremde Waage).
- Beide mit getrennter Policy je Befehl.

Beide Tabellen sind auf Pruefstand und gewachsener Datenbank leer. Eine Zeile ohne ableitbaren Mandanten bricht die
Migration ab, statt pauschal zugeordnet zu werden - dieselbe Regel wie Teil 2 und wie der Waagen-Sicherheitsvertrag.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "waagen_wiegungen_mandant_20261103"
down_revision = "rls_domain_ops_teil2_20261028"
branch_labels = None
depends_on = None

WAAGEN = "domain_ops.ops_waagen"
WIEGUNGEN = "domain_ops.ops_wiegungen"
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


def _exists(bind, table: str) -> bool:
    return bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


def _has_column(bind, table: str, column: str) -> bool:
    return bind.execute(sa.text(
        "SELECT 1 FROM pg_attribute WHERE attrelid = to_regclass(:t) AND attname = :c AND NOT attisdropped"),
        {"t": table, "c": column}).scalar() is not None


def _has_constraint(bind, table: str, name: str) -> bool:
    return bind.execute(sa.text("SELECT 1 FROM pg_constraint WHERE conrelid = to_regclass(:t) AND conname = :n"),
                        {"t": table, "n": name}).scalar() is not None


def _foreign_keys(bind, table: str, column: str, parent: str) -> list[str]:
    return list(bind.execute(sa.text(
        "SELECT k.conname FROM pg_constraint k WHERE k.conrelid = to_regclass(:t) AND k.contype = 'f' "
        "AND k.confrelid = to_regclass(:p) AND (SELECT array_agg(a.attname::text) FROM pg_attribute a "
        "WHERE a.attrelid = k.conrelid AND a.attnum = ANY(k.conkey)) = ARRAY[CAST(:c AS text)]"),
        {"t": table, "p": parent, "c": column}).scalars().all())


def _enable(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({OWN})")


def upgrade() -> None:
    bind = op.get_bind()
    if not (_exists(bind, WAAGEN) and _exists(bind, WIEGUNGEN)):
        return
    op.execute(f"LOCK TABLE {WAAGEN}, {WIEGUNGEN} IN ACCESS EXCLUSIVE MODE")

    offen = bind.execute(sa.text(
        f"SELECT count(*) FROM {WAAGEN} WHERE tenant_id IS NULL OR btrim(tenant_id) = ''")).scalar()  # nosec B608
    if offen:
        raise RuntimeError(f"{WAAGEN}: {offen} Waagen ohne Mandanten; Herkunft klaeren, nicht pauschal zuordnen")
    op.execute(f"ALTER TABLE {WAAGEN} ALTER COLUMN tenant_id TYPE character varying(120)")
    op.execute(f"ALTER TABLE {WAAGEN} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()")
    op.execute(f"ALTER TABLE {WAAGEN} ALTER COLUMN tenant_id SET NOT NULL")
    if _has_constraint(bind, WAAGEN, "ck_ops_waagen_tenant_nonblank"):
        op.execute(f"ALTER TABLE {WAAGEN} VALIDATE CONSTRAINT ck_ops_waagen_tenant_nonblank")
    if not _has_constraint(bind, WAAGEN, "uq_ops_waagen_id_tenant"):
        op.execute(f"ALTER TABLE {WAAGEN} ADD CONSTRAINT uq_ops_waagen_id_tenant UNIQUE (id, tenant_id)")

    if not _has_column(bind, WIEGUNGEN, "tenant_id"):
        op.execute(f"ALTER TABLE {WIEGUNGEN} ADD COLUMN tenant_id character varying(120)")
    op.execute(f"""UPDATE {WIEGUNGEN} w SET tenant_id = a.tenant_id FROM {WAAGEN} a
                   WHERE w.tenant_id IS NULL AND w.waage_id = a.id""")  # nosec B608
    ohne = bind.execute(sa.text(f"SELECT count(*) FROM {WIEGUNGEN} WHERE tenant_id IS NULL")).scalar()  # nosec B608
    if ohne:
        raise RuntimeError(f"{WIEGUNGEN}: {ohne} Wiegungen ohne Waage und Mandant; Herkunft klaeren, nicht pauschal zuordnen")
    op.execute(f"ALTER TABLE {WIEGUNGEN} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()")
    op.execute(f"ALTER TABLE {WIEGUNGEN} ALTER COLUMN tenant_id SET NOT NULL")
    op.execute(f"CREATE INDEX IF NOT EXISTS ix_ops_wiegungen_tenant_id ON {WIEGUNGEN} (tenant_id)")
    for alt in _foreign_keys(bind, WIEGUNGEN, "waage_id", WAAGEN):
        op.execute(f"ALTER TABLE {WIEGUNGEN} DROP CONSTRAINT {alt}")
    op.execute(f"ALTER TABLE {WIEGUNGEN} ADD CONSTRAINT fk_ops_wiegungen_waage_id_tenant FOREIGN KEY (waage_id, tenant_id) "
               f"REFERENCES {WAAGEN} (id, tenant_id) ON DELETE SET NULL (waage_id)")

    _enable(WAAGEN)
    _enable(WIEGUNGEN)


def downgrade() -> None:
    bind = op.get_bind()
    if not (_exists(bind, WAAGEN) and _exists(bind, WIEGUNGEN)):
        return
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {WIEGUNGEN}")
    op.execute(f"ALTER TABLE {WIEGUNGEN} DISABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {WIEGUNGEN} DROP CONSTRAINT IF EXISTS fk_ops_wiegungen_waage_id_tenant")
    op.execute(f"ALTER TABLE {WIEGUNGEN} ADD CONSTRAINT ops_wiegungen_waage_id_fkey FOREIGN KEY (waage_id) "
               f"REFERENCES {WAAGEN} (id) ON DELETE SET NULL")
    op.execute("DROP INDEX IF EXISTS domain_ops.ix_ops_wiegungen_tenant_id")
    op.execute(f"ALTER TABLE {WIEGUNGEN} DROP COLUMN IF EXISTS tenant_id")
    # Waagen behalten Mandant und Policies (Stand waage_tenant_20261030); nur die Verschaerfung faellt.
    op.execute(f"ALTER TABLE {WAAGEN} DROP CONSTRAINT IF EXISTS uq_ops_waagen_id_tenant")
    op.execute(f"ALTER TABLE {WAAGEN} ALTER COLUMN tenant_id DROP NOT NULL")
    op.execute(f"ALTER TABLE {WAAGEN} ALTER COLUMN tenant_id DROP DEFAULT")
