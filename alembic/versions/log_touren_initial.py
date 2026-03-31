"""
Verladung Domain Models Migration
Creates tables for Tours, Stops, Delivery Notes, and Events
"""

from typing import Optional
from alembic import op
import sqlalchemy as sa
from app.core.uuid7 import default_prefixed_id, uuid7

# Revision identifiers
revision = "log_touren_initial"
down_revision = "ops_domain_initial"  # Depends on ops_domain_initial
branch_labels = None
depends_on = None


def generate_uuid() -> str:
    return uuid7()


def upgrade():
    # Create domain_log schema
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_log")
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_ops")
    
    # Create enum types if they don't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE tour_status AS ENUM ('planned', 'loading', 'dispatched', 'in_transit', 'completed', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE tour_type AS ENUM ('stueckgut', 'solo', 'express', 'grossgut');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE stop_status AS ENUM ('open', 'loading', 'unloading', 'completed', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE dn_status AS ENUM ('ready', 'loaded', 'delivered', 'returned');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE event_type AS ENUM (
                'TOUR_CREATED', 'TOUR_UPDATED', 'LOADING_STARTED', 'LOADING_FINISHED',
                'DISPATCHED', 'STOP_ARRIVED', 'STOP_DEPARTED', 'DELIVERY_COMPLETED', 'EXCEPTION'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create log_touren table
    op.create_table(
        "log_touren",
        sa.Column("id", sa.String, primary_key=True, default=default_prefixed_id("TOUR")),
        sa.Column("tour_no", sa.String(50), nullable=False, unique=True),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("week", sa.String(10)),
        sa.Column("type", sa.String(20), default="stueckgut"),
        sa.Column("status", sa.String(20), default="planned"),
        sa.Column("notes", sa.Text),
        sa.Column("driver_id", sa.String, sa.ForeignKey("domain_ops.ops_fahrer.id", ondelete="SET NULL")),
        sa.Column("vehicle_id", sa.String, sa.ForeignKey("domain_ops.ops_fahrzeuge.id", ondelete="SET NULL")),
        sa.Column("planned_departure_at", sa.DateTime(timezone=True)),
        sa.Column("actual_departure_at", sa.DateTime(timezone=True)),
        sa.Column("planned_arrival_at", sa.DateTime(timezone=True)),
        sa.Column("actual_arrival_at", sa.DateTime(timezone=True)),
        sa.Column("totals_json", sa.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("created_by", sa.String(100)),
        sa.Column("updated_by", sa.String(100)),
        schema="domain_log"
    )
    
    # Create log_tour_stops table
    op.create_table(
        "log_tour_stops",
        sa.Column("id", sa.String, primary_key=True, default=lambda: f"STOP-{uuid7()[:8].upper()}"),
        sa.Column("tour_id", sa.String, sa.ForeignKey("domain_log.log_touren.id", ondelete="CASCADE")),
        sa.Column("sequence", sa.Integer, nullable=False),
        sa.Column("status", sa.String(20), default="open"),
        sa.Column("customer_id", sa.String(100)),
        sa.Column("customer_name", sa.String(200)),
        sa.Column("address_id", sa.String(100)),
        sa.Column("address_label", sa.String(200)),
        sa.Column("street", sa.String(300)),
        sa.Column("zip_code", sa.String(20)),
        sa.Column("city", sa.String(200)),
        sa.Column("country", sa.String(10), default="DE"),
        sa.Column("time_window_from", sa.DateTime(timezone=True)),
        sa.Column("time_window_to", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text),
        sa.Column("totals_json", sa.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        schema="domain_log"
    )
    
    # Create log_tour_delivery_notes table
    op.create_table(
        "log_tour_delivery_notes",
        sa.Column("id", sa.String, primary_key=True, default=default_prefixed_id("DN")),
        sa.Column("tour_id", sa.String, sa.ForeignKey("domain_log.log_touren.id", ondelete="CASCADE")),
        sa.Column("stop_id", sa.String, sa.ForeignKey("domain_log.log_tour_stops.id", ondelete="CASCADE")),
        sa.Column("dn_no", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), default="ready"),
        sa.Column("order_id", sa.String(100)),
        sa.Column("customer_ref", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("loaded_at", sa.DateTime(timezone=True)),
        sa.Column("delivered_at", sa.DateTime(timezone=True)),
        sa.Column("items_lines", sa.Integer, default=0),
        sa.Column("items_pieces", sa.Integer, default=0),
        sa.Column("items_weight_kg", sa.Float, default=0),
        sa.Column("items_volume_m3", sa.Float, default=0),
        sa.Column("created_at_record", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        schema="domain_log"
    )
    
    # Create log_tour_events table
    op.create_table(
        "log_tour_events",
        sa.Column("id", sa.String, primary_key=True, default=default_prefixed_id("EVT")),
        sa.Column("tour_id", sa.String, sa.ForeignKey("domain_log.log_touren.id", ondelete="CASCADE")),
        sa.Column("at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("message", sa.Text),
        sa.Column("user_id", sa.String(100)),
        sa.Column("user_name", sa.String(200)),
        sa.Column("metadata_json", sa.JSON),
        schema="domain_log"
    )
    
    # Create indexes
    op.create_index("ix_log_touren_status", "log_touren", ["status"], schema="domain_log")
    op.create_index("ix_log_touren_tour_no", "log_touren", ["tour_no"], schema="domain_log")
    op.create_index("ix_log_touren_date", "log_touren", ["date"], schema="domain_log")
    op.create_index("ix_log_touren_week", "log_touren", ["week"], schema="domain_log")
    op.create_index("ix_log_stops_tour_id", "log_tour_stops", ["tour_id"], schema="domain_log")
    op.create_index("ix_log_stops_sequence", "log_tour_stops", ["sequence"], schema="domain_log")
    op.create_index("ix_log_dn_tour_id", "log_tour_delivery_notes", ["tour_id"], schema="domain_log")
    op.create_index("ix_log_dn_stop_id", "log_tour_delivery_notes", ["stop_id"], schema="domain_log")
    op.create_index("ix_log_events_tour_id", "log_tour_events", ["tour_id"], schema="domain_log")
    op.create_index("ix_log_events_at", "log_tour_events", ["at"], schema="domain_log")


def downgrade():
    # Drop tables in reverse order
    op.drop_table("log_tour_events", schema="domain_log")
    op.drop_table("log_tour_delivery_notes", schema="domain_log")
    op.drop_table("log_tour_stops", schema="domain_log")
    op.drop_table("log_touren", schema="domain_log")
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS event_type CASCADE;")
    op.execute("DROP TYPE IF EXISTS dn_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS stop_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS tour_type CASCADE;")
    op.execute("DROP TYPE IF EXISTS tour_status CASCADE;")
