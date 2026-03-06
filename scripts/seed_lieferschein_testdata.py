#!/usr/bin/env python3
"""
Seed-Script: Kunden/Debitoren und Artikel für Lieferschein-Tests
Erstellt realistische Testdaten für die Lieferschein-Erfassung
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from decimal import Decimal
from app.core.uuid7 import uuid7

from app.core.database import SessionLocal
from app.infrastructure.models import Article, Customer

def seed_customers(db, tenant_id: str = "default"):
    """Seed Kunden/Debitoren für Lieferschein-Tests"""
    print("Seeding Kunden/Debitoren...")
    
    customers_data = [
        {
            "id": uuid7(),
            "customer_number": "K-10001",
            "company_name": "Mustermann Agrar GmbH",
            "contact_person": "Max Mustermann",
            "email": "max.mustermann@mustermann-agrar.de",
            "phone": "+49 171 1234567",
            "address": "Hauptstraße 123, 48143 Münster",
            "city": "Münster",
            "postal_code": "48143",
            "country": "Deutschland",
            "industry": "Agrarhandel",
            "customer_type": "business",
            "credit_limit": Decimal("50000.00"),
            "payment_terms": 30,
            "tax_id": "DE123456789",
            "tenant_id": tenant_id,
            "is_active": True,
        },
        {
            "id": uuid7(),
            "customer_number": "K-10002",
            "company_name": "Schmidt Landwirtschaft",
            "contact_person": "Anna Schmidt",
            "email": "anna@schmidt-land.de",
            "phone": "+49 152 9876543",
            "address": "Dorfstraße 45",
            "city": "Osnabrück",
            "postal_code": "49074",
            "country": "Deutschland",
            "industry": "Landwirtschaft",
            "customer_type": "business",
            "credit_limit": Decimal("25000.00"),
            "payment_terms": 14,
            "tax_id": "DE987654321",
            "tenant_id": tenant_id,
            "is_active": True,
        },
        {
            "id": uuid7(),
            "customer_number": "K-10003",
            "company_name": "Weber Agrar Service",
            "contact_person": "Thomas Weber",
            "email": "thomas.weber@weber-agrar.com",
            "phone": "+49 175 5551234",
            "address": "Landweg 78",
            "city": "Nordwalde",
            "postal_code": "48356",
            "country": "Deutschland",
            "industry": "Lohnunternehmen",
            "customer_type": "business",
            "credit_limit": Decimal("75000.00"),
            "payment_terms": 30,
            "tax_id": "DE555666777",
            "tenant_id": tenant_id,
            "is_active": True,
        },
        {
            "id": uuid7(),
            "customer_number": "K-10004",
            "company_name": "Bauer Hof GmbH & Co. KG",
            "contact_person": "Klaus Bauer",
            "email": "klaus@bauer-hof.de",
            "phone": "+49 2501 778899",
            "address": "Hofweg 5",
            "city": "Havixbeck",
            "postal_code": "48167",
            "country": "Deutschland",
            "industry": "Landwirtschaft",
            "customer_type": "business",
            "credit_limit": Decimal("100000.00"),
            "payment_terms": 30,
            "tax_id": "DE111222333",
            "tenant_id": tenant_id,
            "is_active": True,
        },
        {
            "id": uuid7(),
            "customer_number": "K-10005",
            "company_name": "Fischer Gemüsebau",
            "contact_person": "Sandra Fischer",
            "email": "sandra@fischer-gemuese.de",
            "phone": "+49 251 445566",
            "address": "Feldweg 22",
            "city": "Münster",
            "postal_code": "48163",
            "country": "Deutschland",
            "industry": "Gemüsebau",
            "customer_type": "business",
            "credit_limit": Decimal("30000.00"),
            "payment_terms": 14,
            "tax_id": "DE444555666",
            "tenant_id": tenant_id,
            "is_active": True,
        },
    ]
    
    from sqlalchemy import text
    created_count = 0
    for customer_data in customers_data:
        # Prüfe ob Kunde bereits existiert (per SQL)
        check_result = db.execute(
            text("SELECT customer_number FROM domain_crm.customers WHERE customer_number = :num AND tenant_id = :tid"),
            {"num": customer_data["customer_number"], "tid": tenant_id}
        ).first()
        
        if not check_result:
            # Füge Kunde direkt per SQL ein (nur existierende Spalten)
            # Address muss als JSON sein
            import json
            address_json = json.dumps({"street": customer_data["address"]})
            
            db.execute(
                text("""
                    INSERT INTO domain_crm.customers 
                    (id, customer_number, company_name, contact_person, email, phone, address, 
                     tenant_id, is_active, credit_limit, payment_terms, created_at)
                    VALUES 
                    (:id, :customer_number, :company_name, :contact_person, :email, :phone, CAST(:address AS jsonb),
                     :tenant_id, :is_active, :credit_limit, :payment_terms, NOW())
                """),
                {
                    "id": customer_data["id"],
                    "customer_number": customer_data["customer_number"],
                    "company_name": customer_data["company_name"],
                    "contact_person": customer_data["contact_person"],
                    "email": customer_data["email"],
                    "phone": customer_data["phone"],
                    "address": address_json,
                    "tenant_id": tenant_id,
                    "is_active": customer_data["is_active"],
                    "credit_limit": customer_data["credit_limit"],
                    "payment_terms": customer_data["payment_terms"],
                }
            )
            created_count += 1
            db.commit()
    
    print(f"   [OK] {created_count} neue Kunden erstellt, {len(customers_data)} Kunden geprueft")
    return customers_data


def seed_articles(db, tenant_id: str = "default"):
    """Seed Artikel für Lieferschein-Tests"""
    print("Seeding Artikel...")
    
    articles_data = [
        {
            "id": uuid7(),
            "article_number": "ART-10001",
            "name": "Weizen Saatgut Premium",
            "description": "Hochwertiges Weizensaatgut, ertragsstark, zertifiziert",
            "suchbegriff": "Weizen Saatgut",
            "hersteller": "KWS Saat SE",
            "herkunftsland": "DE",
            "mehrwertsteuer_prozent": Decimal("19.00"),
            "warengruppe": "Saatgut",
            "unit": "kg",
            "category": "Saatgut",
            "subcategory": "Getreide",
            "barcode": "4001234567890",
            "purchase_price": Decimal("2.50"),
            "sales_price": Decimal("3.95"),
            "currency": "EUR",
            "min_stock": Decimal("100.00"),
            "max_stock": Decimal("5000.00"),
            "current_stock": Decimal("2500.00"),
            "available_stock": Decimal("2500.00"),
            "weight": Decimal("1.00"),
            "lagerartikel": True,
            "chargenpflicht": True,
            "tenant_id": tenant_id,
            "is_active": True,
        },
        {
            "id": uuid7(),
            "article_number": "ART-10002",
            "name": "Stickstoff-Dünger 27%",
            "description": "Mineralischer Stickstoffdünger, 27% N-Gehalt",
            "suchbegriff": "Stickstoff Dünger",
            "hersteller": "Yara Deutschland",
            "herkunftsland": "DE",
            "mehrwertsteuer_prozent": Decimal("19.00"),
            "warengruppe": "Düngemittel",
            "unit": "kg",
            "category": "Düngemittel",
            "subcategory": "Mineraldünger",
            "barcode": "4001234567891",
            "purchase_price": Decimal("0.85"),
            "sales_price": Decimal("1.25"),
            "currency": "EUR",
            "min_stock": Decimal("5000.00"),
            "max_stock": Decimal("50000.00"),
            "current_stock": Decimal("25000.00"),
            "available_stock": Decimal("25000.00"),
            "weight": Decimal("50.00"),
            "lagerartikel": True,
            "chargenpflicht": False,
            "tenant_id": tenant_id,
            "is_active": True,
        },
        {
            "id": uuid7(),
            "article_number": "ART-10003",
            "name": "Glyphosat Herbizid 360g/l",
            "description": "Breitbandherbizid, glyphosathaltig, 5 Liter Kanister",
            "suchbegriff": "Glyphosat Herbizid",
            "hersteller": "Bayer CropScience",
            "herkunftsland": "DE",
            "mehrwertsteuer_prozent": Decimal("19.00"),
            "warengruppe": "Pflanzenschutz",
            "gefahrgutklasse": "GHS09",
            "unit": "L",
            "category": "Pflanzenschutz",
            "subcategory": "Herbizide",
            "barcode": "4001234567892",
            "purchase_price": Decimal("18.50"),
            "sales_price": Decimal("28.90"),
            "currency": "EUR",
            "min_stock": Decimal("50.00"),
            "max_stock": Decimal("500.00"),
            "current_stock": Decimal("200.00"),
            "available_stock": Decimal("200.00"),
            "weight": Decimal("5.20"),
            "lagerartikel": True,
            "chargenpflicht": True,
            "qs_pruefung_erforderlich": True,
            "tenant_id": tenant_id,
            "is_active": True,
        },
        {
            "id": uuid7(),
            "article_number": "ART-10004",
            "name": "Raps Saatgut Hybrid",
            "description": "Hochleistungs-Rapssaatgut, hybrid, ertragsstark",
            "suchbegriff": "Raps Saatgut",
            "hersteller": "DSV Saaten",
            "herkunftsland": "DE",
            "mehrwertsteuer_prozent": Decimal("19.00"),
            "warengruppe": "Saatgut",
            "unit": "kg",
            "category": "Saatgut",
            "subcategory": "Ölpflanzen",
            "barcode": "4001234567893",
            "purchase_price": Decimal("4.20"),
            "sales_price": Decimal("6.50"),
            "currency": "EUR",
            "min_stock": Decimal("50.00"),
            "max_stock": Decimal("2000.00"),
            "current_stock": Decimal("800.00"),
            "available_stock": Decimal("800.00"),
            "weight": Decimal("1.00"),
            "lagerartikel": True,
            "chargenpflicht": True,
            "tenant_id": tenant_id,
            "is_active": True,
        },
        {
            "id": uuid7(),
            "article_number": "ART-10005",
            "name": "Mais Saatgut Silo",
            "description": "Maissaatgut für Silomais, frühreif, hoher Ertrag",
            "suchbegriff": "Mais Saatgut",
            "hersteller": "Pioneer Hi-Bred",
            "herkunftsland": "DE",
            "mehrwertsteuer_prozent": Decimal("19.00"),
            "warengruppe": "Saatgut",
            "unit": "kg",
            "category": "Saatgut",
            "subcategory": "Getreide",
            "barcode": "4001234567894",
            "purchase_price": Decimal("3.80"),
            "sales_price": Decimal("5.95"),
            "currency": "EUR",
            "min_stock": Decimal("200.00"),
            "max_stock": Decimal("3000.00"),
            "current_stock": Decimal("1500.00"),
            "available_stock": Decimal("1500.00"),
            "weight": Decimal("1.00"),
            "lagerartikel": True,
            "chargenpflicht": True,
            "tenant_id": tenant_id,
            "is_active": True,
        },
        {
            "id": uuid7(),
            "article_number": "ART-10006",
            "name": "Phosphat-Dünger 18%",
            "description": "Phosphatdünger, 18% P2O5, granuliert",
            "suchbegriff": "Phosphat Dünger",
            "hersteller": "EuroChem",
            "herkunftsland": "DE",
            "mehrwertsteuer_prozent": Decimal("19.00"),
            "warengruppe": "Düngemittel",
            "unit": "kg",
            "category": "Düngemittel",
            "subcategory": "Mineraldünger",
            "barcode": "4001234567895",
            "purchase_price": Decimal("0.75"),
            "sales_price": Decimal("1.15"),
            "currency": "EUR",
            "min_stock": Decimal("3000.00"),
            "max_stock": Decimal("40000.00"),
            "current_stock": Decimal("18000.00"),
            "available_stock": Decimal("18000.00"),
            "weight": Decimal("50.00"),
            "lagerartikel": True,
            "chargenpflicht": False,
            "tenant_id": tenant_id,
            "is_active": True,
        },
        {
            "id": uuid7(),
            "article_number": "ART-10007",
            "name": "Fungizid Tebuconazol",
            "description": "Fungizid gegen Getreidekrankheiten, 250ml Flasche",
            "suchbegriff": "Fungizid Tebuconazol",
            "hersteller": "BASF",
            "herkunftsland": "DE",
            "mehrwertsteuer_prozent": Decimal("19.00"),
            "warengruppe": "Pflanzenschutz",
            "gefahrgutklasse": "GHS07",
            "unit": "L",
            "category": "Pflanzenschutz",
            "subcategory": "Fungizide",
            "barcode": "4001234567896",
            "purchase_price": Decimal("22.00"),
            "sales_price": Decimal("34.50"),
            "currency": "EUR",
            "min_stock": Decimal("30.00"),
            "max_stock": Decimal("300.00"),
            "current_stock": Decimal("120.00"),
            "available_stock": Decimal("120.00"),
            "weight": Decimal("0.30"),
            "lagerartikel": True,
            "chargenpflicht": True,
            "qs_pruefung_erforderlich": True,
            "tenant_id": tenant_id,
            "is_active": True,
        },
        {
            "id": uuid7(),
            "article_number": "ART-10008",
            "name": "Kartoffel Saatgut",
            "description": "Zertifiziertes Pflanzkartoffeln, mittelfrüh, festkochend",
            "suchbegriff": "Kartoffel Saatgut",
            "hersteller": "Norika",
            "herkunftsland": "DE",
            "mehrwertsteuer_prozent": Decimal("19.00"),
            "warengruppe": "Saatgut",
            "unit": "kg",
            "category": "Saatgut",
            "subcategory": "Gemüse",
            "barcode": "4001234567897",
            "purchase_price": Decimal("1.80"),
            "sales_price": Decimal("2.95"),
            "currency": "EUR",
            "min_stock": Decimal("500.00"),
            "max_stock": Decimal("10000.00"),
            "current_stock": Decimal("3500.00"),
            "available_stock": Decimal("3500.00"),
            "weight": Decimal("1.00"),
            "lagerartikel": True,
            "chargenpflicht": True,
            "tenant_id": tenant_id,
            "is_active": True,
        },
        {
            "id": uuid7(),
            "article_number": "ART-10009",
            "name": "Kali-Dünger 40%",
            "description": "Kaliumdünger, 40% K2O, für alle Kulturen",
            "suchbegriff": "Kali Dünger",
            "hersteller": "K+S",
            "herkunftsland": "DE",
            "mehrwertsteuer_prozent": Decimal("19.00"),
            "warengruppe": "Düngemittel",
            "unit": "kg",
            "category": "Düngemittel",
            "subcategory": "Mineraldünger",
            "barcode": "4001234567898",
            "purchase_price": Decimal("0.65"),
            "sales_price": Decimal("0.95"),
            "currency": "EUR",
            "min_stock": Decimal("2000.00"),
            "max_stock": Decimal("30000.00"),
            "current_stock": Decimal("12000.00"),
            "available_stock": Decimal("12000.00"),
            "weight": Decimal("50.00"),
            "lagerartikel": True,
            "chargenpflicht": False,
            "tenant_id": tenant_id,
            "is_active": True,
        },
        {
            "id": uuid7(),
            "article_number": "ART-10010",
            "name": "Insektizid Lambda-Cyhalothrin",
            "description": "Insektizid gegen Schädlinge, 1 Liter Flasche",
            "suchbegriff": "Insektizid Lambda",
            "hersteller": "Syngenta",
            "herkunftsland": "DE",
            "mehrwertsteuer_prozent": Decimal("19.00"),
            "warengruppe": "Pflanzenschutz",
            "gefahrgutklasse": "GHS06",
            "unit": "L",
            "category": "Pflanzenschutz",
            "subcategory": "Insektizide",
            "barcode": "4001234567899",
            "purchase_price": Decimal("35.00"),
            "sales_price": Decimal("52.00"),
            "currency": "EUR",
            "min_stock": Decimal("20.00"),
            "max_stock": Decimal("200.00"),
            "current_stock": Decimal("85.00"),
            "available_stock": Decimal("85.00"),
            "weight": Decimal("1.10"),
            "lagerartikel": True,
            "chargenpflicht": True,
            "qs_pruefung_erforderlich": True,
            "tenant_id": tenant_id,
            "is_active": True,
        },
    ]
    
    created_count = 0
    for article_data in articles_data:
        # Prüfe ob Artikel bereits existiert
        existing = db.query(Article.article_number).filter(
            Article.article_number == article_data["article_number"],
            Article.tenant_id == tenant_id
        ).first()
        
        if not existing:
            article = Article(**article_data)
            db.add(article)
            created_count += 1
            # Commit einzeln, um UUID-Probleme zu vermeiden
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"   [WARN] Fehler beim Erstellen von Artikel {article_data['article_number']}: {e}")
    
    print(f"   [OK] {created_count} neue Artikel erstellt, {len(articles_data)} Artikel geprueft")
    return articles_data


def main():
    """Main seed function"""
    print("=" * 60)
    print("Lieferschein Test-Daten Seeding")
    print("=" * 60)
    
    db = SessionLocal()
    
    # Hole oder erstelle default tenant (als String UUID)
    try:
        from app.infrastructure.models import Tenant
        tenant = db.query(Tenant).filter(Tenant.name == "default").first()
        if not tenant:
            # Erstelle default tenant
            tenant_id_str = uuid7()
            tenant = Tenant(id=tenant_id_str, name="default", is_active=True)
            db.add(tenant)
            db.commit()
            tenant_id = tenant_id_str
        else:
            tenant_id = str(tenant.id) if hasattr(tenant.id, '__str__') else tenant.id
    except Exception as e:
        print(f"Warning: Could not get tenant: {e}")
        # Fallback: verwende einen Standard-UUID
        tenant_id = "00000000-0000-0000-0000-000000000000"
    
    try:
        # Seed data
        customers = seed_customers(db, tenant_id)
        articles = seed_articles(db, tenant_id)
        
        # Commit
        db.commit()
        print("\n[OK] Alle Test-Daten erfolgreich eingefuegt!")
        
        # Summary (verwende direkte SQL-Abfragen, um Modell-Probleme zu vermeiden)
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        
        try:
            from sqlalchemy import text
            customer_result = db.execute(text("SELECT COUNT(*) FROM domain_crm.customers WHERE tenant_id = :tid"), {"tid": tenant_id})
            customer_count = customer_result.scalar()
            article_result = db.execute(text("SELECT COUNT(*) FROM domain_inventory.articles WHERE tenant_id = :tid"), {"tid": tenant_id})
            article_count = article_result.scalar()
            
            print(f"   Kunden in DB: {customer_count}")
            print(f"   Artikel in DB: {article_count}")
        except Exception as e:
            print(f"   [WARN] Konnte Zaehlung nicht durchfuehren: {e}")
            print(f"   Kunden: mindestens {len(customers)} erstellt")
            print(f"   Artikel: mindestens {len(articles)} erstellt")
        
        print("\n[OK] Ready to test Lieferschein-Erfassung!")
        print("   → http://localhost:3000/verkauf/lieferschein-erfassung")
        
    except Exception as e:
        print(f"\n[ERROR] Fehler beim Seeden: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

