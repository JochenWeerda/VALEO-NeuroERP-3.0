"""
VALEO-NeuroERP Database Connection and Setup
PostgreSQL database connection with SQLAlchemy
"""

import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup for PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,  # Better for PostgreSQL
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    echo=settings.DEBUG,  # SQL query logging in debug mode
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Session:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all database tables
    """
    try:
        logger.info("Creating database tables...")
        outbox_models = None
        ops_models = None
        l3c_models = None
        
        # Import all models to register them with Base
        try:
            from app.crm import models as crm_models
            logger.info("CRM models imported")
        except Exception as e:
            logger.warning(f"CRM models import failed: {e}")

        # Ensure outbox table is part of metadata
        try:
            from app.infrastructure.eventbus import outbox as outbox_models  # noqa: F401
            logger.info("Outbox models imported")
        except Exception as e:
            logger.warning(f"Outbox models import failed: {e}")

        try:
            from app.domains.operations import models as ops_models  # noqa: F401
            logger.info("Operations models imported")
        except Exception as e:
            logger.warning(f"Operations models import failed: {e}")

        try:
            from app.infrastructure.models import l3c_models  # noqa: F401
            logger.info("L3C models imported")
        except Exception as e:
            logger.warning(f"L3C models import failed: {e}")

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        logger.warning("Trying essential table fallback creation...")
        try:
            with engine.begin() as conn:
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS domain_ops"))
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS domain_inventory"))

            essential_tables = []
            if outbox_models is not None:
                essential_tables.append(outbox_models.OutboxEvent.__table__)
            if ops_models is not None:
                essential_tables.extend(
                    [
                        ops_models.Waage.__table__,
                        ops_models.Wiegung.__table__,
                        ops_models.Fahrzeug.__table__,
                        ops_models.Fahrer.__table__,
                        ops_models.FahrzeugTour.__table__,
                    ]
                )
            if l3c_models is not None:
                essential_tables.extend(
                    [
                        l3c_models.AgrarContract.__table__,
                        l3c_models.WeighingTicket.__table__,
                        l3c_models.AgrarContractAllocation.__table__,
                    ]
                )

            for table in essential_tables:
                try:
                    table.create(bind=engine, checkfirst=True)
                    logger.info("Ensured table exists: %s", table.fullname)
                except Exception as table_error:
                    logger.warning("Table create failed for %s, trying SQL fallback: %s", table.fullname, table_error)
                    if table.fullname == "domain_inventory.agrar_contracts":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_inventory.agrar_contracts (
                                        id VARCHAR PRIMARY KEY,
                                        contract_number VARCHAR(50) NOT NULL,
                                        contract_type VARCHAR(10) NOT NULL,
                                        harvest_year INTEGER NOT NULL,
                                        partner_id VARCHAR(64) NOT NULL,
                                        article_id VARCHAR(64) NOT NULL,
                                        pricing_model VARCHAR(10) NOT NULL,
                                        pool_group_id VARCHAR(64),
                                        fixed_price DECIMAL(12, 2),
                                        currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
                                        total_quantity_kg DECIMAL(12, 3) NOT NULL,
                                        remaining_quantity_kg DECIMAL(12, 3) NOT NULL,
                                        status VARCHAR(20) NOT NULL DEFAULT 'open',
                                        valid_from TIMESTAMPTZ,
                                        valid_until TIMESTAMPTZ,
                                        tenant_id VARCHAR NOT NULL,
                                        created_at TIMESTAMPTZ DEFAULT now(),
                                        updated_at TIMESTAMPTZ
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_inventory.agrar_contracts")
                    elif table.fullname == "domain_inventory.weighing_tickets":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_inventory.weighing_tickets (
                                        id VARCHAR PRIMARY KEY,
                                        ticket_number VARCHAR(50) NOT NULL,
                                        scale_id VARCHAR(50),
                                        vehicle_plate VARCHAR(20),
                                        gross_weight DECIMAL(12, 3),
                                        tare_weight DECIMAL(12, 3),
                                        net_weight DECIMAL(12, 3),
                                        first_weighing_at TIMESTAMPTZ,
                                        second_weighing_at TIMESTAMPTZ,
                                        moisture_pct DECIMAL(5, 2),
                                        protein_pct DECIMAL(5, 2),
                                        impurities_pct DECIMAL(5, 2),
                                        hl_weight DECIMAL(6, 2),
                                        billing_weight DECIMAL(12, 3),
                                        quality_data JSONB,
                                        contract_id VARCHAR,
                                        allocated_quantity_kg DECIMAL(12, 3),
                                        allocation_status VARCHAR(20) NOT NULL DEFAULT 'unallocated',
                                        weighing_date TIMESTAMPTZ DEFAULT now(),
                                        status VARCHAR(20) DEFAULT 'open',
                                        direction VARCHAR(10) DEFAULT 'in',
                                        reference_doc VARCHAR(100),
                                        tenant_id VARCHAR NOT NULL,
                                        created_at TIMESTAMPTZ DEFAULT now(),
                                        updated_at TIMESTAMPTZ
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_inventory.weighing_tickets")
                    elif table.fullname == "domain_inventory.agrar_contract_allocations":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_inventory.agrar_contract_allocations (
                                        id VARCHAR PRIMARY KEY,
                                        contract_id VARCHAR NOT NULL,
                                        ticket_id VARCHAR,
                                        allocation_quantity_kg DECIMAL(12, 3) NOT NULL,
                                        allocated_at TIMESTAMPTZ DEFAULT now(),
                                        note TEXT,
                                        tenant_id VARCHAR NOT NULL,
                                        created_at TIMESTAMPTZ DEFAULT now()
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_inventory.agrar_contract_allocations")
                    else:
                        raise
        except Exception as fallback_error:
            logger.warning(f"Essential table fallback creation failed: {fallback_error}")
        logger.warning("Continuing without full database tables (Testing mode)")
        # Don't raise - allow server to start for UI testing
        # raise

def reset_database():
    """
    Drop all tables and recreate them (for development/testing)
    """
    try:
        logger.warning("Resetting database - dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("All tables dropped successfully")
        create_tables()
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        raise

def init_db():
    """
    Initialize database with sample data
    """
    try:
        logger.info("Initializing database with sample data...")

        # Use SQLAlchemy session for data seeding
        db = SessionLocal()

        # Sample data will be inserted via Alembic migrations
        # This function can be used for additional runtime initialization if needed

        db.close()
        logger.info("Database initialization completed")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
