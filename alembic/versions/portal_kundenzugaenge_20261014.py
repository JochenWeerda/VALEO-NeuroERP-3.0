"""Portal: gepruefte Zuordnung einer Anmeldung zu Kundenkonten (TENANT-DOC-001).

Bis 14.10.2026 bestimmte das Portal den Kunden aus einem frei uebergebenen Parameter, aus der Anmeldekennung
selbst oder gar nicht. Jetzt gilt nur, was hier zugeordnet ist: eine Anmeldung (OIDC ``sub``) darf je Mandant ein
oder mehrere CRM-Kundenkonten sehen. Eine Zuordnung wird widerrufen, nicht geloescht — wer wann wen sehen durfte,
bleibt nachvollziehbar. Jede Zuordnung traegt die Rolle der Person im Betrieb (Inhaber, Mitarbeiter, Buchhaltung,
bevollmaechtigter Berater); der Server prueft Mandant, Kundenbeziehung und Rolle bei jedem Zugriff.
"""
from alembic import op

revision = "portal_kundenzugaenge_20261014"
down_revision = "studio_history_20261014"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE SCHEMA IF NOT EXISTS domain_portal;
    CREATE TABLE domain_portal.kundenzugaenge (
      id VARCHAR(36) PRIMARY KEY,
      tenant_id VARCHAR NOT NULL,
      subject VARCHAR NOT NULL,
      customer_id VARCHAR NOT NULL,
      rolle VARCHAR(16) NOT NULL CHECK (rolle IN ('inhaber', 'mitarbeiter', 'buchhaltung', 'berater')),
      gueltig_bis TIMESTAMPTZ,
      angelegt_von VARCHAR NOT NULL,
      angelegt_am TIMESTAMPTZ NOT NULL DEFAULT now(),
      widerrufen_von VARCHAR,
      widerrufen_am TIMESTAMPTZ,
      CONSTRAINT ck_kundenzugang_widerruf CHECK ((widerrufen_am IS NULL) = (widerrufen_von IS NULL))
    );
    CREATE UNIQUE INDEX ux_kundenzugang_aktiv ON domain_portal.kundenzugaenge(tenant_id, subject, customer_id)
      WHERE widerrufen_am IS NULL;
    CREATE INDEX ix_kundenzugang_kunde ON domain_portal.kundenzugaenge(tenant_id, customer_id);
    CREATE FUNCTION domain_portal.kundenzugang_nicht_loeschen() RETURNS trigger
      LANGUAGE plpgsql AS $$ BEGIN
        RAISE EXCEPTION 'Kundenzugaenge werden widerrufen, nicht geloescht';
      END $$;
    CREATE TRIGGER kundenzugang_kein_delete BEFORE DELETE
      ON domain_portal.kundenzugaenge FOR EACH ROW
      EXECUTE FUNCTION domain_portal.kundenzugang_nicht_loeschen();
    CREATE TRIGGER kundenzugang_kein_truncate BEFORE TRUNCATE
      ON domain_portal.kundenzugaenge FOR EACH STATEMENT
      EXECUTE FUNCTION domain_portal.kundenzugang_nicht_loeschen();
    """)


def downgrade():
    op.execute("DROP TABLE domain_portal.kundenzugaenge")
    op.execute("DROP FUNCTION domain_portal.kundenzugang_nicht_loeschen()")
