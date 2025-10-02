#!/usr/bin/env python3
"""
Demo für den CREATE-Modus des APM-Frameworks.
Generiert Code-Artefakte basierend auf dem Lösungsdesign.
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
        if "Transaction" in prompt:
            return """
            ```python
            from enum import Enum
            from datetime import datetime
            from typing import Optional, Dict, Any
            
            class TransactionType(Enum):
                INBOUND = "inbound"
                OUTBOUND = "outbound"
                TRANSFER = "transfer"
            
            class TransactionStatus(Enum):
                PENDING = "pending"
                PROCESSING = "processing"
                COMPLETED = "completed"
                FAILED = "failed"
                CANCELLED = "cancelled"
            
            class Transaction:
                def __init__(self, 
                             id: str,
                             type: TransactionType,
                             amount: float,
                             source_account: str,
                             target_account: str,
                             status: TransactionStatus = TransactionStatus.PENDING,
                             created_at: Optional[datetime] = None,
                             updated_at: Optional[datetime] = None,
                             version: int = 1,
                             metadata: Optional[Dict[str, Any]] = None):
                    self.id = id
                    self.type = type
                    self.amount = amount
                    self.source_account = source_account
                    self.target_account = target_account
                    self.status = status
                    self.created_at = created_at or datetime.now()
                    self.updated_at = updated_at or datetime.now()
                    self.version = version
                    self.metadata = metadata or {}
                
                def to_dict(self) -> Dict[str, Any]:
                    return {
                        "id": self.id,
                        "type": self.type.value,
                        "amount": self.amount,
                        "source_account": self.source_account,
                        "target_account": self.target_account,
                        "status": self.status.value,
                        "created_at": self.created_at,
                        "updated_at": self.updated_at,
                        "version": self.version,
                        "metadata": self.metadata
                    }
                
                @classmethod
                def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
                    return cls(
                        id=data["id"],
                        type=TransactionType(data["type"]),
                        amount=data["amount"],
                        source_account=data["source_account"],
                        target_account=data["target_account"],
                        status=TransactionStatus(data["status"]),
                        created_at=data.get("created_at"),
                        updated_at=data.get("updated_at"),
                        version=data.get("version", 1),
                        metadata=data.get("metadata", {})
                    )
                
                def update_status(self, status: TransactionStatus) -> None:
                    self.status = status
                    self.updated_at = datetime.now()
                    self.version += 1
            ```
            """
        elif "ChunkManager" in prompt:
            return """
            ```python
            from typing import List, Dict, Any, Callable, Awaitable
            import asyncio
            import logging
            
            from ..models.transaction import Transaction
            
            logger = logging.getLogger(__name__)
            
            class ChunkManager:
                def __init__(self, chunk_size: int = 100):
                    self.chunk_size = chunk_size
                    logger.info(f"ChunkManager initialisiert mit Chunk-Größe {chunk_size}")
                
                def split_into_chunks(self, transactions: List[Transaction]) -> List[List[Transaction]]:
                    # Teilt eine Liste von Transaktionen in Chunks auf.
                    chunks = [transactions[i:i + self.chunk_size] for i in range(0, len(transactions), self.chunk_size)]
                    logger.info(f"{len(transactions)} Transaktionen in {len(chunks)} Chunks aufgeteilt")
                    return chunks
                
                async def process_chunks(self, 
                                         chunks: List[List[Transaction]], 
                                         processor_func: Callable[[List[Transaction]], Awaitable[Dict[str, Any]]],
                                         save_point_interval: int = 1) -> List[Dict[str, Any]]:
                    # Verarbeitet Chunks von Transaktionen mit Savepoints.
                    results = []
                    savepoint_counter = 0
                    
                    for i, chunk in enumerate(chunks):
                        try:
                            # Savepoint erstellen, falls erforderlich
                            if savepoint_counter == 0:
                                logger.info(f"Savepoint erstellt vor Chunk {i+1}/{len(chunks)}")
                                # Hier würde in der realen Implementierung ein Savepoint erstellt werden
                            
                            # Chunk verarbeiten
                            logger.info(f"Verarbeite Chunk {i+1}/{len(chunks)} mit {len(chunk)} Transaktionen")
                            chunk_result = await processor_func(chunk)
                            results.append(chunk_result)
                            
                            # Savepoint-Zähler aktualisieren
                            savepoint_counter = (savepoint_counter + 1) % save_point_interval
                            
                        except Exception as e:
                            logger.error(f"Fehler bei der Verarbeitung von Chunk {i+1}: {str(e)}")
                            # Hier würde in der realen Implementierung ein Rollback zum letzten Savepoint erfolgen
                            raise
                    
                    return results
            ```
            """
        elif "AsyncAuditLogger" in prompt:
            return """
            ```python
            import asyncio
            import logging
            from typing import Dict, Any, List, Optional
            from datetime import datetime
            
            from ..models.transaction import Transaction
            
            logger = logging.getLogger(__name__)
            
            class AsyncAuditLogger:
                def __init__(self, max_queue_size: int = 1000, batch_size: int = 50):
                    self.queue = asyncio.Queue(maxsize=max_queue_size)
                    self.batch_size = batch_size
                    self.running = False
                    self.worker_task = None
                    self.logs = []
                    logger.info(f"AsyncAuditLogger initialisiert mit max_queue_size={max_queue_size}, batch_size={batch_size}")
                
                async def start(self) -> None:
                    # Startet den asynchronen Logger.
                    if self.running:
                        logger.warning("AsyncAuditLogger läuft bereits")
                        return
                    
                    self.running = True
                    self.worker_task = asyncio.create_task(self._worker())
                    logger.info("AsyncAuditLogger gestartet")
                
                async def stop(self) -> None:
                    # Stoppt den asynchronen Logger.
                    if not self.running:
                        logger.warning("AsyncAuditLogger läuft nicht")
                        return
                    
                    self.running = False
                    if self.worker_task:
                        await self.worker_task
                    logger.info("AsyncAuditLogger gestoppt")
                
                async def log(self, transaction: Transaction, action: str, details: Optional[Dict[str, Any]] = None) -> None:
                    # Protokolliert eine Transaktion.
                    log_entry = {
                        "timestamp": datetime.now(),
                        "transaction_id": transaction.id,
                        "action": action,
                        "transaction_type": transaction.type.value,
                        "transaction_status": transaction.status.value,
                        "details": details or {}
                    }
                    
                    try:
                        await self.queue.put(log_entry)
                    except asyncio.QueueFull:
                        logger.error("Audit-Log-Queue ist voll, Eintrag wird verworfen")
                
                async def _worker(self) -> None:
                    # Worker-Funktion für die asynchrone Verarbeitung der Log-Einträge.
                    batch = []
                    
                    while self.running or not self.queue.empty():
                        try:
                            # Warte auf einen Log-Eintrag mit Timeout
                            try:
                                log_entry = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                                batch.append(log_entry)
                                self.queue.task_done()
                            except asyncio.TimeoutError:
                                # Timeout, aber möglicherweise noch Einträge im Batch
                                pass
                            
                            # Batch verarbeiten, wenn voll oder wenn nicht mehr laufend und keine weiteren Einträge
                            if len(batch) >= self.batch_size or (not self.running and batch and self.queue.empty()):
                                await self._process_batch(batch)
                                batch = []
                                
                        except Exception as e:
                            logger.error(f"Fehler im Audit-Log-Worker: {str(e)}")
                            # Batch trotz Fehler verarbeiten
                            if batch:
                                await self._process_batch(batch)
                                batch = []
                
                async def _process_batch(self, batch: List[Dict[str, Any]]) -> None:
                    # Verarbeitet einen Batch von Log-Einträgen.
                    if not batch:
                        return
                    
                    try:
                        # Hier würden die Log-Einträge in der realen Implementierung in eine Datenbank geschrieben
                        # Für diese Demo werden sie einfach im Speicher gehalten
                        self.logs.extend(batch)
                        logger.info(f"Batch mit {len(batch)} Log-Einträgen verarbeitet")
                    except Exception as e:
                        logger.error(f"Fehler bei der Verarbeitung des Log-Batches: {str(e)}")
                
                async def get_logs(self) -> List[Dict[str, Any]]:
                    # Gibt alle protokollierten Einträge zurück.
                    return self.logs
            ```
            """
        else:
            return "Simulierte RAG-Antwort für: " + prompt[:30] + "..."

async def run_create_demo():
    """Führt die Demo für den CREATE-Modus aus."""
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
        print("CREATE-MODE DEMO")
        print("="*80)
        print("Diese Demo zeigt die Generierung von Code-Artefakten basierend auf dem Lösungsdesign.")
        print("="*80)
        
        # PLAN-Ergebnis simulieren
        plan_result_id = ObjectId()
        plan_result = {
            "_id": plan_result_id,
            "project_id": project_id,
            "project_plan": {
                "name": "Optimierung der Transaktionsverarbeitung",
                "description": "Implementierung eines skalierbaren Systems zur Verarbeitung hoher Transaktionsvolumen mit Fokus auf Effizienz und Datenintegrität.",
                "milestones": [
                    {
                        "name": "Anforderungsanalyse und Systemdesign",
                        "description": "Detaillierte Analyse der Anforderungen und Erstellung eines Systemdesigns",
                        "effort_days": 5,
                        "start_date": "01.07.2025",
                        "end_date": "07.07.2025"
                    },
                    {
                        "name": "Implementierung des Chunk-basierten Verarbeitungsmodells",
                        "description": "Entwicklung des Kernmoduls für die Chunk-basierte Transaktionsverarbeitung",
                        "effort_days": 10,
                        "start_date": "08.07.2025",
                        "end_date": "21.07.2025"
                    }
                ]
            },
            "solution_design": {
                "overview": "Das System verwendet einen Chunk-basierten Ansatz für die Transaktionsverarbeitung mit Savepoints zur Fehlerbehandlung.",
                "decisions": [
                    {
                        "name": "Chunked Processing mit Savepoints",
                        "description": "Verarbeitung von Transaktionen in Chunks mit Savepoints",
                        "rationale": "Bietet die beste Balance zwischen Performance und Fehlertoleranz."
                    },
                    {
                        "name": "Asynchrone Audit-Logging",
                        "description": "Trennung des Audit-Loggings vom kritischen Pfad",
                        "rationale": "Verbessert die Performance ohne Kompromisse bei Compliance."
                    },
                    {
                        "name": "Optimistisches Locking für Parallelzugriffe",
                        "description": "Verwendung von optimistischem Locking für Transaktionen",
                        "rationale": "Ermöglicht höheren Durchsatz bei gleichzeitigen Zugriffen."
                    }
                ]
            },
            "tasks": [
                {
                    "name": "Implementierung der Basis-Transaktionsklassen",
                    "description": "Entwicklung der grundlegenden Klassen für die Transaktionsverarbeitung",
                    "effort_hours": 32,
                    "priority": 2
                },
                {
                    "name": "Implementierung des Chunk-Managers",
                    "description": "Entwicklung des Chunk-Managers zur Verwaltung der Transaktions-Chunks",
                    "effort_hours": 40,
                    "priority": 2
                },
                {
                    "name": "Entwicklung des asynchronen Audit-Logging",
                    "description": "Implementierung des Audit-Logging-Systems mit asynchroner Verarbeitung",
                    "effort_hours": 16,
                    "priority": 3
                }
            ],
            "timestamp": datetime.now(),
            "status": "completed"
        }
        
        # PLAN-Ergebnis in der Datenbank speichern
        await mongodb.insert_one("plan_results", plan_result)
        
        print(f"\nPLAN-Ergebnis simuliert mit ID: {plan_result_id}")
        print(f"Projektplan: {plan_result['project_plan']['name']}")
        print(f"Lösungsdesign: {plan_result['solution_design']['overview']}")
        print(f"Anzahl der Aufgaben: {len(plan_result['tasks'])}")
        
        # CREATE-Mode ausführen
        create_result = await workflow.run_create_mode(str(plan_result_id))
        
        print(f"\nCREATE-Mode abgeschlossen mit ID: {create_result.get('id')}")
        
        # Code-Artefakte ausgeben
        artifacts = create_result.get('artifacts', [])
        print(f"\nAnzahl der Code-Artefakte: {len(artifacts)}")
        
        for i, artifact in enumerate(artifacts, 1):
            print(f"\nArtefakt {i}: {artifact.get('name')}")
            print(f"Typ: {artifact.get('type')}")
            print(f"Pfad: {artifact.get('path')}")
            print(f"Beschreibung: {artifact.get('description')}")
            print("\nCode-Ausschnitt:")
            code = artifact.get('content', '')
            print(code[:200] + "..." if len(code) > 200 else code)
        
        # Verbindung schließen
        workflow.close()
        
        print("\n" + "="*80)
        print("CREATE-Mode Demo erfolgreich abgeschlossen")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Fehler bei der CREATE-Mode Demo: {str(e)}")
        raise

async def main():
    """Hauptfunktion."""
    await run_create_demo()

if __name__ == "__main__":
    asyncio.run(main())
