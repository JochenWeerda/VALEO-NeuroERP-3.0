#!/usr/bin/env python3
"""
Einfaches DB-Initialisierungs-Skript
Erstellt nur die Tabellen ohne FastAPI-Context
"""

import sys
from pathlib import Path

# Füge Projekt-Root zu sys.path hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def init_database():
    print("=" * 80)
    print("PostgreSQL Datenbank-Initialisierung")
    print("=" * 80)
    
    # Schritt 1: DB-Verbindung testen
    print("\n1. Teste PostgreSQL-Verbindung...")
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print(f"   ✅ Verbindung erfolgreich: {engine.url}")
    except Exception as e:
        print(f"   ❌ Verbindungsfehler: {e}")
        return False
    
    # Schritt 2: Schemas prüfen
    print("\n2. Prüfe Schemas...")
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'domain_%'")
            schemas = [row[0] for row in result]
            print(f"   ✅ Gefundene Schemas: {schemas}")
            
            if len(schemas) < 4:
                print(f"   ⚠️  Fehlende Schemas werden erstellt...")
                conn.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
                conn.execute("CREATE SCHEMA IF NOT EXISTS domain_crm")
                conn.execute("CREATE SCHEMA IF NOT EXISTS domain_inventory")
                conn.execute("CREATE SCHEMA IF NOT EXISTS domain_erp")
                conn.commit()
    except Exception as e:
        print(f"   ❌ Schema-Fehler: {e}")
        return False
    
    # Schritt 3: Tabellen erstellen
    print("\n3. Erstelle Tabellen...")
    try:
        from app.core.database import Base
        Base.metadata.create_all(bind=engine)
        print(f"   ✅ Tabellen erstellt")
        
        # Zähle erstellte Tabellen
        with engine.connect() as conn:
            result = conn.execute("""
                SELECT schemaname, tablename 
                FROM pg_tables 
                WHERE schemaname LIKE 'domain_%'
                ORDER BY schemaname, tablename
            """)
            tables = list(result)
            print(f"   ✅ {len(tables)} Tabellen in 4 Schemas:")
            for schema, table in tables:
                print(f"      - {schema}.{table}")
    except Exception as e:
        print(f"   ❌ Tabellen-Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 80)
    print("✅ Datenbank-Initialisierung ERFOLGREICH")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)

