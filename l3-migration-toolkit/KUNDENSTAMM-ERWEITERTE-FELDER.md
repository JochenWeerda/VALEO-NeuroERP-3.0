# Kundenstamm - Erweiterte Felder aus Screenshots

**Datum:** 2025-10-26  
**Status:** ✅ Zu ergänzen

## 📋 Neue Kategorien aus ChatGPT-Analyse

Sie haben mir **weitere Felder** aus den L3-Kundenstamm-Screenshots übergeben. Diese müssen zum bestehenden Schema hinzugefügt werden.

### ✅ Bereits implementiert (aus bisheriger Analyse)
- Kunden-Anschrift
- Rechnung/Kontoauszug
- Kundenrabatte
- Preise / Rabatte
- Bank / Zahlungsverkehr
- Wegbeschreibung
- Sonstiges
- Selektionen
- Schnittstelle

### 🔄 Neu zu ergänzen

#### 11. Kundenprofil
```
- Firmenname
- Gründung (Datum)
- Jahresumsatz (Währung)
- Berufsgenossenschaft
- Berufsgen.-Nr.
- Branche (mit Schlüssel)
```

#### 12. Versandinformationen
```
- Versandart Rechnung
- Versandart Mahnung
- Versandart Kontaktzusammenstellung
- Dispo-Nummer
- Initialisierungsweisung
- Versandmedien: Brief/E-Mail (kombinierbar)
- ZUGFeRD Auswahl
```

#### 13. Lieferung/Zahlung – Zahlungsbedingungen
```
- Liefer-Bedingung
- Zahlungsbedingung
- Fälligkeit ab (Rechnungsdatum / Termin / Valuta)
- Pro-Forma-Rechnung ja/nein
- Pro-Forma-Rabatt 1 / 2
- Einzel-/Sammelversand-Avis
- Versand-Avis an Vertreter / Beauftragte
```

#### 14. Datenschutz
```
- Bis (gültig bis)
- Einwilligung
- Anlagedatum
- Anlagebearbeiter
- Zusatzbemerkung
```

#### 15. Genossenschaftsanteile
```
- Geschäftsguthaben-Konto
- Konto-Nr.
- Mitgliedschaft gekündigt (ja/nein)
- Kündigungsgrund
- Datum Kündigung
- Datum Austritt
- Mitglieds-Nr.
- Anzahl Pflichtanteile
- Gekündigte Pflichtanteile
- Datum Eintritt
```

#### 16. E-Mail-Verteiler
```
- Verteiler-Name
- Bezeichnung
- E-Mail-Adresse
```

#### 17. Langtext (Freitextbereich)
```
- Kein explizites Feld, aber Textkomponente für ergänzende Informationen
```

#### 18. Betriebsgemeinschaften
```
- Verb.-Nr. / Bezeichnung
- Mitglieder der Gemeinschaft: Kunden-Nr. und -Name
- Anteil (%)
```

#### 21. Chef-Anweisung
```
- Freitext-Feld oder Anweisungsfenster
```

#### 22. Ansprechpartner (Untertabelle!)
```
- Priorität
- Name / Vorname
- Position / Abteilung
- Telefon 1 / 2 / Mobil
- E-Mail
- Adresse (Straße, PLZ, Ort)
- Anrede / Brief-Anrede
- Geburtsdatum
- Hobbys
- Info 1 / Info 2
- Empfänger Rechnung per Mail
- Empfänger Mahnung per Mail
- Kontaktart
- Erstanlage / Erstanlage von
- CAD-System
- Softwaresysteme
- Datenschutzbeauftragter
```

#### 23. Kundenstammdaten – Erfassung
```
Reiter: Kundenanschrift / Rechnungsanschrift
- Name 1-3
- Straße, Land, PLZ, Ort
- Postf./PLZ/Ort
- Telefon, Telefax
- E-Mail, Homepage
- Anrede / Briefanrede
- Freifelder (1–3)
- Gebiet

Reiter: Allgemein
- Staat
- Bundesland
- Kunde seit
- Debitoren-Konto / Hauptkonto
- Disponent
- VB (Vertriebsbeauftragter)
- ABC/Umsatzstatus
- Betriebs-Nr.
- UST-ID
- Steuer-Nr.
- Sperrgrund
- Kunden-Gruppe
- Fax-Sperre
- Info-Felder 4–6
```

#### 24. Kundenerweiterung / Rechnung & Kontoauszug
```
- Kunden-Gruppe
- Kundentyp: Organ, Konzern-intern
- Kontoauszugsoptionen (Druck, getrennt, Nachdruck etc.)
- Letzte Auszugs-Nr. / Datum
- Saldo
- Druck Werbetext / Versandspesen
- Einzel-/Sammel-Abrechnung
- Verwaltungsgemeinkosten-Aufschlag
- Rechnungsnummernkreis
- Bonusberechtigung
- Selbstabrechner (Verkauf / Zukauf)
- Bemerkenswerte Forderung
- Umsatzsteuer-Optierer
```

#### 25. CPD-Konto anlegen
```
- Kunden-Nr.
- Debitoren-Konto
- Suchbegriff
- Kundenname (1–3)
- Straße
- Land, PLZ, Ort, Postf./Ort
- Telefon 1/2, Telefax
- Anrede, Briefanrede
- E-Mail, Homepage
- Geschäftsstelle
- Kostenstelle
- Rechnungsart
- Sammelrechnung
- Rechnungsformular
- VB
- Gebiet
- Zahlungsbedingungen (Skonto %, Tage, netto)
```

#### 26. Menüstruktur (Hauptnavigation)
```
Diese Felder gehören nicht direkt zur Kundenstamm-Maske,
sondern zur Hauptnavigation/Layout
```

## 🎯 Empfehlung

### Option 1: Haupttabelle erweitern
Alle neuen Felder zur bestehenden `kunden`-Tabelle hinzufügen.

**Vorteile:**
- Einfache Abfragen
- Alle Daten an einem Ort

**Nachteile:**
- Sehr große Tabelle (~150+ Spalten)
- Performance-Probleme möglich

### Option 2: Separate Tabellen (Normalisierung)
```
kunden (Haupttabelle)
├── kunden_profil (FK zu kunden.kunden_nr)
├── kunden_versand (FK zu kunden.kunden_nr)
├── kunden_datenschutz (FK zu kunden.kunden_nr)
├── kunden_genossenschaft (FK zu kunden.kunden_nr)
├── kunden_email_verteiler (FK zu kunden.kunden_nr)
├── kunden_betriebsgemeinschaften (FK zu kunden.kunden_nr)
├── kunden_ansprechpartner (FK zu kunden.kunden_nr) ⭐ WICHTIG!
└── kunden_freitext (FK zu kunden.kunden_nr)
```

**Vorteile:**
- Bessere Performance
- Klarere Struktur
- Einfacher zu erweitern

**Nachteile:**
- Komplexere Abfragen (JOINs)
- Mehr Tabellen

## 📊 Empfohlene Struktur

Ich empfehle **Option 2 (Normalisierung)** mit folgenden separaten Tabellen:

### 1. `kunden_profil`
```sql
CREATE TABLE kunden_profil (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr),
    firmenname VARCHAR(200),
    gruendung DATE,
    jahresumsatz DECIMAL(15,2),
    berufsgenossenschaft VARCHAR(100),
    berufsgen_nr VARCHAR(50),
    branche VARCHAR(100),
    branche_schluessel VARCHAR(20)
);
```

### 2. `kunden_ansprechpartner` ⭐ KRITISCH!
```sql
CREATE TABLE kunden_ansprechpartner (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr),
    prioritaet INTEGER,
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
    brief_anrede VARCHAR(20),
    geburtsdatum DATE,
    hobbys TEXT,
    info1 TEXT,
    info2 TEXT,
    empfanger_rechnung_email BOOLEAN DEFAULT FALSE,
    empfanger_mahnung_email BOOLEAN DEFAULT FALSE,
    kontaktart VARCHAR(50),
    cad_system VARCHAR(100),
    softwaresysteme VARCHAR(200),
    datenschutzbeauftragter BOOLEAN DEFAULT FALSE,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. `kunden_versand`
```sql
CREATE TABLE kunden_versand (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr),
    versandart_rechnung VARCHAR(50),
    versandart_mahnung VARCHAR(50),
    versandart_kontakt VARCHAR(50),
    dispo_nummer VARCHAR(50),
    initialisierungsweisung TEXT,
    versandmedien_brief BOOLEAN DEFAULT TRUE,
    versandmedien_email BOOLEAN DEFAULT FALSE,
    zugferd_auswahl VARCHAR(50)
);
```

### 4. `kunden_datenschutz`
```sql
CREATE TABLE kunden_datenschutz (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr),
    gueltig_bis DATE,
    einwilligung BOOLEAN DEFAULT FALSE,
    anlagedatum DATE,
    anlagebearbeiter VARCHAR(100),
    zusatzbemerkung TEXT
);
```

### 5. `kunden_genossenschaft`
```sql
CREATE TABLE kunden_genossenschaft (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr),
    geschaeftsguthaben_konto VARCHAR(50),
    konto_nr VARCHAR(50),
    mitgliedschaft_gekuendigt BOOLEAN DEFAULT FALSE,
    kuendigungsgrund TEXT,
    datum_kuendigung DATE,
    datum_austritt DATE,
    mitglieds_nr VARCHAR(50),
    anzahl_pflichtanteile INTEGER DEFAULT 0,
    gekuendigte_pflichtanteile INTEGER DEFAULT 0,
    datum_eintritt DATE
);
```

### 6. `kunden_email_verteiler`
```sql
CREATE TABLE kunden_email_verteiler (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr),
    verteiler_name VARCHAR(100),
    bezeichnung VARCHAR(200),
    email VARCHAR(100)
);
```

### 7. `kunden_betriebsgemeinschaften`
```sql
CREATE TABLE kunden_betriebsgemeinschaften (
    id SERIAL PRIMARY KEY,
    kunden_nr VARCHAR(20) REFERENCES kunden(kunden_nr),
    verb_nr VARCHAR(50),
    bezeichnung VARCHAR(200),
    anteil DECIMAL(5,2) CHECK (anteil >= 0 AND anteil <= 100)
);
```

### 8. `kunden_freitext`
```sql
CREATE TABLE kunden_freitext (
    kunden_nr VARCHAR(20) PRIMARY KEY REFERENCES kunden(kunden_nr),
    chef_anweisung TEXT,
    langtext TEXT,
    bemerkungen TEXT
);
```

## 📈 Gesamtübersicht

### Bestehende Felder
- **60 Felder** in Haupttabelle `kunden`
- **10 Tabs** im Frontend

### Neue Felder
- **~50 Felder** in separaten Tabellen
- **~8 neue Tabs** im Frontend

### Gesamt
- **~110 Felder** insgesamt
- **~18 Tabs** im Frontend

## 🚀 Nächste Schritte

1. ✅ **Bestehendes Schema beibehalten** (`kunden`-Tabelle)
2. ✅ **Separate Tabellen erstellen** für neue Felder
3. ✅ **Tabs im Frontend erweitern**
4. ✅ **Relations definieren** (JOINs)
5. ✅ **Migration-Script erstellen**

**Soll ich die vollständigen SQL-CREATE-Statements für alle neuen Tabellen erstellen?**

