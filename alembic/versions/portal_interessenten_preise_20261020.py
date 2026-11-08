"""Kundenportal: Interessenten und Preisspiegel als Tabellen statt Arbeitsspeicher.

Revision ID: portal_interessenten_preise_20261020
Revises: webshop_tabellen_20261020

``portal_interessent_service`` hielt Selbstregistrierungen (Name, E-Mail, Telefon, Betrieb) nur im Speicher; ein
Neustart verlor jeden Interessenten. ``portal_preisspiegel_service`` zeigte Portalkunden erfundene Getreidepreise
aus einer Saat-Liste als Handelskurse. Beides liegt jetzt mandantengenau in ``domain_shared`` (20.10.2026).
"""
from alembic import op

revision = "portal_interessenten_preise_20261020"
down_revision = "webshop_tabellen_20261020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.portal_interessenten (
            interessent_id    VARCHAR(64)   PRIMARY KEY,
            tenant_id         VARCHAR(80)   NOT NULL,
            status            VARCHAR(20)   NOT NULL DEFAULT 'interessent',
            vorname           VARCHAR(120)  NOT NULL,
            nachname          VARCHAR(120)  NOT NULL,
            email             VARCHAR(255)  NOT NULL,
            telefon           VARCHAR(64),
            betrieb_name      VARCHAR(255),
            betrieb_typ       VARCHAR(40),
            flaeche_ha        NUMERIC(12, 2),
            hauptkulturen     JSONB         NOT NULL DEFAULT '[]'::jsonb,
            tiere_anzahl      INTEGER,
            tierart           VARCHAR(120),
            plz               VARCHAR(16),
            ort               VARCHAR(120),
            interesse_themen  JSONB         NOT NULL DEFAULT '[]'::jsonb,
            anmerkung         TEXT,
            zugewiesen_an     VARCHAR(120),
            kunden_nr         VARCHAR(64),
            qualifiziert_am   TIMESTAMPTZ,
            konvertiert_am    TIMESTAMPTZ,
            erstellt_am       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
            aktualisiert_am   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
            CONSTRAINT ck_portal_interessent_status
                CHECK (status IN ('interessent', 'qualifiziert', 'kunde', 'abgelehnt', 'inaktiv'))
        )
    """)
    # Doppelregistrierung: eine aktive Registrierung je E-Mail und Mandant (inaktive duerfen sich neu melden).
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_portal_interessent_email ON domain_shared.portal_interessenten "
               "(tenant_id, lower(email)) WHERE status <> 'inaktiv'")
    op.execute("CREATE INDEX IF NOT EXISTS ix_portal_interessent_tenant "
               "ON domain_shared.portal_interessenten (tenant_id, erstellt_am DESC)")
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.portal_preise (
            preis_id          VARCHAR(64)   PRIMARY KEY,
            tenant_id         VARCHAR(80)   NOT NULL,
            artikel_id        VARCHAR(64)   NOT NULL,
            artikel_name      VARCHAR(255)  NOT NULL,
            frucht_gruppe     VARCHAR(80)   NOT NULL,
            variante          VARCHAR(40)   NOT NULL,
            preis_eur_dt      NUMERIC(10, 2) NOT NULL,
            basis_qualitaet   VARCHAR(120)  NOT NULL,
            ernte_jahr        INTEGER       NOT NULL,
            liefermonat       VARCHAR(7),
            aufschlag_eur_dt  NUMERIC(10, 2) NOT NULL DEFAULT 0,
            quelle            VARCHAR(40)   NOT NULL DEFAULT 'manuell',
            gueltig_ab        DATE          NOT NULL,
            gueltig_bis       DATE,
            hinweis           TEXT,
            gepflegt_von      VARCHAR(120)  NOT NULL,
            abgeloest_am      TIMESTAMPTZ,
            erstellt_am       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
            aktualisiert_am   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
            CONSTRAINT ck_portal_preis_variante CHECK (variante IN
                ('altware_ab_hof', 'altware_frei_lager', 'neue_ernte_frei_lager', 'neue_ernte_ab_hof'))
        )
    """)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_portal_preis_aktuell ON domain_shared.portal_preise "
               "(tenant_id, artikel_id, variante, ernte_jahr) WHERE abgeloest_am IS NULL")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_shared.portal_preise")
    op.execute("DROP TABLE IF EXISTS domain_shared.portal_interessenten")
