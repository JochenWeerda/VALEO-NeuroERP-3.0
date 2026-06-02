"""Catch-up: Performance-Indizes auf bereits migrierten DBs anlegen.

Revision ID: perf_indexes_apply_20260602
Revises: kunden_lookup_view_20260602
Create Date: 2026-06-02

performance_indexes_20260526 war ursprünglich fehlerhaft (unqualifizierte
Tabellennamen lösten nicht auf die domain_*-Schemata auf; mehrere Spaltennamen
existierten nicht). Auf Umgebungen, die diese Revision bereits als No-op
durchlaufen haben (z. B. die DEV-DB), wurden deshalb 0 Indizes angelegt.

Diese Migration legt die — inzwischen korrigierte, schema-qualifizierte —
kanonische Index-Liste idempotent nach (CREATE INDEX CONCURRENTLY IF NOT EXISTS,
Tabellen-Guard). Frischinstallationen haben die Indizes bereits aus
performance_indexes_20260526; dort greift schlicht das IF NOT EXISTS. Single
Source of Truth bleibt PERF_INDEXES in performance_indexes_20260526.py.
"""

import importlib.util
import os

from alembic import op

revision = "perf_indexes_apply_20260602"
down_revision = "kunden_lookup_view_20260602"
branch_labels = None
depends_on = None


def _load_source():
    """Lädt die kanonische Index-Liste + Helfer aus performance_indexes_20260526."""
    path = os.path.join(os.path.dirname(__file__), "performance_indexes_20260526.py")
    spec = importlib.util.spec_from_file_location("_perf_idx_source", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def upgrade() -> None:
    src = _load_source()
    with op.get_context().autocommit_block():
        src.apply_indexes()


def downgrade() -> None:
    # Bewusst kein Drop: Die Indizes „gehören" fachlich performance_indexes_20260526.
    # Ein Downgrade dieser Catch-up-Revision soll die (ggf. dort schon vorhandenen)
    # Indizes nicht entfernen. Das Entfernen erfolgt beim Downgrade von
    # performance_indexes_20260526.
    pass
