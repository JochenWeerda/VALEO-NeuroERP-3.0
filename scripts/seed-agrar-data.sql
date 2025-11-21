-- VALEO NeuroERP - Agrar Seed Data
-- Realistische Testdaten für PSM, Saatgut, Dünger

-- PSM Produkte
INSERT INTO agrar_psm_products (product_name, active_ingredient, product_type, registration_number, manufacturer, approval_status, application_areas, dosage_instructions, safety_interval_days, water_protection_class, bee_hazard) VALUES
('Funguran progress', 'Kupferoxychlorid', 'Fungizid', '006689-00', 'BASF SE', 'active', 'Kartoffel, Wein, Hopfen', '1,5-2,0 kg/ha', 21, 'WG2', 'B4'),
('Karate Zeon', 'Lambda-Cyhalothrin', 'Insektizid', '024139-00', 'Syngenta Agro GmbH', 'active', 'Getreide, Raps, Kartoffel', '75 ml/ha', 35, 'WG2', 'B1'),
('Roundup PowerFlex', 'Glyphosat', 'Herbizid', '024257-00', 'Bayer CropScience', 'active', 'Vor der Saat', '3-4 l/ha', 0, 'WG3', 'B4'),
('Amistar', 'Azoxystrobin', 'Fungizid', '024641-00', 'Syngenta Agro GmbH', 'active', 'Getreide, Kartoffel', '0,8-1,0 l/ha', 35, 'WG2', 'B1'),
('Biscaya', 'Thiacloprid', 'Insektizid', '006249-00', 'Bayer CropScience', 'active', 'Raps, Getreide', '0,3 l/ha', 28, 'WG2', 'B1'),
('Primus', 'Flonicamid', 'Insektizid', '006845-00', 'ISK Biosciences Europe', 'active', 'Kartoffel, Gemüse', '0,2 kg/ha', 21, 'WG2', 'B4'),
('Stomp Aqua', 'Pendimethalin', 'Herbizid', '024436-00', 'BASF SE', 'active', 'Wintergetreide, Mais', '3,3 l/ha', 0, 'WG2', 'B4'),
('Acanto', 'Picoxystrobin', 'Fungizid', '024592-00', 'DuPont de Nemours', 'active', 'Getreide', '0,75-1,0 l/ha', 35, 'WG2', 'B1'),
('Boxer', 'Prosulfocarb', 'Herbizid', '006512-00', 'Syngenta Agro GmbH', 'active', 'Winterweizen, Wintergerste', '4,0 l/ha', 0, 'WG2', 'B4'),
('Folicur', 'Tebuconazol', 'Fungizid', '005457-00', 'Bayer CropScience', 'active', 'Getreide', '1,0-1,5 l/ha', 35, 'WG2', 'B4'),
('Teppeki', 'Flonicamid', 'Insektizid', '024760-00', 'ISK Biosciences Europe', 'active', 'Gemüse, Kartoffel', '0,14 kg/ha', 14, 'WG2', 'B4'),
('Spectrum', 'Dimethenamid-P', 'Herbizid', '006856-00', 'BASF SE', 'active', 'Mais', '1,4 l/ha', 0, 'WG2', 'B4');

-- Saatgut
INSERT INTO agrar_saatgut (product_name, crop_type, variety, certification, tkm, germination_rate, producer, batch_number, packaging_unit, price_per_unit, stock_quantity, harvest_year) VALUES
('Winterweizen Elixer', 'Weizen', 'Elixer', 'Z-Saatgut', 48.5, 95.0, 'KWS Saat SE', 'WW23-45678', '25 kg Sack', 42.50, 2500.0, 2023),
('Wintergerste KWS Higgins', 'Gerste', 'KWS Higgins', 'Z-Saatgut', 52.0, 96.0, 'KWS Saat SE', 'WG23-12345', '25 kg Sack', 38.90, 1800.0, 2023),
('Mais LG 31.218', 'Mais', 'LG 31.218', 'Z-Saatgut', 320.0, 98.0, 'Limagrain GmbH', 'M23-98765', '50.000 Korn', 185.00, 500.0, 2023),
('Raps Architekt', 'Raps', 'Architekt', 'Z-Saatgut', 5.2, 92.0, 'NPZ Lembke', 'R23-55555', '1,5 Mio Korn', 145.00, 350.0, 2023),
('Sommergerste RGT Planet', 'Gerste', 'RGT Planet', 'Z-Saatgut', 49.0, 95.0, 'RAGT Saaten', 'SG23-77777', '25 kg Sack', 36.00, 1200.0, 2023),
('Kartoffel Belana', 'Kartoffel', 'Belana', 'Pflanzgut', 0.0, 0.0, 'Europlant', 'K23-33333', '25 kg Sack', 52.00, 3000.0, 2023),
('Zuckerrübe Conviso', 'Zuckerrübe', 'Conviso Smart', 'Pilliert', 0.0, 98.0, 'KWS Saat SE', 'ZR23-88888', '150.000 Korn', 320.00, 180.0, 2023),
('Triticale Tulus', 'Triticale', 'Tulus', 'Z-Saatgut', 55.0, 94.0, 'Saaten Union', 'T23-44444', '25 kg Sack', 35.50, 800.0, 2023),
('Dinkel Badenkrone', 'Dinkel', 'Badenkrone', 'Z-Saatgut', 42.0, 93.0, 'Saaten Union', 'D23-66666', '25 kg Sack', 48.00, 600.0, 2023),
('Hafer Poseidon', 'Hafer', 'Poseidon', 'Z-Saatgut', 38.0, 95.0, 'Nordsaat', 'H23-11111', '25 kg Sack', 32.00, 500.0, 2023);

-- Düngemittel
INSERT INTO agrar_duengemittel (product_name, type, composition, n_content, p_content, k_content, mg_content, s_content, organic_matter, manufacturer, packaging_unit, price_per_unit, stock_quantity) VALUES
('SSA 26+13', 'Mineralisch', 'Schwefelsaures Ammoniak', 26.0, 0.0, 0.0, 0.0, 13.0, 0.0, 'SKW Stickstoffwerke', '500 kg BigBag', 285.00, 15000.0),
('DAP 18-46', 'Mineralisch', 'Diammonphosphat', 18.0, 46.0, 0.0, 0.0, 0.0, 0.0, 'EuroChem Agro', '500 kg BigBag', 395.00, 12000.0),
('NPK 15-15-15', 'Mineralisch', 'Mehrnährstoff', 15.0, 15.0, 15.0, 0.0, 0.0, 0.0, 'Yara GmbH', '500 kg BigBag', 320.00, 18000.0),
('KAS 27', 'Mineralisch', 'Kalkammonsalpeter', 27.0, 0.0, 0.0, 0.0, 0.0, 0.0, 'Yara GmbH', '500 kg BigBag', 265.00, 25000.0),
('Kali 60', 'Mineralisch', 'Kaliumchlorid', 0.0, 0.0, 60.0, 0.0, 0.0, 0.0, 'K+S Minerals', '500 kg BigBag', 245.00, 20000.0),
('Harnstoff 46', 'Mineralisch', 'Carbamid', 46.0, 0.0, 0.0, 0.0, 0.0, 0.0, 'SKW Stickstoffwerke', '500 kg BigBag', 305.00, 22000.0),
('PK 0-20-30', 'Mineralisch', 'Phosphat-Kali', 0.0, 20.0, 30.0, 0.0, 0.0, 0.0, 'EuroChem Agro', '500 kg BigBag', 310.00, 8000.0),
('Bittersalz 16', 'Mineralisch', 'Magnesiumsulfat', 0.0, 0.0, 0.0, 16.0, 13.0, 0.0, 'K+S Minerals', '25 kg Sack', 18.50, 5000.0),
('Kalkstickstoff', 'Mineralisch', 'Calciumcyanamid', 19.8, 0.0, 0.0, 0.0, 0.0, 0.0, 'AlzChem AG', '500 kg BigBag', 295.00, 6000.0),
('Organischer NPK 5-3-2', 'Organisch', 'Hornmehl-Basis', 5.0, 3.0, 2.0, 0.0, 0.0, 75.0, 'Biofa AG', '25 kg Sack', 45.00, 3500.0);

-- Statusmeldung
SELECT '✅ Agrar Seed-Daten erfolgreich eingefügt:' AS status;
SELECT COUNT(*) AS psm_products FROM agrar_psm_products;
SELECT COUNT(*) AS saatgut FROM agrar_saatgut;
SELECT COUNT(*) AS duengemittel FROM agrar_duengemittel;

