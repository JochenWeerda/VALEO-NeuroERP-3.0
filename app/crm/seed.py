"""
CRM Seed Data - Realistische Testdaten (10+ pro Entität)
"""

import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from . import models


def seed_crm_data(db: Session, tenant_id: str = "default"):
    """Seed CRM tables with realistic data"""
    
    # 10+ Contacts (Kunden & Lieferanten)
    contacts_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Max Mustermann",
            "company": "Mustermann Agrar GmbH",
            "email": "max.mustermann@mustermann-agrar.de",
            "phone": "+49 171 1234567",
            "type": models.ContactType.CUSTOMER,
            "address_street": "Hauptstraße 123",
            "address_zip": "48143",
            "address_city": "Münster",
            "address_country": "Deutschland",
            "notes": "Hauptkontakt für Agrargeschäft, spezialisiert auf Getreidehandel",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Anna Schmidt",
            "company": "Schmidt Landwirtschaft",
            "email": "anna@schmidt-land.de",
            "phone": "+49 152 9876543",
            "type": models.ContactType.CUSTOMER,
            "address_street": "Dorfstraße 45",
            "address_zip": "49074",
            "address_city": "Osnabrück",
            "address_country": "Deutschland",
            "notes": "Bio-Betrieb, Schwerpunkt Kartoffeln und Gemüse",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Thomas Weber",
            "company": "Weber Agrar Service",
            "email": "thomas.weber@weber-agrar.com",
            "phone": "+49 175 5551234",
            "type": models.ContactType.CUSTOMER,
            "address_street": "Landweg 78",
            "address_zip": "48356",
            "address_city": "Nordwalde",
            "address_country": "Deutschland",
            "notes": "Lohnunternehmen, regelmäßige Großbestellungen PSM",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Julia Meier",
            "company": "Saatgut Nord GmbH",
            "email": "j.meier@saatgut-nord.de",
            "phone": "+49 40 123456",
            "type": models.ContactType.SUPPLIER,
            "address_street": "Hafenstraße 12",
            "address_zip": "20359",
            "address_city": "Hamburg",
            "address_country": "Deutschland",
            "notes": "Lieferant für Saatgut, Sonderkondition 3% Skonto",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Klaus Bauer",
            "company": "Bauer Hof GmbH & Co. KG",
            "email": "klaus@bauer-hof.de",
            "phone": "+49 2501 778899",
            "type": models.ContactType.CUSTOMER,
            "address_street": "Hofweg 5",
            "address_zip": "48167",
            "address_city": "Havixbeck",
            "address_country": "Deutschland",
            "notes": "Großkunde, 250ha Ackerfläche, Weizen & Mais",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Petra Hoffmann",
            "company": "Düngemittel AG",
            "email": "p.hoffmann@duengemittel-ag.de",
            "phone": "+49 221 334455",
            "type": models.ContactType.SUPPLIER,
            "address_street": "Industriestraße 88",
            "address_zip": "50668",
            "address_city": "Köln",
            "address_country": "Deutschland",
            "notes": "Hauptlieferant Düngemittel, Zahlungsziel 30 Tage",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Michael Krüger",
            "company": "Krüger Landmaschinen",
            "email": "m.krueger@landmaschinen-krueger.de",
            "phone": "+49 5242 667788",
            "type": models.ContactType.SUPPLIER,
            "address_street": "Technikpark 3",
            "address_zip": "33378",
            "address_city": "Rheda-Wiedenbrück",
            "address_country": "Deutschland",
            "notes": "Lieferant Ersatzteile & Technik, Service-Vertrag aktiv",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Sandra Fischer",
            "company": "Fischer Gemüsebau",
            "email": "sandra@fischer-gemuese.de",
            "phone": "+49 251 445566",
            "type": models.ContactType.CUSTOMER,
            "address_street": "Feldweg 22",
            "address_zip": "48163",
            "address_city": "Münster",
            "address_country": "Deutschland",
            "notes": "Gemüsebau-Spezialist, Gewächshäuser, benötigt Sonderdünger",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Frank Schulz",
            "company": "Schulz Viehzucht",
            "email": "f.schulz@schulz-vieh.de",
            "phone": "+49 5971 889900",
            "type": models.ContactType.CUSTOMER,
            "address_street": "Stallweg 11",
            "address_zip": "48720",
            "address_city": "Rosendahl",
            "address_country": "Deutschland",
            "notes": "Schweinezucht, 800 Tiere, Futtermittel-Großabnehmer",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Monika Braun",
            "company": "BIO Hof Braun",
            "email": "monika@biohof-braun.de",
            "phone": "+49 2591 123789",
            "type": models.ContactType.CUSTOMER,
            "address_street": "Ökoweg 7",
            "address_zip": "48653",
            "address_city": "Coesfeld",
            "address_country": "Deutschland",
            "notes": "Bio-zertifiziert, nur organische Düngemittel, 80ha",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Jürgen Vogel",
            "company": "Vogel Pflanzenschutz GmbH",
            "email": "j.vogel@vogel-psm.de",
            "phone": "+49 521 556677",
            "type": models.ContactType.SUPPLIER,
            "address_street": "Chemiepark 15",
            "address_zip": "33609",
            "address_city": "Bielefeld",
            "address_country": "Deutschland",
            "notes": "PSM-Lieferant, BVL-zertifiziert, breites Sortiment",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Sabine Klein",
            "company": "Klein & Partner Agrarberatung",
            "email": "klein@agrar-beratung.de",
            "phone": "+49 251 778899",
            "type": models.ContactType.CUSTOMER,
            "address_street": "Beratungsplatz 2",
            "address_zip": "48149",
            "address_city": "Münster",
            "address_country": "Deutschland",
            "notes": "Agrarberatung, vermittelt Kunden, Partner-Rabatt 5%",
            "tenant_id": tenant_id
        },
    ]
    
    for contact_data in contacts_data:
        contact = models.Contact(**contact_data)
        db.add(contact)
    
    # 10+ Leads
    leads_data = [
        {
            "id": str(uuid.uuid4()),
            "company": "Neuland Agrar e.K.",
            "contact_person": "Stefan Neumann",
            "email": "s.neumann@neuland-agrar.de",
            "phone": "+49 2502 445566",
            "source": "Website-Anfrage",
            "potential": 25000,
            "priority": models.LeadPriority.HIGH,
            "status": models.LeadStatus.QUALIFIED,
            "assigned_to": "Vertrieb Nord",
            "expected_close_date": datetime.now() + timedelta(days=14),
            "notes": "Interessiert an Komplett-Paket Saatgut + Dünger für 150ha",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "company": "Grünland Pflegedienst",
            "contact_person": "Andrea Grün",
            "email": "info@gruenland-pflege.de",
            "phone": "+49 5971 334455",
            "source": "Messe Agritechnica",
            "potential": 8000,
            "priority": models.LeadPriority.MEDIUM,
            "status": models.LeadStatus.NEW,
            "assigned_to": "Vertrieb Süd",
            "expected_close_date": datetime.now() + timedelta(days=30),
            "notes": "Kleiner Betrieb, Erstgespräch geplant",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "company": "Hofgut Sonnenschein",
            "contact_person": "Familie Sonnenberg",
            "email": "kontakt@hofgut-sonnenschein.de",
            "phone": "+49 2541 667788",
            "source": "Empfehlung Kunde",
            "potential": 15000,
            "priority": models.LeadPriority.HIGH,
            "status": models.LeadStatus.QUALIFIED,
            "assigned_to": "Vertrieb West",
            "expected_close_date": datetime.now() + timedelta(days=7),
            "notes": "Umstellung auf Bio, braucht Beratung & Erstausstattung",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "company": "Tierhaltung Westfalen GmbH",
            "contact_person": "Dr. Werner Wolf",
            "email": "w.wolf@tierhaltung-west.de",
            "phone": "+49 2381 998877",
            "source": "Kaltakquise",
            "potential": 40000,
            "priority": models.LeadPriority.HIGH,
            "status": models.LeadStatus.NEW,
            "assigned_to": "Vertrieb Nord",
            "expected_close_date": datetime.now() + timedelta(days=45),
            "notes": "Großbetrieb Schweine & Rinder, Futtermittel-Bedarf hoch",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "company": "Obstbau Meyer",
            "contact_person": "Lisa Meyer",
            "email": "l.meyer@obstbau-meyer.de",
            "phone": "+49 2572 112233",
            "source": "Google Ads",
            "potential": 5000,
            "priority": models.LeadPriority.LOW,
            "status": models.LeadStatus.NEW,
            "assigned_to": "Vertrieb Ost",
            "expected_close_date": datetime.now() + timedelta(days=60),
            "notes": "Obstplantage 20ha, saisonale Bestellung PSM",
            "tenant_id": tenant_id
        },
    ]
    
    for lead_data in leads_data:
        lead = models.Lead(**lead_data)
        db.add(lead)
    
    # 10+ Activities
    # (Aktivitäten für die ersten 3 Contacts)
    contact_ids = [c["id"] for c in contacts_data]
    
    activities_data = [
        {
            "id": str(uuid.uuid4()),
            "contact_id": contact_ids[0],
            "type": models.ActivityType.CALL,
            "date": datetime.now() - timedelta(days=2),
            "subject": "Erstkontakt Getreidehandel",
            "notes": "Telefonat geführt, Interesse an Weizenverkauf, Termin vereinbart",
            "status": models.ActivityStatus.COMPLETED,
            "created_by": "user1",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "contact_id": contact_ids[0],
            "type": models.ActivityType.MEETING,
            "date": datetime.now() + timedelta(days=5),
            "subject": "Präsentation Produktportfolio",
            "notes": "Termin: 10 Uhr, Besprechungsraum 2, Muster mitbringen",
            "status": models.ActivityStatus.PLANNED,
            "created_by": "user1",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "contact_id": contact_ids[1],
            "type": models.ActivityType.EMAIL,
            "date": datetime.now() - timedelta(days=1),
            "subject": "Angebot Bio-Saatgut versendet",
            "notes": "Angebot ANG-2025-045 per E-Mail, Rückmeldung bis 20.10.",
            "status": models.ActivityStatus.COMPLETED,
            "created_by": "user2",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "contact_id": contact_ids[2],
            "type": models.ActivityType.VISIT,
            "date": datetime.now() - timedelta(days=7),
            "subject": "Hofbesichtigung & Bedarfsanalyse",
            "notes": "Vor-Ort-Termin, Flächen begutachtet, PSM-Bedarf ermittelt",
            "status": models.ActivityStatus.COMPLETED,
            "created_by": "user1",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "contact_id": contact_ids[2],
            "type": models.ActivityType.CALL,
            "date": datetime.now() + timedelta(days=3),
            "subject": "Follow-up Angebot",
            "notes": "Nachfassen zu Angebot, Preisverhandlung möglich",
            "status": models.ActivityStatus.PLANNED,
            "created_by": "user1",
            "tenant_id": tenant_id
        },
    ]
    
    for activity_data in activities_data:
        activity = models.Activity(**activity_data)
        db.add(activity)
    
    # 5+ Betriebsprofile
    betriebsprofile_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Mustermann Agrar Betriebsprofil",
            "betriebsform": "Ackerbau",
            "flaeche_ha": 250,
            "tierbestand": 0,
            "contact_id": contact_ids[0],
            "notes": "Weizen, Gerste, Raps, 3-Frucht-Folge, moderne Technik",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Schmidt Bio-Betrieb",
            "betriebsform": "Gemüsebau (Bio)",
            "flaeche_ha": 35,
            "tierbestand": 15,
            "contact_id": contact_ids[1],
            "notes": "Demeter-zertifiziert, Kartoffeln, Möhren, Hühner",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Weber Lohnunternehmen",
            "betriebsform": "Dienstleistung",
            "flaeche_ha": 0,
            "tierbestand": 0,
            "contact_id": contact_ids[2],
            "notes": "Maschinenpark: 3 Mähdrescher, 2 Traktoren, GPS-gesteuert",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bauer Hof Großbetrieb",
            "betriebsform": "Ackerbau & Viehzucht",
            "flaeche_ha": 250,
            "tierbestand": 120,
            "contact_id": contact_ids[4],
            "notes": "Milchkühe 80 Stück, Bullenmast 40, Weizen & Mais Anbau",
            "tenant_id": tenant_id
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Sonnenfeld Ökohof",
            "betriebsform": "Ackerbau (Bio)",
            "flaeche_ha": 120,
            "tierbestand": 0,
            "notes": "Bioland-zertifiziert, Dinkel & Hafer, Direktvermarktung",
            "tenant_id": tenant_id
        },
    ]
    
    for profil_data in betriebsprofile_data:
        profil = models.BetriebsProfil(**profil_data)
        db.add(profil)
    
    db.commit()
    
    print(f"✅ CRM Seed-Daten erstellt:")
    print(f"   - {len(contacts_data)} Kontakte")
    print(f"   - {len(leads_data)} Leads")
    print(f"   - {len(activities_data)} Aktivitäten")
    print(f"   - {len(betriebsprofile_data)} Betriebsprofile")

