# ✅ Kundenstamm - Finale Konsolidierung

**Datum:** 2025-10-26  
**Status:** ✅ BEREIT FÜR IMPLEMENTATION

## 📊 Vergleichs-Ergebnisse

### Feld-Statistik
- **Bestehende Felder:** 56
- **ChatGPT Felder:** 170
- **Neue Felder:** 144 ✨
- **Fehlende Felder:** 30 ⚠️
- **Gemeinsame Felder:** 26 ✅

### Tab-Statistik
- **Bestehende Tabs:** 10
- **ChatGPT Tabs:** 23
- **Neue Tabs:** 13 ✨

## 🎯 Konsolidierungs-Strategie

### Option A: Single-Table-Approach (NICHT empfohlen)
- Alle Felder in eine `kunden`-Tabelle → **~200 Spalten**
- ❌ Performance-Probleme
- ❌ Unübersichtlich
- ❌ Wartungsprobleme

### Option B: Normalisierte Struktur ✅ EMPFOHLEN

**Haupttabelle:** `kunden` (Kern-Daten)
**Untertabellen:** Separated Concerns

## 📋 Vorgeschlagene Tabellen-Struktur

### 1. `kunden` (Haupttabelle) - 60 Felder
```sql
-- Bestehende Struktur beibehalten
-- Basis-Daten: Name, Adresse, Kontakt
```

### 2. `kunden_profil` - 13 Felder
```sql
CREATE TABLE kunden_profil (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr),
    firmenname VARCHAR(200),
    gruendung DATE,
    jahresumsatz DECIMAL(15,2),
    berufsgenossenschaft VARCHAR(100),
    berufsgen_nr VARCHAR(50),
    branche VARCHAR(100),
    mitbewerber VARCHAR(200),
    engpaesse TEXT,
    organisationsstruktur TEXT,
    mitarbeiteranzahl INTEGER,
    wettbewerbsdifferenzierung TEXT,
    betriebsrat BOOLEAN DEFAULT FALSE,
    unternehmensphilosophie TEXT
);
```

### 3. `kunden_ansprechpartner` ⭐ KRITISCH! - 21 Felder
```sql
CREATE TABLE kunden_ansprechpartner (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr),
    vorname VARCHAR(100),
    nachname VARCHAR(100),
    position VARCHAR(100),
    abteilung VARCHAR(100),
    telefon1 VARCHAR(50),
    telefon2 VARCHAR(50),
    mobil VARCHAR(50),
    email VARCHAR(100),
    strasse VARCHAR(100),
    plz VARCHAR(10),
    ort VARCHAR(100),
    anrede VARCHAR(20),
    briefanrede VARCHAR(50),
    geburtsdatum DATE,
    hobbys TEXT,
    info1 TEXT,
    info2 TEXT,
    empfanger_rechnung_email BOOLEAN DEFAULT FALSE,
    empfanger_mahnung_email BOOLEAN DEFAULT FALSE,
    kontaktart VARCHAR(50),
    erstanlage DATE,
    cad_system VARCHAR(100),
    softwaresysteme VARCHAR(200),
    datenschutzbeauftragter BOOLEAN DEFAULT FALSE,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. `kunden_versand` - 6 Felder
```sql
CREATE TABLE kunden_versand (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr),
    versandart_rechnung VARCHAR(50),
    versandart_mahnung VARCHAR(50),
    versandart_kontakt VARCHAR(50),
    dispo_nummer VARCHAR(50),
    initialisierungsweisung TEXT,
    versandmedium VARCHAR(50) -- Brief/E-Mail/ZUGFeRD
);
```

### 5. `kunden_lieferung_zahlung` - 6 Felder
```sql
CREATE TABLE kunden_lieferung_zahlung (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr),
    lieferbedingung VARCHAR(100),
    zahlungsbedingung VARCHAR(100),
    faelligkeit_ab VARCHAR(50), -- Rechnungsdatum/Termin/Valuta
    pro_forma_rechnung BOOLEAN DEFAULT FALSE,
    pro_forma_rabatt1 DECIMAL(5,2),
    pro_forma_rabatt2 DECIMAL(5,2),
    einzel_sammelversand_avis VARCHAR(50)
);
```

### 6. `kunden_datenschutz` - 4 Felder
```sql
CREATE TABLE kunden_datenschutz (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr),
    einwilligung BOOLEAN DEFAULT FALSE,
    anlagedatum DATE,
    anlagebearbeiter VARCHAR(100),
    zusatzbemerkung TEXT
);
```

### 7. `kunden_genossenschaft` - 8 Felder
```sql
CREATE TABLE kunden_genossenschaft (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr),
    geschaeftsguthaben_konto VARCHAR(50),
    mitgliedschaft_gekuendigt BOOLEAN DEFAULT FALSE,
    kuendigungsgrund TEXT,
    datum_kuendigung DATE,
    datum_austritt DATE,
    mitgliedsnummer VARCHAR(50),
    pflichtanteile INTEGER DEFAULT 0,
    eintrittsdatum DATE
);
```

### 8. `kunden_email_verteiler` - 3 Felder (Mehrfach!)
```sql
CREATE TABLE kunden_email_verteiler (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr),
    verteilername VARCHAR(100),
    bezeichnung VARCHAR(200),
    email VARCHAR(100)
);
```

### 9. `kunden_betriebsgemeinschaften` - 4 Felder (Mehrfach!)
```sql
CREATE TABLE kunden_betriebsgemeinschaften (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr),
    verbundnummer VARCHAR(50),
    mitglieder_kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr),
    anteil_prozent DECIMAL(5,2) CHECK (anteil_prozent >= 0 AND anteil_prozent <= 100)
);
```

### 10. `kunden_freitext` - 3 Felder
```sql
CREATE TABLE kunden_freitext (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr),
    chef_anweisung TEXT,
    langtext TEXT,
    bemerkungen TEXT
);
```

### 11. `kunden_allgemein_erweitert` - 15 Felder
```sql
CREATE TABLE kunden_allgemein_erweitert (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr),
    staat VARCHAR(100),
    bundesland VARCHAR(100),
    kunde_seit DATE,
    debitoren_konto VARCHAR(50),
    deb_kto_hauptkonto VARCHAR(50),
    disponent VARCHAR(100),
    vertriebsbeauftragter VARCHAR(100),
    abc_umsatzstatus VARCHAR(50),
    betriebsnummer VARCHAR(50),
    ust_id_nr VARCHAR(50),
    steuernummer VARCHAR(50),
    sperrgrund TEXT,
    kundengruppe VARCHAR(100),
    fax_sperre BOOLEAN DEFAULT FALSE,
    infofeld4 TEXT,
    infofeld5 TEXT,
    infofeld6 TEXT
);
```

### 12. `kunden_cpd_konto` - 12 Felder
```sql
CREATE TABLE kunden_cpd_konto (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr),
    debitoren_konto VARCHAR(50),
    suchbegriff VARCHAR(100),
    rechnungsadresse TEXT,
    geschaeftsstelle VARCHAR(100),
    kostenstelle VARCHAR(100),
    rechnungsart VARCHAR(50),
    sammelrechnung BOOLEAN DEFAULT FALSE,
    rechnungsformular VARCHAR(100),
    vb VARCHAR(100),
    gebiet VARCHAR(100),
    zahlungsbedingungen TEXT
);
```

### 13. `kunden_rabatte_detail` - 6 Felder (Mehrfach!)
```sql
CREATE TABLE kunden_rabatte_detail (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr),
    artikel_nr VARCHAR(50),
    bezeichnung VARCHAR(200),
    rabatt DECIMAL(5,2),
    rabatt_gueltig_bis DATE,
    rabatt_liste_id INTEGER REFERENCES rabatt_listen(id)
);
```

### 14. `kunden_preise_detail` - 10 Felder (Mehrfach!)
```sql
CREATE TABLE kunden_preise_detail (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr),
    artikel_nr VARCHAR(50),
    bezeichnung VARCHAR(200),
    preis_netto DECIMAL(10,2),
    preis_inkl_fracht DECIMAL(10,2),
    preis_einheit VARCHAR(20),
    rabatt_erlaubt BOOLEAN DEFAULT TRUE,
    sonderfracht DECIMAL(10,2),
    zahlungsbedingung VARCHAR(100),
    gueltig_bis DATE,
    bediener VARCHAR(100)
);
```

## 📊 Finale Statistik

### Tabellen gesamt: 14
- 1 Haupttabelle (`kunden`)
- 13 Untertabellen

### Felder gesamt: ~200
- Haupttabelle: 60 Felder
- Untertabellen: ~140 Felder

### Frontend-Tabs: 23
- Bestehend: 10 Tabs
- Neu: 13 Tabs

## 🚀 Implementierungs-Plan

### Phase 1: SQL-Tabellen erstellen
```bash
psql -U valeo -d valeo_neuro_erp -f schemas/sql/kundenstamm_complete.sql
```

### Phase 2: Mask Builder Schema erweitern
- JSON mit allen 23 Tabs erstellen
- Felder zuordnen
- Relations definieren

### Phase 3: Frontend-Integration
- Tabs im UI hinzufügen
- Untertabellen als Sub-Components
- JOIN-Logik im Backend

## ✅ Nächste Schritte

1. **SQL-Tabellen-Generator erstellen** (`generate-complete-tables.py`)
2. **Mask Builder JSON erweitern** (23 Tabs)
3. **Frontend-Komponenten anpassen**
4. **Migration-Script** für L3 → VALEO

**Bereit für Finalisierung!** 🎯

