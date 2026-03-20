"""
VALEO-NeuroERP Database Connection and Setup
PostgreSQL database connection with SQLAlchemy
"""

import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool

from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup for PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,       # matches FastAPI threadpool per worker (min(32,cpu+4)=16 on 12-CPU host)
    max_overflow=5,     # small overflow headroom per worker
    pool_timeout=10,    # fail fast instead of queueing for 30s
    pool_recycle=1800,
    pool_pre_ping=True, # detect stale connections after fork
    echo=settings.DEBUG,
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

        try:
            from app.infrastructure import models as shared_models  # noqa: F401
            logger.info("Shared infrastructure models imported")
        except Exception as e:
            logger.warning(f"Shared infrastructure models import failed: {e}")

        try:
            from app.models import knowledge as knowledge_models  # noqa: F401
            logger.info("Knowledge models imported")
        except Exception as e:
            logger.warning(f"Knowledge models import failed: {e}")

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
                        ops_models.FuhrparkTerminart.__table__,
                        ops_models.FuhrparkRechnung.__table__,
                        ops_models.FuhrparkAusgehendesDokument.__table__,
                        ops_models.Dokument.__table__,
                        ops_models.DokumentVersion.__table__,
                        ops_models.Charge.__table__,
                        ops_models.Rahmenvertrag.__table__,
                        ops_models.ZertifikatEintrag.__table__,
                    ]
                )
            if l3c_models is not None:
                essential_tables.extend(
                    [
                        l3c_models.AgrarContract.__table__,
                        l3c_models.WeighingTicket.__table__,
                        l3c_models.WeighingMeasurement.__table__,
                        l3c_models.AgrarContractAllocation.__table__,
                        l3c_models.AgrarSettlement.__table__,
                        l3c_models.AgrarSettlementDeduction.__table__,
                        l3c_models.Silo.__table__,
                        l3c_models.SiloLot.__table__,
                        l3c_models.SiloLotMovement.__table__,
                        l3c_models.SiloQualitySnapshot.__table__,
                        l3c_models.ArticleBatch.__table__,
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
                    elif table.fullname == "domain_inventory.agrar_settlements":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_inventory.agrar_settlements (
                                        id VARCHAR PRIMARY KEY,
                                        settlement_number VARCHAR(50) NOT NULL,
                                        contract_id VARCHAR,
                                        ticket_id VARCHAR,
                                        supplier_id VARCHAR(64) NOT NULL,
                                        article_id VARCHAR(64),
                                        gross_quantity_kg DECIMAL(12, 3) NOT NULL,
                                        billing_quantity_kg DECIMAL(12, 3) NOT NULL,
                                        unit_price_eur_per_ton DECIMAL(12, 2) NOT NULL,
                                        gross_amount_eur DECIMAL(14, 2) NOT NULL,
                                        total_deductions_eur DECIMAL(14, 2) NOT NULL DEFAULT 0,
                                        net_amount_eur DECIMAL(14, 2) NOT NULL,
                                        currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
                                        status VARCHAR(20) NOT NULL DEFAULT 'draft',
                                        posted_journal_ref VARCHAR(64),
                                        posted_at TIMESTAMPTZ,
                                        note TEXT,
                                        tenant_id VARCHAR NOT NULL,
                                        created_at TIMESTAMPTZ DEFAULT now(),
                                        updated_at TIMESTAMPTZ
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_inventory.agrar_settlements")
                    elif table.fullname == "domain_inventory.agrar_settlement_deductions":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_inventory.agrar_settlement_deductions (
                                        id VARCHAR PRIMARY KEY,
                                        settlement_id VARCHAR NOT NULL,
                                        deduction_type VARCHAR(20) NOT NULL,
                                        mode VARCHAR(20) NOT NULL,
                                        rate_per_ton_eur DECIMAL(12, 2),
                                        fixed_amount_eur DECIMAL(12, 2),
                                        basis_quantity_tons DECIMAL(12, 3),
                                        amount_eur DECIMAL(14, 2) NOT NULL,
                                        note TEXT,
                                        tenant_id VARCHAR NOT NULL,
                                        created_at TIMESTAMPTZ DEFAULT now()
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_inventory.agrar_settlement_deductions")
                    elif table.fullname == "domain_inventory.weighing_measurements":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_inventory.weighing_measurements (
                                        id VARCHAR PRIMARY KEY,
                                        ticket_id VARCHAR NOT NULL REFERENCES domain_inventory.weighing_tickets(id),
                                        metric_key VARCHAR(50) NOT NULL,
                                        metric_value DECIMAL(10, 3) NOT NULL,
                                        unit VARCHAR(20),
                                        measured_at TIMESTAMPTZ,
                                        tenant_id VARCHAR NOT NULL,
                                        created_at TIMESTAMPTZ DEFAULT now()
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_inventory.weighing_measurements")
                    elif table.fullname == "domain_inventory.silos":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_inventory.silos (
                                        id VARCHAR PRIMARY KEY,
                                        silo_number VARCHAR(50) NOT NULL,
                                        name VARCHAR(120),
                                        article_id VARCHAR(64),
                                        capacity_tons DECIMAL(12, 3) NOT NULL,
                                        tenant_id VARCHAR NOT NULL,
                                        is_active BOOLEAN NOT NULL DEFAULT TRUE,
                                        created_at TIMESTAMPTZ DEFAULT now(),
                                        updated_at TIMESTAMPTZ
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_inventory.silos")
                    elif table.fullname == "domain_inventory.silo_lots":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_inventory.silo_lots (
                                        id VARCHAR PRIMARY KEY,
                                        silo_id VARCHAR NOT NULL REFERENCES domain_inventory.silos(id),
                                        virtual_lot_number VARCHAR(64) NOT NULL,
                                        source_ticket_id VARCHAR REFERENCES domain_inventory.weighing_tickets(id),
                                        source_partner_id VARCHAR(64),
                                        article_id VARCHAR(64),
                                        quantity_tons DECIMAL(12, 3) NOT NULL,
                                        moisture_pct DECIMAL(5, 2),
                                        protein_pct DECIMAL(5, 2),
                                        impurities_pct DECIMAL(5, 2),
                                        hl_weight DECIMAL(6, 2),
                                        status VARCHAR(20) NOT NULL DEFAULT 'active',
                                        tenant_id VARCHAR NOT NULL,
                                        created_at TIMESTAMPTZ DEFAULT now(),
                                        updated_at TIMESTAMPTZ
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_inventory.silo_lots")
                    elif table.fullname == "domain_inventory.silo_lot_movements":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_inventory.silo_lot_movements (
                                        id VARCHAR PRIMARY KEY,
                                        silo_lot_id VARCHAR NOT NULL REFERENCES domain_inventory.silo_lots(id),
                                        movement_type VARCHAR(20) NOT NULL,
                                        quantity_tons DECIMAL(12, 3) NOT NULL,
                                        note TEXT,
                                        tenant_id VARCHAR NOT NULL,
                                        created_at TIMESTAMPTZ DEFAULT now()
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_inventory.silo_lot_movements")
                    elif table.fullname == "domain_inventory.silo_quality_snapshots":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_inventory.silo_quality_snapshots (
                                        id VARCHAR PRIMARY KEY,
                                        silo_id VARCHAR NOT NULL REFERENCES domain_inventory.silos(id),
                                        total_quantity_tons DECIMAL(12, 3) NOT NULL DEFAULT 0,
                                        moisture_avg_pct DECIMAL(5, 2),
                                        protein_avg_pct DECIMAL(5, 2),
                                        impurities_avg_pct DECIMAL(5, 2),
                                        hl_weight_avg DECIMAL(6, 2),
                                        lot_count INTEGER NOT NULL DEFAULT 0,
                                        tenant_id VARCHAR NOT NULL,
                                        created_at TIMESTAMPTZ DEFAULT now()
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_inventory.silo_quality_snapshots")
                    elif table.fullname == "domain_inventory.article_batches":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_inventory.article_batches (
                                        id VARCHAR PRIMARY KEY,
                                        article_id VARCHAR NOT NULL,
                                        batch_number VARCHAR(50) NOT NULL,
                                        warehouse_id VARCHAR NOT NULL,
                                        quantity DECIMAL(12, 3) DEFAULT 0,
                                        expiry_date TIMESTAMPTZ,
                                        tenant_id VARCHAR NOT NULL,
                                        created_at TIMESTAMPTZ DEFAULT now()
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_inventory.article_batches")
                    elif table.fullname == "domain_ops.ops_dokumente":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_ops.ops_dokumente (
                                        id VARCHAR PRIMARY KEY,
                                        name VARCHAR(255) NOT NULL,
                                        typ VARCHAR(20) NOT NULL,
                                        kategorie VARCHAR(100) NOT NULL,
                                        groesse INTEGER DEFAULT 0,
                                        speicherpfad VARCHAR(500),
                                        mime_type VARCHAR(100),
                                        beschreibung TEXT,
                                        schlagwoerter VARCHAR(500),
                                        version INTEGER DEFAULT 1,
                                        referenz_typ VARCHAR(50),
                                        referenz_id VARCHAR(100),
                                        status VARCHAR(20) DEFAULT 'aktiv',
                                        hochgeladen_am TIMESTAMPTZ DEFAULT now(),
                                        hochgeladen_von VARCHAR(100),
                                        geloescht_am TIMESTAMPTZ,
                                        geloescht_von VARCHAR(100),
                                        created_at TIMESTAMPTZ DEFAULT now(),
                                        updated_at TIMESTAMPTZ DEFAULT now(),
                                        created_by VARCHAR(100),
                                        updated_by VARCHAR(100)
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_ops.ops_dokumente")
                    elif table.fullname == "domain_ops.ops_dokument_versionen":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_ops.ops_dokument_versionen (
                                        id VARCHAR PRIMARY KEY,
                                        dokument_id VARCHAR REFERENCES domain_ops.ops_dokumente(id) ON DELETE CASCADE,
                                        version INTEGER NOT NULL,
                                        name VARCHAR(255) NOT NULL,
                                        groesse INTEGER DEFAULT 0,
                                        speicherpfad VARCHAR(500),
                                        aenderungsbemerkung TEXT,
                                        erstellt_am TIMESTAMPTZ DEFAULT now(),
                                        erstellt_von VARCHAR(100)
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_ops.ops_dokument_versionen")
                    elif table.fullname == "domain_ops.ops_rahmenvertraege":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_ops.ops_rahmenvertraege (
                                        id VARCHAR PRIMARY KEY,
                                        nummer VARCHAR(50) UNIQUE NOT NULL,
                                        partner VARCHAR(255) NOT NULL,
                                        partner_id VARCHAR(100) NOT NULL,
                                        typ VARCHAR(50) NOT NULL,
                                        artikel VARCHAR(100) NOT NULL,
                                        artikel_id VARCHAR(100) NOT NULL,
                                        menge DOUBLE PRECISION NOT NULL,
                                        restmenge DOUBLE PRECISION NOT NULL,
                                        preis DECIMAL(14, 2) NOT NULL,
                                        laufzeit_bis TIMESTAMPTZ NOT NULL,
                                        status VARCHAR(30) DEFAULT 'aktiv',
                                        created_at TIMESTAMPTZ DEFAULT now(),
                                        updated_at TIMESTAMPTZ DEFAULT now(),
                                        created_by VARCHAR(100),
                                        updated_by VARCHAR(100)
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_ops.ops_rahmenvertraege")
                    elif table.fullname == "domain_ops.ops_zertifikate":
                        with engine.begin() as conn:
                            conn.execute(
                                text(
                                    """
                                    CREATE TABLE IF NOT EXISTS domain_ops.ops_zertifikate (
                                        id VARCHAR PRIMARY KEY,
                                        art VARCHAR(120) NOT NULL,
                                        standard VARCHAR(120) NOT NULL,
                                        nummer VARCHAR(120) NOT NULL,
                                        gueltig_bis TIMESTAMPTZ,
                                        audit TIMESTAMPTZ,
                                        status VARCHAR(30) DEFAULT 'gueltig',
                                        created_at TIMESTAMPTZ DEFAULT now(),
                                        updated_at TIMESTAMPTZ DEFAULT now()
                                    )
                                    """
                                )
                            )
                        logger.info("Ensured table exists via SQL fallback: domain_ops.ops_zertifikate")
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
