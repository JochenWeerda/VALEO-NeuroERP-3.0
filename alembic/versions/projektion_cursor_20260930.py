"""Die Projektionsbuchhaltung bekommt eine Migration.

``domain_shared.process_projection_registry``, ``.process_projection_snapshots``
und ``.process_projection_cursors`` wurden von keiner Migration angelegt,
sondern zur Laufzeit — und zwar an **zwei** Stellen: in
``app/services/finance_read_model_service.py`` und, fuer die Cursor-Tabelle
nochmals wortgleich, in ``app/core/projection_cursor_service.py``. Auf einer
frischen Installation gab es die drei Tabellen erst, nachdem jemand eine
Finanz-Projektion abgerufen hatte.

Die Form stammt woertlich aus dieser Laufzeit-DDL. Insbesondere bleiben die
Zeitstempelspalten ``TEXT``: Der Code schreibt ISO-Zeichenketten und vergleicht
sie als Zeichenketten (``str(a) > str(b)``, um den juengsten Stand zu finden).
Ein Wechsel auf ``TIMESTAMPTZ`` wuerde die Tabellen richtiger machen und den
Lesepfad aendern — das ist ein eigener Vorgang, keine Nebenwirkung dieser
Migration.

Keine zusaetzlichen Indizes: Alle drei Tabellen werden ausschliesslich mit
``WHERE tenant_id = …`` und optional ``AND consumer_id = …`` gelesen, und beides
ist Praefix des Primaerschluessels.

Alle drei Tabellen tragen ``tenant_id``, und jede Abfrage filtert danach — hier
gab es kein Mandantenproblem.

Revision ID: projektion_cursor_20260930
Revises: pos_zahlarten_aktionen_20260930
"""

from __future__ import annotations

from alembic import op

revision = "projektion_cursor_20260930"
down_revision = "pos_zahlarten_aktionen_20260930"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_shared.process_projection_registry (
            tenant_id        TEXT    NOT NULL,
            projection_key   TEXT    NOT NULL,
            item_count       INTEGER NOT NULL DEFAULT 0,
            last_rebuilt_at  TEXT    NULL,
            last_accessed_at TEXT    NULL,
            updated_at       TEXT    NOT NULL,
            PRIMARY KEY (tenant_id, projection_key)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_shared.process_projection_snapshots (
            tenant_id      TEXT    NOT NULL,
            projection_key TEXT    NOT NULL,
            schema_version INTEGER NOT NULL DEFAULT 1,
            item_count     INTEGER NOT NULL DEFAULT 0,
            payload        TEXT    NOT NULL,
            rebuilt_at     TEXT    NOT NULL,
            updated_at     TEXT    NOT NULL,
            PRIMARY KEY (tenant_id, projection_key)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_shared.process_projection_cursors (
            tenant_id            TEXT    NOT NULL,
            consumer_id          TEXT    NOT NULL,
            projection_key       TEXT    NOT NULL,
            schema_version       INTEGER NOT NULL DEFAULT 1,
            cursor_token         TEXT    NULL,
            last_event_id        TEXT    NULL,
            source_rebuilt_at    TEXT    NULL,
            replay_from_event_id TEXT    NULL,
            replay_to_event_id   TEXT    NULL,
            status               TEXT    NOT NULL DEFAULT 'active',
            updated_at           TEXT    NOT NULL,
            PRIMARY KEY (tenant_id, consumer_id, projection_key)
        )
        """
    )


def downgrade() -> None:
    # Kein DROP TABLE: Die Tabellen tragen den Fortschritt der Projektionen.
    # Ein Ruecknehmen wuerde jeden Cursor verlieren und die Read Models
    # stillschweigend von vorne beginnen lassen. Diese Migration legt die
    # Tabellen nur an; zurueckzunehmen ist daran nichts.
    pass
