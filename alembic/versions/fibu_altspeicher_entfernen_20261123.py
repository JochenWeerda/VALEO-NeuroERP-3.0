"""Die Schein-Fibu auf vier leeren public-Tabellen entfaellt (M3).

Revision ID: fibu_altspeicher_entfernen_20261123
Revises: beleg_altspeicher_entfernen_20261117

``public.offene_posten``, ``public.buchungen``, ``public.konten`` und ``public.anlagen`` stammen aus der ersten
Finanzmigration. Nur der Router ``app/routers/fibu_router.py`` las und schrieb sie: Debitoren/Kreditoren, Mahnstufe
ohne Mahnung, "Zahlungslauf" ohne Zahlung, Buchungen am Journal vorbei, Bilanz/GuV/BWA aus leeren Tabellen. Fuehrend
sind ``domain_erp.offene_posten``, ``domain_erp.journal_entries``, ``domain_erp.chart_of_accounts`` und die
Anlagenbuchhaltung unter ``/api/v1/finance/asset-accounting``.

Haelt an, wenn ein bestehender Mandant dort doch Zeilen hat - die werden nicht stillschweigend geloescht.
Der Rueckweg legt die Tabellen leer wieder an (``fibu_altspeicher_entfernen_20261123.sql``, per pg_dump aus einer
frisch migrierten Datenbank: Schluessel, Indizes, RLS).
"""
from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "fibu_altspeicher_entfernen_20261123"
down_revision = "beleg_altspeicher_entfernen_20261117"
branch_labels = None
depends_on = None

TABELLEN = ("public.offene_posten", "public.buchungen", "public.konten", "public.anlagen")


def _vorhanden(bind, name: str) -> bool:
    return bool(bind.exec_driver_sql(f"SELECT to_regclass('{name}') IS NOT NULL").scalar())  # nosec B608


def upgrade() -> None:
    bind = op.get_bind()
    funde = [
        f"{tabelle}: {anzahl}"
        for tabelle in TABELLEN
        if _vorhanden(bind, tabelle)
        for anzahl in [bind.exec_driver_sql(  # nosec B608 - Namen aus TABELLEN
            f"SELECT COUNT(*) FROM {tabelle} a JOIN domain_shared.tenants t ON t.id = a.tenant_id::text").scalar()]
        if anzahl
    ]
    if funde:
        raise RuntimeError("Alte Fibu-Tabellen enthalten Zeilen bestehender Mandanten - erst pruefen: "
                           + ", ".join(funde))
    for tabelle in TABELLEN:
        op.execute(f"DROP TABLE IF EXISTS {tabelle}")


def downgrade() -> None:
    bind = op.get_bind()
    if all(_vorhanden(bind, t) for t in TABELLEN):
        return
    bind.exec_driver_sql(Path(__file__).with_suffix(".sql").read_text(encoding="utf-8"))
