#!/usr/bin/env python
"""
Skript zum Laden der VALEO-NeuroERP Dokumentation in MongoDB.
"""

import os
from datetime import datetime
from typing import List, Dict, Any
import re
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings

# MongoDB Verbindung
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "valeo_neuroerp"
COLLECTION_NAME = "documentation"

def create_indices(collection) -> None:
    """Erstellt die notwendigen Indizes in der Collection."""
    try:
        # Textindex für Volltextsuche
        collection.create_index([
            ("content", "text"),
            ("sections.content", "text"),
            ("sections.title", "text"),
            ("metadata.title", "text")
        ])
        
        # Index für Zeitstempel
        collection.create_index("metadata.updated_at")
        
        print("Indizes erfolgreich erstellt.")
    except Exception as e:
        print(f"Fehler beim Erstellen der Indizes: {str(e)}")

def extract_sections(content: str) -> List[Dict[str, str]]:
    """Extrahiert Abschnitte aus dem Markdown-Inhalt mit Hierarchie-Tracking."""
    sections = []
    section_stack = []  # Stack für verschachtelte Abschnitte
    current_content = []
    lines = content.split("\n")
    
    for line in lines:
        # Erkenne Überschriften
        if line.startswith("#"):
            # Verarbeite gesammelten Inhalt für aktuellen Abschnitt
            if section_stack:
                section_stack[-1]["content"] = "\n".join(current_content).strip()
                current_content = []
            
            # Bestimme Level der neuen Überschrift
            level = len(re.match(r"^#+", line).group())
            title = line.lstrip("#").strip()
            
            # Erstelle neuen Abschnitt
            new_section = {
                "title": title,
                "content": "",
                "level": level,
                "parent": None
            }
            
            # Aktualisiere Hierarchie
            while section_stack and section_stack[-1]["level"] >= level:
                completed_section = section_stack.pop()
                if completed_section["content"].strip():  # Nur nicht-leere Abschnitte speichern
                    sections.append(completed_section)
            
            # Setze Parent-Referenz
            if section_stack:
                new_section["parent"] = section_stack[-1]["title"]
            
            section_stack.append(new_section)
        else:
            # Füge Zeile zum aktuellen Inhalt hinzu
            current_content.append(line)
    
    # Verarbeite verbleibenden Inhalt
    if section_stack:
        section_stack[-1]["content"] = "\n".join(current_content).strip()
    
    # Füge verbleibende Abschnitte hinzu
    while section_stack:
        completed_section = section_stack.pop()
        if completed_section["content"].strip():  # Nur nicht-leere Abschnitte speichern
            sections.append(completed_section)
    
    return sections

def process_document(file_path: str, embeddings: OpenAIEmbeddings) -> Dict[str, Any]:
    """Verarbeitet ein einzelnes Dokument."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extrahiere Metadaten
        title = os.path.splitext(os.path.basename(file_path))[0]
        sections = extract_sections(content)
        
        # Erstelle Embeddings für jeden Abschnitt
        for section in sections:
            section_text = f"{section['title']}\n{section['content']}"
            section["embedding"] = embeddings.embed_query(section_text)
        
        # Erstelle Dokument
        document = {
            "file_path": file_path,
            "content": content,
            "sections": sections,
            "metadata": {
                "title": title,
                "updated_at": datetime.now(),
                "sections": [section["title"] for section in sections]
            }
        }
        
        return document
    except Exception as e:
        print(f"Fehler beim Verarbeiten von {file_path}: {str(e)}")
        return None

def find_markdown_files(root_dir: str) -> List[str]:
    """Findet alle Markdown-Dateien im angegebenen Verzeichnis und Unterverzeichnissen."""
    markdown_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(('.md', '.MD')):
                full_path = os.path.join(dirpath, filename)
                markdown_files.append(full_path)
    return markdown_files

def main():
    # Initialisiere MongoDB und Embeddings
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    embeddings = OpenAIEmbeddings()
    
    # Erstelle Indizes
    create_indices(collection)
    
    # Finde alle Markdown-Dateien
    doc_paths = find_markdown_files(".")
    
    # Filtere unerwünschte Dateien aus
    excluded_dirs = {"venv", "node_modules", "__pycache__"}
    doc_paths = [
        path for path in doc_paths 
        if not any(excluded in path for excluded in excluded_dirs)
    ]
    
    print(f"Gefunden: {len(doc_paths)} Markdown-Dateien")
    
    # Lösche bestehende Dokumente
    collection.delete_many({})
    print("Bestehende Dokumente gelöscht.")
    
    # Verarbeite jedes Dokument
    for file_path in doc_paths:
        print(f"Verarbeite {file_path}...")
        document = process_document(file_path, embeddings)
        
        if document:
            result = collection.insert_one(document)
            print(f"Dokument {file_path} erfolgreich gespeichert (ID: {result.inserted_id})")
    
    print("Dokumentenverarbeitung abgeschlossen.")

if __name__ == "__main__":
    main()