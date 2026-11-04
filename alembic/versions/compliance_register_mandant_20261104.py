"""Batch 9: Compliance-Register und Zertifikate im Mandanten, Disposition und zertifikate_api entfernt.

Revision ID: compliance_register_mandant_20261104
Revises: scheinwege_mandant_20261103

Nutzerentscheidung 04.11.2026: Seed-Tabellen ohne Studio-Maske oder mit Ersatz werden entfernt, ersetzter
Altbestand ohne Nutzer darf geloescht werden.

- ``ops_disposition``: handgepflegter Bestand/Mindestbestand/Empfehlung, ersetzt durch den Bestellvorschlag
  (rechnet aus echtem Bestand und Meldebestand) -> entfernt. Enthaelt sie anderes als Seed (ART-001..003) und
  Testreste (ART-TEST-001), bricht die Migration ab.
- ``ops_zertifikate_api``: zweiter Zertifikatsweg, dessen POST vom ersten ueberdeckt war und dessen Lesewege den
  Mandanten aus dem Pfad nahmen bzw. alle Mandanten lasen -> entfernt (leer; Zeilen braechen ab).
- Cross-Compliance, ENNI, QS-Checkliste, Zulassungen, Kunden-Sachkunde, Saatgut-Nachbau, VVVO und Zertifikate
  (Studio-Masken vorhanden): Seed-Zeilen (exakte Signaturen aus ``seed_compliance_data`` bzw. ``_seed``) und die
  Testreste von ``test_process_kernel_wave9_integration`` werden geloescht, dann Mandantenspalte mit RLS (Policy je
  Befehl). Uebrige Zeilen ohne Mandant: Default-Mandant (Nutzerentscheidung 28.10.2026); fehlt er -> Abbruch.

Gewachsene Datenbank 04.11.2026: alle Zeilen der zehn Tabellen sind Seed oder Testrest.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "compliance_register_mandant_20261104"
down_revision = "scheinwege_mandant_20261103"
branch_labels = None
depends_on = None

#: Nutzerentscheidung 28.10.2026 (Altbestand -> Default Tenant), nur fuer verbleibende echte Zeilen.
ALTBESTAND_MANDANT = "00000000-0000-0000-0000-000000000001"
OPS = "domain_ops"
DISPOSITION = f"{OPS}.ops_disposition"
ZERT_API = f"{OPS}.ops_zertifikate_api"

#: Tabelle -> Bedingung, die genau die frueheren Seed-Zeilen (und bekannten Testreste) trifft.
SEEDS = {
    f"{OPS}.ops_compliance_items": "(bereich, anforderung) IN (('Gewaesserschutz', 'Gewaesserrandstreifen 5m'), "
                                   "('Duengeverordnung', 'Naehrstoffbilanz erstellt'), "
                                   "('PSM-Dokumentation', 'Anwendungsprotokolle vollstaendig'))",
    f"{OPS}.ops_enni_meldungen": "(typ, betrieb, vvvo) IN (('DBE', 'Landwirtschaft Mueller', '03-276-1234'), "
                                 "('WDE', 'Agrar Schmidt', '03-276-5678'))",
    f"{OPS}.ops_qs_checks": "(bereich, pruefpunkt) IN (('Wareneingangskontrolle', 'Lieferschein-Pruefung'), "
                            "('Temperaturkontrolle', 'Lagerungstemperatur dokumentiert'))",
    f"{OPS}.ops_zulassungen_register": "(produkt, nummer) IN (('Roundup PowerFlex', '024567-00'), ('Fungizid X', '024568-00'))",
    f"{OPS}.ops_sachkunde_register": "(kundennr, nachweis_nr) = ('K-10023', 'SK-NDS-2022-4567')",
    f"{OPS}.ops_saatgut_nachbau": "(betrieb, sorte, erntejahr) = ('Landwirtschaft Mueller', 'Weichweizen Eltan', 2024)",
    f"{OPS}.ops_vvvo_register": "(betriebsname, vvvo) = ('Landwirtschaft Mueller', '03-276-123456')",
    f"{OPS}.ops_zertifikate": "nummer IN ('BIO-2025-1234', 'QS-2025-5678', 'GGN-12345678') "
                              "OR (art = 'qs_gap' AND standard = 'QS' AND nummer = 'QS-2025-9999')",
}
TABELLEN = tuple(SEEDS)
DISPOSITION_ALT = "artikel_id IN ('ART-001', 'ART-002', 'ART-003', 'ART-TEST-001')"
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


def _entfernen(bind, table: str, nur_diese: str | None) -> None:
    if not _exists(bind, table):
        return
    bedingung = f"NOT ({nur_diese})" if nur_diese else "TRUE"
    fremd = bind.execute(sa.text(f"SELECT count(*) FROM {table} WHERE {bedingung}")).scalar()  # nosec B608
    if fremd:
        raise RuntimeError(f"{table}: {fremd} Zeilen ausser Seed/Testrest; erst uebernehmen, dann entfernen")
    op.execute(f"DROP TABLE {table}")


def upgrade() -> None:
    bind = op.get_bind()
    present = [t for t in TABELLEN if _exists(bind, t)]
    gesperrt = present + [t for t in (DISPOSITION, ZERT_API) if _exists(bind, t)]
    if gesperrt:
        op.execute(f"LOCK TABLE {', '.join(gesperrt)} IN ACCESS EXCLUSIVE MODE")
    _entfernen(bind, DISPOSITION, DISPOSITION_ALT)
    _entfernen(bind, ZERT_API, None)

    for table in present:
        op.execute(f"DELETE FROM {table} WHERE {SEEDS[table]}")  # nosec B608
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
        _enable(table)


def downgrade() -> None:
    """Struktur zurueck; geloeschte Seeds, Testreste und entfernte Tabelleninhalte kommen nicht wieder."""
    bind = op.get_bind()
    for table in TABELLEN:
        if not _exists(bind, table):
            continue
        for name in POLICIES:
            op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
        op.execute(f"DROP INDEX IF EXISTS {OPS}.ix_{table.split('.')[1]}_tenant_id")
        op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS tenant_id")
    op.execute(f"""CREATE TABLE IF NOT EXISTS {DISPOSITION} (
        id varchar PRIMARY KEY, artikel varchar(255) NOT NULL, artikel_id varchar(80), bestand double precision,
        mindestbestand double precision, bedarf double precision, empfehlung varchar(255), prioritaet varchar(30),
        created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now())""")
