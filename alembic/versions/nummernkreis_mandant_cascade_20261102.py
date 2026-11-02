"""Nummernkreise gehoeren dem Mandanten: Fremdschluessel mit ON DELETE CASCADE.

Revision ID: nummernkreis_mandant_cascade_20261102
Revises: partner_kontonummern_20261102

Seit Stufe 3b legt die erste Kunden- bzw. Lieferantenrolle den Kontonummernkreis des Mandanten an
(``domain_shared.number_ranges``). Ein Kreis ohne seinen Mandanten hat keine Bedeutung; der bisherige
Fremdschluessel ohne Regel verhinderte aber das Entfernen eines Mandanten (z.B. Testmandanten), sobald einmal
ein Kunde angelegt war. Daten aendert die Migration nicht.
"""
from __future__ import annotations

from alembic import op

revision = "nummernkreis_mandant_cascade_20261102"
down_revision = "partner_kontonummern_20261102"
branch_labels = None
depends_on = None

TABLE = "domain_shared.number_ranges"
FK = "number_ranges_tenant_id_fkey"


def _fk(on_delete: str) -> None:
    op.execute(f"ALTER TABLE {TABLE} DROP CONSTRAINT IF EXISTS {FK}")
    op.execute(f"ALTER TABLE {TABLE} ADD CONSTRAINT {FK} FOREIGN KEY (tenant_id) "
               f"REFERENCES domain_shared.tenants(id) {on_delete}")


def upgrade() -> None:
    _fk("ON DELETE CASCADE")


def downgrade() -> None:
    _fk("")
