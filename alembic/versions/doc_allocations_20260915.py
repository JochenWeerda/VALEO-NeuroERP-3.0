"""FSX-MENGENMODELL: positionsbezogene n:m-Zuordnung zwischen Belegen

Zwei Tabellen, und die Aufteilung traegt die entscheidende Zusicherung:

``doc_allocation_sources``
    Eine Zeile je Quellposition mit Gesamt- und zugeordneter Menge. Sie ist der
    Ort, an dem die Restmenge lebt — und den eine Transaktion sperrt, bevor sie
    zuordnet. Die CHECK-Bedingung ``allocated_quantity <= quantity`` ist die
    eigentliche Grenze; sie liegt in der Datenbank, weil nur dort
    Nebenlaeufigkeit haelt.

``doc_allocations``
    Die n:m-Zeilen: Quellposition -> Zielposition mit Menge und Einheit.

Ueber eine reine Zuordnungstabelle waere die Regel nicht durchsetzbar: Zwei
gleichzeitige Transaktionen laesen beide die vorhandenen Zeilen, kaemen beide
auf dieselbe Restmenge und fuegten beide ein. Dieselbe Lektion wie FSX-011 —
Nachschlagen genuegt nicht.

Revision ID: doc_allocations_20260915
Revises: flow_spine_instance_documents_20260915
Create Date: 2026-09-15
"""

from alembic import op
import sqlalchemy as sa


revision = "doc_allocations_20260915"
down_revision = "flow_spine_instance_documents_20260915"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_docs")

    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS domain_docs.doc_allocation_sources (
              id                  VARCHAR PRIMARY KEY,
              tenant_id           VARCHAR(120) NOT NULL,
              document_type       VARCHAR(80)  NOT NULL,
              document_id         VARCHAR(120) NOT NULL,
              line_id             VARCHAR(120) NOT NULL,
              article_id          VARCHAR(120),
              quantity            NUMERIC(18,6) NOT NULL,
              allocated_quantity  NUMERIC(18,6) NOT NULL DEFAULT 0,
              unit                VARCHAR(20)  NOT NULL,
              created_at          TIMESTAMPTZ DEFAULT NOW(),
              updated_at          TIMESTAMPTZ DEFAULT NOW(),
              CONSTRAINT ck_doc_allocation_source_qty_positive
                CHECK (quantity > 0),
              CONSTRAINT ck_doc_allocation_source_alloc_nonneg
                CHECK (allocated_quantity >= 0),
              -- Die eigentliche Zusicherung des Modells.
              CONSTRAINT ck_doc_allocation_source_not_overallocated
                CHECK (allocated_quantity <= quantity)
            );

            CREATE UNIQUE INDEX IF NOT EXISTS uq_doc_allocation_source
              ON domain_docs.doc_allocation_sources
                 (tenant_id, document_type, document_id, line_id);

            CREATE INDEX IF NOT EXISTS ix_doc_allocation_source_article
              ON domain_docs.doc_allocation_sources (tenant_id, article_id);

            CREATE TABLE IF NOT EXISTS domain_docs.doc_allocations (
              id                   VARCHAR PRIMARY KEY,
              tenant_id            VARCHAR(120) NOT NULL,
              source_id            VARCHAR NOT NULL
                                   REFERENCES domain_docs.doc_allocation_sources(id)
                                   ON DELETE CASCADE,
              target_document_type VARCHAR(80)  NOT NULL,
              target_document_id   VARCHAR(120) NOT NULL,
              target_line_id       VARCHAR(120) NOT NULL,
              quantity             NUMERIC(18,6) NOT NULL,
              unit                 VARCHAR(20)  NOT NULL,
              entered_quantity     NUMERIC(18,6),
              entered_unit         VARCHAR(20),
              reason               VARCHAR(80),
              note                 TEXT,
              created_by           VARCHAR(120),
              created_at           TIMESTAMPTZ DEFAULT NOW(),
              CONSTRAINT ck_doc_allocation_qty_positive CHECK (quantity > 0)
            );

            -- Dieselbe Quelle nicht zweimal auf dieselbe Zielposition: sonst
            -- entstuenden zwei Zeilen, die zusammen doppelt zaehlen, ohne dass
            -- es jemandem auffiele.
            CREATE UNIQUE INDEX IF NOT EXISTS uq_doc_allocation_pair
              ON domain_docs.doc_allocations
                 (tenant_id, source_id, target_document_type,
                  target_document_id, target_line_id);

            -- Rueckweg: welche Quellen speisen diesen Zielbeleg?
            CREATE INDEX IF NOT EXISTS ix_doc_allocation_target
              ON domain_docs.doc_allocations
                 (tenant_id, target_document_type, target_document_id);
            """
        )
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_docs.doc_allocations")
    op.execute("DROP TABLE IF EXISTS domain_docs.doc_allocation_sources")
