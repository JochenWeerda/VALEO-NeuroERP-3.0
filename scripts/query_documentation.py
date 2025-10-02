"""
Skript zum Abfragen der VALEO-NeuroERP Dokumentation aus MongoDB mittels RAG.
"""

import os
from typing import List, Dict, Any
from pymongo import MongoClient, DESCENDING
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain_openai import OpenAIEmbeddings

# MongoDB Verbindung
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "valeo_neuroerp"
COLLECTION_NAME = "documentation"

class DocumentationRetriever:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]
        self.embeddings = OpenAIEmbeddings()

    def search_similar_chunks(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Sucht ähnliche Dokumentchunks basierend auf einer Anfrage."""
        # Query-Embedding erstellen
        query_embedding = self.embeddings.embed_query(query)
        
        # Ähnliche Chunks finden
        similar_chunks = []
        for doc in self.collection.find():
            for chunk in doc.get("chunks", []):
                if "embedding" in chunk:
                    similarity = cosine_similarity(
                        [query_embedding],
                        [chunk["embedding"]]
                    )[0][0]
                    
                    similar_chunks.append({
                        "text": chunk["text"],
                        "similarity": similarity,
                        "doc_title": doc.get("metadata", {}).get("title", ""),
                        "file_path": doc.get("file_path", "")
                    })
        
        # Nach Ähnlichkeit sortieren und Top-N zurückgeben
        similar_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_chunks[:n_results]

    def text_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Führt eine Textsuche in den Dokumenten durch."""
        try:
            # Suche in allen Feldern
            results = list(self.collection.find(
                {
                    "$or": [
                        {"content": {"$regex": query, "$options": "i"}},
                        {"sections.content": {"$regex": query, "$options": "i"}},
                        {"sections.title": {"$regex": query, "$options": "i"}},
                        {"metadata.title": {"$regex": query, "$options": "i"}},
                        {"file_path": {"$regex": query, "$options": "i"}}
                    ]
                }
            ).limit(limit))
            
            # Füge Relevanz-Score hinzu
            for doc in results:
                score = 0
                # Score für Titel
                if "metadata" in doc and "title" in doc["metadata"]:
                    title = doc["metadata"]["title"]
                    score += title.lower().count(query.lower()) * 2
                
                # Score für Inhalt
                if "content" in doc:
                    content = doc["content"]
                    score += content.lower().count(query.lower())
                
                # Score für Abschnitte
                if "sections" in doc:
                    for section in doc["sections"]:
                        if "title" in section:
                            score += section["title"].lower().count(query.lower()) * 1.5
                        if "content" in section:
                            score += section["content"].lower().count(query.lower())
                
                doc["score"] = score
            
            # Sortiere nach Score
            results.sort(key=lambda x: x.get("score", 0), reverse=True)
            return results
            
        except Exception as e:
            print(f"Fehler bei der Textsuche: {str(e)}")
            return []

    def semantic_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Führt eine semantische Suche mit Embeddings durch und berücksichtigt die Dokumentstruktur."""
        try:
            query_embedding = self.embeddings.embed_query(query)
            
            # Hole alle Dokumente
            documents = list(self.collection.find())
            
            # Berechne Ähnlichkeiten mit Kontext
            similarities = []
            for doc in documents:
                # Erstelle Hierarchie-Map für schnellen Zugriff
                section_map = {
                    section.get("title", ""): {
                        "content": section.get("content", ""),
                        "embedding": section.get("embedding", []),
                        "parent": section.get("parent", None)
                    }
                    for section in doc.get("sections", [])
                }
                
                # Berechne Ähnlichkeit für jeden Abschnitt mit Kontext
                for section in doc.get("sections", []):
                    if "embedding" in section:
                        # Basis-Ähnlichkeit
                        base_similarity = cosine_similarity(
                            [query_embedding],
                            [section["embedding"]]
                        )[0][0]
                        
                        # Kontext-Ähnlichkeit (Parent-Abschnitte)
                        context_similarity = 0.0
                        parent_title = section.get("parent")
                        depth = 0
                        while parent_title and depth < 3:  # Maximal 3 Ebenen nach oben
                            if parent_title in section_map:
                                parent_section = section_map[parent_title]
                                if "embedding" in parent_section:
                                    parent_sim = cosine_similarity(
                                        [query_embedding],
                                        [parent_section["embedding"]]
                                    )[0][0]
                                    # Gewichtung nimmt mit Tiefe ab
                                    context_similarity += parent_sim * (0.5 ** (depth + 1))
                                parent_title = parent_section.get("parent")
                            depth += 1
                        
                        # Kombinierte Ähnlichkeit (70% Basis + 30% Kontext)
                        final_similarity = 0.7 * base_similarity + 0.3 * context_similarity
                        
                        result = {
                            "content": section.get("content", ""),
                            "title": section.get("title", ""),
                            "source": doc.get("source", ""),
                            "file_path": doc.get("file_path", ""),
                            "metadata": doc.get("metadata", {}),
                            "similarity": float(final_similarity),
                            "context_path": []
                        }
                        
                        # Füge Pfad zum Abschnitt hinzu
                        current_title = section.get("title")
                        while current_title:
                            result["context_path"].insert(0, current_title)
                            current_title = section_map.get(current_title, {}).get("parent")
                        
                        similarities.append((result, final_similarity))
            
            # Sortiere nach Ähnlichkeit
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Gib die Top-N Ergebnisse zurück
            return [doc for doc, _ in similarities[:limit]]
            
        except Exception as e:
            print(f"Fehler bei der semantischen Suche: {str(e)}")
            return []

    def search_sections(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Sucht in einzelnen Abschnitten der Dokumente."""
        try:
            # Hole alle Dokumente
            documents = list(self.collection.find())
            results = []
            
            for doc in documents:
                # Durchsuche jeden Abschnitt
                for section in doc.get("sections", []):
                    if query.lower() in section.get("title", "").lower() or query.lower() in section.get("content", "").lower():
                        result = {
                            "metadata": doc.get("metadata", {}),
                            "source": doc.get("source", ""),
                            "file_path": doc.get("file_path", ""),
                            "section": section,
                            "score": (
                                section.get("title", "").lower().count(query.lower()) * 2 +  # Titel zählt doppelt
                                section.get("content", "").lower().count(query.lower())
                            )
                        }
                        results.append(result)
            
            # Sortiere nach Score
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            print(f"Fehler bei der Abschnittssuche: {str(e)}")
            return []

    def get_document_sections(self, doc_title: str) -> List[str]:
        """Gibt alle Abschnitte eines Dokuments zurück."""
        doc = self.collection.find_one({"metadata.title": doc_title})
        if doc:
            return doc.get("metadata", {}).get("sections", [])
        return []

    def get_recent_updates(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Ruft die zuletzt aktualisierten Dokumente ab."""
        try:
            return list(self.collection.find().sort("metadata.updated_at", DESCENDING).limit(limit))
        except Exception as e:
            print(f"Fehler beim Abrufen der Updates: {str(e)}")
            return []

def main():
    retriever = DocumentationRetriever()
    
    # Beispielsuchen
    print("\nTextsuche nach 'Compliance':")
    results = retriever.text_search("Compliance")
    for doc in results:
        print(f"- {doc.get('metadata', {}).get('title', '')}: {doc.get('score', 0)}")
    
    print("\nSemantische Suche nach 'Qualitätssicherung':")
    results = retriever.semantic_search("Qualitätssicherung")
    for doc in results:
        print(f"- {doc.get('metadata', {}).get('title', '')}: {doc.get('similarity', 0):.2f}")
    
    print("\nAktualisierte Dokumente:")
    updates = retriever.get_recent_updates()
    for doc in updates:
        print(f"- {doc.get('metadata', {}).get('title', '')}")

if __name__ == "__main__":
    main() 