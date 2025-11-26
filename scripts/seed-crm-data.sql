-- CRM Seed Data - 10+ realistische Datensätze

-- 12 Contacts
INSERT INTO crm_contacts (id, name, company, email, phone, type, address_street, address_zip, address_city, address_country, notes, tenant_id) VALUES
('c1', 'Max Mustermann', 'Mustermann Agrar GmbH', 'max.mustermann@mustermann-agrar.de', '+49 171 1234567', 'customer', 'Hauptstraße 123', '48143', 'Münster', 'Deutschland', 'Hauptkontakt für Agrargeschäft, spezialisiert auf Getreidehandel', 'default'),
('c2', 'Anna Schmidt', 'Schmidt Landwirtschaft', 'anna@schmidt-land.de', '+49 152 9876543', 'customer', 'Dorfstraße 45', '49074', 'Osnabrück', 'Deutschland', 'Bio-Betrieb, Schwerpunkt Kartoffeln und Gemüse', 'default'),
('c3', 'Thomas Weber', 'Weber Agrar Service', 'thomas.weber@weber-agrar.com', '+49 175 5551234', 'customer', 'Landweg 78', '48356', 'Nordwalde', 'Deutschland', 'Lohnunternehmen, regelmäßige Großbestellungen PSM', 'default'),
('c4', 'Julia Meier', 'Saatgut Nord GmbH', 'j.meier@saatgut-nord.de', '+49 40 123456', 'supplier', 'Hafenstraße 12', '20359', 'Hamburg', 'Deutschland', 'Lieferant für Saatgut, Sonderkondition 3% Skonto', 'default'),
('c5', 'Klaus Bauer', 'Bauer Hof GmbH & Co. KG', 'klaus@bauer-hof.de', '+49 2501 778899', 'customer', 'Hofweg 5', '48167', 'Havixbeck', 'Deutschland', 'Großkunde, 250ha Ackerfläche, Weizen & Mais', 'default'),
('c6', 'Petra Hoffmann', 'Düngemittel AG', 'p.hoffmann@duengemittel-ag.de', '+49 221 334455', 'supplier', 'Industriestraße 88', '50668', 'Köln', 'Deutschland', 'Hauptlieferant Düngemittel, Zahlungsziel 30 Tage', 'default'),
('c7', 'Michael Krüger', 'Krüger Landmaschinen', 'm.krueger@landmaschinen-krueger.de', '+49 5242 667788', 'supplier', 'Technikpark 3', '33378', 'Rheda-Wiedenbrück', 'Deutschland', 'Lieferant Ersatzteile & Technik, Service-Vertrag aktiv', 'default'),
('c8', 'Sandra Fischer', 'Fischer Gemüsebau', 'sandra@fischer-gemuese.de', '+49 251 445566', 'customer', 'Feldweg 22', '48163', 'Münster', 'Deutschland', 'Gemüsebau-Spezialist, Gewächshäuser, benötigt Sonderdünger', 'default'),
('c9', 'Frank Schulz', 'Schulz Viehzucht', 'f.schulz@schulz-vieh.de', '+49 5971 889900', 'customer', 'Stallweg 11', '48720', 'Rosendahl', 'Deutschland', 'Schweinezucht, 800 Tiere, Futtermittel-Großabnehmer', 'default'),
('c10', 'Monika Braun', 'BIO Hof Braun', 'monika@biohof-braun.de', '+49 2591 123789', 'customer', 'Ökoweg 7', '48653', 'Coesfeld', 'Deutschland', 'Bio-zertifiziert, nur organische Düngemittel, 80ha', 'default'),
('c11', 'Jürgen Vogel', 'Vogel Pflanzenschutz GmbH', 'j.vogel@vogel-psm.de', '+49 521 556677', 'supplier', 'Chemiepark 15', '33609', 'Bielefeld', 'Deutschland', 'PSM-Lieferant, BVL-zertifiziert, breites Sortiment', 'default'),
('c12', 'Sabine Klein', 'Klein & Partner Agrarberatung', 'klein@agrar-beratung.de', '+49 251 778899', 'customer', 'Beratungsplatz 2', '48149', 'Münster', 'Deutschland', 'Agrarberatung, vermittelt Kunden, Partner-Rabatt 5%', 'default');

-- 5 Leads
INSERT INTO crm_leads (id, company, contact_person, email, phone, source, potential, priority, status, assigned_to, expected_close_date, notes, tenant_id) VALUES
('l1', 'Neuland Agrar e.K.', 'Stefan Neumann', 's.neumann@neuland-agrar.de', '+49 2502 445566', 'Website-Anfrage', 25000, 'high', 'qualified', 'Vertrieb Nord', CURRENT_TIMESTAMP + INTERVAL '14 days', 'Interessiert an Komplett-Paket Saatgut + Dünger für 150ha', 'default'),
('l2', 'Grünland Pflegedienst', 'Andrea Grün', 'info@gruenland-pflege.de', '+49 5971 334455', 'Messe Agritechnica', 8000, 'medium', 'new', 'Vertrieb Süd', CURRENT_TIMESTAMP + INTERVAL '30 days', 'Kleiner Betrieb, Erstgespräch geplant', 'default'),
('l3', 'Hofgut Sonnenschein', 'Familie Sonnenberg', 'kontakt@hofgut-sonnenschein.de', '+49 2541 667788', 'Empfehlung Kunde', 15000, 'high', 'qualified', 'Vertrieb West', CURRENT_TIMESTAMP + INTERVAL '7 days', 'Umstellung auf Bio, braucht Beratung & Erstausstattung', 'default'),
('l4', 'Tierhaltung Westfalen GmbH', 'Dr. Werner Wolf', 'w.wolf@tierhaltung-west.de', '+49 2381 998877', 'Kaltakquise', 40000, 'high', 'new', 'Vertrieb Nord', CURRENT_TIMESTAMP + INTERVAL '45 days', 'Großbetrieb Schweine & Rinder, Futtermittel-Bedarf hoch', 'default'),
('l5', 'Obstbau Meyer', 'Lisa Meyer', 'l.meyer@obstbau-meyer.de', '+49 2572 112233', 'Google Ads', 5000, 'low', 'new', 'Vertrieb Ost', CURRENT_TIMESTAMP + INTERVAL '60 days', 'Obstplantage 20ha, saisonale Bestellung PSM', 'default');

-- 5 Activities
INSERT INTO crm_activities (id, contact_id, type, date, subject, notes, status, created_by, tenant_id) VALUES
('a1', 'c1', 'call', CURRENT_TIMESTAMP - INTERVAL '2 days', 'Erstkontakt Getreidehandel', 'Telefonat geführt, Interesse an Weizenverkauf, Termin vereinbart', 'completed', 'user1', 'default'),
('a2', 'c1', 'meeting', CURRENT_TIMESTAMP + INTERVAL '5 days', 'Präsentation Produktportfolio', 'Termin: 10 Uhr, Besprechungsraum 2, Muster mitbringen', 'planned', 'user1', 'default'),
('a3', 'c2', 'email', CURRENT_TIMESTAMP - INTERVAL '1 day', 'Angebot Bio-Saatgut versendet', 'Angebot ANG-2025-045 per E-Mail, Rückmeldung bis 20.10.', 'completed', 'user2', 'default'),
('a4', 'c3', 'visit', CURRENT_TIMESTAMP - INTERVAL '7 days', 'Hofbesichtigung & Bedarfsanalyse', 'Vor-Ort-Termin, Flächen begutachtet, PSM-Bedarf ermittelt', 'completed', 'user1', 'default'),
('a5', 'c3', 'call', CURRENT_TIMESTAMP + INTERVAL '3 days', 'Follow-up Angebot', 'Nachfassen zu Angebot, Preisverhandlung möglich', 'planned', 'user1', 'default');

-- 5 Betriebsprofile
INSERT INTO crm_betriebsprofile (id, name, betriebsform, flaeche_ha, tierbestand, contact_id, notes, tenant_id) VALUES
('b1', 'Mustermann Agrar Betriebsprofil', 'Ackerbau', 250, 0, 'c1', 'Weizen, Gerste, Raps, 3-Frucht-Folge, moderne Technik', 'default'),
('b2', 'Schmidt Bio-Betrieb', 'Gemüsebau (Bio)', 35, 15, 'c2', 'Demeter-zertifiziert, Kartoffeln, Möhren, Hühner', 'default'),
('b3', 'Weber Lohnunternehmen', 'Dienstleistung', 0, 0, 'c3', 'Maschinenpark: 3 Mähdrescher, 2 Traktoren, GPS-gesteuert', 'default'),
('b4', 'Bauer Hof Großbetrieb', 'Ackerbau & Viehzucht', 250, 120, 'c5', 'Milchkühe 80 Stück, Bullenmast 40, Weizen & Mais Anbau', 'default'),
('b5', 'Sonnenfeld Ökohof', 'Ackerbau (Bio)', 120, 0, NULL, 'Bioland-zertifiziert, Dinkel & Hafer, Direktvermarktung', 'default');

SELECT '✅ CRM Seed-Daten erfolgreich eingefügt:' AS status;
SELECT COUNT(*) AS contacts FROM crm_contacts;
SELECT COUNT(*) AS leads FROM crm_leads;
SELECT COUNT(*) AS activities FROM crm_activities;
SELECT COUNT(*) AS betriebsprofile FROM crm_betriebsprofile;

