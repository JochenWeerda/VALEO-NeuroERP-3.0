"""Der eigene Mahnstufen-Verlauf entfaellt - der Verlauf sind die Mahnungen (M3, ein Mahnweg).

Revision ID: mahnstufen_verlauf_entfernen_20261123
Revises: finance_router_altspeicher_entfernen_20261123

``domain_finance.finance_mahnstufen_audit`` schrieb "Mahnstufe eskalieren" bis 23.11.2026 neben dem Mahnlauf (eigene
Stufen bis INKASSO, ohne Mahnung, ohne Stufe am Posten). Seit #168 erzeugt die Eskalation eine Mahnung ueber
FinanceDunningService.run_dunning, und der Verlauf liest domain_erp.dunning_notices; niemand liest oder schreibt die
Tabelle mehr.

Haelt an, wenn ein bestehender Mandant dort Zeilen hat. Rueckweg: Tabelle leer wieder anlegen (pg_dump, mit RLS).
"""
from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "mahnstufen_verlauf_entfernen_20261123"
down_revision = "finance_router_altspeicher_entfernen_20261123"
branch_labels = None
depends_on = None

TABELLE = "domain_finance.finance_mahnstufen_audit"


def _vorhanden(bind) -> bool:
    return bool(bind.exec_driver_sql(f"SELECT to_regclass('{TABELLE}') IS NOT NULL").scalar())  # nosec B608


def upgrade() -> None:
    bind = op.get_bind()
    if not _vorhanden(bind):
        return
    anzahl = bind.exec_driver_sql(  # nosec B608 - fester Name
        f"SELECT COUNT(*) FROM {TABELLE} a JOIN domain_shared.tenants t ON t.id = a.tenant_id::text").scalar()
    if anzahl:
        raise RuntimeError(f"{TABELLE} enthaelt {anzahl} Zeilen bestehender Mandanten - erst pruefen")
    op.execute(f"DROP TABLE {TABELLE}")


def downgrade() -> None:
    bind = op.get_bind()
    if _vorhanden(bind):
        return
    bind.exec_driver_sql(Path(__file__).with_suffix(".sql").read_text(encoding="utf-8"))
