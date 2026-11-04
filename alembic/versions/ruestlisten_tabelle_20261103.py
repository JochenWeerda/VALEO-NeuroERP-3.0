"""Rüstlisten (Kommissioniervorbereitung): Tabelle, die der Weg /lager/ruestliste schon benutzt.

Revision ID: ruestlisten_tabelle_20261103
Revises: rahmenauftrag_afa_tabellen_20261102

``app/api/v1/endpoints/ruestliste.py`` liest und schreibt ``domain_inventory.ruestlisten``; keine Migration und
kein Modell legten sie an. Die Liste antwortete deshalb auf jeder Installation leer (der Fehler wurde verschluckt),
Anlegen und jeder Statuswechsel mit 503. Gefunden mit der Studio-Liste lager/kommissionierung (Batch 2,
03.11.2026) ueber tests/test_table_reference_inventory.py.

Wie die uebrigen Mandantentabellen: ``tenant_id`` aus dem Kontext als Vorgabe, RLS mit getrennter Policy je
Befehl. Der Weg schrieb bisher ohne Mandant und las alle Mandanten; das erledigt jetzt RLS. Status und Prioritaet
folgen den Werten des Wegs; die Ruestlistennummer ist je Mandant eindeutig.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "ruestlisten_tabelle_20261103"
down_revision = "rahmenauftrag_afa_tabellen_20261102"
branch_labels = None
depends_on = None

TABELLE = "domain_inventory.ruestlisten"
OWN = "tenant_id = public.rls_current_tenant()"


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_inventory")
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABELLE} (
            id varchar PRIMARY KEY,
            tenant_id varchar NOT NULL DEFAULT public.rls_current_tenant(),
            ruestlisten_nr varchar(30) NOT NULL,
            auftrag_nr varchar(64) NOT NULL,
            status varchar(20) NOT NULL DEFAULT 'OFFEN'
                CONSTRAINT ck_ruestlisten_status CHECK (status IN ('OFFEN', 'IN_BEARBEITUNG', 'VERARBEITET', 'ABGEBROCHEN')),
            positionen jsonb NOT NULL DEFAULT '[]'::jsonb,
            erstellt_fuer varchar(120) NOT NULL,
            prioritaet varchar(10) NOT NULL DEFAULT 'NORMAL'
                CONSTRAINT ck_ruestlisten_prioritaet CHECK (prioritaet IN ('NORMAL', 'HOCH', 'EILIG')),
            bemerkung text,
            erstellt_am timestamptz NOT NULL DEFAULT now(),
            verarbeitet_am timestamptz,
            CONSTRAINT uq_ruestlisten_tenant_nr UNIQUE (tenant_id, ruestlisten_nr)
        )""")
    op.execute(f"CREATE INDEX IF NOT EXISTS ix_ruestlisten_tenant_status ON {TABELLE} (tenant_id, status, erstellt_am DESC)")
    op.execute(f"ALTER TABLE {TABELLE} ENABLE ROW LEVEL SECURITY")
    for kind in ("select", "insert", "update", "delete"):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{kind} ON {TABELLE}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {TABELLE} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {TABELLE} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {TABELLE} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {TABELLE} FOR DELETE USING ({OWN})")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": TABELLE}).scalar() is None:
        return
    # Nur eine leere Tabelle entfernen: Ruestlisten sind Lagerbelege.
    if not bind.execute(sa.text(f"SELECT EXISTS (SELECT 1 FROM {TABELLE})")).scalar():  # nosec B608
        op.execute(f"DROP TABLE {TABELLE}")
