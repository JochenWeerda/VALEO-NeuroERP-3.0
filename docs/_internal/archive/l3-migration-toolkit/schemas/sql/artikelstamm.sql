-- L3-Migration: Artikel-Stammdaten
CREATE TABLE IF NOT EXISTS artikelstamm (
    id SERIAL PRIMARY KEY,
    artikel_nr INTEGER NOT NULL UNIQUE,
    kurztext VARCHAR(50) NULL ,
    artikel_gruppe_id INTEGER NULL ,
    bezeichnung VARCHAR(255) NOT NULL ,
    beschreibung TEXT NULL ,
    matchcode_2 VARCHAR(50) NULL ,
    gesperrt BOOLEAN NULL ,
    artikel_art VARCHAR NULL ,
    einheit_id INTEGER NOT NULL ,
    gewicht DECIMAL(12, 3) NULL ,
    hl_gewicht DECIMAL(12, 2) NULL ,
    steuerschluessel_id INTEGER NOT NULL ,
    steuersatz DECIMAL(12, 2) NOT NULL ,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_artikelstamm_artikel_gruppe_id ON artikelstamm(artikel_gruppe_id);
CREATE INDEX idx_artikelstamm_einheit_id ON artikelstamm(einheit_id);