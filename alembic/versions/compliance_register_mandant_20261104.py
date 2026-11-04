"""Batch 9: Compliance-Register und Zertifikate im Mandanten, Disposition und zertifikate_api entfernt.

Revision ID: compliance_register_mandant_20261104
Revises: scheinwege_mandant_20261103

Nutzerentscheidung 04.11.2026: Seed-Tabellen ohne Studio-Maske oder mit Ersatz werden entfernt, ersetzter
Altbestand ohne Nutzer darf geloescht werden.

- ``ops_disposition`` und ``ops_zertifikate_api`` sind ausgemustert; ihre vorhandenen Zeilen sind
  laut Nutzerentscheidung 04.11.2026 Testdaten. Nach Verbraucherabbau werden beide Tabellen ohne CASCADE entfernt.
- Cross-Compliance, ENNI, QS-Checkliste, Zulassungen, Kunden-Sachkunde, Saatgut-Nachbau, VVVO und Zertifikate
  (Studio-Masken vorhanden): exakte Signaturen aus ``seed_compliance_data`` bzw. ``_seed``:
  eindeutig nachweisbare Seed-Zeilen werden geloescht, dann Mandantenspalte mit RLS (Policy je
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

#: Nur vollstaendige, deterministische Geschaeftsfelder der urspruenglichen Seeds.
#: Zufalls-IDs und Erzeugungszeitpunkte sind nicht reproduzierbar; Testreste unbekannter
#: Herkunft bleiben erhalten. Zeitwerte entsprechen den naiven datetime()-Seedwerten.
SEEDS = {
    f"{OPS}.ops_compliance_items": "(bereich, anforderung, erfuellt, nachweis, frist) IN ("
        "('Gewaesserschutz', 'Gewaesserrandstreifen 5m', TRUE, 'Feldprotokoll', '2026-12-31 00:00:00'), "
        "('Duengeverordnung', 'Naehrstoffbilanz erstellt', TRUE, 'Bilanz 2025/26', '2026-03-31 00:00:00'), "
        "('PSM-Dokumentation', 'Anwendungsprotokolle vollstaendig', FALSE, '', '2026-03-15 00:00:00'))",
    f"{OPS}.ops_enni_meldungen": "(typ, betrieb, vvvo, datum, status, naehrstoff_n, naehrstoff_p, naehrstoff_k) IN ("
        "('DBE', 'Landwirtschaft Mueller', '03-276-1234', '2026-01-15 00:00:00', 'bestaetigt', 180, 60, 120), "
        "('WDE', 'Agrar Schmidt', '03-276-5678', '2026-02-01 00:00:00', 'gesendet', 150, 45, 90))",
    f"{OPS}.ops_qs_checks": "(bereich, pruefpunkt, erfuellt, bemerkung, geprueft_am) IN ("
        "('Wareneingangskontrolle', 'Lieferschein-Pruefung', TRUE, 'Vollstaendig', '2026-02-10 00:00:00'), "
        "('Temperaturkontrolle', 'Lagerungstemperatur dokumentiert', TRUE, 'Im Normbereich', '2026-02-10 00:00:00'))",
    f"{OPS}.ops_zulassungen_register": "(produkt, typ, nummer, behoerde, gueltig_bis, status) IN ("
        "('Roundup PowerFlex', 'PSM', '024567-00', 'BVL', '2026-12-31 00:00:00', 'aktiv'), "
        "('Fungizid X', 'PSM', '024568-00', 'BVL', '2025-06-30 00:00:00', 'auslaufend'))",
    f"{OPS}.ops_sachkunde_register": "(kunde, kundennr, nachweis_nr, ausstellungsdatum, gueltig_bis, ausstellende_stelle, status) = "
        "('Landwirtschaft Mueller', 'K-10023', 'SK-NDS-2022-4567', '2022-03-15 00:00:00', '2025-03-15 00:00:00', 'LWK Niedersachsen', 'ablaufend')",
    f"{OPS}.ops_saatgut_nachbau": "(betrieb, sorte, kultur, flaeche, erntejahr, gebuehr, status) = "
        "('Landwirtschaft Mueller', 'Weichweizen Eltan', 'Weichweizen', 45.5, 2024, 682.50, 'bezahlt')",
    f"{OPS}.ops_vvvo_register": "(betriebsname, vvvo, bundesland, tierart, status, letzte_aktualisierung) = "
        "('Landwirtschaft Mueller', '03-276-123456', 'Niedersachsen', 'Rind (Milch)', 'aktiv', '2026-01-15 00:00:00')",
    f"{OPS}.ops_zertifikate": "(art, standard, nummer, gueltig_bis, audit, status) IN ("
        "('Bio-Zertifikat', 'EU-Bio-Verordnung', 'BIO-2025-1234', '2026-12-31 00:00:00', '2026-02-15 00:00:00', 'gueltig'), "
        "('QS-Zertifikat', 'QS-GAP', 'QS-2025-5678', '2026-06-30 00:00:00', '2025-12-01 00:00:00', 'gueltig'), "
        "('GlobalG.A.P.', 'GGN', 'GGN-12345678', '2025-09-30 00:00:00', '2025-08-15 00:00:00', 'ablaufend'))",
}
TABELLEN = tuple(SEEDS)
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


def _entfernen(bind, table: str) -> None:
    # Die beiden ausgemusterten Tabellen enthalten laut Nutzerentscheidung nur Testdaten.
    if _exists(bind, table):
        op.execute(f"DROP TABLE {table}")


def _seed_loeschen(bind, table: str) -> None:
    # Bereits mandantengebundene Zeilen koennen echte Geschaeftsdaten sein.
    if not _has_column(bind, table, "tenant_id"):
        op.execute(f"DELETE FROM {table} WHERE {SEEDS[table]}")  # nosec B608


def upgrade() -> None:
    bind = op.get_bind()
    present = [t for t in TABELLEN if _exists(bind, t)]
    gesperrt = present + [t for t in (DISPOSITION, ZERT_API) if _exists(bind, t)]
    if gesperrt:
        op.execute(f"LOCK TABLE {', '.join(gesperrt)} IN ACCESS EXCLUSIVE MODE")
    _entfernen(bind, DISPOSITION)
    _entfernen(bind, ZERT_API)

    for table in present:
        _seed_loeschen(bind, table)
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
