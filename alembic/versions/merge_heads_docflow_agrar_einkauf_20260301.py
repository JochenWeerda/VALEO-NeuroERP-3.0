"""Merge heads: Agrar, Einkauf RE-Workflow, Docflow GoBD Schritt 3

Revision ID: merge_heads_20260301
Revises: agrar_maschinen_wetter_20260301, einkauf_re_workflow_20260301, docflow_print_event_20260301
Create Date: 2026-03-01

Führt alle aktuellen Branch-Heads zu einem gemeinsamen Head zusammen,
damit 'alembic upgrade head' bei Release/Neuinstallation alle Migrationen anwendet.
"""

from __future__ import annotations

from alembic import op


revision = "merge_heads_20260301"
down_revision = (
    "agrar_maschinen_wetter_20260301",
    "einkauf_re_workflow_20260301",
    "docflow_print_event_20260301",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Reine Merge-Revision: keine Schema-Änderungen
    pass


def downgrade() -> None:
    pass
