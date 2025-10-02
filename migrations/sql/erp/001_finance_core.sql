BEGIN;

CREATE SCHEMA IF NOT EXISTS finanz;

CREATE TABLE IF NOT EXISTS finanz.konten (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kontonummer VARCHAR(20) UNIQUE NOT NULL,
    kontobezeichnung VARCHAR(255) NOT NULL,
    kontotyp VARCHAR(50) NOT NULL CHECK (kontotyp IN ('Aktiv', 'Passiv', 'Ertrag', 'Aufwand')),
    kontenklasse VARCHAR(10),
    kontengruppe VARCHAR(50),
    ist_aktiv BOOLEAN DEFAULT true,
    ist_steuerpflichtig BOOLEAN DEFAULT false,
    steuersatz DECIMAL(5,2),
    beschreibung TEXT,
    erstellt_von UUID,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS finanz.bankkonten (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kontoname VARCHAR(100) NOT NULL,
    bankname VARCHAR(100) NOT NULL,
    iban VARCHAR(34),
    bic VARCHAR(11),
    kontonummer VARCHAR(50),
    blz VARCHAR(10),
    waehrung VARCHAR(3) DEFAULT 'EUR',
    kontostand DECIMAL(15,2) DEFAULT 0,
    letzter_abgleich DATE,
    ist_aktiv BOOLEAN DEFAULT true,
    notizen TEXT,
    erstellt_von UUID,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS finanz.debitoren (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kunden_id UUID,
    debitor_nr VARCHAR(20) UNIQUE NOT NULL,
    kreditlimit DECIMAL(15,2) DEFAULT 0,
    zahlungsziel INTEGER DEFAULT 30,
    zahlungsart VARCHAR(50),
    bankverbindung TEXT,
    steuernummer VARCHAR(50),
    ust_id VARCHAR(50),
    ist_aktiv BOOLEAN DEFAULT true,
    notizen TEXT,
    erstellt_von UUID,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS finanz.kreditoren (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lieferanten_id UUID,
    kreditor_nr VARCHAR(20) UNIQUE NOT NULL,
    kreditlimit DECIMAL(15,2) DEFAULT 0,
    zahlungsziel INTEGER DEFAULT 30,
    zahlungsbedingungen TEXT,
    bankverbindung TEXT,
    steuer_id VARCHAR(50),
    ist_aktiv BOOLEAN DEFAULT true,
    notizen TEXT,
    erstellt_von UUID,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS finanz.buchungen (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    buchungsnummer VARCHAR(50) UNIQUE NOT NULL,
    buchungsdatum DATE NOT NULL,
    belegdatum DATE NOT NULL,
    belegnummer VARCHAR(50),
    buchungstext TEXT NOT NULL,
    sollkonto UUID REFERENCES finanz.konten(id),
    habenkonto UUID REFERENCES finanz.konten(id),
    betrag DECIMAL(15,2) NOT NULL,
    waehrung VARCHAR(3) DEFAULT 'EUR',
    steuerbetrag DECIMAL(15,2) DEFAULT 0,
    steuersatz DECIMAL(5,2) DEFAULT 0,
    buchungsart VARCHAR(50),
    referenz_typ VARCHAR(50),
    referenz_id UUID,
    ist_storniert BOOLEAN DEFAULT false,
    storno_buchung_id UUID REFERENCES finanz.buchungen(id),
    erstellt_von UUID,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMIT;