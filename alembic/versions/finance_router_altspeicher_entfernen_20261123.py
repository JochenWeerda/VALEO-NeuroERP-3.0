"""Fuenf Finanz-Alttabellen ohne Migration entfallen (M3).

Revision ID: finance_router_altspeicher_entfernen_20261123
Revises: nebenbuch_abstimmung_tabelle_20261123

``public.wechselkurse``, ``public.buchungsschemata``, ``public.kostenstellen``, ``public.abschluss_checklisten`` und
``public.intercompany_buchungen`` legte keine Migration an; es gab sie nur in gewachsenen Datenbanken (``create_all``).
Nur ``app/finance/router.py`` las und schrieb sie - auf einer frischen Installation scheiterte jeder Weg. Fuehrend sind
``/api/v1/exchange-rates``, ``/api/v1/booking-templates``, ``/api/v1/kostenrechnung`` (``domain_finance.kostenstellen``
bleibt) und ``/api/v1/closing-checklists``; Intercompany hatte keinen Nutzer.

Haelt an, wenn ein bestehender Mandant dort Zeilen hat. Kein Rueckweg noetig: eine frische Installation hatte die
Tabellen nie; eine gewachsene bekaeme sie nur leer zurueck, ohne dass ein Weg sie noch nutzt.
"""
from __future__ import annotations

from alembic import op

revision = "finance_router_altspeicher_entfernen_20261123"
down_revision = "nebenbuch_abstimmung_tabelle_20261123"
branch_labels = None
depends_on = None

TABELLEN = ("public.intercompany_buchungen", "public.abschluss_checklisten", "public.kostenstellen",
            "public.buchungsschemata", "public.wechselkurse")


def _vorhanden(bind, name: str) -> bool:
    return bool(bind.exec_driver_sql(f"SELECT to_regclass('{name}') IS NOT NULL").scalar())  # nosec B608


def upgrade() -> None:
    bind = op.get_bind()
    funde = []
    for tabelle in TABELLEN:
        if not _vorhanden(bind, tabelle):
            continue
        anzahl = bind.exec_driver_sql(  # nosec B608 - Namen aus TABELLEN
            f"SELECT COUNT(*) FROM {tabelle} a JOIN domain_shared.tenants t ON t.id = a.tenant_id::text").scalar()
        if anzahl:
            funde.append(f"{tabelle}: {anzahl}")
    if funde:
        raise RuntimeError("Finanz-Alttabellen enthalten Zeilen bestehender Mandanten - erst pruefen: " + ", ".join(funde))
    for tabelle in TABELLEN:
        op.execute(f"DROP TABLE IF EXISTS {tabelle}")


def downgrade() -> None:
    """Bewusst leer (siehe Modulbeschreibung)."""
