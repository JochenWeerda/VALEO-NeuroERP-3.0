"""Der Kontrakt-Overlay ohne Vertragsbezug wird stillgelegt.

Fuer "Kontrakt" standen sechs Tabellen in fuenf Schemata, und **zwei**
vollstaendig ausgebaute, geroutete Implementierungen von Fixierung und
Abrechnung. Das fuehrende Modell ist ``domain_ops.kon_contract`` (+ ``_line``,
``_fixing``, ``_movement``, ``_reminder``): einunddreissig Spalten mit
Preisbildung, Fixierungsfenster, Mengenart und Ueberlieferungsregel, vier
Dienste, vier Endpunktmodule, vier Frontend-Module und Bestand.

Dieses Schema ``domain_kontrakte`` war die zweite Fassung — vier Tabellen
**ohne Kopftabelle**: ``kontrakt_lifecycle`` diente sich selbst als Kopf, und
``kontrakt_id`` war eine freie Zeichenkette, die gegen **keine** Vertragstabelle
geprueft wurde. Eine Fixierung und eine Abrechnung ohne nachweisbaren
Vertragsbezug sind nach GoBD nicht nachvollziehbar und nicht nachpruefbar; das
ist der eigentliche Grund fuer die Stilllegung, nicht die Doppelung.

**Warum das ohne Datenverlust geht:** Alle vier Tabellen hatten am 01.10.2026 in
der gewachsenen **und** in der frisch migrierten Datenbank **null Zeilen**, und
kein Weg des Systems benutzte sie — die sieben Routen des Overlays
(``/api/v1/lifecycle``, ``/fixing``, ``/settlement``) hatten keinen Aufrufer,
weder im Frontend noch im Backend. Es gab also nie einen aufbewahrungspflichtigen
Datensatz. ``downgrade`` legt die Tabellen wieder an.

Entscheidung und Beweislage: ``docs/architecture/domains/kontrakte/fuehrendes-modell.md``.

Revision ID: kontrakt_ordnung_20261001
Revises: kontraktregister_20261001
"""

from __future__ import annotations

from alembic import op

revision = "kontrakt_ordnung_20261001"
down_revision = "kontraktregister_20261001"
branch_labels = None
depends_on = None

TABELLEN = (
    "kontrakt_status_log",
    "kontrakt_settlements",
    "kontrakt_fixings",
    "kontrakt_lifecycle",
)


def upgrade() -> None:
    # Sicherung gegen eine Installation, auf der doch Zeilen liegen: Dann bricht
    # die Migration ab, statt einen Bestand zu entfernen, den niemand erwartet
    # hat. Lieber eine rote Migration als eine stille Loeschung.
    op.execute(
        """
        DO $$
        DECLARE bestand bigint;
        BEGIN
            IF to_regclass('domain_kontrakte.kontrakt_lifecycle') IS NULL THEN
                RETURN;
            END IF;
            SELECT (
                (SELECT count(*) FROM domain_kontrakte.kontrakt_lifecycle)
              + (SELECT count(*) FROM domain_kontrakte.kontrakt_fixings)
              + (SELECT count(*) FROM domain_kontrakte.kontrakt_settlements)
              + (SELECT count(*) FROM domain_kontrakte.kontrakt_status_log)
            ) INTO bestand;
            IF bestand > 0 THEN
                RAISE EXCEPTION
                    'domain_kontrakte traegt % Zeilen. Stilllegung abgebrochen: '
                    'Der Bestand gehoert vor der Loeschung in das fuehrende '
                    'Modell domain_ops.kon_contract uebernommen (siehe '
                    'docs/architecture/domains/kontrakte/fuehrendes-modell.md).',
                    bestand;
            END IF;
        END $$;
        """
    )

    for tabelle in TABELLEN:
        op.execute(f"DROP TABLE IF EXISTS domain_kontrakte.{tabelle}")
    # Nur wenn leer — ein fremdes Objekt in diesem Schema soll die Migration
    # nicht mitnehmen.
    op.execute("DROP SCHEMA IF EXISTS domain_kontrakte RESTRICT")


def downgrade() -> None:
    """Legt die Tabellen in der Form wieder an, in der sie stillgelegt wurden.

    Uebernommen aus ``kontrakt_lifecycle_fixing_20260623``; der Overlay war
    leer, es gibt also keinen Inhalt zurueckzuholen.
    """
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_kontrakte")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_kontrakte.kontrakt_lifecycle (
            id           UUID        PRIMARY KEY,
            kontrakt_id  TEXT        NOT NULL,
            tenant_id    TEXT        NOT NULL,
            kontrakt_nr  TEXT        NOT NULL,
            artikel_id   TEXT        NOT NULL,
            menge_t      NUMERIC     NOT NULL,
            preis_eur_t  NUMERIC     NOT NULL,
            lieferant_id TEXT        NOT NULL,
            periode      TEXT        NOT NULL,
            status       TEXT        NOT NULL,
            created_at   TIMESTAMPTZ NOT NULL,
            updated_at   TIMESTAMPTZ
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_kontrakte.kontrakt_fixings (
            id                 UUID        PRIMARY KEY,
            kontrakt_id        TEXT        NOT NULL,
            tenant_id          TEXT        NOT NULL,
            fixing_datum       TEXT        NOT NULL,
            fixing_preis_eur_t NUMERIC     NOT NULL,
            menge_t            NUMERIC     NOT NULL,
            markt              TEXT        NOT NULL,
            referenz           TEXT        NOT NULL,
            operator           TEXT        NOT NULL,
            created_at         TIMESTAMPTZ NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_kontrakte.kontrakt_settlements (
            id                     UUID        PRIMARY KEY,
            kontrakt_id            TEXT        NOT NULL,
            tenant_id              TEXT        NOT NULL,
            lieferung_datum        TEXT        NOT NULL,
            gelieferte_menge_t     NUMERIC     NOT NULL,
            abrechnungspreis_eur_t NUMERIC     NOT NULL,
            netto_eur              NUMERIC     NOT NULL,
            referenz               TEXT        NOT NULL,
            status                 TEXT        NOT NULL,
            storno_grund           TEXT        NOT NULL,
            operator               TEXT        NOT NULL,
            created_at             TIMESTAMPTZ NOT NULL,
            updated_at             TIMESTAMPTZ
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_kontrakte.kontrakt_status_log (
            id          UUID        PRIMARY KEY,
            kontrakt_id TEXT        NOT NULL,
            tenant_id   TEXT        NOT NULL,
            old_status  TEXT        NOT NULL,
            new_status  TEXT        NOT NULL,
            operator    TEXT        NOT NULL,
            grund       TEXT        NOT NULL,
            created_at  TIMESTAMPTZ NOT NULL
        )
        """
    )
