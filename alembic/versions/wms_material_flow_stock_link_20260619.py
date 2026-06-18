"""WMS-FLOW-001: silo_cells current_stock_kg + BAB-Umlagen-Tabelle

Revision ID: wms_material_flow_stock_link_20260619
Revises: kostenrechnung_stammdaten_20260618
Create Date: 2026-06-19
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "wms_material_flow_stock_link_20260619"
down_revision = "kostenrechnung_stammdaten_20260618"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_procurement")

    # ── WMS-FLOW-001: Ist-Bestand je Silozelle ────────────────────────────
    op.execute("""
        ALTER TABLE domain_inventory.silo_cells
        ADD COLUMN IF NOT EXISTS current_stock_kg NUMERIC(16,3) NOT NULL DEFAULT 0
    """)

    # ── KORE-BAB-001: Kostenumlagen-Tabelle ──────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_finance.kostenstellen_umlagen (
            id                  TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
            tenant_id           VARCHAR(36) NOT NULL,
            periode             TEXT NOT NULL,            -- YYYY-MM
            von_kostenstelle_id VARCHAR(36) NOT NULL
                REFERENCES domain_finance.kostenstellen(id),
            nach_kostenstelle_id VARCHAR(36) NOT NULL
                REFERENCES domain_finance.kostenstellen(id),
            umlage_art          TEXT NOT NULL
                CHECK (umlage_art IN ('PROZENT','BETRAG','MENGE')),
            umlage_wert         NUMERIC(16,4) NOT NULL,  -- % oder EUR oder Einheiten
            umlage_basis        TEXT,                    -- z.B. 'Maschinenst', 'Flaeche'
            umlagebetrag_eur    NUMERIC(16,2),           -- berechnetes Ergebnis
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_kostenstellen_umlage
                UNIQUE (tenant_id, periode, von_kostenstelle_id, nach_kostenstelle_id, umlage_art)
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_kst_umlagen_tenant_periode
        ON domain_finance.kostenstellen_umlagen (tenant_id, periode)
    """)

    # ── QS-CHARGE-001: quality_protocol_id FK in harvest_acceptances ─────
    op.execute("""
        ALTER TABLE domain_agrar.harvest_acceptances
        ADD COLUMN IF NOT EXISTS quality_protocol_id UUID
    """)
    # quality_protocols already exists (domain_agrar schema); no FK to avoid cross-migration deps

    # ── PROC-3WM-001: Matching-Ergebnis-Tabelle ──────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_procurement.procurement_match_results (
            id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
            tenant_id       TEXT NOT NULL,
            po_id           TEXT,
            gr_id           TEXT,
            ap_invoice_id   TEXT,
            match_status    TEXT NOT NULL
                CHECK (match_status IN ('MATCH_OK','MISMATCH','PENDING','CANCELLED')),
            qty_po          NUMERIC(16,3),
            qty_gr          NUMERIC(16,3),
            qty_ap          NUMERIC(16,3),
            price_po        NUMERIC(16,4),
            price_ap        NUMERIC(16,4),
            qty_tolerance_pct  NUMERIC(5,2) DEFAULT 2.0,
            price_tolerance_pct NUMERIC(5,2) DEFAULT 1.0,
            discrepancy_reason TEXT,
            matched_by      TEXT,
            matched_at      TIMESTAMPTZ,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_proc_match_tenant_po
        ON domain_procurement.procurement_match_results (tenant_id, po_id)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_procurement.procurement_match_results")
    op.execute("DROP TABLE IF EXISTS domain_finance.kostenstellen_umlagen")
    op.execute("""
        ALTER TABLE domain_inventory.silo_cells
        DROP COLUMN IF EXISTS current_stock_kg
    """)
    op.execute("""
        ALTER TABLE domain_agrar.harvest_acceptances
        DROP COLUMN IF EXISTS quality_protocol_id
    """)
