"""Die Nebenbuch-Abstimmung bekommt ihre Tabelle auch auf einer frischen Installation (M3).

Revision ID: nebenbuch_abstimmung_tabelle_20261123
Revises: fibu_altspeicher_entfernen_20261123

``public.nebenbuch_abstimmungen`` (Modell ``app.finance.models.NebenbuchAbstimmung``) legte keine Migration an; es
gab sie nur in der gewachsenen Entwicklungsdatenbank (``create_all``). Auf einer frischen Installation scheiterte
schon das Anlegen einer Abstimmung. Spalten wie dort; dazu Mandantenschutz je Befehl.
"""
from __future__ import annotations

from alembic import op

revision = "nebenbuch_abstimmung_tabelle_20261123"
down_revision = "fibu_altspeicher_entfernen_20261123"
branch_labels = None
depends_on = None

TABELLE = "public.nebenbuch_abstimmungen"
OWN = "(tenant_id)::text = public.rls_current_tenant()"
POLICIES = ("tenant_isolation_select", "tenant_isolation_insert", "tenant_isolation_update", "tenant_isolation_delete")


def upgrade() -> None:
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABELLE} (
            id character varying(36) PRIMARY KEY,
            tenant_id character varying(36) NOT NULL,
            abstimmungs_datum date NOT NULL,
            periode character varying(10) NOT NULL,
            buchungskreis character varying(10) NOT NULL,
            status character varying(20),
            nebenbuch_saldo double precision,
            hauptbuch_saldo double precision,
            differenz double precision,
            nicht_abgestimmte json,
            abgestimmt_durch character varying(100),
            created_at timestamp without time zone,
            updated_at timestamp without time zone
        )
    """)
    op.execute(f"CREATE INDEX IF NOT EXISTS ix_nebenbuch_abstimmungen_periode ON {TABELLE} (periode)")
    op.execute(f"CREATE INDEX IF NOT EXISTS ix_nebenbuch_abstimmungen_tenant_id ON {TABELLE} (tenant_id)")
    op.execute(f"ALTER TABLE {TABELLE} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {TABELLE}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {TABELLE} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {TABELLE} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {TABELLE} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {TABELLE} FOR DELETE USING ({OWN})")


def downgrade() -> None:
    # Leer (frische Installation): Tabelle weg wie vorher. Mit Inhalt (gewachsene Datenbank hatte sie schon vorher):
    # Inhalt bleibt, nur der Mandantenschutz geht zurueck.
    bind = op.get_bind()
    if not bind.exec_driver_sql(f"SELECT EXISTS (SELECT 1 FROM {TABELLE})").scalar():  # nosec B608 - fester Name
        op.execute(f"DROP TABLE {TABELLE}")
        return
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {TABELLE}")
    op.execute(f"ALTER TABLE {TABELLE} DISABLE ROW LEVEL SECURITY")
