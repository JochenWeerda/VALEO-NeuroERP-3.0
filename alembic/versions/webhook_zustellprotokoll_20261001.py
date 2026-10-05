"""Ein Zustellversuch braucht einen Nachweis.

``webhook_system.py`` gab ``fehler_count`` und ``letzte_auslosung_am`` aus und
konnte beides nicht belegen: Die alte, nie migrierte Tabelle hatte Zaehler, die
niemand las, und ``domain_shared.webhook_registrations`` hat keine. Ein Zaehler
sagt ausserdem nicht, **was** schiefging — und das ist die Frage, die bei einer
nicht angekommenen Meldung gestellt wird.

Deshalb ein Protokoll statt zweier Zaehler: je Zustellversuch eine Zeile. Die
beiden ausgegebenen Felder werden daraus abgeleitet und sind damit wahr.

``ON DELETE CASCADE``: Wird eine Anbindung abgemeldet, verliert ihr Protokoll
seinen Bezug. Es ist Betriebsnachweis einer Anbindung, keine
aufbewahrungspflichtige Buchung.

Revision ID: webhook_zustellprotokoll_20261001
Revises: lastschrift_mandant_20260930
"""

from __future__ import annotations

from alembic import op

revision = "webhook_zustellprotokoll_20261001"
down_revision = "lastschrift_mandant_20260930"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_shared.webhook_deliveries (
            id           VARCHAR(64)  PRIMARY KEY,
            tenant_id    VARCHAR(80)  NOT NULL,
            webhook_id   VARCHAR(64)  NOT NULL
                REFERENCES domain_shared.webhook_registrations (id) ON DELETE CASCADE,
            event_area   VARCHAR(64)  NOT NULL,
            versucht_am  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            erfolgreich  BOOLEAN      NOT NULL,
            status_code  INTEGER,
            dauer_ms     INTEGER,
            fehler       TEXT,
            signiert     BOOLEAN      NOT NULL DEFAULT FALSE
        )
        """
    )

    # Gelesen wird "die Versuche dieser Anbindung, neueste zuerst".
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_webhook_deliveries_webhook_zeit "
        "ON domain_shared.webhook_deliveries (webhook_id, versucht_am DESC)"
    )
    # Und "was ist in meinem Haus zuletzt schiefgegangen?".
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_webhook_deliveries_tenant_fehler "
        "ON domain_shared.webhook_deliveries (tenant_id, erfolgreich, versucht_am DESC)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_shared.webhook_deliveries")
