"""FSX-011: eindeutiger Belegbezug fuer offene Flow-Spine-Vorgaenge

Ein vorheriges Nachschlagen verhindert keine parallele Doppelanlage: zwei
gleichzeitige Speichervorgaenge sehen beide "kein Fall vorhanden". Die
Eindeutigkeit muss deshalb die Datenbank erzwingen.

Ein Index, nicht zwei. Schluessel:
(tenant_id, process_key, linked_document_type, linked_document_id)

- tenant_id, damit Mandanten sich nicht gegenseitig blockieren.
- process_key, damit derselbe Beleg in zwei Prozessen je einen Fall haben darf.
- kein zweiter, schwacherer Lookup-Index ohne process_key.

Geltungsbereich: partieller Index nur auf **offene** Vorgaenge mit echter
Belegreferenz. Leerstring ist nicht NULL und wuerde alle manuellen Faelle
kollidieren lassen — deshalb btrim <> '' und Normalisierung beim Schreiben.

Revision ID: flow_spine_document_link_unique_20260915
Revises: agrar_harvest_acceptances_sammel_20260911
Create Date: 2026-09-15
"""

from alembic import op
import sqlalchemy as sa


revision = "flow_spine_document_link_unique_20260915"
down_revision = "agrar_harvest_acceptances_sammel_20260911"
branch_labels = None
depends_on = None


INDEX_NAME = "uq_flow_spine_open_by_document"

# Muss mit CLOSED_LIFECYCLE_STATUSES in app/api/v1/endpoints/flow_spines.py
# uebereinstimmen. Weicht eines ab, greift der Index an anderer Stelle als die
# Anwendungslogik — deshalb haelt ein Test die beiden Listen zusammen.
_CLOSED = "'completed', 'cancelled', 'failed'"


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_ops")

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
                UPDATE domain_ops.ops_flow_spine_instances
                   SET linked_document_id = NULL
                 WHERE linked_document_id IS NOT NULL
                   AND btrim(linked_document_id) = '';

                UPDATE domain_ops.ops_flow_spine_instances
                   SET linked_document_type = NULL
                 WHERE linked_document_type IS NOT NULL
                   AND btrim(linked_document_type) = '';

                IF EXISTS (
                  SELECT 1 FROM domain_ops.ops_flow_spine_instances
                  WHERE linked_document_id IS NOT NULL
                    AND btrim(linked_document_id) <> ''
                    AND linked_document_type IS NOT NULL
                    AND btrim(linked_document_type) <> ''
                    AND lifecycle_status NOT IN ({_CLOSED})
                  GROUP BY tenant_id, process_key, linked_document_type, linked_document_id
                  HAVING COUNT(*) > 1
                ) THEN
                  RAISE EXCEPTION 'Duplicate open flow-spine document bindings; no bindings changed'
                    USING HINT = 'Group ops_flow_spine_instances by tenant_id, process_key, linked_document_type, linked_document_id; resolve duplicates with an audited business decision before retrying.';
                END IF;

                CREATE UNIQUE INDEX IF NOT EXISTS {INDEX_NAME}
                  ON domain_ops.ops_flow_spine_instances
                     (tenant_id, process_key, linked_document_type, linked_document_id)
                  WHERE linked_document_id IS NOT NULL
                    AND btrim(linked_document_id) <> ''
                    AND linked_document_type IS NOT NULL
                    AND btrim(linked_document_type) <> ''
                    AND lifecycle_status NOT IN ({_CLOSED});
              END IF;
            END $$;
            """
        )
    )


def downgrade() -> None:
    op.execute(f"DROP INDEX IF EXISTS domain_ops.{INDEX_NAME}")
