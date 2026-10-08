"""Postfaecher je Mandant: ausgehende E-Mails ueber den Dienst des Mandanten.

Revision ID: mailkonto_mandant_20261008
Revises: offenes_schliessen_20261008

Bis 08.10.2026 gab es fuer den Mailversand nur Umgebungsvariablen der Plattform.
Jetzt fuehrt jeder Mandant beliebig viele Postfaecher (info@, dispo@, fibu@,
zentrale@, persoenliche Postfaecher):

* Zugang: IONOS, Google (App-Passwort oder Google-Anmeldung), allgemeines SMTP — oder
  ``zugang_von``: ein Alias, der die Anmeldung eines anderen Postfachs nutzt.
* Geheimnis (Passwort/Refresh-Token) AES-GCM-verschluesselt; Klartext verbietet die
  Pruefbedingung.
* ``verwendungen``: wofuer das Postfach automatisch genommen wird (einkauf, fibu …);
  ``ist_standard``: Rueckfall.
* Zugriff: ``rollen``/``benutzer`` (leer = alle im Mandanten), ``persoenlich_fuer``
  (nur der Inhaber).
"""

from alembic import op

revision = "mailkonto_mandant_20261008"
down_revision = "offenes_schliessen_20261008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_shared.mailkonten (
            id               VARCHAR(36) PRIMARY KEY,
            tenant_id        VARCHAR(64) NOT NULL REFERENCES domain_shared.tenants(id),
            kennung          VARCHAR(40) NOT NULL,
            bezeichnung      VARCHAR(120),
            anbieter         VARCHAR(20) NOT NULL,
            anmeldung        VARCHAR(20) NOT NULL DEFAULT 'passwort',
            smtp_host        VARCHAR(255),
            smtp_port        INTEGER,
            sicherheit       VARCHAR(10) NOT NULL DEFAULT 'starttls',
            benutzer         VARCHAR(255),
            absender_email   VARCHAR(255) NOT NULL,
            absender_name    VARCHAR(255),
            geheimnis        TEXT,
            zugang_von       VARCHAR(36) REFERENCES domain_shared.mailkonten(id),
            ist_standard     BOOLEAN NOT NULL DEFAULT FALSE,
            verwendungen     TEXT[] NOT NULL DEFAULT '{}',
            rollen           TEXT[] NOT NULL DEFAULT '{}',
            benutzer_freigabe TEXT[] NOT NULL DEFAULT '{}',
            persoenlich_fuer VARCHAR(100),
            status           VARCHAR(20) NOT NULL DEFAULT 'neu',
            geprueft_am      TIMESTAMPTZ,
            letzter_fehler   TEXT,
            aktiv            BOOLEAN NOT NULL DEFAULT TRUE,
            created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
            geaendert_von    VARCHAR(100),
            CONSTRAINT ck_mailkonto_anbieter CHECK (anbieter IN ('smtp', 'ionos', 'google', 'alias')),
            CONSTRAINT ck_mailkonto_anmeldung CHECK (anmeldung IN ('passwort', 'oauth2', 'alias')),
            CONSTRAINT ck_mailkonto_sicherheit CHECK (sicherheit IN ('starttls', 'ssl')),
            CONSTRAINT ck_mailkonto_status CHECK (status IN ('neu', 'geprueft', 'fehler')),
            CONSTRAINT ck_mailkonto_port CHECK (smtp_port IS NULL OR smtp_port BETWEEN 1 AND 65535),
            CONSTRAINT ck_mailkonto_geheimnis CHECK (geheimnis IS NULL OR geheimnis LIKE 'v1:%'),
            CONSTRAINT ck_mailkonto_alias CHECK (
                (anbieter = 'alias') = (zugang_von IS NOT NULL)
                AND (anbieter <> 'alias' OR geheimnis IS NULL)
                AND (anbieter = 'alias' OR smtp_host IS NOT NULL)
            ),
            CONSTRAINT ck_mailkonto_nicht_selbst CHECK (zugang_von IS NULL OR zugang_von <> id)
        )
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_mailkonto_kennung "
        "ON domain_shared.mailkonten (tenant_id, kennung) WHERE aktiv"
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_mailkonto_standard "
        "ON domain_shared.mailkonten (tenant_id) WHERE aktiv AND ist_standard"
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_mailkonto_mandant ON domain_shared.mailkonten (tenant_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_shared.mailkonten")
