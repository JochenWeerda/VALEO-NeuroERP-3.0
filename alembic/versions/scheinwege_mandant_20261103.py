"""Batch 8 Scheinwege: Seeds und Testreste weg, Foerderung und Labor im Mandanten, Marketingtabelle entfernt.

Revision ID: scheinwege_mandant_20261103
Revises: waagen_wiegungen_mandant_20261103

Die Wege ``/foerderung``, ``/marketing`` und ``/labor`` legten bei jedem Lesezugriff Demodaten an und lasen und
schrieben ohne Mandanten. Nutzerentscheidung 04.11.2026: Seed-Tabellen ohne Studio-Maske oder mit Ersatz werden
entfernt, ersetzter Altbestand ohne Nutzer darf geloescht werden; Kampagnen fuehrt ``domain_crm.crm_campaigns``.

- ``ops_marketing_kampagnen``: ersetzt durch die CRM-Kampagnen, kein Weg liest sie mehr -> entfernt. Enthaelt sie
  andere Zeilen als die zwei frueheren Seed-Kampagnen, bricht die Migration ab (nichts Echtes wird verworfen).
- ``ops_foerderantraege``, ``ops_labor_proben``, ``ops_labor_auftraege`` (Studio-Masken vorhanden): Seed-Zeilen und
  die Testreste von ``tests/test_labor_api.py`` (Chargen ``TEST-CHARGE-%`` bei ``Test-Labor`` samt Befunden) werden
  geloescht - an ihrer exakten Signatur, nicht an Mustern allein. Danach Mandantenspalte mit RLS (Policy je Befehl),
  Antragsnummer je Mandant eindeutig, Befundspalten, die der Befundweg bisher nur zurueckgab.
- Uebrige Zeilen ohne Mandant (andere Installationen): Nutzerentscheidung 28.10.2026, Default-Mandant
  ``00000000-0000-0000-0000-000000000001``; fehlt er, bricht die Migration ab.

Gewachsene Datenbank 03.11.2026: alle Zeilen der vier Tabellen sind Seed oder Testrest (2 Antraege, 2 Kampagnen,
7 Proben, 74 Auftraege).
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "scheinwege_mandant_20261103"
down_revision = "waagen_wiegungen_mandant_20261103"
branch_labels = None
depends_on = None

#: Nutzerentscheidung 28.10.2026 (Altbestand -> Default Tenant), nur fuer verbleibende echte Zeilen.
ALTBESTAND_MANDANT = "00000000-0000-0000-0000-000000000001"
OPS = "domain_ops"
FOERDER = f"{OPS}.ops_foerderantraege"
PROBEN = f"{OPS}.ops_labor_proben"
AUFTRAEGE = f"{OPS}.ops_labor_auftraege"
MARKETING = f"{OPS}.ops_marketing_kampagnen"
TABELLEN = (FOERDER, PROBEN, AUFTRAEGE)
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))

# Exakte Signaturen der frueheren _seed-Funktionen und der Testreste.
SEED_KAMPAGNEN = ("Herbst-Aktion Weizen", "Fruehjahrs-Duenger-Kampagne")
SEED_ANTRAEGE = "(nummer, programm, flaeche, betrag) IN (('FA-2026-001', 'Greening', 250, 21250), ('FA-2026-002', 'Junglandwirte', 120, 15000))"
SEED_PROBEN = "id IN ('LB-SEED-2026-001', 'LB-SEED-2026-002')"
SEED_AUFTRAEGE = "id IN ('LA-SEED-WEI-001', 'LA-SEED-RAP-002')"
TEST_AUFTRAEGE = "chargen_id IN ('TEST-CHARGE-001', 'TEST-CHARGE-SPERRE-001') AND labor = 'Test-Labor'"


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


def _marketing_entfernen(bind) -> None:
    if not _exists(bind, MARKETING):
        return
    fremd = bind.execute(sa.text(f"SELECT count(*) FROM {MARKETING} WHERE name NOT IN :n").bindparams(  # nosec B608
        sa.bindparam("n", expanding=True)), {"n": list(SEED_KAMPAGNEN)}).scalar()
    if fremd:
        raise RuntimeError(f"{MARKETING}: {fremd} Kampagnen ausser dem Seed; erst in domain_crm.crm_campaigns uebernehmen")
    op.execute(f"DROP TABLE {MARKETING}")


def _seed_und_testreste_loeschen(bind) -> None:
    if _exists(bind, FOERDER):
        op.execute(f"DELETE FROM {FOERDER} WHERE {SEED_ANTRAEGE}")  # nosec B608
    if _exists(bind, PROBEN) and _exists(bind, AUFTRAEGE):
        op.execute(f"DELETE FROM {PROBEN} WHERE probennummer IN (SELECT 'BEF-' || id FROM {AUFTRAEGE} "  # nosec B608
                   f"WHERE {TEST_AUFTRAEGE} OR {SEED_AUFTRAEGE})")
    if _exists(bind, PROBEN):
        op.execute(f"DELETE FROM {PROBEN} WHERE {SEED_PROBEN}")  # nosec B608
    if _exists(bind, AUFTRAEGE):
        op.execute(f"DELETE FROM {AUFTRAEGE} WHERE {TEST_AUFTRAEGE} OR {SEED_AUFTRAEGE}")  # nosec B608


def upgrade() -> None:
    bind = op.get_bind()
    present = [t for t in TABELLEN if _exists(bind, t)]
    gesperrt = present + ([MARKETING] if _exists(bind, MARKETING) else [])
    if gesperrt:
        op.execute(f"LOCK TABLE {', '.join(gesperrt)} IN ACCESS EXCLUSIVE MODE")
    _marketing_entfernen(bind)
    _seed_und_testreste_loeschen(bind)

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
    """Struktur zurueck; geloeschte Seeds und Testreste kommen nicht wieder (es waren Scheindaten)."""
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
    op.execute(f"""CREATE TABLE IF NOT EXISTS {MARKETING} (
        id varchar PRIMARY KEY, name varchar(255) NOT NULL, typ varchar(80) NOT NULL, zielgruppe varchar(120),
        startdatum timestamptz, enddatum timestamptz, budget numeric(14, 2) DEFAULT 0, status varchar(30) DEFAULT 'geplant',
        created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now())""")
