"""Die Reklamation bekommt eine Nummer, die man nennen kann.

Bisher hatte eine Reklamation nur zwei Schluessel: ``reklamation_id`` (UUID)
und den Primaerschluessel ``REK-`` plus acht zufaellige Hex-Zeichen. Beides
ist keine Belegnummer — nicht fortlaufend, nicht je Mandant, am Telefon nicht
nennbar. Die Maske zeigte ersatzweise den Primaerschluessel, die Liste die
UUID.

Neu ist ``reklamation_nr`` im Format ``REK-JJJJ-NNNNN``, fortlaufend je
Mandant und Geschaeftsjahr. Das Jahr ist das der Betriebszeitzone
(Europe/Berlin, wie ``app.core.business_time``), damit eine Reklamation aus
der Silvesternacht nicht im Vorjahr landet.

Bestandszeilen werden in der Reihenfolge ihrer Anlage nachnummeriert. Der
eindeutige Index ``(tenant_id, reklamation_nr)`` haelt die Vergabe auch dann
fest, wenn zwei Anlagen gleichzeitig laufen; die Anwendung serialisiert sie
zusaetzlich per Advisory-Lock.

``IF NOT EXISTS`` sorgt dafuer, dass die Migration auf frischer und
gewachsener Datenbank laeuft.

Revision ID: reklamation_nummer_20260930
Revises: verkauf_fehlende_spalten_20260929
"""

from __future__ import annotations

from alembic import op

revision = "reklamation_nummer_20260930"
down_revision = "verkauf_fehlende_spalten_20260929"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE domain_ops.reklamationen
            ADD COLUMN IF NOT EXISTS reklamation_nr VARCHAR(40);
        """
    )
    op.execute(
        """
        WITH jahr AS (
            SELECT id, tenant_id,
                   COALESCE(erstellt_am, updated_at, now()) AS angelegt,
                   to_char(COALESCE(erstellt_am, updated_at, now()) AT TIME ZONE 'Europe/Berlin', 'YYYY') AS jj
            FROM domain_ops.reklamationen
            WHERE reklamation_nr IS NULL
        ),
        nummern AS (
            SELECT id,
                   'REK-' || jj || '-' || lpad(
                       row_number() OVER (PARTITION BY tenant_id, jj ORDER BY angelegt, id)::text, 5, '0'
                   ) AS nr
            FROM jahr
        )
        UPDATE domain_ops.reklamationen r
        SET reklamation_nr = nummern.nr
        FROM nummern
        WHERE r.id = nummern.id;
        """
    )
    op.execute(
        """
        ALTER TABLE domain_ops.reklamationen
            ALTER COLUMN reklamation_nr SET NOT NULL;
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_reklamationen_tenant_nr
            ON domain_ops.reklamationen (tenant_id, reklamation_nr);
        """
    )


def downgrade() -> None:
    # Die Nummern bleiben: Sie sind nach aussen genannt worden und lassen sich
    # nicht wiederherstellen. Der Stand davor schreibt die Spalte nicht, darf
    # also nur nicht an der Pflichtbedingung scheitern.
    op.execute(
        """
        ALTER TABLE domain_ops.reklamationen
            ALTER COLUMN reklamation_nr DROP NOT NULL;
        """
    )
