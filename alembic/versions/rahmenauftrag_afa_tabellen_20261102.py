"""Tabellen, die Rahmenauftraege und AfA-Laeufe schon benutzen, auf frischen Installationen anlegen.

Revision ID: rahmenauftrag_afa_tabellen_20261102
Revises: nummernkreis_mandant_cascade_20261102

``sales_blanket_orders.py`` (Rahmenauftraege und ihre Abrufe) und ``asset_accounting.py`` (AfA-Laeufe) schreiben
und lesen ``domain_sales.blanket_orders``, ``domain_sales.blanket_order_releases`` und
``domain_finance.asset_depreciation_runs``. Keine Migration legte sie an; seit die Runtime46-Masken diese Wege
aufrufen, antworteten sie auf jeder frisch migrierten Datenbank mit 503. Die Spalten sind die, die der Code nennt.

Wie die uebrigen Mandantentabellen: RLS mit getrennter Policy je Befehl, ``tenant_id`` aus dem Kontext als
Vorgabe; ein Abruf haengt an seinem Rahmenauftrag, ein AfA-Lauf an seiner Anlage. Bestehende Tabellen bleiben
unberuehrt (``IF NOT EXISTS``); das Downgrade entfernt nur leere Tabellen dieser Migration.

Dazu drei RLS-Luecken:

* ``domain_crm.activities`` und ``public.crm_activities`` waren zurueckgestellt (Ursache "dienst"): crm-core schrieb
  ohne Mandantenkontext. Seit dem kanonischen Aktivitaetsdienst (crm_activity_canonical_20261029) schreibt nur der
  Request im Mandanten; die RLS-Analyse (rls-rollout.json) fuehrt keinen Grund mehr.
* ``domain_ops.waage_import_entries`` trug eine Sammel-Policy fuer alle Befehle; wie ueberall vier getrennte.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rahmenauftrag_afa_tabellen_20261102"
down_revision = "nummernkreis_mandant_cascade_20261102"
branch_labels = None
depends_on = None

OWN = "tenant_id = public.rls_current_tenant()"
TABELLEN = ("domain_sales.blanket_orders", "domain_sales.blanket_order_releases",
            "domain_finance.asset_depreciation_runs")


def _rls(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    for kind in ("select", "insert", "update", "delete"):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{kind} ON {table}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({OWN})")


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_sales")
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_sales.blanket_orders (
            id varchar PRIMARY KEY,
            tenant_id varchar NOT NULL DEFAULT public.rls_current_tenant(),
            customer_id varchar NOT NULL,
            article_id varchar NOT NULL,
            total_quantity numeric(18, 4) NOT NULL CHECK (total_quantity > 0),
            unit_price numeric(18, 4) NOT NULL DEFAULT 0 CHECK (unit_price >= 0),
            valid_from timestamptz NOT NULL,
            valid_to timestamptz NOT NULL,
            status varchar(20) NOT NULL DEFAULT 'AKTIV',
            created_at timestamptz NOT NULL DEFAULT now()
        )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_blanket_orders_tenant_customer "
               "ON domain_sales.blanket_orders (tenant_id, customer_id)")
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_sales.blanket_order_releases (
            id varchar PRIMARY KEY,
            tenant_id varchar NOT NULL DEFAULT public.rls_current_tenant(),
            blanket_order_id varchar NOT NULL REFERENCES domain_sales.blanket_orders (id) ON DELETE CASCADE,
            release_quantity numeric(18, 4) NOT NULL CHECK (release_quantity > 0),
            release_date timestamptz NOT NULL,
            sales_order_ref varchar,
            status varchar(20) NOT NULL DEFAULT 'OFFEN'
        )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_blanket_order_releases_order "
               "ON domain_sales.blanket_order_releases (tenant_id, blanket_order_id)")
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_finance.asset_depreciation_runs (
            id varchar PRIMARY KEY,
            tenant_id varchar NOT NULL DEFAULT public.rls_current_tenant(),
            asset_id varchar NOT NULL REFERENCES domain_finance.fixed_assets (id),
            period_year integer NOT NULL,
            period_month integer NOT NULL CHECK (period_month BETWEEN 1 AND 12),
            depreciation_amount numeric(14, 2) NOT NULL,
            book_value_after numeric(14, 2) NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, asset_id, period_year, period_month)
        )""")
    for table in TABELLEN:
        _rls(table)
    for table in ("domain_crm.activities", "public.crm_activities"):
        _rls(table)
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON domain_ops.waage_import_entries")
    _rls("domain_ops.waage_import_entries")


def downgrade() -> None:
    bind = op.get_bind()
    for kind in ("select", "insert", "update", "delete"):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{kind} ON domain_ops.waage_import_entries")
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{kind} ON domain_crm.activities")
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{kind} ON public.crm_activities")
    op.execute("ALTER TABLE domain_crm.activities DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE public.crm_activities DISABLE ROW LEVEL SECURITY")
    op.execute(f"CREATE POLICY tenant_isolation ON domain_ops.waage_import_entries USING ({OWN}) WITH CHECK ({OWN})")
    for table in reversed(TABELLEN):
        if bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is None:
            continue
        # Nur leere Tabellen entfernen: Rahmenauftraege und AfA-Laeufe sind Geschaeftsdaten.
        if not bind.execute(sa.text(f"SELECT EXISTS (SELECT 1 FROM {table})")).scalar():  # nosec B608
            op.execute(f"DROP TABLE {table}")
