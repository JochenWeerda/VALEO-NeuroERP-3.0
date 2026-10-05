"""Fuehrt die beiden Koepfe zusammen: EUDR-Uebermittlung und Bank-GL-Bindung.

Zwei Agenten haben am selben Tag je eine Migration an denselben Vorlaeufer
gehaengt. Eine Zusammenfuehrung ohne eigenes DDL ist die ehrliche Antwort: Sie
behauptet keine Reihenfolge zwischen zwei Aenderungen, die einander nicht
beruehren, und stellt den Einzelkopf wieder her, den jede Neuinstallation
braucht.

Revision ID: zusammenfuehrung_20261005
Revises: bank_gl_binding_20261001, eudr_uebermittlung_20261001
Create Date: 2026-10-05
"""

from __future__ import annotations

revision = "zusammenfuehrung_20261005"
down_revision = ("bank_gl_binding_20261001", "eudr_uebermittlung_20261001")
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Kein DDL — die Zusammenfuehrung ordnet nur den Revisionsbaum."""


def downgrade() -> None:
    """Kein DDL — die Zusammenfuehrung ordnet nur den Revisionsbaum."""
