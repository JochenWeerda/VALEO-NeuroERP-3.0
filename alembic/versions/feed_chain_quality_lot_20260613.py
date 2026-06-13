"""FEED-CHAIN-003 — quality_lot_profiles + quality_release_decisions (domain_ops).

Löst den In-Memory-Belegbruch: Qualitätsprofil und Freigabeentscheidung überleben
jetzt einen Neustart. Entscheidung „approve" / „reject" schreibt qualitaetsstatus
auf ops_chargen zurück.

Revision ID: feed_chain_quality_lot_20260613
Revises: agri_silo_material_flow_20260612
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "feed_chain_quality_lot_20260613"
down_revision: Union[str, Sequence[str], None] = "agri_silo_material_flow_20260612"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_ops.quality_lot_profiles (
            id                      VARCHAR(64)  PRIMARY KEY,
            lot_id                  VARCHAR(64)  NOT NULL,
            tenant_id               VARCHAR(64)  NOT NULL,
            acceptance_id           VARCHAR(64),
            contract_id             VARCHAR(64),
            protocol_id             VARCHAR(64),
            moisture_pct            DECIMAL(8,4),
            impurities_pct          DECIMAL(8,4),
            protein_pct             DECIMAL(8,4),
            hl_weight               DECIMAL(8,4),
            overall_grade           VARCHAR(16),
            price_deduction_pct     DECIMAL(8,4) NOT NULL DEFAULT 0,
            approval_status         VARCHAR(16)  NOT NULL DEFAULT 'pending',
            schema_version          INTEGER      NOT NULL DEFAULT 1,
            created_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tenant_id, lot_id)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_ops.quality_release_decisions (
            id                          VARCHAR(64) PRIMARY KEY,
            lot_id                      VARCHAR(64) NOT NULL,
            tenant_id                   VARCHAR(64) NOT NULL,
            protocol_id                 VARCHAR(64) NOT NULL,
            decision                    VARCHAR(16) NOT NULL,
            decided_by                  VARCHAR(128) NOT NULL,
            decided_at                  VARCHAR(64)  NOT NULL,
            reason                      TEXT,
            price_deduction_applied_pct DECIMAL(8,4) NOT NULL DEFAULT 0,
            schema_version              INTEGER      NOT NULL DEFAULT 1,
            created_at                  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tenant_id, lot_id)
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_qlp_tenant_lot
            ON domain_ops.quality_lot_profiles (tenant_id, lot_id)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_qrd_tenant_lot
            ON domain_ops.quality_release_decisions (tenant_id, lot_id)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_ops.quality_release_decisions")
    op.execute("DROP TABLE IF EXISTS domain_ops.quality_lot_profiles")
