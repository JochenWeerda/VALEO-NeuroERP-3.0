"""Batch 8 Scheinwege: Seeds und Testreste weg, Foerderung und Labor im Mandanten, Marketingtabelle entfernt.

Revision ID: scheinwege_mandant_20261103
Revises: waagen_wiegungen_mandant_20261103

Die Wege ``/foerderung``, ``/marketing`` und ``/labor`` legten bei jedem Lesezugriff Demodaten an und lasen und
schrieben ohne Mandanten. Nutzerentscheidung 04.11.2026: Seed-Tabellen ohne Studio-Maske oder mit Ersatz werden
entfernt, ersetzter Altbestand ohne Nutzer darf geloescht werden; Kampagnen fuehrt ``domain_crm.crm_campaigns``.

- ``ops_marketing_kampagnen``: nur die vollstaendige Geschaeftssignatur der beiden Seeds ist erlaubt;
  andere oder mehrfache Zeilen blockieren die Entfernung.
- ``ops_foerderantraege``, ``ops_labor_proben``, ``ops_labor_auftraege``: nur vollstaendige Seed-Signaturen werden geloescht.
  Testauftraege und Befunde bleiben erhalten, da Teilkennungen ihre Herkunft nicht beweisen.
  Mandantenspalte und RLS werden eingerichtet; Befundspalten werden ergaenzt.
- Uebrige Zeilen ohne Mandant (andere Installationen): Nutzerentscheidung 28.10.2026, Default-Mandant
  ``00000000-0000-0000-0000-000000000001``; fehlt er, bricht die Migration ab.

Abweichende Marketingzeilen muessen vorab fachlich geklaert werden.
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

# Geschaeftswerte aus f8bbdac5c^; generierte IDs/Zeitstempel sind nicht reproduzierbar.
SEED_KAMPAGNEN = """(name, typ, zielgruppe, startdatum, enddatum, budget, status) IN (
 ('Herbst-Aktion Weizen', 'E-Mail', 'Landwirte', '2025-10-01 00:00:00', '2025-10-31 00:00:00', 2500, 'beendet'),
 ('Fruehjahrs-Duenger-Kampagne', 'Newsletter', 'Ackerbau', '2026-02-15 00:00:00', '2026-03-31 00:00:00', 3000, 'aktiv'))"""
SEED_ANTRAEGE = """(nummer, programm, antragsdatum, flaeche, betrag, status) IN (
 ('FA-2026-001', 'Greening', '2026-03-15 00:00:00', 250, 21250, 'bewilligt'),
 ('FA-2026-002', 'Junglandwirte', '2026-04-01 00:00:00', 120, 15000, 'eingereicht'))"""
SEED_PROBEN = """(id, probennummer, typ, artikel, datum, labor, status) IN (
 ('LB-SEED-2026-001', 'LB-2026-001', 'Qualitaetspruefung', 'Weizen Premium', '2026-02-10 00:00:00', 'Lufa Nord-West', 'abgeschlossen'),
 ('LB-SEED-2026-002', 'LB-2026-002', 'Rueckstandsanalyse', 'Raps', '2026-02-11 00:00:00', 'SGS', 'in-bearbeitung'))"""
SEED_AUFTRAEGE = """(id, chargen_id, labor, analysen, auftragsdatum, status) IN (
 ('LA-SEED-WEI-001', '251011-WEI-001', 'Lufa Nord-West', 4, '2026-02-10 00:00:00', 'in-bearbeitung'),
 ('LA-SEED-RAP-002', '251010-RAP-002', 'SGS', 6, '2026-02-09 00:00:00', 'abgeschlossen'))"""


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
    if _has_column(bind, MARKETING, "tenant_id"):
        bestand = bind.execute(sa.text(f"SELECT count(*) FROM {MARKETING}")).scalar()  # nosec B608
        if bestand:
            raise RuntimeError(f"{MARKETING}: bereits mandantengebundener Bestand; vor Entfernung fachlich klaeren")
    bestand = bind.execute(sa.text(f"SELECT count(*) FROM {MARKETING} WHERE ({SEED_KAMPAGNEN}) IS NOT TRUE")).scalar()  # nosec B608
    mehrfach = bind.execute(sa.text(f"SELECT count(*) FROM (SELECT name FROM {MARKETING} GROUP BY name HAVING count(*) > 1) d")).scalar()  # nosec B608
    if bestand or mehrfach:
        raise RuntimeError(f"{MARKETING}: {bestand} abweichende Kampagnen und {mehrfach} doppelte Namen; Bestand fachlich klaeren")
    op.execute(f"DROP TABLE {MARKETING}")


def _seed_loeschen(bind) -> None:
    for table, predicate in ((FOERDER, SEED_ANTRAEGE), (PROBEN, SEED_PROBEN), (AUFTRAEGE, SEED_AUFTRAEGE)):
        if not _exists(bind, table):
            continue
        # Bereits zugeordnete oder erweiterte Zeilen koennen echte Nutzdaten tragen.
        if _has_column(bind, table, "tenant_id") or (table == PROBEN and any(
            _has_column(bind, table, column) for column in ("analysewerte", "grenzwerte", "bemerkung")
        )):
            continue
        if table == FOERDER:
            predicate += f" AND nummer IN (SELECT nummer FROM {FOERDER} GROUP BY nummer HAVING count(*) = 1)"
        op.execute(f"DELETE FROM {table} WHERE {predicate}")  # nosec B608


def upgrade() -> None:
    bind = op.get_bind()
    present = [t for t in TABELLEN if _exists(bind, t)]
    gesperrt = present + ([MARKETING] if _exists(bind, MARKETING) else [])
    if gesperrt:
        op.execute(f"LOCK TABLE {', '.join(gesperrt)} IN ACCESS EXCLUSIVE MODE")
    _marketing_entfernen(bind)
    _seed_loeschen(bind)

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
    """Struktur zurueck; vorhandene Fach- und Altzeilen bleiben erhalten."""
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
