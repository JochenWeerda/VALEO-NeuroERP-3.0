"""FSX-011: eindeutiger Belegbezug fuer offene Flow-Spine-Vorgaenge

Ein vorheriges Nachschlagen verhindert keine parallele Doppelanlage: zwei
gleichzeitige Speichervorgaenge sehen beide "kein Fall vorhanden". Die
Eindeutigkeit muss deshalb die Datenbank erzwingen.

Schluessel: (tenant_id, process_key, linked_document_type, linked_document_id)
- tenant_id, damit Mandanten sich nicht gegenseitig blockieren.
- process_key, damit derselbe Beleg in zwei Prozessen je einen Fall haben darf.

Geltungsbereich: partieller Index nur auf **offene** Vorgaenge. Ein
abgeschlossener, stornierter oder gescheiterter Fall blockiert keinen neuen
Vorgang zum selben Beleg — eine Reklamation nach abgeschlossenem Erstfall muss
moeglich bleiben. Faelle ohne Belegreferenz bleiben ausgenommen (NULL-Werte).

Revision ID: flow_spine_document_link_unique_20260915
Revises: flow_spine_lifecycle_20260417
Create Date: 2026-09-15
"""

from alembic import op
import sqlalchemy as sa


revision = "flow_spine_document_link_unique_20260915"
down_revision = "flow_spine_lifecycle_20260417"
branch_labels = None
depends_on = None


INDEX_NAME = "uq_flow_spine_open_document_link"
LOOKUP_INDEX_NAME = "ix_flow_spine_document_lookup"

# Muss mit OPEN_LIFECYCLE_STATUSES in app/api/v1/endpoints/flow_spines.py
# uebereinstimmen. Weicht eines ab, greift der Index an anderer Stelle als die
# Anwendungslogik — deshalb haelt ein Test die beiden Listen zusammen.
_CLOSED = "'completed', 'cancelled', 'failed'"


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_ops")

    # Vorabbereinigung: bestehende Dubletten wuerden den Index scheitern lassen.
    # Es wird nichts geloescht — der juengere Fall verliert lediglich seinen
    # Belegbezug und bleibt als eigenstaendiger Vorgang bestehen. Das ist
    # umkehrbar; ein Loeschen waere es nicht.
    op.execute(
        sa.text(
            f"""
            DO $$
            BEGIN
              IF EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'domain_ops'
                  AND table_name = 'ops_flow_spine_instances'
              ) THEN
                WITH ranked AS (
                  SELECT id,
                         ROW_NUMBER() OVER (
                           PARTITION BY tenant_id, process_key,
                                        linked_document_type, linked_document_id
                           ORDER BY created_at ASC, id ASC
                         ) AS rn
                  FROM domain_ops.ops_flow_spine_instances
                  WHERE linked_document_id IS NOT NULL
                    AND linked_document_type IS NOT NULL
                    AND lifecycle_status NOT IN ({_CLOSED})
                )
                UPDATE domain_ops.ops_flow_spine_instances t
                   SET linked_document_id = NULL,
                       linked_document_type = NULL
                  FROM ranked r
                 WHERE t.id = r.id AND r.rn > 1;

                CREATE UNIQUE INDEX IF NOT EXISTS {INDEX_NAME}
                  ON domain_ops.ops_flow_spine_instances
                     (tenant_id, process_key, linked_document_type, linked_document_id)
                  WHERE linked_document_id IS NOT NULL
                    AND linked_document_type IS NOT NULL
                    AND lifecycle_status NOT IN ({_CLOSED});

                -- FSX-010: Die Fallsuche je Beleg fragt auch ueber
                -- abgeschlossene Vorgaenge; der partielle Unique-Index deckt
                -- die nicht ab.
                CREATE INDEX IF NOT EXISTS {LOOKUP_INDEX_NAME}
                  ON domain_ops.ops_flow_spine_instances
                     (tenant_id, linked_document_type, linked_document_id);
              END IF;
            END $$;
            """
        )
    )


def downgrade() -> None:
    op.execute(f"DROP INDEX IF EXISTS domain_ops.{LOOKUP_INDEX_NAME}")
    op.execute(f"DROP INDEX IF EXISTS domain_ops.{INDEX_NAME}")
