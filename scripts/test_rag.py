"""
Test-Skript für die RAG-Integration der VALEO-NeuroERP Dokumentation.
"""

import unittest
from load_docs_to_mongodb import DocumentProcessor
from query_documentation import DocumentationRetriever
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Any
from pymongo import MongoClient
import numpy as np
import time

class TestRAGIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Wird einmal vor allen Tests ausgeführt."""
        # Erstelle temporäres Verzeichnis
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_doc_path = os.path.join(cls.temp_dir, "test_doc.md")
        
        # Erstelle Testdokument
        with open(cls.test_doc_path, "w", encoding="utf-8") as f:
            f.write("""# Test Dokument

## Compliance-System

Das VALEO-NeuroERP Compliance-System ist eine integrierte Lösung für die Qualitätssicherung.
Es umfasst Validatoren für QS, GMP und EU-Regularien.

### Komponenten

- Backend mit Pydantic-Modellen
- Monitoring-System
- API-Endpunkte

## Dokumentation

Die technische Dokumentation enthält:
- Installationsanleitung
- Wartungshinweise
- Best Practices""")
        
        # Initialisiere Processor und Retriever
        cls.processor = DocumentProcessor()
        cls.retriever = DocumentationRetriever()
        
        # Lösche bestehende Dokumente
        cls.processor.collection.delete_many({})
        
        # Verarbeite Testdokument
        cls.processor.store_document(cls.test_doc_path)

    def setUp(self):
        """Wird vor jedem Test ausgeführt."""
        # Warte kurz, damit die Indizes erstellt werden können
        time.sleep(1)

    def test_document_storage(self):
        """Testet die Dokumentspeicherung."""
        doc = self.retriever.db.rag_documents.find_one({"metadata.title": os.path.basename(self.test_doc_path)})
        self.assertIsNotNone(doc, "Dokument wurde nicht gespeichert")
        self.assertIn("content", doc, "Kein Inhalt im Dokument")
        self.assertIn("metadata", doc, "Keine Metadaten im Dokument")

    def test_text_search(self):
        """Testet die Textsuche."""
        results = self.retriever.text_search("Compliance")
        self.assertTrue(len(results) > 0, "Keine Suchergebnisse gefunden")
        self.assertIn("Compliance", results[0]["content"], "Suchbegriff nicht im Ergebnis gefunden")

    def test_semantic_search(self):
        """Testet die semantische Suche."""
        results = self.retriever.semantic_search("Qualitätssicherung")
        self.assertTrue(len(results) > 0, "Keine semantischen Suchergebnisse gefunden")
        self.assertIsNotNone(results[0].get("similarity"), "Ähnlichkeitswert fehlt")
        self.assertGreater(results[0]["similarity"], 0, "Ähnlichkeitswert muss positiv sein")

    def test_section_search(self):
        """Testet die Abschnittssuche."""
        results = self.retriever.search_sections("Komponenten")
        self.assertTrue(len(results) > 0, "Keine Abschnitte gefunden")
        self.assertTrue(
            "Komponenten" in results[0]["section"]["title"] or
            "Komponenten" in results[0]["section"]["content"],
            "Suchbegriff weder im Titel noch im Content gefunden"
        )

    def test_section_retrieval(self):
        """Testet das Abrufen von Dokumentabschnitten."""
        doc = self.retriever.db.rag_documents.find_one({"metadata.title": os.path.basename(self.test_doc_path)})
        sections = doc.get("sections", [])
        
        # Prüfe die Anzahl der Hauptabschnitte (nur # und ##)
        main_sections = [s for s in sections if s["level"] <= 2]
        self.assertEqual(len(main_sections), 3, "Falsche Anzahl von Hauptabschnitten")
        
        # Prüfe die Reihenfolge und Titel der Hauptabschnitte
        self.assertEqual(main_sections[0]["title"], "Test Dokument", "Falscher erster Abschnittstitel")
        self.assertEqual(main_sections[1]["title"], "Compliance-System", "Falscher zweiter Abschnittstitel")
        self.assertEqual(main_sections[2]["title"], "Dokumentation", "Falscher dritter Abschnittstitel")
        
        # Prüfe den Inhalt der Abschnitte
        self.assertIn("Komponenten", main_sections[1]["content"], "Unterabschnitt nicht im Hauptabschnitt enthalten")
        self.assertIn("Installationsanleitung", main_sections[2]["content"], "Aufzählungspunkte nicht im Abschnitt enthalten")

    def test_recent_updates(self):
        """Testet das Abrufen kürzlich aktualisierter Dokumente."""
        updates = self.retriever.get_recent_updates(limit=5)
        self.assertTrue(len(updates) > 0, "Keine aktualisierten Dokumente gefunden")
        self.assertIsNotNone(updates[0].get("metadata", {}).get("updated_at"), "Zeitstempel fehlt")

    def test_document_structure(self):
        """Testet die Dokumentenstruktur."""
        doc = self.retriever.db.rag_documents.find_one({"metadata.title": os.path.basename(self.test_doc_path)})
        self.assertIsNotNone(doc, "Testdokument nicht gefunden")
        self.assertIn("sections", doc, "Keine Abschnitte im Dokument")
        self.assertIn("embedding", doc, "Kein Embedding im Dokument")
        self.assertIn("section_titles", doc["metadata"], "Keine Abschnittstitel in Metadaten")

    @classmethod
    def tearDownClass(cls):
        """Wird einmal nach allen Tests ausgeführt."""
        # Lösche Testdokument und temporäres Verzeichnis
        os.remove(cls.test_doc_path)
        os.rmdir(cls.temp_dir)
        
        # Lösche Testdaten aus der Datenbank
        cls.processor.collection.delete_many({})

if __name__ == "__main__":
    unittest.main() 