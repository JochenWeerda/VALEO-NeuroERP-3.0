"""DocFlow-Stand ``confirmed``: Auftragsbestaetigung (BELEG-052, Nutzerentscheidung 09.11.2026).

Revision ID: docflow_auftragsbestaetigung_20261109
Revises: docflow_kopfbausteine_20261109

Die Auftragsbestaetigung ist fachlich wichtig und faellt nicht mit "offen" zusammen: Ein freigegebener Auftrag
(``open``) wird mit der Aktion "Auftrag bestaetigen" zu ``confirmed``. Folgebelege und Storno bleiben moeglich.
"""
from __future__ import annotations

from alembic import op

revision = "docflow_auftragsbestaetigung_20261109"
down_revision = "docflow_kopfbausteine_20261109"
branch_labels = None
depends_on = None

_ALT = "'draft', 'open', 'completed', 'posted', 'reversed', 'cancelled'"


def upgrade() -> None:
    op.execute("ALTER TABLE domain_docflow.document_headers DROP CONSTRAINT IF EXISTS chk_docflow_header_status")
    op.execute("ALTER TABLE domain_docflow.document_headers ADD CONSTRAINT chk_docflow_header_status "
               f"CHECK (status IN ({_ALT}, 'confirmed'))")


def downgrade() -> None:
    bestaetigt = op.get_bind().exec_driver_sql(
        "SELECT count(*) FROM domain_docflow.document_headers WHERE status = 'confirmed'").scalar()
    if bestaetigt:
        raise RuntimeError(f"{bestaetigt} bestaetigte Belege: Der Stand confirmed laesst sich nicht entfernen.")
    op.execute("ALTER TABLE domain_docflow.document_headers DROP CONSTRAINT IF EXISTS chk_docflow_header_status")
    op.execute(f"ALTER TABLE domain_docflow.document_headers ADD CONSTRAINT chk_docflow_header_status CHECK (status IN ({_ALT}))")
