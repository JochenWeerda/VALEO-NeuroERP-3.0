"""Hinweisgebermeldungen bekommen eine Migration, eine Form und einen Mandanten.

Was vorher war
--------------

``domain_compliance.whistleblower_reports`` wurde von **keiner** Migration
angelegt, sondern zur Laufzeit vom Endpunkt selbst
(``compliance_whistleblower.py``, ``CREATE TABLE IF NOT EXISTS``). Das Schema
hing damit davon ab, welcher Endpunkt zuerst aufgerufen worden war.

Und es gab **zwei** Endpunkte mit **unvereinbaren** Formen:

| ``compliance_whistleblower.py`` | ``compliance_whistleblower_lksg.py`` |
|---|---|
| ``report_token`` | — |
| ``description_encrypted`` | ``description`` |
| ``severity`` | — |
| ``submitted_at`` | ``created_at`` |
| ``notes`` | — |
| — | ``contact_email`` |
| — | ``anonymous`` |
| **kein ``tenant_id``** | ``tenant_id`` |

Wer zuerst lief, bestimmte die Tabelle; der andere bekam dauerhaft
``503 whistleblower_reports table not available``. Auf einer frischen
Installation war damit einer der beiden Wege immer kaputt.

Schwerer noch: In der zur Laufzeit erzeugten Form fehlt ``tenant_id``. Deshalb
listete ``GET /reports`` **alle** Meldungen **aller** Mandanten. Die
EU-Hinweisgeberrichtlinie verlangt Vertraulichkeit (Art. 16); schon die
Existenz, Kategorie und Schwere einer Meldung eines anderen Mandanten gehoert
nicht in eine fremde Liste.

Was diese Migration tut
-----------------------

Sie legt **eine** Tabelle mit der Vereinigung beider Formen an und macht
``tenant_id`` zur Pflicht — aber nur, wenn das ohne Datenverlust geht.

Zum Mandanten bei Bestandszeilen: Aus einer Zeile ohne ``tenant_id`` laesst
sich der Mandant **nicht** ableiten. Ihn zu erraten hiesse, eine
Hinweisgebermeldung dem falschen Haus zuzuordnen — das ist schlimmer als eine
Zeile, die niemand sieht. Deshalb:

- Ist die Spalte leer oder die Tabelle leer, wird ``NOT NULL`` gesetzt.
- Gibt es Zeilen ohne Mandanten, bleibt die Spalte nullbar. Der Code schreibt
  ``tenant_id`` immer und filtert immer danach; eine solche Altzeile wird damit
  unsichtbar. Fuer eine Vertraulichkeitsfrage ist das die sichere Richtung.

``description_encrypted`` traegt nie Geheimtext — der Endpunkt schrieb den
Klartext hinein. Ein Name, der Verschluesselung verspricht, ist schlechter als
einer, der es nicht tut: Er laedt dazu ein, sich auf etwas zu verlassen, das
nicht da ist. Die fuehrende Spalte heisst deshalb ``description``; ein
vorhandenes ``description_encrypted`` wird uebernommen (Nachfuellung, aendert
am Inhalt nichts) und bleibt danach als leere Altspalte stehen, statt still
geloescht zu werden.

Revision ID: whistleblower_eine_tabelle_20260930
Revises: reklamation_nummer_20260930
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "whistleblower_eine_tabelle_20260930"
down_revision = "reklamation_nummer_20260930"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_compliance")

    # Die Vereinigung beider Formen. IF NOT EXISTS, damit die Migration auch
    # dort laeuft, wo der Endpunkt die Tabelle schon zur Laufzeit angelegt hat.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_compliance.whistleblower_reports (
            id            VARCHAR(64)  PRIMARY KEY,
            tenant_id     VARCHAR(64),
            report_token  VARCHAR(32)  UNIQUE,
            category      VARCHAR(64)  NOT NULL,
            description   TEXT,
            contact_email VARCHAR(255),
            anonymous     BOOLEAN      NOT NULL DEFAULT TRUE,
            severity      VARCHAR(16)  NOT NULL DEFAULT 'MITTEL',
            status        VARCHAR(32)  NOT NULL DEFAULT 'EINGEGANGEN',
            notes         JSONB        NOT NULL DEFAULT '[]'::jsonb,
            created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )
        """
    )

    # Fuer eine Installation, auf der die Laufzeitfassung schon steht.
    op.execute(
        """
        ALTER TABLE domain_compliance.whistleblower_reports
            ADD COLUMN IF NOT EXISTS tenant_id     VARCHAR(64),
            ADD COLUMN IF NOT EXISTS report_token  VARCHAR(32),
            ADD COLUMN IF NOT EXISTS description   TEXT,
            ADD COLUMN IF NOT EXISTS contact_email VARCHAR(255),
            ADD COLUMN IF NOT EXISTS anonymous     BOOLEAN NOT NULL DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS severity      VARCHAR(16) NOT NULL DEFAULT 'MITTEL',
            ADD COLUMN IF NOT EXISTS status        VARCHAR(32) NOT NULL DEFAULT 'EINGEGANGEN',
            ADD COLUMN IF NOT EXISTS notes         JSONB NOT NULL DEFAULT '[]'::jsonb,
            ADD COLUMN IF NOT EXISTS created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            ADD COLUMN IF NOT EXISTS updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
        """
    )

    # Der Token gehoert zum kurzen Weg, nicht zum LkSG-Weg: Dort meldet jemand
    # ueber ein Formular und bekommt keinen Token. Die Laufzeitfassung hatte
    # ihn als NOT NULL angelegt — auf einer solchen Installation waere der
    # LkSG-Weg weiter kaputt, nur mit einer anderen Fehlermeldung.
    op.execute(
        "ALTER TABLE domain_compliance.whistleblower_reports "
        "ALTER COLUMN report_token DROP NOT NULL"
    )

    # Nachfuellung: Wo die Laufzeitfassung submitted_at und
    # description_encrypted fuehrte, wandert der Wert in die fuehrenden
    # Spalten. Nur WHERE ... IS NULL — am Inhalt aendert sich nichts.
    verbindung = op.get_bind()
    for alt, neu in (("description_encrypted", "description"),
                     ("submitted_at", "created_at")):
        vorhanden = verbindung.execute(
            text(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_schema = 'domain_compliance' "
                "AND table_name = 'whistleblower_reports' AND column_name = :spalte"
            ),
            {"spalte": alt},
        ).scalar()
        if vorhanden:
            op.execute(
                f"UPDATE domain_compliance.whistleblower_reports "  # nosec B608
                f"SET {neu} = {alt} WHERE {neu} IS NULL AND {alt} IS NOT NULL"
            )

    # Der Mandant wird Pflicht — aber nur, wenn keine Zeile ohne ihn steht.
    # Ihn zu erraten hiesse, eine Hinweisgebermeldung dem falschen Haus
    # zuzuordnen.
    ohne_mandant = verbindung.execute(
        text(
            "SELECT count(*) FROM domain_compliance.whistleblower_reports "
            "WHERE tenant_id IS NULL"
        )
    ).scalar()
    if not ohne_mandant:
        op.execute(
            "ALTER TABLE domain_compliance.whistleblower_reports "
            "ALTER COLUMN tenant_id SET NOT NULL"
        )

    # Die Frage an diese Tabelle lautet immer: „Welche Meldungen hat *mein*
    # Haus, neueste zuerst?" Genau darauf liegt der Index.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_whistleblower_reports_tenant_created "
        "ON domain_compliance.whistleblower_reports (tenant_id, created_at DESC)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_whistleblower_reports_token "
        "ON domain_compliance.whistleblower_reports (report_token)"
    )


def downgrade() -> None:
    # Kein DROP TABLE: Die Tabelle traegt Hinweisgebermeldungen. Ein Rueckbau
    # nimmt nur zurueck, was diese Migration hinzugefuegt hat, ohne Inhalt zu
    # verlieren — und die Mandantenpflicht, damit die alte Laufzeitfassung
    # wieder schreiben koennte.
    op.execute(
        "ALTER TABLE domain_compliance.whistleblower_reports "
        "ALTER COLUMN tenant_id DROP NOT NULL"
    )
    op.execute("DROP INDEX IF EXISTS domain_compliance.ix_whistleblower_reports_tenant_created")
    op.execute("DROP INDEX IF EXISTS domain_compliance.ix_whistleblower_reports_token")
