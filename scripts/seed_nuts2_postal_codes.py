"""
Seed script for NUTS-2 Postal Code mappings.
Imports NUTS-2 codes from Eurostat correspondence tables.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.infrastructure.models import Nuts2PostalCode
from modules.agrar.services.nuts2_service import bulk_import_nuts2_postal_codes


def seed_nuts2_postal_codes_de():
    """
    Seed NUTS-2 postal code mappings for Germany.
    
    Diese Daten sollten idealerweise aus offiziellen Eurostat-Quellen importiert werden.
    Hier: Beispiel-Daten für wichtige PLZ-Bereiche.
    """
    db: Session = SessionLocal()
    
    try:
        # Beispiel-Daten für Deutschland (vereinfacht)
        # In Produktion: Import aus Eurostat CSV/XML
        entries = [
            # Sachsen (DE12)
            {"postal_code": "01067", "city": "Dresden", "country_code": "DE", "nuts2_code": "DE12", "nuts_version": "NUTS 2024"},
            {"postal_code": "01069", "city": "Dresden", "country_code": "DE", "nuts2_code": "DE12", "nuts_version": "NUTS 2024"},
            {"postal_code": "04103", "city": "Leipzig", "country_code": "DE", "nuts2_code": "DE12", "nuts_version": "NUTS 2024"},
            {"postal_code": "04105", "city": "Leipzig", "country_code": "DE", "nuts2_code": "DE12", "nuts_version": "NUTS 2024"},
            {"postal_code": "04107", "city": "Leipzig", "country_code": "DE", "nuts2_code": "DE12", "nuts_version": "NUTS 2024"},
            {"postal_code": "04109", "city": "Leipzig", "country_code": "DE", "nuts2_code": "DE12", "nuts_version": "NUTS 2024"},
            
            # Sachsen-Anhalt (DE14)
            {"postal_code": "06108", "city": "Halle (Saale)", "country_code": "DE", "nuts2_code": "DE14", "nuts_version": "NUTS 2024"},
            {"postal_code": "06110", "city": "Halle (Saale)", "country_code": "DE", "nuts2_code": "DE14", "nuts_version": "NUTS 2024"},
            {"postal_code": "39104", "city": "Magdeburg", "country_code": "DE", "nuts2_code": "DE14", "nuts_version": "NUTS 2024"},
            {"postal_code": "39106", "city": "Magdeburg", "country_code": "DE", "nuts2_code": "DE14", "nuts_version": "NUTS 2024"},
            {"postal_code": "39108", "city": "Magdeburg", "country_code": "DE", "nuts2_code": "DE14", "nuts_version": "NUTS 2024"},
            
            # Thüringen (DE16)
            {"postal_code": "99084", "city": "Erfurt", "country_code": "DE", "nuts2_code": "DE16", "nuts_version": "NUTS 2024"},
            {"postal_code": "99085", "city": "Erfurt", "country_code": "DE", "nuts2_code": "DE16", "nuts_version": "NUTS 2024"},
            {"postal_code": "99086", "city": "Erfurt", "country_code": "DE", "nuts2_code": "DE16", "nuts_version": "NUTS 2024"},
            {"postal_code": "07743", "city": "Jena", "country_code": "DE", "nuts2_code": "DE16", "nuts_version": "NUTS 2024"},
            {"postal_code": "07745", "city": "Jena", "country_code": "DE", "nuts2_code": "DE16", "nuts_version": "NUTS 2024"},
            
            # Brandenburg (DE40)
            {"postal_code": "14467", "city": "Potsdam", "country_code": "DE", "nuts2_code": "DE40", "nuts_version": "NUTS 2024"},
            {"postal_code": "14469", "city": "Potsdam", "country_code": "DE", "nuts2_code": "DE40", "nuts_version": "NUTS 2024"},
            {"postal_code": "14471", "city": "Potsdam", "country_code": "DE", "nuts2_code": "DE40", "nuts_version": "NUTS 2024"},
            {"postal_code": "03046", "city": "Cottbus", "country_code": "DE", "nuts2_code": "DE40", "nuts_version": "NUTS 2024"},
            {"postal_code": "03048", "city": "Cottbus", "country_code": "DE", "nuts2_code": "DE40", "nuts_version": "NUTS 2024"},
            
            # Mecklenburg-Vorpommern (DE80)
            {"postal_code": "18055", "city": "Rostock", "country_code": "DE", "nuts2_code": "DE80", "nuts_version": "NUTS 2024"},
            {"postal_code": "18057", "city": "Rostock", "country_code": "DE", "nuts2_code": "DE80", "nuts_version": "NUTS 2024"},
            {"postal_code": "19053", "city": "Schwerin", "country_code": "DE", "nuts2_code": "DE80", "nuts_version": "NUTS 2024"},
            {"postal_code": "19055", "city": "Schwerin", "country_code": "DE", "nuts2_code": "DE80", "nuts_version": "NUTS 2024"},
            
            # Bayern (DE21 - Oberbayern)
            {"postal_code": "80331", "city": "München", "country_code": "DE", "nuts2_code": "DE21", "nuts_version": "NUTS 2024"},
            {"postal_code": "80335", "city": "München", "country_code": "DE", "nuts2_code": "DE21", "nuts_version": "NUTS 2024"},
            {"postal_code": "80339", "city": "München", "country_code": "DE", "nuts2_code": "DE21", "nuts_version": "NUTS 2024"},
            
            # Niedersachsen (DE91)
            {"postal_code": "30159", "city": "Hannover", "country_code": "DE", "nuts2_code": "DE91", "nuts_version": "NUTS 2024"},
            {"postal_code": "30161", "city": "Hannover", "country_code": "DE", "nuts2_code": "DE91", "nuts_version": "NUTS 2024"},
            {"postal_code": "30163", "city": "Hannover", "country_code": "DE", "nuts2_code": "DE91", "nuts_version": "NUTS 2024"},
            
            # Nordrhein-Westfalen (DEA1 - Düsseldorf)
            {"postal_code": "40210", "city": "Düsseldorf", "country_code": "DE", "nuts2_code": "DEA1", "nuts_version": "NUTS 2024"},
            {"postal_code": "40211", "city": "Düsseldorf", "country_code": "DE", "nuts2_code": "DEA1", "nuts_version": "NUTS 2024"},
            {"postal_code": "40213", "city": "Düsseldorf", "country_code": "DE", "nuts2_code": "DEA1", "nuts_version": "NUTS 2024"},
        ]
        
        count = bulk_import_nuts2_postal_codes(db, entries)
        print(f"✅ {count} NUTS-2 postal code mappings imported successfully")
        
    except Exception as e:
        print(f"❌ Error seeding NUTS-2 postal codes: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_nuts2_postal_codes_de()


