"""supply_chain_events — append-only Ketten-Ereignis-Log (DOM-SUPPLY-004.2)

Revisionsfestes, append-only Protokoll der Lieferkette (Wiegung→Annahme→Lager→
Abrechnung). Rückgrat ist die weighing_ticket-ID. Der Service schreibt nur INSERT
(kein UPDATE/DELETE) und leitet daraus den kanonischen Übergabestatus ab.

Revision ID: supply_chain_events_20260610
Revises: crm_capture_inbox_kim_20260609
Create Date: 2026-06-10
"""

from __future__ import annotations

from alembic import op

revision = "supply_chain_events_20260610"
down_revision = "crm_capture_inbox_kim_20260609"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_inventory.supply_chain_events (
            id               UUID PRIMARY KEY,
            tenant_id        TEXT NOT NULL,
            ticket_id        TEXT,                 -- weighing_ticket = Rückgrat
            stage            TEXT NOT NULL,        -- wiegung|annahme|lager|abrechnung|kette
            ref_type         TEXT,                 -- weighing_ticket|harvest_acceptance|silo_lot|settlement
            ref_id           TEXT,
            ref_label        TEXT,                 -- z.B. WG-2026-00001
            event_type       TEXT NOT NULL,        -- erfasst|freigegeben|eingelagert|abgerechnet|abweichung|korrektur|storniert|notiz
            status_from      TEXT,
            status_to        TEXT,
            menge_kg         NUMERIC(14,2),
            abweichung_grund TEXT,
            payload          JSONB,
            bediener         TEXT,
            source           TEXT NOT NULL DEFAULT 'manual',  -- backfill|auto|manual
            occurred_at      TIMESTAMPTZ,
            created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_sc_events_ticket "
        "ON domain_inventory.supply_chain_events (tenant_id, ticket_id, occurred_at)"
    )
    # Idempotenter Backfill: je (tenant, ref, event) genau ein synthetischer Eintrag.
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_sc_events_backfill "
        "ON domain_inventory.supply_chain_events (tenant_id, stage, ref_id, event_type) "
        "WHERE source = 'backfill'"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_inventory.ux_sc_events_backfill")
    op.execute("DROP INDEX IF EXISTS domain_inventory.ix_sc_events_ticket")
    op.execute("DROP TABLE IF EXISTS domain_inventory.supply_chain_events")
