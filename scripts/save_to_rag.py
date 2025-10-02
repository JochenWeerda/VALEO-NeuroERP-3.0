"""
Script zum Speichern von Dokumenten im RAG-System.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_paths() -> Path:
    """Erstellt die notwendigen Verzeichnisse."""
    try:
        # Projektroot-Verzeichnis finden
        project_root = Path(__file__).parent.parent
        
        # FAISS DB Verzeichnis
        db_path = project_root / "data" / "faiss_db"
        db_path.mkdir(parents=True, exist_ok=True)
        
        return db_path
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Verzeichnisse: {str(e)}")
        raise

def process_document(filepath: str, db_path: Optional[Path] = None) -> bool:
    """
    Verarbeitet ein Dokument und speichert es im RAG-System.
    
    Args:
        filepath: Pfad zum Dokument
        db_path: Optional, Pfad zur FAISS-Datenbank
        
    Returns:
        bool: True wenn erfolgreich, False sonst
    """
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            logger.error(f"Datei nicht gefunden: {filepath}")
            return False
            
        if db_path is None:
            db_path = setup_paths()
        
        logger.info(f"Verarbeite Dokument: {filepath}")
        
        # Dokument laden
        loader = TextLoader(str(filepath), encoding='utf-8')
        documents = loader.load()
        
        # Text in Chunks aufteilen
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Dokument in {len(chunks)} Chunks aufgeteilt")
        
        # Embeddings erstellen
        logger.info("Erstelle Embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Vectorstore erstellen oder laden
        index_path = db_path / "index.faiss"
        docstore_path = db_path / "docstore.json"
        
        if index_path.exists() and docstore_path.exists():
            try:
                logger.info("Lade existierenden Vectorstore...")
                vectorstore = FAISS.load_local(str(db_path), embeddings, allow_dangerous_deserialization=True)
                vectorstore.add_documents(chunks)
                logger.info("Chunks zum existierenden Vectorstore hinzugefügt")
            except Exception as e:
                logger.warning(f"Konnte existierenden Vectorstore nicht laden: {str(e)}")
                logger.info("Erstelle neuen Vectorstore...")
                vectorstore = FAISS.from_documents(chunks, embeddings)
        else:
            logger.info("Erstelle neuen Vectorstore...")
            vectorstore = FAISS.from_documents(chunks, embeddings)
        
        # Vectorstore speichern
        vectorstore.save_local(str(db_path))
        logger.info(f"Vectorstore in {db_path} gespeichert")
        
        return True
        
    except Exception as e:
        logger.error(f"Fehler bei der Verarbeitung von {filepath}: {str(e)}")
        return False

def main(files: List[str]) -> None:
    """
    Hauptfunktion zum Verarbeiten mehrerer Dateien.
    
    Args:
        files: Liste der zu verarbeitenden Dateien
    """
    try:
        if not files:
            logger.error("Keine Dateien angegeben")
            print("Verwendung: python save_to_rag.py datei1 [datei2 ...]")
            sys.exit(1)
        
        db_path = setup_paths()
        logger.info(f"Starte Verarbeitung von {len(files)} Dateien...")
        
        success_count = 0
        for filepath in files:
            if process_document(filepath, db_path):
                success_count += 1
        
        logger.info(f"Verarbeitung abgeschlossen. {success_count} von {len(files)} Dateien erfolgreich verarbeitet.")
        
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[1:]) 