"""
Optimierte Datenbankabfragen für das ERP-System

Dieses Skript enthält optimierte Datenbankabfragen basierend auf den Ergebnissen 
der Datenbankoptimierungsphase. Es dient als Beispiel und Referenz für Best Practices.
"""

import time
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, func, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("optimized_queries")

# SQLAlchemy-Basis erstellen
Base = declarative_base()

# Modellklassen definieren
class Artikel(Base):
    """Artikelmodell mit optimierten Indizes"""
    __tablename__ = "artikel"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(50))
    
    # Beziehungen
    chargen = relationship("Charge", back_populates="artikel")
    
    # Indizes für optimierte Abfragen
    __table_args__ = (
        Index('idx_artikel_name', name),
        Index('idx_artikel_kategorie', category),
    )
    
    def __repr__(self):
        return f"<Artikel(id={self.id}, name='{self.name}', code='{self.code}')>"


class Charge(Base):
    """Chargenmodell mit optimierten Indizes"""
    __tablename__ = "charge"
    
    id = Column(Integer, primary_key=True)
    charge_number = Column(String(20), unique=True, nullable=False)
    artikel_id = Column(Integer, ForeignKey("artikel.id"), nullable=False)
    production_date = Column(String(10), nullable=False)  # Format: YYYY-MM-DD
    
    # Beziehungen
    artikel = relationship("Artikel", back_populates="chargen")
    
    # Indizes für optimierte Abfragen
    __table_args__ = (
        Index('idx_charge_artikel_id', artikel_id),
        Index('idx_charge_prod_datum', production_date),
    )
    
    def __repr__(self):
        return f"<Charge(id={self.id}, charge_number='{self.charge_number}')>"


# Verbindung zur Datenbank herstellen
def get_db_session() -> Session:
    """Erstellt eine Datenbankverbindung und gibt die Session zurück"""
    # In-Memory SQLite-Datenbank für Beispielzwecke
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def seed_demo_data(db: Session):
    """Füllt die Datenbank mit Demo-Daten"""
    # Artikel erstellen
    articles = [
        Artikel(id=1, name="Weizenschrot", code="WS-001", price=12.99, category="Getreide"),
        Artikel(id=2, name="Gerstenflocken", code="GF-002", price=10.50, category="Getreide"),
        Artikel(id=3, name="Mineralfutter", code="MF-003", price=25.75, category="Zusatzstoffe"),
        Artikel(id=4, name="Rapsextraktionsschrot", code="RES-004", price=18.20, category="Ölsaaten"),
        Artikel(id=5, name="Sojaextraktionsschrot", code="SES-005", price=22.40, category="Ölsaaten")
    ]
    db.add_all(articles)
    
    # Chargen erstellen
    charges = [
        Charge(id=1, artikel_id=1, charge_number="CH-001-2024", production_date="2024-01-15"),
        Charge(id=2, artikel_id=2, charge_number="CH-002-2024", production_date="2024-01-20"),
        Charge(id=3, artikel_id=3, charge_number="CH-003-2024", production_date="2024-02-05"),
        Charge(id=4, artikel_id=4, charge_number="CH-004-2024", production_date="2024-02-10"),
        Charge(id=5, artikel_id=5, charge_number="CH-005-2024", production_date="2024-02-15"),
        Charge(id=6, artikel_id=1, charge_number="CH-006-2024", production_date="2024-02-20"),
        Charge(id=7, artikel_id=2, charge_number="CH-007-2024", production_date="2024-02-25"),
        Charge(id=8, artikel_id=3, charge_number="CH-008-2024", production_date="2024-03-01"),
        Charge(id=9, artikel_id=4, charge_number="CH-009-2024", production_date="2024-03-05"),
        Charge(id=10, artikel_id=5, charge_number="CH-010-2024", production_date="2024-03-10")
    ]
    db.add_all(charges)
    
    db.commit()


# Originale (ineffiziente) Implementierungen
def get_articles_original(db: Session, category: Optional[str] = None) -> List[Artikel]:
    """Originale ineffiziente Implementierung der Artikel-Abfrage"""
    start_time = time.time()
    
    # Alle Artikel abrufen und dann filtern
    articles = db.query(Artikel).all()
    
    if category:
        articles = [a for a in articles if a.category == category]
    
    # Ineffiziente Sortierung in Python
    articles = sorted(articles, key=lambda a: a.name)
    
    duration = time.time() - start_time
    logger.info(f"Originalabfrage für Artikel dauerte {duration:.4f}s")
    
    return articles


def get_charges_original(db: Session, artikel_id: Optional[int] = None) -> List[Dict]:
    """Originale ineffiziente Implementierung der Chargen-Abfrage mit N+1-Problem"""
    start_time = time.time()
    
    # Alle Chargen abrufen
    charges = db.query(Charge).all()
    result = []
    
    for charge in charges:
        if artikel_id and charge.artikel_id != artikel_id:
            continue
            
        # N+1-Problem: Separate Abfrage für jeden Artikel
        artikel = db.query(Artikel).filter(Artikel.id == charge.artikel_id).first()
        
        charge_data = {
            "id": charge.id,
            "charge_number": charge.charge_number,
            "artikel_id": charge.artikel_id,
            "artikel_name": artikel.name if artikel else None,
            "production_date": charge.production_date
        }
        result.append(charge_data)
    
    duration = time.time() - start_time
    logger.info(f"Originalabfrage für Chargen dauerte {duration:.4f}s")
    
    return result


# Optimierte Implementierungen
def get_articles_optimized(
    db: Session, 
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
) -> Dict:
    """Optimierte Implementierung der Artikel-Abfrage mit Filterung und Paginierung in der Datenbank"""
    start_time = time.time()
    
    # Basisabfrage mit effizienter Datenbankfilterung und -sortierung
    query = db.query(Artikel)
    
    # Filterung anwenden
    if category:
        query = query.filter(Artikel.category == category)
    
    # Sortierung in der Datenbank durchführen
    query = query.order_by(Artikel.name)
    
    # Paginierung in der Datenbank durchführen
    total = query.count()
    articles = query.offset((page - 1) * page_size).limit(page_size).all()
    
    duration = time.time() - start_time
    logger.info(f"Optimierte Abfrage für Artikel dauerte {duration:.4f}s")
    
    return {
        "items": articles,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


def get_charges_optimized(db: Session, artikel_id: Optional[int] = None) -> List[Dict]:
    """Optimierte Implementierung der Chargen-Abfrage mit Batch-Abruf statt N+1-Abfragen"""
    start_time = time.time()
    
    # Basisabfrage
    query = db.query(Charge)
    
    # Filterung anwenden
    if artikel_id:
        query = query.filter(Charge.artikel_id == artikel_id)
    
    # Alle benötigten Chargen auf einmal abrufen
    charges = query.all()
    
    # Wenn keine Chargen gefunden wurden, leere Liste zurückgeben
    if not charges:
        return []
    
    # Alle benötigten Artikel-IDs sammeln
    artikel_ids = {charge.artikel_id for charge in charges}
    
    # Batch-Abruf aller benötigten Artikel
    artikel_dict = {
        artikel.id: artikel 
        for artikel in db.query(Artikel).filter(Artikel.id.in_(artikel_ids))
    }
    
    # Ergebnisse zusammenstellen
    result = []
    for charge in charges:
        artikel = artikel_dict.get(charge.artikel_id)
        charge_data = {
            "id": charge.id,
            "charge_number": charge.charge_number,
            "artikel_id": charge.artikel_id,
            "artikel_name": artikel.name if artikel else None,
            "production_date": charge.production_date
        }
        result.append(charge_data)
    
    duration = time.time() - start_time
    logger.info(f"Optimierte Abfrage für Chargen dauerte {duration:.4f}s")
    
    return result


def get_charge_details_optimized(db: Session, charge_id: int) -> Dict:
    """Optimierte Implementierung der Chargen-Details-Abfrage mit JOIN statt N+1-Abfragen"""
    start_time = time.time()
    
    # JOIN-Operation für effiziente Abfrage
    result = db.query(
        Charge, 
        Artikel.name.label("artikel_name"),
        Artikel.code.label("artikel_code")
    ).join(
        Artikel, Charge.artikel_id == Artikel.id
    ).filter(
        Charge.id == charge_id
    ).first()
    
    if not result:
        return None
    
    charge, artikel_name, artikel_code = result
    
    charge_data = {
        "id": charge.id,
        "charge_number": charge.charge_number,
        "artikel_id": charge.artikel_id,
        "artikel_name": artikel_name,
        "artikel_code": artikel_code,
        "production_date": charge.production_date
    }
    
    duration = time.time() - start_time
    logger.info(f"Optimierte Abfrage für Chargendetails dauerte {duration:.4f}s")
    
    return charge_data


def batch_processing_example(db: Session, artikel_ids: List[int], batch_size: int = 100) -> None:
    """Beispiel für Batch-Processing bei großen Datensätzen"""
    start_time = time.time()
    
    # Verarbeitung in Batches
    for i in range(0, len(artikel_ids), batch_size):
        batch = artikel_ids[i:i+batch_size]
        
        # Batch-Abfrage für effiziente Verarbeitung
        artikel_batch = db.query(Artikel).filter(Artikel.id.in_(batch)).all()
        
        # Verarbeitung des Batches
        for artikel in artikel_batch:
            # Hier können beliebige Operationen auf dem Artikel durchgeführt werden
            logger.debug(f"Verarbeite Artikel: {artikel.name}")
    
    duration = time.time() - start_time
    logger.info(f"Batch-Verarbeitung dauerte {duration:.4f}s")


def run_benchmark():
    """Führt einen Benchmark der optimierten vs. originalen Abfragen durch"""
    logger.info("Starte Benchmark...")
    
    # Datenbankverbindung herstellen
    db = get_db_session()
    
    # Demo-Daten erstellen
    seed_demo_data(db)
    
    # Benchmark: Artikel abrufen
    logger.info("\n=== Benchmark: Artikel abrufen ===")
    articles_original = get_articles_original(db, category="Getreide")
    logger.info(f"Original: {len(articles_original)} Artikel gefunden")
    
    articles_optimized = get_articles_optimized(db, category="Getreide")
    logger.info(f"Optimiert: {articles_optimized['total']} Artikel gefunden, {len(articles_optimized['items'])} angezeigt")
    
    # Benchmark: Chargen abrufen
    logger.info("\n=== Benchmark: Chargen abrufen ===")
    charges_original = get_charges_original(db)
    logger.info(f"Original: {len(charges_original)} Chargen gefunden")
    
    charges_optimized = get_charges_optimized(db)
    logger.info(f"Optimiert: {len(charges_optimized)} Chargen gefunden")
    
    # Benchmark: Chargendetails abrufen
    logger.info("\n=== Benchmark: Chargendetails abrufen ===")
    # Original (simuliert durch get_charges_original mit Filterung)
    charge_original = next((c for c in get_charges_original(db) if c["id"] == 1), None)
    
    # Optimiert
    charge_optimized = get_charge_details_optimized(db, 1)
    
    # Benchmark: Batch-Processing
    logger.info("\n=== Benchmark: Batch-Processing ===")
    artikel_ids = list(range(1, 6))  # In der Praxis wären dies viel mehr IDs
    batch_processing_example(db, artikel_ids)
    
    logger.info("\nBenchmark abgeschlossen.")


if __name__ == "__main__":
    run_benchmark() 