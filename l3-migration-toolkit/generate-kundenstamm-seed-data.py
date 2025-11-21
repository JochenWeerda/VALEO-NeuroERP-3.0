#!/usr/bin/env python3
"""
Generiert Seed-Daten für Kundenstamm-Tabellen
"""

import random
from datetime import datetime, timedelta

# Fiktive Firmennamen für Testdaten
COMPANY_NAMES = [
    "Bauernhof Müller GmbH",
    "Agrar-Genossenschaft Süd e.V.",
    "Landwirtschaft Meier AG",
    "Biohof Schmidt KG",
    "Agrarhandel Nord GmbH",
    "Landhandel Weber e.K.",
    "Agrar-Betrieb Hansen GmbH",
    "Bauernhof Fischer KG",
    "Agrar-Genossenschaft Ost e.V.",
    "Landwirtschaft Becker AG"
]

STREETS = [
    "Dorfstraße", "Hauptstraße", "Mühlenweg", "Bahnhofstraße",
    "Kirchplatz", "Gartenstraße", "Bauernweg", "Stallgasse"
]

CITIES = [
    ("26127", "Oldenburg"),
    ("49080", "Osnabrück"),
    ("48143", "Münster"),
    ("30159", "Hannover"),
    ("28195", "Bremen"),
    ("01067", "Dresden"),
    ("01069", "Dresden"),
    ("20095", "Hamburg")
]

POSITIONS = [
    "Geschäftsführer", "Einkaufsleiter", "Lagerleiter", "Disponent",
    "Landwirt", "Meister", "Leiter Produktion"
]

def generate_kunden_sql(n=10):
    """Generiert INSERT-Statements für kunden-Tabelle"""
    sql = "\n-- ============================================================================\n"
    sql += "-- SEED DATA: Kunden\n"
    sql += "-- ============================================================================\n\n"
    
    for i in range(1, n + 1):
        kunden_nr = f"K{i:05d}"
        name = random.choice(COMPANY_NAMES)
        plz, ort = random.choice(CITIES)
        street = random.choice(STREETS)
        street_nr = random.randint(1, 99)
        
        # Berechne Werte vorher (außerhalb des f-strings)
        tel = f'+49 441 12{random.randint(1000, 9999)}'
        fax = f'+49 441 12{random.randint(1000, 9999)}'
        email_domain = name.lower().replace(" ", "").replace(".", "").replace("gmbh", "").replace("kg", "").replace("e.k.", "").replace("e.v.", "").replace("ag", "")
        email = f'info@{email_domain}.de'
        homepage = f'www.{email_domain}.de'
        zahlungsbedingungen = random.randint(10, 30)
        skonto = round(random.uniform(0, 3), 2)
        selbstabholer_rabatt = round(random.uniform(0, 5), 2)
        gueltig_ab_days = random.randint(1, 730)
        gueltig_bis_days = random.randint(365, 1095)
        webshop_kunde = str(random.choice([True, False])).lower()
        
        sql += f"""INSERT INTO kunden (
    kunden_nr, name1, name2, strasse, plz, ort, land,
    tel, fax, email, homepage,
    zahlungsbedingungen_tage, skonto, waehrung,
    selbstabholer_rabatt, gueltig_ab, gueltig_bis,
    sprachschluessel, webshop_kunde, erstellt_am
) VALUES (
    '{kunden_nr}',
    '{name}',
    'Landwirtschaftsbetrieb',
    '{street} {street_nr}',
    '{plz}',
    '{ort}',
    'Deutschland',
    '{tel}',
    '{fax}',
    '{email}',
    '{homepage}',
    {zahlungsbedingungen},
    {skonto},
    'EUR',
    {selbstabholer_rabatt},
    CURRENT_DATE - INTERVAL '{gueltig_ab_days} days',
    CURRENT_DATE + INTERVAL '{gueltig_bis_days} days',
    'DE',
    {webshop_kunde},
    CURRENT_TIMESTAMP
);

"""
    
    return sql

def generate_kunden_profil_sql(n=10):
    """Generiert INSERT-Statements für kunden_profil"""
    sql = "\n-- ============================================================================\n"
    sql += "-- SEED DATA: Kundenprofil\n"
    sql += "-- ============================================================================\n\n"
    
    branchen = ["Landwirtschaft", "Agrarhandel", "Viehzucht", "Ackerbau", "Gemüseanbau"]
    
    for i in range(1, n + 1):
        kunden_nr = f"K{i:05d}"
        firmenname = random.choice(COMPANY_NAMES)
        gruendung = (datetime.now() - timedelta(days=random.randint(1000, 10950))).strftime("%Y-%m-%d")
        jahresumsatz = random.randint(500000, 5000000)
        branche = random.choice(branchen)
        mitarbeiteranzahl = random.randint(5, 50)
        
        sql += f"""INSERT INTO kunden_profil (
    kunden_nr, firmenname, gruendung, jahresumsatz, branche,
    mitarbeiteranzahl, erstellt_am
) VALUES (
    '{kunden_nr}',
    '{firmenname}',
    '{gruendung}',
    {jahresumsatz},
    '{branche}',
    {mitarbeiteranzahl},
    CURRENT_TIMESTAMP
);

"""
    
    return sql

def generate_kunden_ansprechpartner_sql(n=10):
    """Generiert INSERT-Statements für kunden_ansprechpartner"""
    sql = "\n-- ============================================================================\n"
    sql += "-- SEED DATA: Kunden-Ansprechpartner\n"
    sql += "-- ============================================================================\n\n"
    
    vornamen = ["Hans", "Peter", "Klaus", "Thomas", "Michael", "Andreas", "Christian", "Wolfgang"]
    nachnamen = ["Müller", "Schmidt", "Meier", "Weber", "Fischer", "Hansen", "Becker", "Wagner"]
    
    for i in range(1, n + 1):
        kunden_nr = f"K{i:05d}"
        # Jeder Kunde hat 1-3 Ansprechpartner
        for j in range(random.randint(1, 3)):
            vorname = random.choice(vornamen)
            nachname = random.choice(nachnamen)
            position = random.choice(POSITIONS)
            telefon = f'+49 441 12{random.randint(1000, 9999)}'
            email_contact = f'{vorname.lower()}.{nachname.lower()}@{kunden_nr.lower()}.de'
            
            sql += f"""INSERT INTO kunden_ansprechpartner (
    kunden_nr, prioritaet, vorname, nachname, position,
    telefon1, email, anrede,
    erstellt_am
) VALUES (
    '{kunden_nr}',
    {j},
    '{vorname}',
    '{nachname}',
    '{position}',
    '{telefon}',
    '{email_contact}',
    'Herr',
    CURRENT_TIMESTAMP
);

"""
    
    return sql

def generate_sql():
    """Generiert vollständiges Seed-Daten SQL"""
    sql = """-- ============================================================================
-- SEED DATA: Kundenstamm - Testdaten
-- Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
-- Total Records: ~50
-- ============================================================================

"""
    
    # Haupttabellen
    sql += generate_kunden_sql(10)
    sql += generate_kunden_profil_sql(10)
    sql += generate_kunden_ansprechpartner_sql(10)
    
    return sql

if __name__ == "__main__":
    sql_output = generate_sql()
    
    output_file = "schemas/sql/kundenstamm_seed_data.sql"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_output)
    
    print("=" * 80)
    print("✅ SEED-DATEN GENERATOR ABGESCHLOSSEN")
    print("=" * 80)
    print(f"\n📄 Datei erstellt: {output_file}")
    print(f"📊 Datensätze: ~50 Records")
    print(f"\n🎯 Nächste Schritte:")
    print(f"   1. In PostgreSQL importieren:")
    print(f"      Get-Content {output_file} | docker exec -i valeo-staging-postgres psql -U valeo_staging -d valeo_neuro_erp_staging")
    print(f"   2. Frontend-Seiten erstellen")
    print(f"   3. API-Endpoints implementieren")
