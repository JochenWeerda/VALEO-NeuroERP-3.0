"""Buchungsschluessel fuer Bestandsbewegungen - doppelte Bewegungen technisch ausgeschlossen (24.11.2026).

Revision ID: bestandsbuchung_schluessel_20261124
Revises: position_preisbezug_20261124

Nutzerauftrag 24.11.2026 (Schnitt 2b-2): dauerhafte Idempotenz der Bestandsbuchung; wiederholte Ereignisse,
parallele Buchungen und Transaktionsabbrueche duerfen keine zweite Bewegung erzeugen. ``inventory_stock_movements``
hatte keinen fachlichen Schluessel (nur ``id``). Eine Buchung beansprucht vor allen Wirkungen (Lagerplatz,
Bewegung, Artikelbestand) ihren Schluessel in ``bestandsbuchung_schluessel``; der Primaerschluessel
``(tenant_id, schluessel)`` laesst parallele Zweitversuche warten und danach nichts buchen, ein Abbruch nimmt den
Anspruch mit zurueck.
"""
from __future__ import annotations

from alembic import op

revision = "bestandsbuchung_schluessel_20261124"
down_revision = "position_preisbezug_20261124"
branch_labels = None
depends_on = None

TABELLE = "domain_inventory.bestandsbuchung_schluessel"
OWN = "(tenant_id)::text = public.rls_current_tenant()"


def upgrade() -> None:
    op.execute(f"""
        CREATE TABLE {TABELLE} (
            tenant_id varchar NOT NULL,
            schluessel varchar(200) NOT NULL,
            bewegung_id varchar,
            erstellt_am timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT pk_bestandsbuchung_schluessel PRIMARY KEY (tenant_id, schluessel),
            CONSTRAINT fk_bestandsbuchung_bewegung FOREIGN KEY (bewegung_id, tenant_id)
                REFERENCES domain_inventory.inventory_stock_movements (id, tenant_id) ON DELETE CASCADE
        )
    """)
    op.execute(f"ALTER TABLE {TABELLE} ENABLE ROW LEVEL SECURITY")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {TABELLE} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {TABELLE} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {TABELLE} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {TABELLE} FOR DELETE USING ({OWN})")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_inventory.bestandsbuchung_schluessel")
