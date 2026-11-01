#!/usr/bin/env python3
"""
Seed CRM test data directly into database
Creates sample farm profiles
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from app.core.uuid7 import uuid7

from app.core.database import SessionLocal
from app.infrastructure.models import FarmProfile

def seed_farm_profiles(db):
    """Seed test farm profiles"""
    print("🚜 Seeding Farm Profiles...")
    
    profiles = [
        {
            "id": uuid7(),
            "farm_name": "Bio-Hof Schmidt",
            "owner": "Hans Schmidt",
            "total_area": 150.5,
            "crops": [
                {"crop": "Weizen", "area": 80},
                {"crop": "Gerste", "area": 45},
                {"crop": "Raps", "area": 25.5}
            ],
            "livestock": [
                {"type": "Milchkühe", "count": 60},
                {"type": "Kälber", "count": 15}
            ],
            "location": {
                "latitude": 52.520008,
                "longitude": 13.404954,
                "address": "Hauptstraße 123, 12345 Teststadt, Deutschland"
            },
            "certifications": ["Bio", "QS", "HACCP"],
            "notes": "Traditionsreicher Betrieb seit 1950",
            "tenant_id": "00000000-0000-0000-0000-000000000001",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
        {
            "id": uuid7(),
            "farm_name": "Hof Müller",
            "owner": "Thomas Müller",
            "total_area": 85.0,
            "crops": [
                {"crop": "Mais", "area": 50},
                {"crop": "Sonnenblumen", "area": 35}
            ],
            "livestock": [
                {"type": "Schweine", "count": 200}
            ],
            "location": {
                "latitude": 51.165691,
                "longitude": 10.451526,
                "address": "Dorfstraße 45, 34567 Musterstadt, Deutschland"
            },
            "certifications": ["QS"],
            "notes": "Spezialisiert auf Schweinezucht",
            "tenant_id": "00000000-0000-0000-0000-000000000001",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
        {
            "id": uuid7(),
            "farm_name": "Gemüsehof Weber",
            "owner": "Maria Weber",
            "total_area": 25.0,
            "crops": [
                {"crop": "Kartoffeln", "area": 10},
                {"crop": "Möhren", "area": 8},
                {"crop": "Kohl", "area": 7}
            ],
            "livestock": [],
            "location": {
                "latitude": 53.551086,
                "longitude": 9.993682,
                "address": "Feldweg 7, 20095 Hamburg, Deutschland"
            },
            "certifications": ["Bio", "GAP"],
            "notes": "Bio-Gemüsebau mit Direktvermarktung",
            "tenant_id": "00000000-0000-0000-0000-000000000001",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
    ]
    
    for profile_data in profiles:
        profile = FarmProfile(**profile_data)
        db.add(profile)
    
    print(f"   ✅ Created {len(profiles)} farm profiles")

def main():
    """Main seeding function"""
    print("=" * 60)
    print("🌱 CRM Data Seeding")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Seed data
        seed_farm_profiles(db)
        
        # Commit
        db.commit()
        print("\n✅ All test data seeded successfully!")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Summary")
        print("=" * 60)
        
        profile_count = db.query(FarmProfile).count()
        
        print(f"   Farm Profiles in DB: {profile_count}")
        
        print("\n🎉 Ready to test in browser!")
        print("   → http://localhost:3000/crm/aktivitaeten")
        print("   → http://localhost:3000/crm/betriebsprofile")
        
    except Exception as e:
        print(f"\n❌ Error seeding data: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()


