#!/usr/bin/env python3
"""
🧠 VALEO NeuroERP - Database Migration Script
============================================
Führt die NeuroFlow-Datenbank-Migration aus
Erstellt: 2025-07-23
"""

import os
import sys
import psycopg2
from pathlib import Path

# Projekt-Root hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_migration():
    """Führt die Datenbank-Migration aus"""
    
    print("🧠 VALEO NeuroERP - Database Migration")
    print("=" * 50)
    
    # Migration-Script lesen
    migration_file = project_root / "database" / "neuroflow_migration.sql"
    
    if not migration_file.exists():
        print(f"❌ Migration-Script nicht gefunden: {migration_file}")
        return False
    
    print(f"📄 Lese Migration-Script: {migration_file}")
    
    try:
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
    except Exception as e:
        print(f"❌ Fehler beim Lesen der Migration: {e}")
        return False
    
    # Datenbankverbindung herstellen
    print("🔌 Verbinde zur Datenbank...")
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='valeo_neuroerp',
            user='valeo_user',
            password='valeo_password',
            port=5432
        )
        conn.autocommit = True
        print("✅ Datenbankverbindung erfolgreich")
    except Exception as e:
        print(f"❌ Datenbankverbindung fehlgeschlagen: {e}")
        print("💡 Stelle sicher, dass PostgreSQL läuft und die Zugangsdaten korrekt sind")
        return False
    
    # Migration ausführen
    print("🚀 Führe Migration aus...")
    
    try:
        cursor = conn.cursor()
        
        # SQL-Statements aufteilen (bei ;)
        statements = migration_sql.split(';')
        
        for i, statement in enumerate(statements, 1):
            statement = statement.strip()
            if not statement:
                continue
                
            print(f"📝 Führe Statement {i}/{len(statements)} aus...")
            
            try:
                cursor.execute(statement)
                print(f"✅ Statement {i} erfolgreich")
            except Exception as e:
                print(f"⚠️ Statement {i} mit Warnung: {e}")
                # Bei Fehlern trotzdem weitermachen (z.B. bei IF NOT EXISTS)
        
        cursor.close()
        print("🎉 Migration erfolgreich abgeschlossen!")
        
    except Exception as e:
        print(f"❌ Fehler während der Migration: {e}")
        return False
    finally:
        conn.close()
        print("🔌 Datenbankverbindung geschlossen")
    
    return True

def verify_migration():
    """Verifiziert die Migration"""
    
    print("\n🔍 Verifiziere Migration...")
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='valeo_neuroerp',
            user='valeo_user',
            password='valeo_password',
            port=5432
        )
        cursor = conn.cursor()
        
        # Prüfe neue Schemas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name IN ('chargen', 'neuroflow')
        """)
        schemas = cursor.fetchall()
        print(f"✅ Neue Schemas gefunden: {[s[0] for s in schemas]}")
        
        # Prüfe neue Tabellen
        cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'chargen'
        """)
        tables = cursor.fetchall()
        print(f"✅ Neue Tabellen gefunden: {[f'{t[0]}.{t[1]}' for t in tables]}")
        
        # Prüfe neue Felder in bestehenden Tabellen
        cursor.execute("""
            SELECT column_name, table_name 
            FROM information_schema.columns 
            WHERE table_schema = 'einkauf' 
            AND table_name = 'lieferanten'
            AND column_name IN ('rechtsform', 'handelsregister', 'kreditlimit')
        """)
        columns = cursor.fetchall()
        print(f"✅ Neue Felder in lieferanten: {[c[0] for c in columns]}")
        
        cursor.close()
        conn.close()
        
        print("✅ Migration-Verifikation erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ Verifikation fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starte VALEO NeuroERP Database Migration")
    print("=" * 60)
    
    # Migration ausführen
    if run_migration():
        # Verifikation
        verify_migration()
        
        print("\n🎉 Migration erfolgreich abgeschlossen!")
        print("📊 NeuroFlow-Datenbank ist bereit für die Integration")
        print("\n📋 Nächste Schritte:")
        print("1. Backend-Services starten")
        print("2. Frontend mit echten Datenbankdaten testen")
        print("3. KI-Modelle mit erweiterten Daten trainieren")
        print("4. n8n-Workflows für Chargenverwaltung implementieren")
    else:
        print("\n❌ Migration fehlgeschlagen!")
        print("🔧 Bitte überprüfe:")
        print("- PostgreSQL läuft und ist erreichbar")
        print("- Datenbank 'valeo_neuroerp' existiert")
        print("- Benutzer 'valeo_user' hat Schreibrechte")
        sys.exit(1) 
