"""FSX-DOC-LINKS: beteiligte Belege je Flow-Spine-Vorgang

Der fuehrende Einstiegsbeleg bleibt unveraendert auf der Instanz
(``linked_document_id``/``linked_document_type``) — dort haengt der partielle
Unique-Index aus FSX-011, und dort greift der Schutz gegen Umbiegen aus
FSX-012. Diese Tabelle traegt die **weiteren** Belege desselben Vorgangs.

Zwei Kardinalitaeten, bewusst so gewaehlt:

* Ein Beleg darf in **mehreren** Vorgaengen beteiligt sein — eine Sammelrechnung
  ueber drei Lieferscheine gehoert zu drei Vorgaengen. Deshalb **keine** globale
  Eindeutigkeit auf (tenant_id, document_type, document_id).
* Derselbe Beleg **nicht zweimal** im selben Vorgang — dafuer die Eindeutigkeit
  auf (tenant_id, instance_id, document_type, document_id). Sie macht das
  Anhaengen idempotent.

Mengen stehen hier ausdruecklich nicht. Welche Teilmenge einer Lieferposition
auf welche Rechnungsposition laeuft, ist das positionsbezogene n:m-Modell und
gehoert in den Belegfluss.

Revision ID: flow_spine_instance_documents_20260915
Revises: flow_spine_document_link_unique_20260915
Create Date: 2026-09-15
"""

from alembic import op
import sqlalchemy as sa


revision = "flow_spine_instance_documents_20260915"
down_revision = "flow_spine_document_link_unique_20260915"
branch_labels = None
depends_on = None


TABLE = "ops_flow_spine_instance_documents"
UNIQUE_NAME = "uq_flow_spine_instance_document"
LOOKUP_NAME = "ix_flow_spine_instance_document_lookup"


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
                CREATE TABLE IF NOT EXISTS domain_ops.{TABLE} (
                  id             VARCHAR PRIMARY KEY,
                  instance_id    VARCHAR(36) NOT NULL
                                 REFERENCES domain_ops.ops_flow_spine_instances(id)
                                 ON DELETE CASCADE,
                  tenant_id      VARCHAR(120) NOT NULL DEFAULT 'default',
                  process_key    VARCHAR(120) NOT NULL,
                  document_type  VARCHAR(80)  NOT NULL,
                  document_id    VARCHAR(120) NOT NULL,
                  relation       VARCHAR(60),
                  linked_by      VARCHAR(120),
                  created_at     TIMESTAMPTZ DEFAULT NOW()
                );

                -- Derselbe Beleg nicht zweimal im selben Vorgang.
                CREATE UNIQUE INDEX IF NOT EXISTS {UNIQUE_NAME}
                  ON domain_ops.{TABLE}
                     (tenant_id, instance_id, document_type, document_id);

                -- Rueckwaertssuche: welcher Vorgang beteiligt diesen Beleg?
                -- Traegt die Sammelrechnung, die aus mehreren Vorgaengen
                -- erreichbar sein muss.
                CREATE INDEX IF NOT EXISTS {LOOKUP_NAME}
                  ON domain_ops.{TABLE}
                     (tenant_id, document_type, document_id);
              END IF;
            END $$;
            """
        )
    )


def downgrade() -> None:
    op.execute(f"DROP TABLE IF EXISTS domain_ops.{TABLE}")
