from pymongo import MongoClient
import datetime

def store_structure():
    # MongoDB Verbindung
    client = MongoClient('mongodb://localhost:27017/')
    db = client['valeo_neurodb']
    collection = db['system_structure']
    
    # Struktur-Dokument
    structure = {
        "version": "1.04",
        "timestamp": datetime.datetime.now(),
        "type": "system_structure",
        "content": {
            "systemarchitektur": {
                "backend": {
                    "framework": "Node.js + Express",
                    "features": [
                        "Microservices-Architektur",
                        "Redis Caching",
                        "MongoDB",
                        "PostgreSQL",
                        "Load Balancing"
                    ]
                },
                "frontend": {
                    "framework": "React",
                    "features": [
                        "Lazy Loading",
                        "Client-side Caching",
                        "PWA",
                        "Offline-First",
                        "Modulare Komponenten"
                    ]
                },
                "ki_integration": {
                    "komponenten": [
                        "Lokales LLM",
                        "GPT-4 API",
                        "Caching",
                        "Asynchrone Verarbeitung",
                        "Batch-Processing"
                    ]
                }
            },
            "kernmodule": {
                "belegerfassung": [
                    "Schnelle Eingabemasken",
                    "Lokale Zwischenspeicherung",
                    "Automatische Nummerierung",
                    "Vorlagen-System",
                    "Offline-Fähigkeit"
                ],
                "warenwirtschaft": [
                    "Echtzeit-Bestandsführung",
                    "Optimierte Datenbankabfragen",
                    "Caching-Layer",
                    "Batch-Updates",
                    "Indexierte Suche"
                ],
                "finanzbuchhaltung": [
                    "Performante Kontenrahmen-Struktur",
                    "Optimierte Buchungsengine",
                    "Periodische Berechnungen",
                    "Inkrementelle Updates",
                    "Automatische Abstimmung"
                ],
                "crm": [
                    "Kontakt-Basisdaten im Cache",
                    "Lazy Loading",
                    "Optimierte Suche",
                    "Priorisierte Updates",
                    "Effiziente Historie"
                ]
            },
            "technische_anforderungen": {
                "server": {
                    "cpu": "4 Cores",
                    "ram": "16 GB",
                    "storage": "256 GB SSD",
                    "network": "1 Gbit/s"
                },
                "client": {
                    "browser": "Modern",
                    "ram": "4 GB",
                    "internet": "Stabil",
                    "requirements": "HTML5"
                }
            },
            "performance_ziele": {
                "antwortzeiten": {
                    "belegerfassung": "< 1s",
                    "suche": "< 2s",
                    "reports": "< 5s",
                    "ki_analysen": "< 3s",
                    "stammdaten": "< 1s"
                },
                "nutzer": {
                    "gleichzeitig": 20,
                    "skalierbar": 50,
                    "load_balancing": 15
                }
            },
            "implementierung": {
                "phase1": {
                    "dauer": "4 Wochen",
                    "fokus": ["Basis-Datenbankstruktur", "Core-Services", "Authentifizierung", "UI"]
                },
                "phase2": {
                    "dauer": "4 Wochen",
                    "fokus": ["Belegerfassung", "Warenwirtschaft", "Finanzbuchhaltung", "CRM"]
                },
                "phase3": {
                    "dauer": "2 Wochen",
                    "fokus": ["Lokales LLM", "Automatisierung", "Assistenz", "Vorschläge"]
                },
                "phase4": {
                    "dauer": "2 Wochen",
                    "fokus": ["Performance", "Caching", "Tests", "Dokumentation"]
                }
            }
        }
    }
    
    # Speichern in MongoDB
    collection.insert_one(structure)
    
    print("Struktur erfolgreich in MongoDB gespeichert")

if __name__ == "__main__":
    store_structure() 