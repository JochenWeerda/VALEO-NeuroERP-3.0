"""Loeschauftrag mit Vier-Augen-Freigabe (M7 Loeschkonzept, Nutzerentscheid 26.11.2026).

Revision ID: loeschauftrag_20261126
Revises: aufbewahrung_geltendes_recht_20261125

Die Loeschpruefung (``app/services/loeschpruefung.py``) zeigt, was nach Fristablauf loeschbar waere. Geloescht wird
nur ueber einen Auftrag: beantragt -> freigegeben (zweite Person, nie ein technisches Konto) -> ausgefuehrt. Der
Loeschnachweis traegt Zaehlwerte und IDs, keine Inhalte. Die Prueflogik steht in ``app/services/loeschlauf.py``;
die Datenbank sichert die Funktionstrennung zusaetzlich (Freigeber <> Antragsteller).
"""
from __future__ import annotations

from alembic import op

revision = "loeschauftrag_20261126"
down_revision = "aufbewahrung_geltendes_recht_20261125"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE domain_shared.loeschauftraege (
            id text PRIMARY KEY,
            tenant_id text NOT NULL REFERENCES domain_shared.tenants (id),
            kategorie text NOT NULL,
            satz_ids jsonb NOT NULL,
            anzahl integer NOT NULL CHECK (anzahl >= 0),
            status text NOT NULL DEFAULT 'beantragt'
                CHECK (status IN ('beantragt', 'freigegeben', 'abgelehnt', 'ausgefuehrt')),
            beantragt_von text NOT NULL,
            beantragt_am timestamptz NOT NULL DEFAULT now(),
            entschieden_von text,
            entschieden_am timestamptz,
            grund text,
            ausgefuehrt_von text,
            ausgefuehrt_am timestamptz,
            nachweis jsonb,
            CONSTRAINT ck_loeschauftrag_vier_augen CHECK (entschieden_von IS NULL OR entschieden_von <> beantragt_von)
        )
    """)
    op.execute("CREATE INDEX ix_loeschauftraege_tenant_status ON domain_shared.loeschauftraege (tenant_id, status)")
    op.execute("ALTER TABLE domain_shared.loeschauftraege ENABLE ROW LEVEL SECURITY")
    op.execute("CREATE POLICY tenant_isolation_select ON domain_shared.loeschauftraege FOR SELECT USING ((tenant_id)::text = public.rls_current_tenant())")
    op.execute("CREATE POLICY tenant_isolation_insert ON domain_shared.loeschauftraege FOR INSERT WITH CHECK ((tenant_id)::text = public.rls_current_tenant())")
    op.execute("CREATE POLICY tenant_isolation_update ON domain_shared.loeschauftraege FOR UPDATE USING ((tenant_id)::text = public.rls_current_tenant()) WITH CHECK ((tenant_id)::text = public.rls_current_tenant())")
    op.execute("CREATE POLICY tenant_isolation_delete ON domain_shared.loeschauftraege FOR DELETE USING ((tenant_id)::text = public.rls_current_tenant())")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_shared.loeschauftraege")
