"""Foerderantraege, Marketingkampagnen, Laborproben und -auftraege im Mandanten (Batch 8 Scheinwege).

Revision ID: scheinwege_mandant_20261103
Revises: waagen_wiegungen_mandant_20261103

Die vier Tabellen hatten keine Mandantenspalte; ihre Wege legten bei jedem Lesezugriff Demodaten an und lasen und
schrieben mandantenuebergreifend. Die Wege setzen den Mandanten jetzt aus der Anmeldung; hier kommt die Spalte mit
RLS (getrennte Policy je Befehl), dazu fuer Antragsnummern Eindeutigkeit je Mandant und fuer Befunde die Spalten, die
der Befundweg bisher nur zurueckgab.

Altbestand: Nutzerentscheidung 28.10.2026 - mandantenlose Live-Altbestaende gehoeren dem Default-Mandanten
``00000000-0000-0000-0000-000000000001`` (Rollout als Migration, kein Code-Rueckfall). Gilt nur fuer Zeilen, die
beim Upgrade schon ohne Mandant da sind; existiert der Mandant nicht, bricht die Migration ab, statt zu raten.
Gewachsene Datenbank 03.11.2026: 2 Antraege und 2 Kampagnen (beide aus dem frueheren Seed), 7 Proben (2 Seed,
5 Befunde), 74 Laborauftraege. Geloescht wird nichts; der Seed ist im Code entfernt.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "scheinwege_mandant_20261103"
down_revision = "waagen_wiegungen_mandant_20261103"
branch_labels = None
depends_on = None

#: Nutzerentscheidung 28.10.2026 (Altbestand -> Default Tenant), nur fuer diese einmalige Zuordnung.
ALTBESTAND_MANDANT = "00000000-0000-0000-0000-000000000001"
OPS = "domain_ops"
FOERDER = f"{OPS}.ops_foerderantraege"
PROBEN = f"{OPS}.ops_labor_proben"
TABELLEN = (FOERDER, f"{OPS}.ops_marketing_kampagnen", PROBEN, f"{OPS}.ops_labor_auftraege")
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


def _exists(bind, table: str) -> bool:
    return bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


def _has_column(bind, table: str, column: str) -> bool:
    return bind.execute(sa.text(
        "SELECT 1 FROM pg_attribute WHERE attrelid = to_regclass(:t) AND attname = :c AND NOT attisdropped"),
        {"t": table, "c": column}).scalar() is not None


def _enable(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({OWN})")


def upgrade() -> None:
    bind = op.get_bind()
    present = [t for t in TABELLEN if _exists(bind, t)]
    if not present:
        return
    op.execute(f"LOCK TABLE {', '.join(present)} IN ACCESS EXCLUSIVE MODE")

    for table in present:
        if not _has_column(bind, table, "tenant_id"):
            op.execute(f"ALTER TABLE {table} ADD COLUMN tenant_id character varying(120)")
        offen = bind.execute(sa.text(f"SELECT count(*) FROM {table} WHERE tenant_id IS NULL")).scalar()  # nosec B608
        if offen:
            vorhanden = bind.execute(sa.text("SELECT 1 FROM domain_shared.tenants WHERE id = :t"),
                                     {"t": ALTBESTAND_MANDANT}).scalar()
            if not vorhanden:
                raise RuntimeError(f"{table}: {offen} Zeilen ohne Mandant, Default-Mandant fehlt; nicht pauschal zuordnen")
            op.execute(sa.text(f"UPDATE {table} SET tenant_id = :t WHERE tenant_id IS NULL").bindparams(  # nosec B608
                t=ALTBESTAND_MANDANT))
        op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()")
        op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET NOT NULL")
        op.execute(f"CREATE INDEX IF NOT EXISTS ix_{table.split('.')[1]}_tenant_id ON {table} (tenant_id)")

    if FOERDER in present:
        doppelt = bind.execute(sa.text(
            f"SELECT count(*) FROM (SELECT 1 FROM {FOERDER} GROUP BY tenant_id, nummer HAVING count(*) > 1) d")).scalar()  # nosec B608
        if doppelt:
            raise RuntimeError(f"{FOERDER}: {doppelt} doppelte Antragsnummern im Mandanten; vor der Eindeutigkeit klaeren")
        op.execute(f"ALTER TABLE {FOERDER} ADD CONSTRAINT uq_ops_foerderantraege_tenant_nummer UNIQUE (tenant_id, nummer)")

    if PROBEN in present:
        op.execute(f"ALTER TABLE {PROBEN} ADD COLUMN IF NOT EXISTS analysewerte jsonb")
        op.execute(f"ALTER TABLE {PROBEN} ADD COLUMN IF NOT EXISTS grenzwerte jsonb")
        op.execute(f"ALTER TABLE {PROBEN} ADD COLUMN IF NOT EXISTS bemerkung text")

    for table in present:
        _enable(table)


def downgrade() -> None:
    bind = op.get_bind()
    for table in TABELLEN:
        if not _exists(bind, table):
            continue
        for name in POLICIES:
            op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
    if _exists(bind, FOERDER):
        op.execute(f"ALTER TABLE {FOERDER} DROP CONSTRAINT IF EXISTS uq_ops_foerderantraege_tenant_nummer")
    if _exists(bind, PROBEN):
        # Befundangaben sind Belege: Spalten nur entfernen, wenn sie leer sind.
        belegt = bind.execute(sa.text(
            f"SELECT count(*) FROM {PROBEN} WHERE analysewerte IS NOT NULL OR grenzwerte IS NOT NULL OR bemerkung IS NOT NULL")).scalar()  # nosec B608
        if belegt:
            raise RuntimeError(f"{PROBEN}: {belegt} Befunde mit Angaben; Downgrade wuerde sie loeschen")
        for spalte in ("analysewerte", "grenzwerte", "bemerkung"):
            op.execute(f"ALTER TABLE {PROBEN} DROP COLUMN IF EXISTS {spalte}")
    for table in TABELLEN:
        if _exists(bind, table):
            op.execute(f"DROP INDEX IF EXISTS {OPS}.ix_{table.split('.')[1]}_tenant_id")
            op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS tenant_id")
