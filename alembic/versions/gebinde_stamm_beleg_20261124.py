"""Gebinde-Mengeneinheit am Stamm, Gebindefaktoren je Artikel, versionierte Berechnungsabbilder (24.11.2026).

Revision ID: gebinde_stamm_beleg_20261124
Revises: mengeneinheit_aeins_felder_20261124

Schnitt 2b-1 der Mengeneinheiten nach a.eins (docs/design/mengeneinheiten-aeins-uebernahme.md, Abschnitt 3 und 4):

* ``domain_shared.artikel_mengeneinheiten``: Gebindetyp (0-9 ohne die in a.eins deaktiven 6/7), Ergebniseinheit,
  Faktorherkunft (1-4, Pflicht bei einem Gebinde), Faktoren 1-4 der Stufe Mengeneinheit, LVS-Relevanz (0 nicht
  relevant, 1 relevant, 2 buchend) und LVS-Default-Lokalitaet. Bestehende Zeilen werden Typ 0 (kein Gebinde) und
  LVS 0 - ihr heutiger Stand, kein erfundener Faktor.
* ``domain_shared.artikel_gebindefaktoren``: Faktoren der Stufe 3 Artikel, referenziell an
  ``domain_inventory.articles`` und die Mengeneinheit desselben Mandanten gebunden (zusammengesetzte Fremdschluessel).
  Die a.eins-Stufen 2 Artikelstamm und 4 Artikel-Auspraegung haben in VALEO noch kein Gegenstueck; sie sind erst
  pflegbar, wenn die Zuordnung fachlich festgelegt ist (kein freier Bezug, keine parallele Stammdatenstruktur).
* ``domain_docflow.document_item_gebinde_abbilder``: jede Berechnung einer Position als neue, unveraenderliche Version
  (nur anfuegen). ``document_items.gebinde_berechnung`` traegt die geltende Version; sie ist aenderbar, solange der
  Beleg nicht verbindlich gebucht ist, und ab dann gesperrt (Trigger). Storno und Retoure rechnen aus dem Abbild.
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
ABBILDER = "domain_docflow.document_item_gebinde_abbilder"
OWN = "(tenant_id)::text = public.rls_current_tenant()"
#: Ab diesen Belegstaenden ist eine Position verbindlich gebucht und ihr Abbild unveraenderlich.
GEBUCHT = "('posted', 'completed', 'reversed', 'cancelled')"
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


def _rls(tabelle: str) -> None:
    op.execute(f"ALTER TABLE {tabelle} ENABLE ROW LEVEL SECURITY")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {tabelle} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {tabelle} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {tabelle} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {tabelle} FOR DELETE USING ({OWN})")


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
            stufe smallint NOT NULL CONSTRAINT ck_gebindefaktor_stufe CHECK (stufe = 3),
            artikel_id varchar NOT NULL,
            faktor1 numeric(18,6),
            faktor2 numeric(18,6),
            faktor3 numeric(18,6),
            faktor4 numeric(18,6),
            geaendert_von varchar(200),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT uq_gebindefaktor UNIQUE (tenant_id, einheit_kuerzel, stufe, artikel_id),
            CONSTRAINT fk_gebindefaktor_artikel FOREIGN KEY (artikel_id, tenant_id)
                REFERENCES domain_inventory.articles (id, tenant_id) ON DELETE CASCADE,
            CONSTRAINT fk_gebindefaktor_einheit FOREIGN KEY (tenant_id, einheit_kuerzel)
                REFERENCES {ME} (tenant_id, einheit_kuerzel) ON DELETE CASCADE
        )
    """)
    op.execute(f"CREATE INDEX ix_gebindefaktor_artikel ON {FAKTOREN} (artikel_id, tenant_id)")
    _rls(FAKTOREN)

    op.execute(f"""
        CREATE TABLE {ABBILDER} (
            id varchar(36) PRIMARY KEY,
            tenant_id varchar NOT NULL,
            position_id varchar NOT NULL,
            version integer NOT NULL CHECK (version >= 1),
            abbild jsonb NOT NULL CHECK (jsonb_typeof(abbild) = 'object'),
            erstellt_von varchar(200),
            erstellt_am timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT uq_gebinde_abbild_version UNIQUE (position_id, version),
            CONSTRAINT fk_gebinde_abbild_position FOREIGN KEY (position_id, tenant_id)
                REFERENCES {POSITION} (id, tenant_id) ON DELETE CASCADE
        )
    """)
    _rls(ABBILDER)
    op.execute(f"ALTER TABLE {POSITION} ADD COLUMN IF NOT EXISTS gebinde_berechnung jsonb")
    op.execute(f"""
        CREATE OR REPLACE FUNCTION domain_docflow.gebinde_position_gebucht(p_header varchar, p_tenant varchar)
        RETURNS boolean LANGUAGE sql STABLE AS $$
            SELECT EXISTS (SELECT 1 FROM domain_docflow.document_headers h
                           WHERE h.id = p_header AND h.tenant_id = p_tenant AND h.status IN {GEBUCHT})
        $$
    """)
    op.execute("""
        CREATE OR REPLACE FUNCTION domain_docflow.gebinde_berechnung_sperre() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.gebinde_berechnung IS DISTINCT FROM OLD.gebinde_berechnung
               AND domain_docflow.gebinde_position_gebucht(OLD.header_id, OLD.tenant_id) THEN
                RAISE EXCEPTION 'Gebinderechnung einer gebuchten Belegposition ist festgeschrieben (Position %)', OLD.id
                    USING ERRCODE = 'check_violation';
            END IF;
            RETURN NEW;
        END;
        $$
    """)
    op.execute(f"CREATE TRIGGER trg_gebinde_berechnung_sperre BEFORE UPDATE OF gebinde_berechnung ON {POSITION} "
               "FOR EACH ROW EXECUTE FUNCTION domain_docflow.gebinde_berechnung_sperre()")
    op.execute("""
        CREATE OR REPLACE FUNCTION domain_docflow.gebinde_abbild_nur_anfuegen() RETURNS trigger
        LANGUAGE plpgsql AS $$
        DECLARE kopf varchar;
        BEGIN
            IF TG_OP = 'UPDATE' THEN
                RAISE EXCEPTION 'Gebinde-Abbilder sind unveraenderlich (Version % der Position %)',
                    OLD.version, OLD.position_id USING ERRCODE = 'check_violation';
            END IF;
            SELECT header_id INTO kopf FROM domain_docflow.document_items
             WHERE id = COALESCE(NEW.position_id, OLD.position_id);
            IF kopf IS NOT NULL AND domain_docflow.gebinde_position_gebucht(kopf, COALESCE(NEW.tenant_id, OLD.tenant_id)) THEN
                RAISE EXCEPTION 'Position % gehoert zu einem gebuchten Beleg - Abbilder unveraenderlich',
                    COALESCE(NEW.position_id, OLD.position_id) USING ERRCODE = 'check_violation';
            END IF;
            RETURN COALESCE(NEW, OLD);
        END;
        $$
    """)
    op.execute(f"CREATE TRIGGER trg_gebinde_abbild_nur_anfuegen BEFORE INSERT OR UPDATE OR DELETE ON {ABBILDER} "
               "FOR EACH ROW EXECUTE FUNCTION domain_docflow.gebinde_abbild_nur_anfuegen()")


def downgrade() -> None:
    op.execute(f"DROP TRIGGER IF EXISTS trg_gebinde_berechnung_sperre ON {POSITION}")
    op.execute("DROP TABLE IF EXISTS domain_docflow.document_item_gebinde_abbilder")
    op.execute("DROP FUNCTION IF EXISTS domain_docflow.gebinde_abbild_nur_anfuegen()")
    op.execute("DROP FUNCTION IF EXISTS domain_docflow.gebinde_berechnung_sperre()")
    op.execute("DROP FUNCTION IF EXISTS domain_docflow.gebinde_position_gebucht(varchar, varchar)")
    op.execute("ALTER TABLE domain_docflow.document_items DROP COLUMN IF EXISTS gebinde_berechnung")
    op.execute("DROP TABLE IF EXISTS domain_shared.artikel_gebindefaktoren")
    for name in ("lvs", "gebinde_herkunft", "faktorherkunft", "gebindetyp"):
        op.execute(f"ALTER TABLE {ME} DROP CONSTRAINT IF EXISTS ck_mengeneinheit_{name}")
    for name, _ in reversed(ME_SPALTEN):
        op.execute(f"ALTER TABLE {ME} DROP COLUMN IF EXISTS {name}")
