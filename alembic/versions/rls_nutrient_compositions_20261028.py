"""Row-level security for domain_agrar.nutrient_compositions (Naehrstoffgehalte der Duengemittel).

Revision ID: rls_nutrient_compositions_20261028
Revises: crm_leads_spalten_20261028

Bis 28.10.2026 nahm der einzige Schreiber (``nutrient_compositions.py``) den Mandanten aus ``?tenant_id=`` bzw. dem
Rumpf mit dem Standardmandanten als Rueckfall; das war der Grund, die Tabelle zurueckzustellen. Jetzt kommt er aus dem
Token: getrennte Policies je Befehl, kein 'system'-Lesen (live 0 Zeilen), Vorgabe aus dem Kontext.

``domain_inventory.articles.duengemittel_inhalte_id`` verweist ueber ``(id, tenant_id)``; FK-Pruefungen umgehen RLS,
nur der Verbundschluessel verhindert den Verweis eines Artikels auf die Naehrstoffe eines anderen Mandanten.
SET NULL leert nur die Verweisspalte.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_nutrient_compositions_20261028"
down_revision = "crm_leads_spalten_20261028"
branch_labels = None
depends_on = None

T = "domain_agrar.nutrient_compositions"
ARTIKEL = "domain_inventory.articles"
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


def _exists(bind, table: str) -> bool:
    return bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


def upgrade() -> None:
    bind = op.get_bind()
    if not _exists(bind, T):
        return
    op.execute(f"LOCK TABLE {T}, {ARTIKEL} IN ACCESS EXCLUSIVE MODE")
    unklar = bind.execute(sa.text(
        f"SELECT count(*) FROM {T} WHERE tenant_id IS NULL OR tenant_id IN ('', 'default', 'system', 'legacy-unassigned')")).scalar()
    if unklar:
        raise RuntimeError(f"{T}: {unklar} Zeilen ohne eindeutigen Mandanten; Herkunft klaeren")
    fremd = bind.execute(sa.text(
        f"SELECT count(*) FROM {ARTIKEL} a JOIN {T} n ON n.id = a.duengemittel_inhalte_id "
        "WHERE n.tenant_id IS DISTINCT FROM a.tenant_id")).scalar()
    if fremd:
        raise RuntimeError(f"{ARTIKEL}.duengemittel_inhalte_id: {fremd} Artikel verweisen auf Naehrstoffe eines anderen Mandanten")
    op.execute(f"ALTER TABLE {T} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()")
    op.execute(f"ALTER TABLE {T} ADD CONSTRAINT uq_nutrient_compositions_id_tenant UNIQUE (id, tenant_id)")
    alt = bind.execute(sa.text(
        "SELECT conname FROM pg_constraint WHERE conrelid = to_regclass(:a) AND confrelid = to_regclass(:t) "
        "AND contype = 'f'"), {"a": ARTIKEL, "t": T}).scalar()
    if alt:
        op.execute(f"ALTER TABLE {ARTIKEL} DROP CONSTRAINT {alt}")
    op.execute(
        f"ALTER TABLE {ARTIKEL} ADD CONSTRAINT fk_articles_duengemittel_inhalte_id_tenant "
        f"FOREIGN KEY (duengemittel_inhalte_id, tenant_id) REFERENCES {T} (id, tenant_id) "
        "ON DELETE SET NULL (duengemittel_inhalte_id)"
    )
    op.execute(f"ALTER TABLE {T} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {T}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {T} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {T} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {T} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {T} FOR DELETE USING ({OWN})")


def downgrade() -> None:
    bind = op.get_bind()
    if not _exists(bind, T):
        return
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {T}")
    op.execute(f"ALTER TABLE {T} DISABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {ARTIKEL} DROP CONSTRAINT IF EXISTS fk_articles_duengemittel_inhalte_id_tenant")
    op.execute(f"ALTER TABLE {ARTIKEL} ADD CONSTRAINT articles_duengemittel_inhalte_id_fkey "
               f"FOREIGN KEY (duengemittel_inhalte_id) REFERENCES {T} (id)")
    op.execute(f"ALTER TABLE {T} DROP CONSTRAINT IF EXISTS uq_nutrient_compositions_id_tenant")
    op.execute(f"ALTER TABLE {T} ALTER COLUMN tenant_id DROP DEFAULT")
