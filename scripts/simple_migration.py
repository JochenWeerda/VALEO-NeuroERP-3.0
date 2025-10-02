#!/usr/bin/env python3
"""
🧠 VALEO NeuroERP - Simple Database Migration
============================================
Vereinfachte Migration für NeuroFlow-Erweiterungen
Erstellt: 2025-07-23
"""

import psycopg2
import time
from pathlib import Path

def wait_for_postgres():
    """Wartet auf PostgreSQL-Verfügbarkeit"""
    print("⏳ Warte auf PostgreSQL...")
    
    for attempt in range(30):  # 30 Versuche
        try:
            conn = psycopg2.connect(
                host='localhost',
                database='postgres',  # Standard-DB
                user='valeo_user',
                password='valeo_password',
                port=5432
            )
            conn.close()
            print("✅ PostgreSQL ist verfügbar")
            return True
        except:
            print(f"⏳ Versuch {attempt + 1}/30...")
            time.sleep(2)
    
    print("❌ PostgreSQL nicht verfügbar nach 60 Sekunden")
    return False

def create_database():
    """Erstellt die Datenbank falls sie nicht existiert"""
    print("🗄️ Erstelle Datenbank...")
    
    try:
        # Verbinde zur Standard-DB
        conn = psycopg2.connect(
            host='localhost',
            database='postgres',
            user='valeo_user',
            password='valeo_password',
            port=5432
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Prüfe ob Datenbank existiert
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'valeo_neuroerp'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE valeo_neuroerp")
            print("✅ Datenbank 'valeo_neuroerp' erstellt")
        else:
            print("✅ Datenbank 'valeo_neuroerp' existiert bereits")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Datenbank: {e}")
        return False

def run_migration():
    """Führt die Migration aus"""
    print("🚀 Führe NeuroFlow-Migration aus...")
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='valeo_neuroerp',
            user='valeo_user',
            password='valeo_password',
            port=5432
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 1. Chargen-Schema erstellen
        print("📦 Erstelle Chargen-Schema...")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS chargen")
        
        # 2. Chargen-Tabelle erstellen
        print("📋 Erstelle Chargen-Tabelle...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chargen.chargen (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                charge_nr VARCHAR(50) UNIQUE NOT NULL,
                artikel_nr VARCHAR(50) NOT NULL,
                artikel_name VARCHAR(200) NOT NULL,
                lieferant_nr VARCHAR(50),
                lieferant_name VARCHAR(200),
                produktionsdatum DATE NOT NULL,
                verfallsdatum DATE,
                charge_groesse DECIMAL(10,4) NOT NULL,
                einheit VARCHAR(20) NOT NULL,
                qualitaets_status VARCHAR(50) DEFAULT 'OFFEN',
                vlog_gmo_status VARCHAR(50) DEFAULT 'UNBEKANNT',
                risiko_score INTEGER DEFAULT 50,
                qualitaets_score INTEGER DEFAULT 75,
                ki_risiko_bewertung TEXT,
                qualitaets_vorhersage VARCHAR(50),
                anomalie_erkennung BOOLEAN DEFAULT false,
                ki_empfehlungen TEXT,
                workflow_status VARCHAR(50) DEFAULT 'NEU',
                n8n_integration BOOLEAN DEFAULT false,
                automatisierung_status VARCHAR(50) DEFAULT 'MANUELL',
                workflow_trigger VARCHAR(100),
                automatisierte_prozesse TEXT[],
                qualitaets_zertifikate TEXT[],
                compliance_dokumente TEXT[],
                erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                erstellt_von UUID,
                geaendert_von UUID
            )
        """)
        
        # 3. Einkauf-Schema erstellen falls nicht vorhanden
        print("🛒 Erstelle Einkauf-Schema...")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS einkauf")
        
        # 4. Lieferanten-Tabelle erstellen falls nicht vorhanden
        print("👥 Erstelle Lieferanten-Tabelle...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS einkauf.lieferanten (
                lieferant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                lieferant_nr VARCHAR(50) UNIQUE NOT NULL,
                firmenname VARCHAR(200) NOT NULL,
                ansprechpartner VARCHAR(100),
                telefon VARCHAR(50),
                email VARCHAR(100),
                webseite VARCHAR(200),
                steuernummer VARCHAR(50),
                ust_id VARCHAR(50),
                zahlungsziel INTEGER DEFAULT 30,
                skonto_prozent DECIMAL(5,2) DEFAULT 0,
                bewertung INTEGER DEFAULT 3,
                status VARCHAR(50) DEFAULT 'AKTIV',
                rechtsform VARCHAR(50),
                handelsregister VARCHAR(100),
                kreditlimit DECIMAL(12,2) DEFAULT 0,
                zuverlaessigkeits_score INTEGER DEFAULT 75,
                qualitaets_score INTEGER DEFAULT 75,
                liefer_score INTEGER DEFAULT 75,
                durchschnittliche_lieferzeit INTEGER DEFAULT 7,
                mindestbestellwert DECIMAL(10,2) DEFAULT 0,
                kostenlose_lieferung_ab DECIMAL(10,2) DEFAULT 0,
                iso_9001 BOOLEAN DEFAULT false,
                iso_14001 BOOLEAN DEFAULT false,
                weitere_zertifizierungen TEXT,
                ist_bevorzugt BOOLEAN DEFAULT false,
                ist_zertifiziert BOOLEAN DEFAULT false,
                ist_lokal BOOLEAN DEFAULT false,
                vertriebsmitarbeiter VARCHAR(100),
                kostenstelle VARCHAR(50),
                notizen TEXT,
                erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 5. CRM-Schema erstellen falls nicht vorhanden
        print("👤 Erstelle CRM-Schema...")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS crm")
        
        # 6. Kunden-Tabelle erstellen falls nicht vorhanden
        print("👥 Erstelle Kunden-Tabelle...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crm.kunden (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                kunden_nr VARCHAR(50) UNIQUE NOT NULL,
                firmenname VARCHAR(200) NOT NULL,
                kundentyp VARCHAR(50),
                branche VARCHAR(100),
                umsatzklasse VARCHAR(50),
                kundenstatus VARCHAR(50) DEFAULT 'AKTIV',
                kundenbewertung INTEGER DEFAULT 3,
                kundenseit VARCHAR(50),
                zahlungsziel INTEGER DEFAULT 30,
                skonto_prozent DECIMAL(5,2) DEFAULT 0,
                erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 7. Produktion-Schema erstellen falls nicht vorhanden
        print("🏭 Erstelle Produktion-Schema...")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS produktion")
        
        # 8. Artikel-Tabelle erstellen falls nicht vorhanden
        print("📦 Erstelle Artikel-Tabelle...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produktion.artikel (
                artikel_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                bezeichnung VARCHAR(200) NOT NULL,
                beschreibung TEXT,
                einheit VARCHAR(20),
                kategorie VARCHAR(100),
                preis DECIMAL(10,2),
                waehrung VARCHAR(3) DEFAULT 'EUR',
                stock_quantity INTEGER DEFAULT 0,
                erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 9. Personal-Schema erstellen falls nicht vorhanden
        print("👨‍💼 Erstelle Personal-Schema...")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS personal")
        
        # 10. Mitarbeiter-Tabelle erstellen falls nicht vorhanden
        print("👥 Erstelle Mitarbeiter-Tabelle...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personal.mitarbeiter (
                mitarbeiter_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                vorname VARCHAR(100) NOT NULL,
                nachname VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                abteilung VARCHAR(100),
                position VARCHAR(100),
                telefon VARCHAR(50),
                mobil VARCHAR(50),
                status VARCHAR(50) DEFAULT 'AKTIV',
                erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                geaendert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 11. Indizes erstellen
        print("🔍 Erstelle Indizes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chargen_charge_nr ON chargen.chargen(charge_nr)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chargen_artikel_nr ON chargen.chargen(artikel_nr)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chargen_lieferant_nr ON chargen.chargen(lieferant_nr)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lieferanten_firmenname ON einkauf.lieferanten(firmenname)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_kunden_firmenname ON crm.kunden(firmenname)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_artikel_bezeichnung ON produktion.artikel(bezeichnung)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mitarbeiter_name ON personal.mitarbeiter(nachname, vorname)")
        
        cursor.close()
        conn.close()
        
        print("✅ Migration erfolgreich abgeschlossen!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler während der Migration: {e}")
        return False

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
        
        # Prüfe Schemas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name IN ('chargen', 'einkauf', 'crm', 'produktion', 'personal')
        """)
        schemas = cursor.fetchall()
        print(f"✅ Schemas gefunden: {[s[0] for s in schemas]}")
        
        # Prüfe Tabellen
        cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema IN ('chargen', 'einkauf', 'crm', 'produktion', 'personal')
        """)
        tables = cursor.fetchall()
        print(f"✅ Tabellen gefunden: {[f'{t[0]}.{t[1]}' for t in tables]}")
        
        cursor.close()
        conn.close()
        
        print("✅ Migration-Verifikation erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ Verifikation fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    print("🧠 VALEO NeuroERP - Simple Database Migration")
    print("=" * 60)
    
    # Warte auf PostgreSQL
    if not wait_for_postgres():
        exit(1)
    
    # Erstelle Datenbank
    if not create_database():
        exit(1)
    
    # Führe Migration aus
    if run_migration():
        # Verifikation
        verify_migration()
        
        print("\n🎉 Migration erfolgreich abgeschlossen!")
        print("📊 NeuroFlow-Datenbank ist bereit für die Integration")
        print("\n📋 Verfügbare Services:")
        print("• Chargenverwaltung: chargen.chargen")
        print("• Lieferantenstammdaten: einkauf.lieferanten")
        print("• Kundenstammdaten: crm.kunden")
        print("• Artikelstammdaten: produktion.artikel")
        print("• Personalstammdaten: personal.mitarbeiter")
    else:
        print("\n❌ Migration fehlgeschlagen!")
        exit(1) 