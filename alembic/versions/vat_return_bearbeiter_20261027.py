"""UStVA-Anmeldungen speichern, wer berechnet, geprueft, freigegeben und uebermittelt hat.

Revision ID: vat_return_bearbeiter_20261027
Revises: rls_domain_shared_20261027

``domain_erp.vat_returns`` kannte nur den Status. Freigebender, Freigabezeitpunkt und ELSTER-Referenz standen bis
27.10.2026 nur in der Antwort: der Freigebende kam aus dem Rumpf, die Referenz wurde erfunden, gespeichert wurde
nichts davon. Jetzt traegt die Anmeldung die geprueften Bearbeiter je Schritt und das Transferticket, das ELSTER bei
der Uebermittlung vergibt.

Die Pruefbedingung haelt den Ablauf fest: freigegeben nur mit Freigebendem, uebermittelt nur mit Uebermittler und
Transferticket. Live gibt es keine Anmeldung (0 Zeilen); eine vorhandene Zeile im Status ``submitted`` ohne
Transferticket wuerde die Migration abbrechen — sie waere eine Schein-Uebermittlung und ist fachlich zu klaeren.
"""
from __future__ import annotations

from alembic import op

revision = "vat_return_bearbeiter_20261027"
down_revision = "rls_domain_shared_20261027"
branch_labels = None
depends_on = None

_SPALTEN = (
    ("calculated_by", "VARCHAR(100)"),
    ("validated_by", "VARCHAR(100)"),
    ("approved_by", "VARCHAR(100)"),
    ("approved_at", "TIMESTAMPTZ"),
    ("submitted_by", "VARCHAR(100)"),
    ("elster_transferticket", "VARCHAR(50)"),
)


def upgrade() -> None:
    for name, typ in _SPALTEN:
        op.execute(f"ALTER TABLE domain_erp.vat_returns ADD COLUMN IF NOT EXISTS {name} {typ}")
    # Die Vorgabe 'draft' gehoert zu keinem Schritt; eine Anmeldung entsteht berechnet.
    op.execute("ALTER TABLE domain_erp.vat_returns ALTER COLUMN status SET DEFAULT 'calculated'")
    op.execute(
        """
        ALTER TABLE domain_erp.vat_returns ADD CONSTRAINT ck_vat_returns_ablauf CHECK (
            status IN ('calculated', 'validated', 'approved', 'submitted')
            AND (status NOT IN ('approved', 'submitted') OR (approved_by IS NOT NULL AND approved_at IS NOT NULL))
            AND (status <> 'submitted'
                 OR (submitted_by IS NOT NULL AND submitted_at IS NOT NULL AND elster_transferticket IS NOT NULL))
        )
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE domain_erp.vat_returns DROP CONSTRAINT IF EXISTS ck_vat_returns_ablauf")
    op.execute("ALTER TABLE domain_erp.vat_returns ALTER COLUMN status SET DEFAULT 'draft'")
    for name, _typ in reversed(_SPALTEN):
        op.execute(f"ALTER TABLE domain_erp.vat_returns DROP COLUMN IF EXISTS {name}")
