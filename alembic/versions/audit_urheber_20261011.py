"""Masken-Audit: gepruefter Urheber.

Revision ID: audit_urheber_20261011
Revises: versandwege_echt_20261008

``crm_action_audit_log`` hielt fest, was geschah, aber nicht, wer es tat. Die
Bewerbungs-Commands schrieben den Urheber in den Freitext der Zusammenfassung —
aus einem Kopf, den der Aufrufer selbst setzt. Die Spalte nimmt die Kennung aus
dem geprueften Token auf. Sie ist nullbar: Bestandszeilen haben keinen belegten
Urheber, und ein erfundener waere schlechter als keiner.
"""

from alembic import op

revision = "audit_urheber_20261011"
down_revision = "versandwege_echt_20261008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE domain_crm.crm_action_audit_log ADD COLUMN IF NOT EXISTS performed_by VARCHAR(120)")


def downgrade() -> None:
    op.execute("ALTER TABLE domain_crm.crm_action_audit_log DROP COLUMN IF EXISTS performed_by")
