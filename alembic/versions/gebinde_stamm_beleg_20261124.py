"""Gebinde-Mengeneinheit am Stamm, Gebindefaktoren je Stufe, Berechnungsabbild je Belegposition (24.11.2026).

Revision ID: gebinde_stamm_beleg_20261124
Revises: mengeneinheit_aeins_felder_20261124

Schnitt 2b-1 der Mengeneinheiten nach a.eins (docs/design/mengeneinheiten-aeins-uebernahme.md, Abschnitt 3):

* ``domain_shared.artikel_mengeneinheiten``: Gebindetyp (0-9 ohne die in a.eins deaktiven 6/7), Ergebniseinheit,
  Faktorherkunft (1-4, Pflicht bei einem Gebinde), Faktoren 1-4 der Stufe Mengeneinheit, LVS-Relevanz (0 nicht
  relevant, 1 relevant, 2 buchend) und LVS-Default-Lokalitaet. Bestehende Zeilen werden Typ 0 (kein Gebinde) und
  LVS 0 - das ist ihr heutiger Stand, kein erfundener Faktor.
* ``domain_shared.artikel_gebindefaktoren``: Faktoren der Stufen 2 Artikelstamm, 3 Artikel, 4 Artikel-Auspraegung je
  Mengeneinheit und Bezug, mandantengeschuetzt je Befehl.
* ``domain_docflow.document_items.gebinde_berechnung``: das Abbild der Gebinderechnung je Position. Einmal
  geschrieben, unveraenderlich (Trigger): historische Belege und ihre Stornos rechnen aus dem Abbild, nicht aus dem
  spaeter geaenderten Stamm.
"""
from __future__ import annotations

from alembic import op

revision = "gebinde_stamm_beleg_20261124"
down_revision = "mengeneinheit_aeins_felder_20261124"
branch_labels = None
depends_on = None

ME = "domain_shared.artikel_mengeneinheiten"
FAKTOREN = "domain_shared.artikel_gebindefaktoren"
POSITION = "domain_docflow.document_items"
OWN = "(tenant_id)::text = public.rls_current_tenant()"
ME_SPALTEN = (
    ("gebindetyp", "smallint NOT NULL DEFAULT 0"),
    ("ergebniseinheit", "varchar(10)"),
    ("faktorherkunft", "smallint"),
    ("faktor1", "numeric(18,6)"),
    ("faktor2", "numeric(18,6)"),
    ("faktor3", "numeric(18,6)"),
    ("faktor4", "numeric(18,6)"),
    ("lvs_relevanz", "smallint NOT NULL DEFAULT 0"),
    ("lvs_default_lokalitaet", "varchar(40)"),
)


def upgrade() -> None:
    for name, typ in ME_SPALTEN:
        op.execute(f"ALTER TABLE {ME} ADD COLUMN IF NOT EXISTS {name} {typ}")
    op.execute(f"ALTER TABLE {ME} ADD CONSTRAINT ck_mengeneinheit_gebindetyp "
               "CHECK (gebindetyp IN (0, 1, 2, 3, 4, 5, 8, 9))")
    op.execute(f"ALTER TABLE {ME} ADD CONSTRAINT ck_mengeneinheit_faktorherkunft "
               "CHECK (faktorherkunft BETWEEN 1 AND 4)")
    op.execute(f"ALTER TABLE {ME} ADD CONSTRAINT ck_mengeneinheit_gebinde_herkunft "
               "CHECK (gebindetyp = 0 OR faktorherkunft IS NOT NULL)")
    op.execute(f"ALTER TABLE {ME} ADD CONSTRAINT ck_mengeneinheit_lvs CHECK (lvs_relevanz BETWEEN 0 AND 2)")

    op.execute(f"""
        CREATE TABLE {FAKTOREN} (
            id varchar(36) PRIMARY KEY,
            tenant_id varchar(36) NOT NULL,
            einheit_kuerzel varchar(10) NOT NULL,
            stufe smallint NOT NULL CHECK (stufe BETWEEN 2 AND 4),
            bezug_id varchar(64) NOT NULL,
            faktor1 numeric(18,6),
            faktor2 numeric(18,6),
            faktor3 numeric(18,6),
            faktor4 numeric(18,6),
            geaendert_von varchar(200),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT uq_gebindefaktor UNIQUE (tenant_id, einheit_kuerzel, stufe, bezug_id)
        )
    """)
    op.execute(f"CREATE INDEX ix_gebindefaktor_tenant ON {FAKTOREN} (tenant_id)")
    op.execute(f"ALTER TABLE {FAKTOREN} ENABLE ROW LEVEL SECURITY")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {FAKTOREN} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {FAKTOREN} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {FAKTOREN} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {FAKTOREN} FOR DELETE USING ({OWN})")

    op.execute(f"ALTER TABLE {POSITION} ADD COLUMN IF NOT EXISTS gebinde_berechnung jsonb")
    op.execute("""
        CREATE OR REPLACE FUNCTION domain_docflow.gebinde_berechnung_unveraenderlich() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            IF OLD.gebinde_berechnung IS NOT NULL
               AND NEW.gebinde_berechnung IS DISTINCT FROM OLD.gebinde_berechnung THEN
                RAISE EXCEPTION 'Gebinderechnung einer Belegposition ist festgeschrieben (Position %)', OLD.id
                    USING ERRCODE = 'check_violation';
            END IF;
            RETURN NEW;
        END;
        $$
    """)
    op.execute(f"CREATE TRIGGER trg_gebinde_berechnung_unveraenderlich BEFORE UPDATE OF gebinde_berechnung "
               f"ON {POSITION} FOR EACH ROW EXECUTE FUNCTION domain_docflow.gebinde_berechnung_unveraenderlich()")


def downgrade() -> None:
    op.execute(f"DROP TRIGGER IF EXISTS trg_gebinde_berechnung_unveraenderlich ON {POSITION}")
    op.execute("DROP FUNCTION IF EXISTS domain_docflow.gebinde_berechnung_unveraenderlich()")
    op.execute("ALTER TABLE domain_docflow.document_items DROP COLUMN IF EXISTS gebinde_berechnung")
    op.execute("DROP TABLE IF EXISTS domain_shared.artikel_gebindefaktoren")
    for name in ("lvs", "gebinde_herkunft", "faktorherkunft", "gebindetyp"):
        op.execute(f"ALTER TABLE {ME} DROP CONSTRAINT IF EXISTS ck_mengeneinheit_{name}")
    for name, _ in reversed(ME_SPALTEN):
        op.execute(f"ALTER TABLE {ME} DROP COLUMN IF EXISTS {name}")
