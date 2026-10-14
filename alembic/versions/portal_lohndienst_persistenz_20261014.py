"""Portal: Lohndienst-Auftraege und Empfehlungen in PostgreSQL; Portalrollen (PORTAL-CONTEXT-001).

Bis 14.10.2026 hielten Lohndienst-Auftraege und Empfehlungen ihre Daten nur im Arbeitsspeicher eines Prozesses: nach
Neustart oder Deployment waren sie verschwunden, bei mehreren Backend-Prozessen sah jeder etwas anderes.

* ``lohndienst_auftraege`` — verbindliche Auftraege mit Pflicht-Mandant und -Kunde, optimistischer Version und
  deterministischer Statusmaschine. Nicht loeschbar: ein Auftrag wird storniert.
* ``lohndienst_ereignisse`` — jede statusrelevante Aenderung mit Akteur, Kanal, Vorher/Nachher, Stand und
  Idempotenzschluessel (eindeutig je Mandant). Nur fortschreibbar. ``(auftrag_id, version)`` ist eindeutig: zwei
  Prozesse koennen denselben Stand nicht zweimal fortschreiben.
* ``empfehlungen`` — Vorschlaege an den Kunden mit Herkunft (``regel`` oder ``ki`` mit Modell), eindeutig je
  Ausloeser: dieselbe Erzeugung legt nichts doppelt an. Gesehen mit Person und Zeit.
* ``kundenzugaenge`` — Portalrollen nach Nutzerentscheidung (Betriebsleiter, Lohndienstleister, Aussendienst
  zusaetzlich) und zugewiesene Schlaege fuer Mitarbeiter.

Additiv: keine bestehende Zeile wird geaendert; die Rollenpruefung wird nur erweitert.
"""
from alembic import op

revision = "portal_lohndienst_persistenz_20261014"
down_revision = "portal_order_idempotency_20261014"
branch_labels = None
depends_on = None

_TYPEN = "'lohn_spritz', 'mahl_misch', 'lohn_mahlen', 'tmr_wagon', 'lohn_saatbett', 'lohn_ernte'"
_STATUS = "'angefragt', 'bestaetigt', 'eingeplant', 'abgeschlossen', 'storniert'"


def upgrade():
    op.execute("""
    ALTER TABLE domain_portal.kundenzugaenge DROP CONSTRAINT IF EXISTS kundenzugaenge_rolle_check;
    ALTER TABLE domain_portal.kundenzugaenge ALTER COLUMN rolle TYPE VARCHAR(20);
    ALTER TABLE domain_portal.kundenzugaenge ADD CONSTRAINT kundenzugaenge_rolle_check CHECK (rolle IN (
      'inhaber', 'betriebsleiter', 'mitarbeiter', 'buchhaltung', 'berater', 'lohndienstleister', 'aussendienst'));
    ALTER TABLE domain_portal.kundenzugaenge ADD COLUMN schlag_ids JSONB
      CONSTRAINT ck_kundenzugang_schlaege CHECK (schlag_ids IS NULL OR jsonb_typeof(schlag_ids) = 'array');
    """)
    op.execute(f"""
    CREATE TABLE domain_portal.lohndienst_auftraege (
      id VARCHAR(36) PRIMARY KEY,
      tenant_id VARCHAR NOT NULL,
      customer_id VARCHAR NOT NULL REFERENCES domain_crm.customers(id),
      typ VARCHAR(20) NOT NULL CHECK (typ IN ({_TYPEN})),
      status VARCHAR(20) NOT NULL DEFAULT 'angefragt' CHECK (status IN ({_STATUS})),
      schlag_ids JSONB NOT NULL DEFAULT '[]' CHECK (jsonb_typeof(schlag_ids) = 'array'),
      schlag_beschreibung TEXT NOT NULL DEFAULT '',
      flaeche_ha NUMERIC(12, 4) CHECK (flaeche_ha IS NULL OR flaeche_ha >= 0),
      wunsch_datum DATE,
      geplant_datum DATE,
      getreide_art TEXT,
      menge_dt NUMERIC(12, 3) CHECK (menge_dt IS NULL OR menge_dt >= 0),
      tierart TEXT,
      tiere_anzahl INTEGER CHECK (tiere_anzahl IS NULL OR tiere_anzahl >= 0),
      psm_mittel JSONB NOT NULL DEFAULT '[]' CHECK (jsonb_typeof(psm_mittel) = 'array'),
      kultur TEXT,
      anmerkung TEXT,
      innendienst_notiz TEXT,
      preis_indikativ_eur NUMERIC(14, 2),
      dienstleister_subject VARCHAR,
      version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
      angelegt_von VARCHAR NOT NULL,
      angelegt_am TIMESTAMPTZ NOT NULL DEFAULT now(),
      geaendert_von VARCHAR NOT NULL,
      geaendert_am TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT ck_lohndienst_eingeplant CHECK (status NOT IN ('eingeplant', 'abgeschlossen') OR geplant_datum IS NOT NULL)
    );
    CREATE INDEX ix_lohndienst_kunde ON domain_portal.lohndienst_auftraege (tenant_id, customer_id, angelegt_am DESC);
    CREATE INDEX ix_lohndienst_status ON domain_portal.lohndienst_auftraege (tenant_id, status);
    CREATE INDEX ix_lohndienst_dienstleister ON domain_portal.lohndienst_auftraege (tenant_id, dienstleister_subject)
      WHERE dienstleister_subject IS NOT NULL;

    CREATE TABLE domain_portal.lohndienst_ereignisse (
      id VARCHAR(36) PRIMARY KEY,
      tenant_id VARCHAR NOT NULL,
      auftrag_id VARCHAR(36) NOT NULL REFERENCES domain_portal.lohndienst_auftraege(id),
      aktion VARCHAR(20) NOT NULL CHECK (aktion IN ('anlegen', 'bestaetigen', 'einplanen', 'abschliessen', 'stornieren')),
      von_status VARCHAR(20),
      nach_status VARCHAR(20) NOT NULL CHECK (nach_status IN ({_STATUS})),
      version INTEGER NOT NULL CHECK (version >= 1),
      akteur VARCHAR NOT NULL,
      kanal VARCHAR(20) NOT NULL CHECK (kanal IN ('portal', 'intern')),
      idempotenz_schluessel VARCHAR(100) NOT NULL,
      anfrage_hash CHAR(64) NOT NULL,
      daten JSONB NOT NULL,
      erfasst_am TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT ux_lohndienst_ereignis_stand UNIQUE (auftrag_id, version),
      CONSTRAINT ux_lohndienst_ereignis_idempotenz UNIQUE (tenant_id, idempotenz_schluessel)
    );

    CREATE FUNCTION domain_portal.nur_fortschreiben() RETURNS trigger
      LANGUAGE plpgsql AS $$ BEGIN
        RAISE EXCEPTION '% wird nur fortgeschrieben, nicht geaendert oder geloescht', TG_TABLE_NAME;
      END $$;
    CREATE TRIGGER lohndienst_ereignisse_nur_fortschreiben BEFORE UPDATE OR DELETE
      ON domain_portal.lohndienst_ereignisse FOR EACH ROW EXECUTE FUNCTION domain_portal.nur_fortschreiben();
    CREATE TRIGGER lohndienst_ereignisse_kein_truncate BEFORE TRUNCATE
      ON domain_portal.lohndienst_ereignisse FOR EACH STATEMENT EXECUTE FUNCTION domain_portal.nur_fortschreiben();
    CREATE TRIGGER lohndienst_auftraege_kein_delete BEFORE DELETE
      ON domain_portal.lohndienst_auftraege FOR EACH ROW EXECUTE FUNCTION domain_portal.nur_fortschreiben();
    CREATE TRIGGER lohndienst_auftraege_kein_truncate BEFORE TRUNCATE
      ON domain_portal.lohndienst_auftraege FOR EACH STATEMENT EXECUTE FUNCTION domain_portal.nur_fortschreiben();

    CREATE TABLE domain_portal.empfehlungen (
      id VARCHAR(36) PRIMARY KEY,
      tenant_id VARCHAR NOT NULL,
      customer_id VARCHAR NOT NULL REFERENCES domain_crm.customers(id),
      typ VARCHAR(30) NOT NULL CHECK (typ IN ('ankauf_kontrakt', 'rohware_angebot', 'lohndienst', 'saatgut_folge',
                                              'duenger_planung', 'vertrag_erinnerung')),
      prioritaet VARCHAR(10) NOT NULL CHECK (prioritaet IN ('hoch', 'mittel', 'niedrig')),
      titel TEXT NOT NULL,
      beschreibung TEXT NOT NULL,
      cta_label TEXT NOT NULL,
      cta_ziel TEXT NOT NULL,
      kontext_schluessel VARCHAR(60) NOT NULL,
      kontext_wert VARCHAR(200) NOT NULL,
      artikel_id VARCHAR(100),
      betrag_indikativ NUMERIC(14, 2),
      gueltig_bis DATE,
      herkunft VARCHAR(10) NOT NULL CHECK (herkunft IN ('regel', 'ki')),
      modell VARCHAR(100),
      gesehen_am TIMESTAMPTZ,
      gesehen_von VARCHAR,
      erzeugt_von VARCHAR NOT NULL,
      erzeugt_am TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT ck_empfehlung_ki_modell CHECK (herkunft <> 'ki' OR modell IS NOT NULL),
      CONSTRAINT ck_empfehlung_gesehen CHECK ((gesehen_am IS NULL) = (gesehen_von IS NULL))
    );
    CREATE UNIQUE INDEX ux_empfehlung_ausloeser ON domain_portal.empfehlungen
      (tenant_id, customer_id, typ, kontext_schluessel, kontext_wert, coalesce(artikel_id, ''), cta_ziel);
    CREATE INDEX ix_empfehlung_kunde ON domain_portal.empfehlungen (tenant_id, customer_id, erzeugt_am DESC);
    """)


def downgrade():
    op.execute("""
    DROP TABLE domain_portal.empfehlungen;
    DROP TABLE domain_portal.lohndienst_ereignisse;
    DROP TABLE domain_portal.lohndienst_auftraege;
    DROP FUNCTION domain_portal.nur_fortschreiben();
    ALTER TABLE domain_portal.kundenzugaenge DROP COLUMN schlag_ids;
    ALTER TABLE domain_portal.kundenzugaenge DROP CONSTRAINT kundenzugaenge_rolle_check;
    ALTER TABLE domain_portal.kundenzugaenge ADD CONSTRAINT kundenzugaenge_rolle_check
      CHECK (rolle IN ('inhaber', 'mitarbeiter', 'buchhaltung', 'berater'));
    ALTER TABLE domain_portal.kundenzugaenge ALTER COLUMN rolle TYPE VARCHAR(16);
    """)
