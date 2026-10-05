"""Fuehrt die beiden Koepfe zusammen: Preisfindung und Journalnummer.

Zwei Agenten haben am selben Tag je eine Migration an
`kontrakt_disposition_20261005` beziehungsweise an den Journalstand gehaengt. Der
zweite Kopf stammt aus `journal_number_tenant_20261005` — der Antwort auf den
Handshake aus dem Genossenschafts-Slice: `journal_entries.entry_number` war
systemweit eindeutig statt je Mandant.

Eine Zusammenfuehrung ohne eigenes DDL ist die ehrliche Antwort: Sie behauptet
keine Reihenfolge zwischen zwei Aenderungen, die einander nicht beruehren, und
stellt den Einzelkopf her, den jede Neuinstallation braucht.

Revision ID: zusammenfuehrung_20261005_preis_journal
Revises: preisfindung_rabattregeln_20261005, journal_number_tenant_20261005
Create Date: 2026-10-05
"""

from __future__ import annotations

revision = "zusammenfuehrung_20261005_preis_journal"
down_revision = (
    "preisfindung_rabattregeln_20261005",
    "journal_number_tenant_20261005",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Kein DDL — die Zusammenfuehrung ordnet nur den Revisionsbaum."""


def downgrade() -> None:
    """Kein DDL — die Zusammenfuehrung ordnet nur den Revisionsbaum."""
