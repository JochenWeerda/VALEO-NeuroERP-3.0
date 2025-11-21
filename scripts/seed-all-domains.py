#!/usr/bin/env python3
"""
Seed-Script: ALLE Domains mit realistischen Testdaten
Führt Alembic-Migrations aus und füllt DB
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database_pg import SessionLocal, engine
from app.crm.seed import seed_crm_data
from app.crm.models import Base as CRMBase

def main():
    """Main seed function"""
    print("🌱 VALEO-NeuroERP - Seed-Script für ALLE Domains")
    print("=" * 60)
    
    # 1. Create tables
    print("\n1️⃣ Erstelle Tabellen...")
    try:
        CRMBase.metadata.create_all(bind=engine)
        print("✅ Tabellen erstellt (CRM)")
    except Exception as e:
        print(f"⚠️ Tabellen-Erstellung: {e}")
    
    # 2. Seed data
    print("\n2️⃣ Fülle Datenbank mit Seed-Daten...")
    db: Session = SessionLocal()
    
    try:
        # CRM
        print("\n📋 CRM-Domain:")
        seed_crm_data(db, tenant_id="default")
        
        # TODO: Agrar
        # print("\n🌾 Agrar-Domain:")
        # seed_agrar_data(db, tenant_id="default")
        
        # TODO: Finance
        # print("\n💰 Finance-Domain:")
        # seed_finance_data(db, tenant_id="default")
        
        # TODO: Einkauf
        # print("\n📦 Einkauf-Domain:")
        # seed_einkauf_data(db, tenant_id="default")
        
        print("\n✅ Alle Seed-Daten erfolgreich eingefügt!")
        
    except Exception as e:
        print(f"\n❌ Fehler beim Seeden: {e}")
        db.rollback()
        raise
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("🎉 Seeding abgeschlossen!")
    print("\n💡 Starte Backend mit: python -m uvicorn main:app --reload")
    print("🌐 Öffne Frontend: http://localhost:3000")


if __name__ == "__main__":
    main()

