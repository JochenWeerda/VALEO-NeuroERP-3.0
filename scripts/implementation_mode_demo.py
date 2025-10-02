#!/usr/bin/env python3
"""
Demo für den IMPLEMENTATION-Modus des APM-Frameworks.
Zeigt die vollständige Implementierung basierend auf den Code-Artefakten.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from bson import ObjectId
from datetime import datetime

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.apm_framework.apm_workflow import APMWorkflow
from backend.apm_framework.mongodb_connector import APMMongoDBConnector
from backend.apm_framework.rag_service import RAGService

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# RAG-Service für Tests
class DummyRAGService:
    async def query(self, prompt, agent_type=None):
        logger.info(f"RAG-Abfrage für {agent_type}: {prompt[:50]}...")
        
        # Simulierte Antworten basierend auf dem Prompt-Inhalt
        if "Implementierungsplan" in prompt:
            return """
            # Implementierungsplan für Transaktionsverarbeitung
            
            ## Verzeichnisstruktur
            ```
            transaction_processing/
            ├── __init__.py
            ├── db/
            │   ├── __init__.py
            │   ├── db_connector.py
            │   └── transaction_repository.py
            ├── models/
            │   ├── __init__.py
            │   └── transaction.py
            ├── core/
            │   ├── __init__.py
            │   ├── chunk_manager.py
            │   ├── savepoint_manager.py
            │   └── audit_logger.py
            ├── utils/
            │   ├── __init__.py
            │   ├── serialization.py
            │   └── performance_metrics.py
            └── tests/
                ├── __init__.py
                ├── test_transaction.py
                ├── test_chunk_manager.py
                └── test_audit_logger.py
            ```
            
            ## Implementierungsschritte
            1. Basisklassen für Transaktionen implementieren
            2. Chunk-Manager für die Verarbeitung entwickeln
            3. Savepoint-Funktionalität integrieren
            4. Asynchronen Audit-Logger implementieren
            5. Datenbankanbindung mit optimistischem Locking entwickeln
            6. Unit-Tests für alle Komponenten schreiben
            7. Integrationstests für den Gesamtprozess erstellen
            8. Performance-Tests durchführen
            
            ## Abhängigkeiten
            - sqlalchemy>=2.0.0
            - psycopg2-binary>=2.9.5
            - asyncio>=3.4.3
            - aioredis>=2.0.0
            - pytest>=7.0.0
            - pytest-asyncio>=0.18.0
            """
        elif "Datenbankanbindung" in prompt:
            return """
            ```python
            # db_connector.py
            import logging
            from typing import Dict, List, Any, Optional
            from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime
            from sqlalchemy.orm import sessionmaker, declarative_base
            from sqlalchemy.exc import SQLAlchemyError
            from datetime import datetime
            
            logger = logging.getLogger(__name__)
            Base = declarative_base()
            
            class DBConnector:
                def __init__(self, connection_string: str):
                    """Initialisiert die Datenbankverbindung.
                    
                    Args:
                        connection_string: Verbindungsstring für die Datenbank
                    """
                    self.engine = create_engine(connection_string)
                    self.metadata = MetaData()
                    self.Session = sessionmaker(bind=self.engine)
                    logger.info("Datenbankverbindung initialisiert")
                
                def create_tables(self):
                    """Erstellt alle Tabellen in der Datenbank."""
                    Base.metadata.create_all(self.engine)
                    logger.info("Datenbanktabellen erstellt")
                
                def get_session(self):
                    """Gibt eine neue Datenbanksession zurück."""
                    return self.Session()
                
                def health_check(self) -> bool:
                    """Führt einen Gesundheitscheck der Datenbankverbindung durch."""
                    try:
                        # Einfache Abfrage zur Überprüfung der Verbindung
                        with self.engine.connect() as conn:
                            conn.execute("SELECT 1")
                        return True
                    except SQLAlchemyError as e:
                        logger.error(f"Database health check failed: {str(e)}")
                        return False
            ```
            """
        elif "Implementierung der Transaktionsverarbeitung" in prompt:
            return """
            ```python                                                                                                                                                           
             # transaction_repository.py
             import logging
             from typing import List, Dict, Any, Optional
             from sqlalchemy.orm import Session
             from sqlalchemy.exc import SQLAlchemyError
             from sqlalchemy import text
             from datetime import datetime
             
             from ..models.transaction import Transaction, TransactionStatus
             
             logger = logging.getLogger(__name__)
             
             class TransactionRepository:
                 def __init__(self, session: Session):
                     """Initialisiert das Repository mit einer Datenbanksession.
                     
                     Args:
                         session: SQLAlchemy-Session
                     """
                     self.session = session
                 
                 def save(self, transaction: Transaction) -> bool:
                     """Speichert eine Transaktion in der Datenbank.
                     
                     Args:
                         transaction: Zu speichernde Transaktion
                         
                     Returns:
                         True, wenn erfolgreich, sonst False
                     """
                     try:
                         self.session.add(transaction)
                         self.session.commit()
                         logger.info(f"Transaktion {transaction.id} gespeichert")
                         return True
                     except SQLAlchemyError as e:
                         self.session.rollback()
                         logger.error(f"Fehler beim Speichern der Transaktion: {str(e)}")
                         return False
                 
                 def save_batch(self, transactions: List[Transaction]) -> Dict[str, Any]:
                     """Speichert einen Batch von Transaktionen mit optimistischem Locking.
                     
                     Args:
                         transactions: Liste von Transaktionen
                         
                     Returns:
                         Ergebnis mit Anzahl erfolgreicher und fehlgeschlagener Transaktionen
                     """
                     successful = 0
                     failed = 0
                     
                     try:
                         # Optimistisches Locking durch Versionsüberprüfung
                         for transaction in transactions:
                             try:
                                 # Versionsüberprüfung
                                 if transaction.id:
                                     db_version = self.session.query(Transaction).filter_by(
                                         id=transaction.id).first()
                                     if db_version and db_version.version != transaction.version:
                                         logger.warning(f"Versionskonflikt für Transaktion {transaction.id}")
                                         failed += 1
                                         continue
                                 
                                 # Version inkrementieren
                                 transaction.version += 1
                                 transaction.updated_at = datetime.now()
                                 
                                 self.session.add(transaction)
                                 successful += 1
                             except SQLAlchemyError as e:
                                 logger.error(f"Fehler bei Transaktion {transaction.id}: {str(e)}")
                                 failed += 1
                         
                         self.session.commit()
                         logger.info(f"Batch mit {successful} Transaktionen gespeichert, {failed} fehlgeschlagen")
                     except SQLAlchemyError as e:
                         self.session.rollback()
                         logger.error(f"Fehler beim Batch-Speichern: {str(e)}")
                         return {"success": False, "successful": successful, "failed": failed + len(transactions) - successful}
                     
                     return {"success": True, "successful": successful, "failed": failed}
                 
                 def find_by_id(self, transaction_id: str) -> Optional[Transaction]:
                     """Findet eine Transaktion anhand ihrer ID.
                     
                     Args:
                         transaction_id: ID der Transaktion
                         
                     Returns:
                         Transaktion oder None
                     """
                     try:
                         return self.session.query(Transaction).filter_by(id=transaction_id).first()
                     except SQLAlchemyError as e:
                         logger.error(f"Fehler beim Suchen der Transaktion: {str(e)}")
                         return None
                 
                 def find_by_status(self, status: TransactionStatus, limit: int = 100) -> List[Transaction]:
                     """Findet Transaktionen anhand ihres Status.
                     
                     Args:
                         status: Status der Transaktionen
                         limit: Maximale Anzahl zurückzugebender Transaktionen
                         
                     Returns:
                         Liste von Transaktionen
                     """
                     try:
                         return self.session.query(Transaction).filter_by(status=status).limit(limit).all()
                     except SQLAlchemyError as e:
                         logger.error(f"Fehler beim Suchen von Transaktionen: {str(e)}")
                         return []
                 
                 def create_savepoint(self, name: str) -> bool:
                     """Erstellt einen Savepoint in der Datenbank.
                     
                     Args:
                         name: Name des Savepoints
                         
                     Returns:
                         True, wenn erfolgreich, sonst False
                     """
                     try:
                         self.session.execute(text(f"SAVEPOINT {name}"))
                         return True
                     except SQLAlchemyError as e:
                         logger.error(f"Fehler beim Erstellen des Savepoints: {str(e)}")
                         return False
                 
                 def rollback_to_savepoint(self, name: str) -> bool:
                     """Setzt die Datenbank auf einen Savepoint zurück.
                     
                     Args:
                         name: Name des Savepoints
                         
                     Returns:
                         True, wenn erfolgreich, sonst False
                     """
                     try:
                         self.session.execute(text(f"ROLLBACK TO SAVEPOINT {name}"))
                         return True
                     except SQLAlchemyError as e:
                         logger.error(f"Fehler beim Zurücksetzen auf Savepoint: {str(e)}")
                         return False
             ```
            """
        elif "Unit-Tests" in prompt:
            return """
            ```python
            # test_transaction.py
            import pytest
            import asyncio
            from datetime import datetime
            from uuid import uuid4
            
            from transaction_processing.models.transaction import Transaction, TransactionType, TransactionStatus
            from transaction_processing.core.chunk_manager import ChunkManager
            from transaction_processing.core.audit_logger import AsyncAuditLogger
            
            @pytest.fixture
            def sample_transaction():
                """Erstellt eine Beispieltransaktion für Tests."""
                return Transaction(
                    id=str(uuid4()),
                    type=TransactionType.TRANSFER,
                    amount=100.0,
                    source_account="ACC123",
                    target_account="ACC456",
                    status=TransactionStatus.PENDING,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    version=1
                )
            
            @pytest.fixture
            def chunk_manager():
                """Erstellt einen ChunkManager für Tests."""
                return ChunkManager(chunk_size=5)
            
            @pytest.fixture
            def audit_logger():
                """Erstellt einen AsyncAuditLogger für Tests."""
                return AsyncAuditLogger()
            
            def test_transaction_creation(sample_transaction):
                """Testet die Erstellung einer Transaktion."""
                assert sample_transaction.id is not None
                assert sample_transaction.type == TransactionType.TRANSFER
                assert sample_transaction.amount == 100.0
                assert sample_transaction.status == TransactionStatus.PENDING
                assert sample_transaction.version == 1
            
            def test_transaction_serialization(sample_transaction):
                """Testet die Serialisierung einer Transaktion."""
                serialized = sample_transaction.to_dict()
                assert serialized["id"] == sample_transaction.id
                assert serialized["type"] == sample_transaction.type.value
                assert serialized["amount"] == sample_transaction.amount
                assert serialized["status"] == sample_transaction.status.value
            
            @pytest.mark.asyncio
            async def test_chunk_processing(chunk_manager, sample_transaction):
                """Testet die Chunk-basierte Verarbeitung von Transaktionen."""
                # Erstelle 12 Transaktionen
                transactions = [sample_transaction]
                for i in range(11):
                    tx = Transaction(
                        id=str(uuid4()),
                        type=TransactionType.TRANSFER,
                        amount=100.0 + i,
                        source_account=f"SRC{i}",
                        target_account=f"TGT{i}",
                        status=TransactionStatus.PENDING,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        version=1
                    )
                    transactions.append(tx)
                
                # Verarbeite in Chunks
                chunks = chunk_manager.split_into_chunks(transactions)
                assert len(chunks) == 3  # 12 Transaktionen / 5 pro Chunk = 3 Chunks
                assert len(chunks[0]) == 5
                assert len(chunks[1]) == 5
                assert len(chunks[2]) == 2
            
            @pytest.mark.asyncio
            async def test_audit_logging(audit_logger, sample_transaction):
                """Testet das asynchrone Audit-Logging."""
                # Starte den Logger
                await audit_logger.start()
                
                # Protokolliere eine Transaktion
                await audit_logger.log(sample_transaction, "CREATED")
                
                # Warte kurz, damit der asynchrone Logger Zeit hat
                await asyncio.sleep(0.1)
                
                # Prüfe, ob die Transaktion protokolliert wurde
                logs = await audit_logger.get_logs()
                assert len(logs) >= 1
                assert any(log["transaction_id"] == sample_transaction.id for log in logs)
                
                # Stoppe den Logger
                await audit_logger.stop()
            ```
            """
        else:
            return "Simulierte RAG-Antwort für: " + prompt[:30] + "..."

async def run_implementation_demo():
    """Führt die Demo für den IMPLEMENTATION-Modus aus."""
    try:
        # MongoDB-Verbindung initialisieren
        mongodb_uri = "mongodb://localhost:27017/"
        db_name = "valeo_neuroerp"
        
        mongodb = APMMongoDBConnector(mongodb_uri, db_name)
        await mongodb.connect()
        
        # Projekt-ID generieren
        project_id = ObjectId()
        
        # APM-Workflow initialisieren
        workflow = APMWorkflow(mongodb, str(project_id))
        
        # RAG-Service setzen
        rag_service = DummyRAGService()
        workflow.set_rag_service(rag_service)
        
        print("\n" + "="*80)
        print("IMPLEMENTATION-MODE DEMO")
        print("="*80)
        print("Diese Demo zeigt die vollständige Implementierung basierend auf den Code-Artefakten.")
        print("="*80)
        
        # CREATE-Ergebnis simulieren
        create_result_id = ObjectId()
        create_result = {
            "_id": create_result_id,
            "project_id": project_id,
            "artifacts": [
                {
                    "name": "Transaction",
                    "path": "models/transaction.py",
                    "type": "python",
                    "description": "Klasse für Transaktionen mit Unterstützung für verschiedene Transaktionstypen",
                    "content": """
                    class Transaction:
                        def __init__(self, id, type, amount, source_account, target_account, status, created_at, updated_at, version=1):
                            self.id = id
                            self.type = type
                            self.amount = amount
                            self.source_account = source_account
                            self.target_account = target_account
                            self.status = status
                            self.created_at = created_at
                            self.updated_at = updated_at
                            self.version = version
                            
                        def to_dict(self):
                            return {
                                "id": self.id,
                                "type": self.type.value,
                                "amount": self.amount,
                                "source_account": self.source_account,
                                "target_account": self.target_account,
                                "status": self.status.value,
                                "created_at": self.created_at,
                                "updated_at": self.updated_at,
                                "version": self.version
                            }
                    """
                },
                {
                    "name": "ChunkManager",
                    "path": "core/chunk_manager.py",
                    "type": "python",
                    "description": "Manager für die Chunk-basierte Verarbeitung von Transaktionen",
                    "content": """
                    class ChunkManager:
                        def __init__(self, chunk_size=100):
                            self.chunk_size = chunk_size
                            
                        def split_into_chunks(self, transactions):
                            return [transactions[i:i + self.chunk_size] for i in range(0, len(transactions), self.chunk_size)]
                            
                        async def process_chunks(self, chunks, processor_func):
                            results = []
                            for i, chunk in enumerate(chunks):
                                chunk_result = await processor_func(chunk)
                                results.append(chunk_result)
                            return results
                    """
                },
                {
                    "name": "AsyncAuditLogger",
                    "path": "core/audit_logger.py",
                    "type": "python",
                    "description": "Asynchroner Logger für Audit-Einträge",
                    "content": """
                    import asyncio
                    from datetime import datetime
                    
                    class AsyncAuditLogger:
                        def __init__(self):
                            self.queue = asyncio.Queue()
                            self.running = False
                            self.worker_task = None
                            self.logs = []
                            
                        async def start(self):
                            self.running = True
                            self.worker_task = asyncio.create_task(self._worker())
                            
                        async def stop(self):
                            self.running = False
                            if self.worker_task:
                                await self.worker_task
                                
                        async def log(self, transaction, action):
                            await self.queue.put({
                                "timestamp": datetime.now(),
                                "transaction_id": transaction.id,
                                "action": action,
                                "details": transaction.to_dict()
                            })
                            
                        async def _worker(self):
                            while self.running or not self.queue.empty():
                                try:
                                    log_entry = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                                    self.logs.append(log_entry)
                                    self.queue.task_done()
                                except asyncio.TimeoutError:
                                    pass
                                    
                        async def get_logs(self):
                            return self.logs
                    """
                }
            ],
            "timestamp": datetime.now(),
            "status": "completed"
        }
        
        # CREATE-Ergebnis in der Datenbank speichern
        await mongodb.insert_one("create_results", create_result)
        
        print(f"\nCREATE-Ergebnis simuliert mit ID: {create_result_id}")
        print(f"Anzahl der Code-Artefakte: {len(create_result['artifacts'])}")
        
        for i, artifact in enumerate(create_result['artifacts'], 1):
            print(f"\nArtefakt {i}: {artifact['name']}")
            print(f"Pfad: {artifact['path']}")
            print(f"Beschreibung: {artifact['description']}")
        
        # IMPLEMENTATION-Mode ausführen
        implementation_result = await workflow.run_implementation_mode(str(create_result_id))
        
        print(f"\nIMPLEMENTATION-Mode abgeschlossen mit ID: {implementation_result.get('id')}")
        
        # Implementierungsplan ausgeben
        implementation_plan = implementation_result.get('implementation_plan', {})
        print(f"\nImplementierungsplan: {implementation_plan.get('name')}")
        print(f"Beschreibung: {implementation_plan.get('description')}")
        
        # Dateien ausgeben
        files = implementation_result.get('files', [])
        print(f"\nAnzahl der implementierten Dateien: {len(files)}")
        
        for i, file in enumerate(files, 1):
            print(f"\nDatei {i}: {file.get('path')}")
            print(f"Typ: {file.get('type')}")
            print(f"Größe: {len(file.get('content', ''))} Zeichen")
        
        # Tests ausgeben
        tests = implementation_result.get('tests', [])
        print(f"\nAnzahl der implementierten Tests: {len(tests)}")
        
        for i, test in enumerate(tests, 1):
            print(f"\nTest {i}: {test.get('name')}")
            print(f"Beschreibung: {test.get('description')}")
            print(f"Status: {test.get('status')}")
        
        # Verbindung schließen
        workflow.close()
        
        print("\n" + "="*80)
        print("IMPLEMENTATION-Mode Demo erfolgreich abgeschlossen")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Fehler bei der IMPLEMENTATION-Mode Demo: {str(e)}")
        raise

async def main():
    """Hauptfunktion."""
    await run_implementation_demo()

if __name__ == "__main__":
    asyncio.run(main())
