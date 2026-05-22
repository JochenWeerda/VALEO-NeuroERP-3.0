"""Merge: agrar_ernte_planung_20260520 + fachliche_vertiefung_wave13_20260522

Beide Zweige teilen denselben Ursprung (ops_wave107_remaining_stubs_20260520).
Diese Merge-Revision vereint sie zu einem einzigen Head, damit
`alembic upgrade head` ohne Fehler funktioniert.

Revision ID: merge_heads_20260522
Revises: agrar_ernte_planung_20260520, fachliche_vertiefung_wave13_20260522
Create Date: 2026-05-22
"""

revision = "merge_heads_20260522"
down_revision = ("agrar_ernte_planung_20260520", "fachliche_vertiefung_wave13_20260522")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
