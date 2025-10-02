***REMOVED***!/usr/bin/env python3
"""
Speichert das aktuelle Handover in MongoDB.
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient

***REMOVED*** MongoDB-Verbindung herstellen
client = MongoClient("mongodb://localhost:27017/")
db = client.valeo_neuroerp
collection = db.handovers

***REMOVED*** Handover-Daten
handover_data = {
    "source_mode": "VAN",
    "target_mode": "PLAN",
    "timestamp": datetime.now(),
    "title": "Multi-Agenten-System Implementation",
    "content": open("memory-bank/handover/current-handover.md").read(),
    "status": "active"
}

***REMOVED*** Altes aktives Handover deaktivieren
collection.update_many(
    {"status": "active"},
    {"$set": {"status": "archived"}}
)

***REMOVED*** Neues Handover speichern
result = collection.insert_one(handover_data)

print(f"Handover in MongoDB gespeichert mit ID: {result.inserted_id}") 