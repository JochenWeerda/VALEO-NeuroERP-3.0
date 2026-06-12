"""Logistik Kern-Tabellen (domain_logistics) — Alembic statt Runtime-DDL.

Revision ID: log_logistics_core_20260612
Revises: crm_kim_perf_indexes_20260612

LOG-PROD-001: Tabellen für Touren/ePOD/Statistik und Frachttarife, die zuvor
per ``CREATE TABLE IF NOT EXISTS`` in ``logistics_tours.py`` /
``logistics_freight.py`` angelegt wurden.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "log_logistics_core_20260612"
down_revision: Union[str, Sequence[str], None] = "crm_kim_perf_indexes_20260612"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE SCHEMA IF NOT EXISTS domain_logistics;

        CREATE TABLE IF NOT EXISTS domain_logistics.tours (
            id          TEXT PRIMARY KEY,
            date        TIMESTAMPTZ,
            vehicle_id  TEXT,
            driver_id   TEXT,
            status      TEXT NOT NULL DEFAULT 'GEPLANT',
            notes       TEXT,
            tenant_id   TEXT,
            created_at  TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS domain_logistics.tour_stops (
            id                  TEXT PRIMARY KEY,
            tour_id             TEXT NOT NULL,
            stop_order          INTEGER NOT NULL DEFAULT 0,
            address             TEXT,
            lat                 DOUBLE PRECISION,
            lng                 DOUBLE PRECISION,
            customer_id         TEXT,
            delivery_note_ref   TEXT,
            planned_arrival     TIMESTAMPTZ,
            actual_arrival      TIMESTAMPTZ,
            status              TEXT NOT NULL DEFAULT 'GEPLANT',
            pod_data            JSONB,
            tenant_id           TEXT,
            created_at          TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS domain_logistics.tour_events (
            id          TEXT PRIMARY KEY,
            tour_id     TEXT NOT NULL,
            event_type  TEXT NOT NULL,
            event_ts    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            lat         DOUBLE PRECISION,
            lng         DOUBLE PRECISION,
            notes       TEXT,
            driver_ref  TEXT,
            tenant_id   TEXT
        );

        CREATE TABLE IF NOT EXISTS domain_logistics.freight_tariffs (
            id                TEXT PRIMARY KEY,
            carrier_id        TEXT NOT NULL,
            zone_from         TEXT,
            zone_to           TEXT,
            weight_from_kg    DOUBLE PRECISION NOT NULL DEFAULT 0,
            weight_to_kg      DOUBLE PRECISION NOT NULL DEFAULT 999999,
            price_per_100kg   DOUBLE PRECISION NOT NULL,
            min_charge        DOUBLE PRECISION NOT NULL DEFAULT 0,
            tenant_id         TEXT,
            created_at        TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS ix_logistics_tours_tenant_created
            ON domain_logistics.tours (tenant_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS ix_logistics_tour_stops_tour_order
            ON domain_logistics.tour_stops (tour_id, stop_order);
        CREATE INDEX IF NOT EXISTS ix_logistics_tour_events_tour_ts
            ON domain_logistics.tour_events (tour_id, event_ts);
        CREATE INDEX IF NOT EXISTS ix_logistics_freight_tariffs_carrier
            ON domain_logistics.freight_tariffs (carrier_id, tenant_id, weight_from_kg);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS domain_logistics.freight_tariffs;
        DROP TABLE IF EXISTS domain_logistics.tour_events;
        DROP TABLE IF EXISTS domain_logistics.tour_stops;
        DROP TABLE IF EXISTS domain_logistics.tours;
        """
    )
