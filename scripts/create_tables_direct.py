#!/usr/bin/env python3
"""
Erstellt Tabellen direkt mit SQLAlchemy
Läuft im Docker-Netzwerk oder nutzt existierende Connection
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.infrastructure.models import Base

# Verwende die korrekte DB-URL
DATABASE_URL = "postgresql://valeo_dev:valeo_dev_2024!@localhost:5432/valeo_neuro_erp"

print("=" * 80)
print("Erstelle Tabellen mit SQLAlchemy")
print("=" * 80)
print(f"Database: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL, echo=True)
    
    print("\n1. Teste Verbindung...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("   ✅ Verbindung erfolgreich")
    
    print("\n2. Erstelle Tabellen...")
    Base.metadata.create_all(bind=engine)
    print("   ✅ Tabellen erstellt")
    
    print("\n3. Prüfe erstellte Tabellen...")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT schemaname, tablename 
            FROM pg_tables 
            WHERE schemaname LIKE 'domain_%'
            ORDER BY schemaname, tablename
        """))
        tables = list(result)
        print(f"   ✅ {len(tables)} Tabellen gefunden:")
        for schema, table in tables:
            print(f"      - {schema}.{table}")
    
    print("\n✅ ERFOLGREICH")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ FEHLER: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

