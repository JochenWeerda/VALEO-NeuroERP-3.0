"""CRM/KIM Cockpit-Performance — fehlende Indizes.

Revision ID: crm_kim_perf_indexes_20260612
Revises: merge_doc_proc_20260612

Geprüft wurden die fünf vom KIM-360°-Cockpit gefilterten Tabellen. Bereits indiziert
(keine Aktion): public.kunden (PK kunden_nr, idx business_partner_id, idx name1),
public.kunden_crm360 (PK kunden_nr), domain_crm.sales_orders (idx customer_id, deleted).
Fehlend (Seq Scan im Hot-Path):
  - public.kunden_ansprechpartner — Ansprechpartner-Filter `WHERE kunden_nr = …`.
  - domain_shared.open_items — Offene-Posten-Filter `WHERE tenant_id … AND partner_id = …`.
Idempotent (``CREATE INDEX IF NOT EXISTS``).
"""

from typing import Sequence, Union

from alembic import op

revision: str = "crm_kim_perf_indexes_20260612"
down_revision: Union[str, Sequence[str], None] = "merge_doc_proc_20260612"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_kunden_ansprechpartner_kunden_nr "
        "ON public.kunden_ansprechpartner (kunden_nr);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_open_items_tenant_partner "
        "ON domain_shared.open_items (tenant_id, partner_id);"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS public.ix_kunden_ansprechpartner_kunden_nr;")
    op.execute("DROP INDEX IF EXISTS domain_shared.ix_open_items_tenant_partner;")
