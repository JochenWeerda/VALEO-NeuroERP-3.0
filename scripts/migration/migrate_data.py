"""
Skript zur Migration der Daten von VALEO-NeuroERP 1.0 nach 2.0
"""

import os
import sys
import json
import shutil
import logging
from typing import Dict, Any, List
from datetime import datetime
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import yaml

# Logging einrichten
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'migration_{datetime.now():%Y%m%d_%H%M%S}.log')
    ]
)
logger = logging.getLogger(__name__)

class DataMigrator:
    """Hauptklasse für die Datenmigration"""
    
    def __init__(self, config_path: str = "config/migration.yaml"):
        self.config = self._load_config(config_path)
        self.old_mongo = AsyncIOMotorClient(self.config["old_mongodb_uri"])
        self.new_mongo = AsyncIOMotorClient(self.config["new_mongodb_uri"])
        
        # Verzeichnisse
        self.old_base = self.config["old_base_dir"]
        self.new_base = self.config["new_base_dir"]
        
        # Status
        self.migration_status = {
            "started_at": datetime.now().isoformat(),
            "steps": [],
            "errors": []
        }
    
    def _load_config(self, path: str) -> Dict[str, Any]:
        """Lädt die Migrations-Konfiguration"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Konfiguration: {e}")
            sys.exit(1)
    
    async def migrate_mongodb(self):
        """Migriert MongoDB-Daten"""
        logger.info("Starte MongoDB-Migration")
        
        try:
            for collection in self.config["mongodb_collections"]:
                logger.info(f"Migriere Collection: {collection}")
                
                # Daten aus alter DB lesen
                old_data = await self.old_mongo[self.config["old_db_name"]][collection].find().to_list(None)
                
                if old_data:
                    # Daten in neue DB schreiben
                    await self.new_mongo[self.config["new_db_name"]][collection].insert_many(old_data)
                
                self.migration_status["steps"].append({
                    "type": "mongodb",
                    "collection": collection,
                    "count": len(old_data),
                    "timestamp": datetime.now().isoformat()
                })
        
        except Exception as e:
            error_msg = f"Fehler bei MongoDB-Migration: {str(e)}"
            logger.error(error_msg)
            self.migration_status["errors"].append({
                "type": "mongodb",
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            })
    
    async def migrate_rag_index(self):
        """Migriert RAG-Index"""
        logger.info("Starte RAG-Index-Migration")
        
        try:
            old_index_path = os.path.join(self.old_base, "data/rag_index")
            new_index_path = os.path.join(self.new_base, "data_integration/rag/index")
            
            if os.path.exists(old_index_path):
                # Verzeichnis erstellen
                os.makedirs(new_index_path, exist_ok=True)
                
                # Index kopieren
                for item in os.listdir(old_index_path):
                    src = os.path.join(old_index_path, item)
                    dst = os.path.join(new_index_path, item)
                    
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                    else:
                        shutil.copytree(src, dst)
                
                self.migration_status["steps"].append({
                    "type": "rag_index",
                    "path": new_index_path,
                    "timestamp": datetime.now().isoformat()
                })
        
        except Exception as e:
            error_msg = f"Fehler bei RAG-Index-Migration: {str(e)}"
            logger.error(error_msg)
            self.migration_status["errors"].append({
                "type": "rag_index",
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            })
    
    async def migrate_langgraph_data(self):
        """Migriert LangGraph-Daten"""
        logger.info("Starte LangGraph-Daten-Migration")
        
        try:
            old_graph_path = os.path.join(self.old_base, "data/langgraph")
            new_graph_path = os.path.join(self.new_base, "data_integration/langgraph/data")
            
            if os.path.exists(old_graph_path):
                # Verzeichnis erstellen
                os.makedirs(new_graph_path, exist_ok=True)
                
                # Daten kopieren und transformieren
                for filename in os.listdir(old_graph_path):
                    if filename.endswith('.json'):
                        with open(os.path.join(old_graph_path, filename), 'r') as f:
                            data = json.load(f)
                        
                        # Daten transformieren
                        transformed_data = self._transform_graph_data(data)
                        
                        # Speichern
                        with open(os.path.join(new_graph_path, filename), 'w') as f:
                            json.dump(transformed_data, f, indent=2)
                
                self.migration_status["steps"].append({
                    "type": "langgraph",
                    "path": new_graph_path,
                    "timestamp": datetime.now().isoformat()
                })
        
        except Exception as e:
            error_msg = f"Fehler bei LangGraph-Daten-Migration: {str(e)}"
            logger.error(error_msg)
            self.migration_status["errors"].append({
                "type": "langgraph",
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            })
    
    def _transform_graph_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transformiert Graph-Daten ins neue Format"""
        return {
            "nodes": [{
                "id": node["id"],
                "type": node.get("type", "default"),
                "properties": node.get("properties", {}),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "2.0"
                }
            } for node in data.get("nodes", [])],
            "edges": [{
                "source": edge["source"],
                "target": edge["target"],
                "type": edge.get("type", "default"),
                "properties": edge.get("properties", {})
            } for edge in data.get("edges", [])]
        }
    
    async def migrate_mcp_data(self):
        """Migriert MCP-Daten"""
        logger.info("Starte MCP-Daten-Migration")
        
        try:
            old_mcp_path = os.path.join(self.old_base, "mcp/data")
            new_mcp_path = os.path.join(self.new_base, "mcp/data")
            
            if os.path.exists(old_mcp_path):
                # Verzeichnis erstellen
                os.makedirs(new_mcp_path, exist_ok=True)
                
                # Daten kopieren und aktualisieren
                for root, _, files in os.walk(old_mcp_path):
                    for file in files:
                        if file.endswith(('.json', '.yaml')):
                            src_path = os.path.join(root, file)
                            rel_path = os.path.relpath(src_path, old_mcp_path)
                            dst_path = os.path.join(new_mcp_path, rel_path)
                            
                            # Verzeichnis erstellen
                            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                            
                            # Daten aktualisieren
                            if file.endswith('.json'):
                                with open(src_path, 'r') as f:
                                    data = json.load(f)
                                data = self._update_mcp_data(data)
                                with open(dst_path, 'w') as f:
                                    json.dump(data, f, indent=2)
                            else:
                                shutil.copy2(src_path, dst_path)
                
                self.migration_status["steps"].append({
                    "type": "mcp",
                    "path": new_mcp_path,
                    "timestamp": datetime.now().isoformat()
                })
        
        except Exception as e:
            error_msg = f"Fehler bei MCP-Daten-Migration: {str(e)}"
            logger.error(error_msg)
            self.migration_status["errors"].append({
                "type": "mcp",
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            })
    
    def _update_mcp_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aktualisiert MCP-Daten auf das neue Format"""
        if isinstance(data, dict):
            return {
                "version": "2.0",
                "updated_at": datetime.now().isoformat(),
                "config": data.get("config", {}),
                "pipeline": {
                    "steps": data.get("pipeline", {}).get("steps", []),
                    "metadata": {
                        "engine": "v2",
                        "compatibility": "2.x"
                    }
                },
                "data": data.get("data", {})
            }
        return data
    
    def save_migration_status(self):
        """Speichert den Migrations-Status"""
        self.migration_status["completed_at"] = datetime.now().isoformat()
        
        status_path = os.path.join(
            self.new_base,
            "logs",
            f"migration_status_{datetime.now():%Y%m%d_%H%M%S}.json"
        )
        
        os.makedirs(os.path.dirname(status_path), exist_ok=True)
        
        with open(status_path, 'w') as f:
            json.dump(self.migration_status, f, indent=2)
        
        logger.info(f"Migrations-Status gespeichert in: {status_path}")
    
    async def run_migration(self):
        """Führt die komplette Migration durch"""
        logger.info("Starte Datenmigration")
        
        try:
            # MongoDB
            await self.migrate_mongodb()
            
            # RAG Index
            await self.migrate_rag_index()
            
            # LangGraph
            await self.migrate_langgraph_data()
            
            # MCP
            await self.migrate_mcp_data()
            
            # Status speichern
            self.save_migration_status()
            
            logger.info("Migration erfolgreich abgeschlossen")
        
        except Exception as e:
            logger.error(f"Kritischer Fehler bei der Migration: {e}")
            raise

async def main():
    """Hauptfunktion"""
    try:
        migrator = DataMigrator()
        await migrator.run_migration()
    except Exception as e:
        logger.error(f"Migration fehlgeschlagen: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 