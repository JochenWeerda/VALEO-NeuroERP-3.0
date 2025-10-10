# VALEO NeuroERP 3.0 - Landhandel-Masken-Katalog

**Branche:** Landhandel & Agrar-Großhandel  
**Version:** 3.0.0  
**Datum:** 2024-10-10  
**Anzahl Masken:** 182

---

## 📊 ÜBERSICHT

| Modul | Anzahl Masken | Status | SAP Fiori Pattern |
|-------|---------------|---------|-------------------|
| **Agrarprodukte** | 28 | ⏳ Zu implementieren | ListReport, ObjectPage, Wizard |
| **Futtermittel** | 22 | ⏳ Zu implementieren | ListReport, ObjectPage |
| **Chargenverwaltung** | 18 | ⏳ Zu implementieren | ObjectPage, Worklist |
| **Waagen & Annahme** | 12 | ⏳ Zu implementieren | Wizard, ObjectPage |
| **Lager & Logistik** | 24 | ⏳ Zu implementieren | ListReport, OverviewPage |
| **Einkauf** | 16 | ⏳ Zu implementieren | ListReport, Wizard |
| **Verkauf** | 18 | ⏳ Zu implementieren | ListReport, ObjectPage |
| **Finanzen** | 14 | ⏳ Zu implementieren | ListReport, OverviewPage |
| **CRM** | 12 | ⏳ Zu implementieren | ListReport, ObjectPage |
| **Compliance & QS** | 14 | ⏳ Zu implementieren | Worklist, ObjectPage |
| **Administration** | 10 | ⏳ Zu implementieren | ListReport, Wizard |
| **Reports & Analytics** | 14 | ⏳ Zu implementieren | OverviewPage |
| **GESAMT** | **182** | - | - |

---

## 🌾 MODUL 1: AGRARPRODUKTE (28 Masken)

### 1.1 Saatgut (8 Masken)

#### 1.1.1 `agrar-saatgut-stamm` - Saatgutstammdaten
- **Pattern:** ObjectPage
- **Sections:**
  - Allgemein (Sorte, Art, Züchter)
  - Zulassung (BSA, EU-Sortenzulassung)
  - Agronomie (TKM, Keimfähigkeit, Aussaatstärke)
  - Preise & Konditionen
  - Verfügbarkeit & Lager
- **MCP-Intent:** `view-seed-master-data`, `edit-seed-data`

#### 1.1.2 `agrar-saatgut-liste` - Saatgut-Übersicht
- **Pattern:** ListReport
- **Filter:** Art, Sorte, Züchter, Zulassungsjahr, Verfügbarkeit
- **Actions:** Neu, Export, Import, Sortenkatalog drucken
- **MCP-Intent:** `list-seeds`, `search-seeds`

#### 1.1.3 `agrar-saatgut-bestellung` - Saatgut bestellen (Wizard)
- **Pattern:** Wizard (5 Steps)
- **Steps:**
  1. Kulturart wählen
  2. Sorte auswählen
  3. Menge & Einheit
  4. Liefertermin
  5. Bestätigung
- **MCP-Intent:** `order-seed-wizard`

#### 1.1.4 `agrar-saatgut-lizenzen` - Saatgut-Lizenzen
- **Pattern:** ListReport
- **Features:** Lizenzgebühren, Nachbaugebühren, Z-Saatgut
- **MCP-Intent:** `manage-seed-licenses`

#### 1.1.5 `agrar-saatgut-zulassungen` - Zulassungsregister
- **Pattern:** ListReport
- **Features:** BSA-Sortenliste, EU-Sortenkatalog, Wertprüfung
- **MCP-Intent:** `manage-seed-approvals`

#### 1.1.6 `agrar-saatgut-prognose` - Absatzprognose Saatgut
- **Pattern:** OverviewPage
- **KPIs:** Absatz letzte Saison, Prognose aktuelle Saison, Verfügbarkeit
- **MCP-Intent:** `forecast-seed-demand`

#### 1.1.7 `agrar-saatgut-qualität` - Qualitätskontrolle Saatgut
- **Pattern:** Worklist
- **Features:** Keimfähigkeitsprüfung, Sortenechtheit, Fremdbesatz
- **MCP-Intent:** `check-seed-quality`

#### 1.1.8 `agrar-saatgut-sorten-finder` - Sortenfinder (AI)
- **Pattern:** Wizard (AI-gestützt)
- **Features:** Standort, Boden, Klima → Sortenempfehlung
- **MCP-Intent:** `recommend-seed-variety`

---

### 1.2 Düngemittel (7 Masken)

#### 1.2.1 `agrar-duenger-stamm` - Düngemittelstammdaten
- **Pattern:** ObjectPage
- **Sections:**
  - Allgemein (Typ, Hersteller, Zusammensetzung)
  - Inhaltsstoffe (N, P, K, S, Mg, etc.)
  - Zulassungen (DüMV, EU-Zulassung)
  - Lagerung (Gefahrstoff, Wassergefährdung)
  - Anwendung (Dosierung, Zeitpunkt, Kultur)
- **MCP-Intent:** `view-fertilizer-master-data`

#### 1.2.2 `agrar-duenger-liste` - Düngemittel-Übersicht
- **Pattern:** ListReport
- **Filter:** Typ, Hersteller, Nährstoffgehalt, Zulassung
- **Actions:** Neu, Export, Düngeplan erstellen
- **MCP-Intent:** `list-fertilizers`

#### 1.2.3 `agrar-duenger-mischungen` - Düngermischungen
- **Pattern:** Wizard
- **Features:** Rezeptur-Designer, Nährstoffberechnung, Mischanlage-Steuerung
- **MCP-Intent:** `create-fertilizer-blend`

#### 1.2.4 `agrar-duenger-zulassungen` - Düngemittel-Zulassungen
- **Pattern:** ListReport
- **Features:** DüMV-Konformität, Analysezertifikate, CE-Kennzeichnung
- **MCP-Intent:** `manage-fertilizer-approvals`

#### 1.2.5 `agrar-duenger-gefahrstoff` - Gefahrstoff-Management
- **Pattern:** Worklist
- **Features:** Sicherheitsdatenblätter, Betriebsanweisungen, Unterweisung
- **MCP-Intent:** `manage-hazardous-materials`

#### 1.2.6 `agrar-duenger-lagerklassen` - Lagerklassen & Trennung
- **Pattern:** ObjectPage
- **Features:** TRGS 510, Zusammenlagerungsverbote, Lagerbelegung
- **MCP-Intent:** `manage-storage-classes`

#### 1.2.7 `agrar-duenger-rechner` - Düngebedarfsrechner
- **Pattern:** Wizard (AI-gestützt)
- **Features:** Bodenanalyse → Düngeempfehlung, DüV-Konformität
- **MCP-Intent:** `calculate-fertilizer-demand`

---

### 1.3 Pflanzenschutz (PSM) (9 Masken)

#### 1.3.1 `agrar-psm-stamm` - PSM-Stammdaten
- **Pattern:** ObjectPage
- **Sections:**
  - Allgemein (Mittel, Hersteller, Wirkstoff)
  - Zulassung (BVL, Zulassungsnummer, Ablauf)
  - Anwendung (Kulturen, Indikationen, Dosierung)
  - Sicherheit (Wasserschutz, Bienenschutz, Abstand)
  - Auflagen (NT, NW, B, etc.)
- **MCP-Intent:** `view-ppm-master-data`

#### 1.3.2 `agrar-psm-liste` - PSM-Übersicht
- **Pattern:** ListReport
- **Filter:** Kultur, Indikation, Wirkstoff, Zulassung, Verfügbarkeit
- **Actions:** Neu, Export, Zulassungskalender
- **MCP-Intent:** `list-plant-protection`

#### 1.3.3 `agrar-psm-abgabedokumentation` - PSM-Abgabe-Dokumentation
- **Pattern:** ObjectPage
- **Features:** Sachkundenachweis prüfen, Verwendungszweck, Auflagen
- **MCP-Intent:** `document-ppm-sale`

#### 1.3.4 `agrar-psm-sachkunde` - Sachkundenachweis-Verwaltung
- **Pattern:** ListReport
- **Features:** Kundensachkunde, Ablauf-Monitoring, Schulungsnachweise
- **MCP-Intent:** `manage-expertise-certificates`

#### 1.3.5 `agrar-psm-zulassungen` - Zulassungsregister PSM
- **Pattern:** ListReport
- **Features:** BVL-Datenbank-Sync, Zulassungsänderungen, Widerrufe
- **MCP-Intent:** `manage-ppm-approvals`

#### 1.3.6 `agrar-psm-auflagen` - Auflagen-Manager
- **Pattern:** Worklist
- **Features:** NT-Auflagen, NW-Auflagen, Bienenschutz, Abstände
- **MCP-Intent:** `manage-ppm-restrictions`

#### 1.3.7 `agrar-psm-wasserschutz` - Wasserschutzgebiets-Prüfung
- **Pattern:** ObjectPage
- **Features:** Geo-Koordinaten, WSG-Zonen, Zugelassene Mittel
- **MCP-Intent:** `check-water-protection`

#### 1.3.8 `agrar-psm-resistenz` - Resistenz-Management
- **Pattern:** OverviewPage
- **Features:** Wirkstoffgruppen, Resistenzstrategie, Wechselempfehlung
- **MCP-Intent:** `manage-resistance`

#### 1.3.9 `agrar-psm-beratung` - PSM-Beratungs-Tool (AI)
- **Pattern:** Wizard (AI-gestützt)
- **Features:** Schadbilder, Diagnose, Mittelempfehlung, Zulassung prüfen
- **MCP-Intent:** `recommend-plant-protection`

---

### 1.4 Biostimulanzien & Sonstiges (4 Masken)

#### 1.4.1 `agrar-biostimulanzien` - Biostimulanzien-Verwaltung
- **Pattern:** ListReport
- **MCP-Intent:** `manage-biostimulants`

#### 1.4.2 `agrar-kalk` - Kalkverwaltung
- **Pattern:** ObjectPage
- **MCP-Intent:** `manage-lime`

#### 1.4.3 `agrar-substrate` - Substrate & Erden
- **Pattern:** ListReport
- **MCP-Intent:** `manage-substrates`

#### 1.4.4 `agrar-sonderkulturen` - Sonderkulturen-Produkte
- **Pattern:** ListReport
- **Features:** Wein, Gemüse, Obst, Hopfen
- **MCP-Intent:** `manage-specialty-products`

---

## 🐄 MODUL 2: FUTTERMITTEL (22 Masken)

### 2.1 Einzelfuttermittel (6 Masken)

#### 2.1.1 `futter-einzel-stamm` - Einzelfuttermittelstamm
- **Pattern:** ObjectPage
- **Sections:**
  - Allgemein (Art, Herkunft, Lieferant)
  - Nährwerte (Energie, Protein, Faser, etc.)
  - QS-Attribute (GVO, VLOG, Aflatoxin)
  - Chargenverwaltung
  - Preise & Konditionen
- **MCP-Intent:** `view-single-feed-master-data`

#### 2.1.2 `futter-einzel-liste` - Einzelfuttermittel-Übersicht
- **Pattern:** ListReport
- **Filter:** Art, Herkunft, GVO-Status, QS-Milch, Verfügbarkeit
- **MCP-Intent:** `list-single-feeds`

#### 2.1.3 `futter-getreide` - Futtergetreide-Verwaltung
- **Pattern:** ListReport
- **Features:** Weizen, Gerste, Mais, Triticale, etc.
- **MCP-Intent:** `manage-feed-grain`

#### 2.1.4 `futter-eiweiss` - Eiweißfuttermittel
- **Pattern:** ListReport
- **Features:** Soja, Raps, Sonnenblumen, Erbsen, etc.
- **MCP-Intent:** `manage-protein-feeds`

#### 2.1.5 `futter-nebenprodukte` - Nebenprodukte
- **Pattern:** ListReport
- **Features:** Schlempen, Biertreber, Melasse, etc.
- **MCP-Intent:** `manage-feed-byproducts`

#### 2.1.6 `futter-mineralfutter` - Mineralfutter-Komponenten
- **Pattern:** ListReport
- **MCP-Intent:** `manage-mineral-components`

---

### 2.2 Mischfuttermittel (8 Masken)

#### 2.2.1 `futter-misch-stamm` - Mischfutter-Stammdaten
- **Pattern:** ObjectPage
- **Sections:**
  - Allgemein (Typ, Tierart, Leistungsstufe)
  - Rezeptur (Komponenten, Anteile)
  - Nährwertdeklaration
  - Zulassung & QS
  - Kalkulation & Preis
- **MCP-Intent:** `view-compound-feed-master-data`

#### 2.2.2 `futter-misch-liste` - Mischfutter-Übersicht
- **Pattern:** ListReport
- **Filter:** Tierart, Leistungsgruppe, Mischanlage, Verfügbarkeit
- **MCP-Intent:** `list-compound-feeds`

#### 2.2.3 `futter-rezeptur-designer` - Rezeptur-Designer
- **Pattern:** Wizard
- **Features:** Komponenten wählen, Nährwertberechnung, Kostenoptimierung
- **MCP-Intent:** `design-feed-recipe`

#### 2.2.4 `futter-rezeptur-optimierung` - Rezepturoptimierung (AI)
- **Pattern:** OverviewPage
- **Features:** Least-Cost-Formulation, Nährstoff-Constraints, Verfügbarkeit
- **MCP-Intent:** `optimize-feed-recipe`

#### 2.2.5 `futter-mischanlage-steuerung` - Mischanlage-Steuerung
- **Pattern:** ObjectPage
- **Features:** Produktionsaufträge, Dosierung, Qualitätskontrolle
- **MCP-Intent:** `control-mixer`

#### 2.2.6 `futter-produktion-planung` - Produktionsplanung
- **Pattern:** Worklist
- **Features:** Kapazitätsplanung, Reihenfolge, Reinigung
- **MCP-Intent:** `plan-feed-production`

#### 2.2.7 `futter-produktionsprotokoll` - Produktionsprotokolle
- **Pattern:** ObjectPage
- **Features:** Chargen-Tracking, Wiegungen, Abweichungen
- **MCP-Intent:** `document-production`

#### 2.2.8 `futter-qs-checks` - QS-Checks Mischfutter
- **Pattern:** Worklist
- **Features:** Sichtkontrolle, Laboranalysen, Freigabe
- **MCP-Intent:** `quality-check-feed`

---

### 2.3 QS & Compliance (Futtermittel) (8 Masken)

#### 2.3.1 `futter-qs-milch` - QS-Milch-Management
- **Pattern:** Worklist
- **Features:** Aflatoxin-Überwachung, QS-Lieferanten, Zertifikate
- **MCP-Intent:** `manage-qs-milk`

#### 2.3.2 `futter-vlog` - VLOG-Verwaltung
- **Pattern:** ObjectPage
- **Features:** GVO-Status, VLOG-Zertifikate, Monitoring
- **MCP-Intent:** `manage-vlog`

#### 2.3.3 `futter-aflatoxin` - Aflatoxin-Monitoring
- **Pattern:** OverviewPage
- **KPIs:** Aktuelle Werte, Grenzwert-Überschreitungen, Laboranalysen
- **MCP-Intent:** `monitor-aflatoxin`

#### 2.3.4 `futter-gvo-screening` - GVO-Screening
- **Pattern:** Worklist
- **Features:** Schnelltests, Laboranalysen, Spuren-Deklaration
- **MCP-Intent:** `screen-gmo`

#### 2.3.5 `futter-qs-lieferanten` - QS-Lieferanten-Verwaltung
- **Pattern:** ListReport
- **Features:** QS-Nummer, Status, Audit-Termine, Bewertung
- **MCP-Intent:** `manage-qs-suppliers`

#### 2.3.6 `futter-hygiene` - Hygiene-Management
- **Pattern:** Worklist
- **Features:** Reinigung, Desinfektion, Schädlingskontrolle
- **MCP-Intent:** `manage-hygiene`

#### 2.3.7 `futter-salmonellen` - Salmonellen-Monitoring
- **Pattern:** OverviewPage
- **Features:** Probenplan, Laborergebnisse, Maßnahmen
- **MCP-Intent:** `monitor-salmonella`

#### 2.3.8 `futter-ruckverfolgung` - Rückverfolgbarkeit
- **Pattern:** ObjectPage
- **Features:** One-Step-Up/Down, Chargen-Tracking, Rückruf-Simulation
- **MCP-Intent:** `trace-feed-batches`

---

## 🏷️ MODUL 3: CHARGENVERWALTUNG (18 Masken)

### 3.1 Chargen-Stammdaten (4 Masken)

#### 3.1.1 `charge-stamm` - Chargenstammdaten
- **Pattern:** ObjectPage (basierend auf chargenverwaltung_model.json)
- **Sections:**
  - Allgemein (Chargen-ID, Artikel, Menge, Lieferant)
  - Warenbewegungen (Eingang, Ausgang, Umlagerung)
  - QS-Attribute (GVO, QS-Milch, Aflatoxin)
  - Nachhaltigkeit (EUDR, Nachhaltig-Raps, ISCC)
  - Status & Historie
  - Dokumente (Zertifikate, Analysen, Lieferscheine)
- **MCP-Intent:** `view-batch-master-data`

#### 3.1.2 `charge-liste` - Chargen-Übersicht
- **Pattern:** ListReport
- **Filter:** Artikel, Status, GVO, EUDR, QS-Milch, Lieferant, Lagerort
- **Actions:** Neu, Sperren, Freigeben, Export, Druck-Etiketten
- **MCP-Intent:** `list-batches`

#### 3.1.3 `charge-wareneingang` - Wareneingang mit Chargendaten (Wizard)
- **Pattern:** Wizard (6 Steps)
- **Steps:**
  1. Lieferant & Lieferschein
  2. Artikel & Menge
  3. Chargen-ID (auto/manuell)
  4. QS-Attribute (OCR-Scanning)
  5. Lagerort zuweisen
  6. Bestätigung & Etiketten-Druck
- **MCP-Intent:** `goods-receipt-wizard`

#### 3.1.4 `charge-id-generator` - Chargen-ID-Generator
- **Pattern:** Wizard
- **Features:** Auto-Generierung nach Schema (Jahr-Monat-Tag-Art-Herkunft-Seq)
- **Beispiel:** `241010-GET-LIEF-001` (10. Okt. 2024, Getreide, Lieferant, Seq. 001)
- **MCP-Intent:** `generate-batch-id`

---

### 3.2 QS-Attribute & Compliance (6 Masken)

#### 3.2.1 `charge-gvo-status` - GVO-Status-Verwaltung
- **Pattern:** Worklist
- **Features:** GVO-frei zertifiziert, Eigenerklärung, Spuren, kennzeichnungspflichtig
- **Validation:** Automatische Befüllung, Manuelle Bestätigung, Warnhinweise
- **MCP-Intent:** `manage-gmo-status`

#### 3.2.2 `charge-vlog-zertifikate` - VLOG-Zertifikate
- **Pattern:** ObjectPage
- **Features:** Zertifikat-Upload, Gültigkeitsprüfung, Verlinkung zu Charge
- **MCP-Intent:** `manage-vlog-certificates`

#### 3.2.3 `charge-qs-milch` - QS-Milch-Attribute
- **Pattern:** ObjectPage
- **Features:** Aflatoxin-Werte, QS-Lieferanten-Status, Analysenzertifikate
- **Validation:** Grenzwertprüfung, Automatische Sperrung bei Überschreitung
- **MCP-Intent:** `manage-qs-milk-attributes`

#### 3.2.4 `charge-eudr-compliance` - EUDR-Konformität
- **Pattern:** ObjectPage
- **Features:** Entwaldungsfreiheit (Stichtag 2020), Geo-Koordinaten, Sorgfaltserklärung
- **Validation:** Pflichtfeld, Automatische Sperrung bei false
- **MCP-Intent:** `manage-eudr-compliance`

#### 3.2.5 `charge-nachhaltigkeit-raps` - Nachhaltigkeit Raps
- **Pattern:** ObjectPage
- **Features:** Landnutzungs-Konformität, Zertifizierung (ISCC, REDcert), Nachhaltigkeitszertifikate
- **MCP-Intent:** `manage-rape-sustainability`

#### 3.2.6 `charge-analysenzertifikate` - Analysenzertifikate-Verwaltung
- **Pattern:** ListReport
- **Features:** Labor, Datum, Ergebnisse, PDF-Upload, Verknüpfung zu Chargen
- **MCP-Intent:** `manage-analysis-certificates`

---

### 3.3 Warenbewegungen & Tracking (4 Masken)

#### 3.3.1 `charge-warenbewegungen` - Warenbewegungsübersicht
- **Pattern:** ListReport
- **Filter:** Charge, Artikel, Bewegungsart, Datum, Bediener
- **Types:** Eingang, Ausgang, Umlagerung, Produktion
- **MCP-Intent:** `list-batch-movements`

#### 3.3.2 `charge-warenausgang` - Warenausgang mit Charge
- **Pattern:** Wizard
- **Features:** Charge auswählen, Menge, Kunde, Lieferschein, Etiketten
- **MCP-Intent:** `goods-issue-batch`

#### 3.3.3 `charge-umlagerung` - Chargen-Umlagerung
- **Pattern:** Wizard
- **Features:** Von/Nach-Lagerort, Menge, Grund, Protokoll
- **MCP-Intent:** `relocate-batch`

#### 3.3.4 `charge-tracking` - Chargen-Tracking (One-Up/Down)
- **Pattern:** ObjectPage
- **Features:** Lieferkette, Vorwärts-/Rückwärtsverfolgung, Rückruf-Simulation
- **MCP-Intent:** `track-batch`

---

### 3.4 Status & Sperrverwaltung (4 Masken)

#### 3.4.1 `charge-status-management` - Status-Management
- **Pattern:** Worklist
- **Status:** Neu, In QS-Prüfung, Gesperrt (Qualität), Freigegeben, Aktiv, Gesperrt (Nachhaltigkeit), Abgelaufen, Verbraucht
- **Features:** Automatische Statuswechsel, Status-Historie, Grund-Dokumentation
- **MCP-Intent:** `manage-batch-status`

#### 3.4.2 `charge-sperrverwaltung` - Sperrverwaltung
- **Pattern:** Worklist
- **Features:** Chargen sperren, Sperrgrund, Freigabeworkflow, Benachrichtigung
- **MCP-Intent:** `manage-batch-blocks`

#### 3.4.3 `charge-freigabe-workflow` - Freigabe-Workflow
- **Pattern:** Worklist
- **Features:** QS-Prüfung, Dokumentenprüfung, Verantwortlicher, Freigabe-Entscheidung
- **MCP-Intent:** `release-batch-workflow`

#### 3.4.4 `charge-audit-trail` - Audit-Trail
- **Pattern:** ObjectPage
- **Features:** Vollständige Änderungshistorie, Benutzer, Zeitstempel, Alte/Neue Werte
- **MCP-Intent:** `view-batch-audit-trail`

---

## ⚖️ MODUL 4: WAAGEN & ANNAHME (12 Masken)

### 4.1 Waagen-Management (4 Masken)

#### 4.1.1 `waage-liste` - Waagen-Übersicht
- **Pattern:** ListReport
- **Features:** Standort, Typ, Kalibrierung, Status, Wartung
- **MCP-Intent:** `list-scales`

#### 4.1.2 `waage-kalibrierung` - Kalibrierungs-Management
- **Pattern:** Worklist
- **Features:** Eichung, Prüffristen, Protokolle, Zertifikate
- **MCP-Intent:** `manage-calibration`

#### 4.1.3 `waage-wiegungen` - Wiegungen-Historie
- **Pattern:** ListReport
- **Filter:** Waage, Datum, Artikel, Kunde, Lieferant
- **MCP-Intent:** `list-weighings`

#### 4.1.4 `waage-schnitt stellen` - Schnittstellen-Manager
- **Pattern:** ObjectPage
- **Features:** API, COM-Port, Datenformat, Auto-Import
- **MCP-Intent:** `manage-scale-interfaces`

---

### 4.2 Warenannahme (8 Masken)

#### 4.2.1 `annahme-lkw-registrierung` - LKW-Registrierung
- **Pattern:** Wizard
- **Features:** Kennzeichen-Scan, Lieferant, Lieferschein-Scan, Warteschlange
- **MCP-Intent:** `register-truck`

#### 4.2.2 `annahme-warteschlange` - Annahme-Warteschlange
- **Pattern:** Worklist
- **Features:** Reihenfolge, Wartezeit, Priorität, Benachrichtigung
- **MCP-Intent:** `manage-queue`

#### 4.2.3 `annahme-voranmeldung` - Voranmeldungs-System
- **Pattern:** ListReport
- **Features:** Online-Anmeldung, Zeitfenster, Kapazitätsplanung
- **MCP-Intent:** `manage-pre-registration`

#### 4.2.4 `annahme-probenahme` - Probenahme-Protokoll
- **Pattern:** ObjectPage
- **Features:** Proben-ID, Analyseparameter, Labor, Status
- **MCP-Intent:** `document-sampling`

#### 4.2.5 `annahme-qualitaets-check` - Schnell-Qualitätsprüfung
- **Pattern:** Wizard
- **Features:** Sichtkontrolle, Feuchtemessung, Protein, Verunreinigungen
- **MCP-Intent:** `quick-quality-check`

#### 4.2.6 `annahme-abrechnung` - Annahme-Abrechnung
- **Pattern:** ObjectPage
- **Features:** Gewicht, Qualitätsabzüge, Preis, Beleg-Erstellung
- **MCP-Intent:** `settle-delivery`

#### 4.2.7 `annahme-lieferschein-scan` - Lieferschein-Scanning (OCR)
- **Pattern:** Wizard
- **Features:** OCR-Erkennung, Auto-Fill, Validierung, Archivierung
- **MCP-Intent:** `scan-delivery-note`

#### 4.2.8 `annahme-lkw-abfertigung` - LKW-Abfertigung
- **Pattern:** Wizard
- **Features:** Wiegung, Qualität OK, Beleg-Druck, Tore-Öffnung
- **MCP-Intent:** `dispatch-truck`

---

## 📦 MODUL 5: LAGER & LOGISTIK (24 Masken)

### 5.1 Lager-Stammdaten (6 Masken)

#### 5.1.1 `lager-standorte` - Standorte-Verwaltung
- **Pattern:** ListReport
- **MCP-Intent:** `manage-locations`

#### 5.1.2 `lager-zonen` - Lagerzonen
- **Pattern:** ObjectPage
- **Features:** Zone, Typ, Kapazität, Temperatur, Feuchtigkeit
- **MCP-Intent:** `manage-zones`

#### 5.1.3 `lager-plaetze` - Lagerplätze
- **Pattern:** ListReport
- **MCP-Intent:** `manage-storage-bins`

#### 5.1.4 `lager-kapazitaeten` - Kapazitäts-Management
- **Pattern:** OverviewPage
- **KPIs:** Belegung, Verfügbar, Reserviert, Prognose
- **MCP-Intent:** `manage-capacity`

#### 5.1.5 `lager-kosten` - Lagerkosten
- **Pattern:** ObjectPage
- **MCP-Intent:** `manage-storage-costs`

#### 5.1.6 `lager-gefahrstoff-zonen` - Gefahrstoff-Lagerzonen
- **Pattern:** ObjectPage
- **Features:** TRGS 510, Lagerklassen, Zusammenlagerung
- **MCP-Intent:** `manage-hazmat-zones`

---

### 5.2 Lagerbewegungen (6 Masken)

#### 5.2.1 `lager-einlagerung` - Einlagerung
- **Pattern:** Wizard
- **MCP-Intent:** `store-goods`

#### 5.2.2 `lager-auslagerung` - Auslagerung
- **Pattern:** Wizard
- **Features:** FIFO, FEFO, Chargen-Auswahl, Kommissionierung
- **MCP-Intent:** `retrieve-goods`

#### 5.2.3 `lager-umlagerung` - Umlagerung
- **Pattern:** Wizard
- **MCP-Intent:** `relocate-goods`

#### 5.2.4 `lager-inventur` - Inventur
- **Pattern:** Worklist
- **Features:** Stichtagsinventur, permanente Inventur, Mobile-App
- **MCP-Intent:** `inventory-count`

#### 5.2.5 `lager-bestandskorrekturen` - Bestandskorrekturen
- **Pattern:** ObjectPage
- **MCP-Intent:** `adjust-stock`

#### 5.2.6 `lager-sperr-bestaende` - Sperrbestand-Management
- **Pattern:** ListReport
- **MCP-Intent:** `manage-blocked-stock`

---

### 5.3 Logistik & Versand (6 Masken)

#### 5.3.1 `logistik-tourenplanung` - Tourenplanung
- **Pattern:** OverviewPage
- **Features:** Routenoptimierung, Fahrzeug-Disposition, Zeitfenster
- **MCP-Intent:** `plan-tours`

#### 5.3.2 `logistik-fahrzeuge` - Fahrzeugverwaltung
- **Pattern:** ListReport
- **MCP-Intent:** `manage-vehicles`

#### 5.3.3 `logistik-fahrer` - Fahrerverwaltung
- **Pattern:** ListReport
- **Features:** Führerscheine, ADR-Schulung, Arbeitszeiten
- **MCP-Intent:** `manage-drivers`

#### 5.3.4 `logistik-lieferscheine` - Lieferschein-Management
- **Pattern:** ListReport
- **MCP-Intent:** `manage-delivery-notes`

#### 5.3.5 `logistik-tracking` - Sendungs-Tracking
- **Pattern:** ObjectPage
- **Features:** GPS-Tracking, ETA, Kunde-Benachrichtigung
- **MCP-Intent:** `track-shipments`

#### 5.3.6 `logistik-frachtkosten` - Frachtkostenberechnung
- **Pattern:** ObjectPage
- **MCP-Intent:** `calculate-freight`

---

### 5.4 Lager-Controlling (6 Masken)

#### 5.4.1 `lager-bestandsuebersicht` - Bestandsübersicht
- **Pattern:** OverviewPage
- **KPIs:** Gesamtbestand, Wert, Bewegungen, Reichweite
- **MCP-Intent:** `overview-stock`

#### 5.4.2 `lager-abc-analyse` - ABC-Analyse
- **Pattern:** OverviewPage
- **MCP-Intent:** `abc-analysis`

#### 5.4.3 `lager-mindestbestaende` - Mindestbestands-Monitoring
- **Pattern:** Worklist
- **MCP-Intent:** `monitor-min-stock`

#### 5.4.4 `lager-lagerdauer` - Lagerdauer-Analyse
- **Pattern:** OverviewPage
- **MCP-Intent:** `analyze-storage-duration`

#### 5.4.5 `lager-umschlag` - Lagerumschlag
- **Pattern:** OverviewPage
- **MCP-Intent:** `analyze-turnover`

#### 5.4.6 `lager-optimierung` - Lager-Optimierung (AI)
- **Pattern:** OverviewPage
- **Features:** Belegungsoptimierung, Wegzeiten-Optimierung
- **MCP-Intent:** `optimize-warehouse`

---

## 🛒 MODUL 6: EINKAUF (16 Masken)

### 6.1 Einkaufs-Stammdaten (4 Masken)

#### 6.1.1 `einkauf-lieferanten` - Lieferanten-Stammdaten
- **Pattern:** ObjectPage
- **MCP-Intent:** `view-supplier-master-data`

#### 6.1.2 `einkauf-lieferanten-bewertung` - Lieferanten-Bewertung
- **Pattern:** OverviewPage
- **KPIs:** Qualität, Pünktlichkeit, Preis, Compliance
- **MCP-Intent:** `rate-suppliers`

#### 6.1.3 `einkauf-konditionen` - Einkaufskonditionen
- **Pattern:** ListReport
- **MCP-Intent:** `manage-purchase-conditions`

#### 6.1.4 `einkauf-lieferantenvertraege` - Lieferantenverträge
- **Pattern:** ObjectPage
- **MCP-Intent:** `manage-supplier-contracts`

---

### 6.2 Bestellwesen (6 Masken)

#### 6.2.1 `einkauf-bestellungen-liste` - Bestellungen-Übersicht
- **Pattern:** ListReport
- **MCP-Intent:** `list-purchase-orders`

#### 6.2.2 `einkauf-bestellung-anlegen` - Bestellung anlegen (Wizard)
- **Pattern:** Wizard
- **MCP-Intent:** `create-purchase-order`

#### 6.2.3 `einkauf-bestellueberwachung` - Bestellüberwachung
- **Pattern:** Worklist
- **Features:** Liefertermine, Mahnungen, Status
- **MCP-Intent:** `monitor-purchase-orders`

#### 6.2.4 `einkauf-bestellvorschlaege` - Bestellvorschläge (AI)
- **Pattern:** Worklist
- **Features:** Mindestbestand, Prognose, Saison, Lieferzeit
- **MCP-Intent:** `suggest-purchase-orders`

#### 6.2.5 `einkauf-rahmenvertraege` - Rahmenverträge
- **Pattern:** ListReport
- **MCP-Intent:** `manage-frame-contracts`

#### 6.2.6 `einkauf-abrufe` - Abrufe aus Rahmenverträgen
- **Pattern:** Wizard
- **MCP-Intent:** `call-off-frame-contract`

---

### 6.3 Einkaufs-Controlling (6 Masken)

#### 6.3.1 `einkauf-preisvergleich` - Preis-Vergleichstool
- **Pattern:** OverviewPage
- **MCP-Intent:** `compare-prices`

#### 6.3.2 `einkauf-preis-historie` - Preis-Historie
- **Pattern:** OverviewPage
- **MCP-Intent:** `view-price-history`

#### 6.3.3 `einkauf-kostenanalyse` - Einkaufs-Kostenanalyse
- **Pattern:** OverviewPage
- **MCP-Intent:** `analyze-purchase-costs`

#### 6.3.4 `einkauf-skonti` - Skonto-Management
- **Pattern:** Worklist
- **MCP-Intent:** `manage-discounts`

#### 6.3.5 `einkauf-budgetueberwachung` - Budget-Überwachung
- **Pattern:** OverviewPage
- **MCP-Intent:** `monitor-budget`

#### 6.3.6 `einkauf-kennzahlen` - Einkaufs-Kennzahlen
- **Pattern:** OverviewPage
- **KPIs:** Einkaufsvolumen, Lieferantreue, Reklamationsquote
- **MCP-Intent:** `purchase-kpis`

---

## 💰 MODUL 7: VERKAUF (18 Masken)

### 7.1 Verkaufs-Stammdaten (4 Masken)

#### 7.1.1 `verkauf-kunden` - Kundenstammdaten
- **Pattern:** ObjectPage
- **MCP-Intent:** `view-customer-master-data`

#### 7.1.2 `verkauf-preislisten` - Preislisten
- **Pattern:** ListReport
- **MCP-Intent:** `manage-price-lists`

#### 7.1.3 `verkauf-konditionen` - Verkaufskonditionen
- **Pattern:** ListReport
- **MCP-Intent:** `manage-sales-conditions`

#### 7.1.4 `verkauf-vertraege` - Kundenverträge
- **Pattern:** ObjectPage
- **MCP-Intent:** `manage-customer-contracts`

---

### 7.2 Auftragsabwicklung (8 Masken)

#### 7.2.1 `verkauf-angebote-liste` - Angebots-Übersicht
- **Pattern:** ListReport
- **MCP-Intent:** `list-quotations`

#### 7.2.2 `verkauf-angebot-erstellen` - Angebot erstellen (Wizard)
- **Pattern:** Wizard
- **MCP-Intent:** `create-quotation`

#### 7.2.3 `verkauf-auftraege-liste` - Auftrags-Übersicht
- **Pattern:** ListReport
- **MCP-Intent:** `list-sales-orders`

#### 7.2.4 `verkauf-auftrag-erfassen` - Auftrag erfassen (Wizard)
- **Pattern:** Wizard
- **MCP-Intent:** `create-sales-order`

#### 7.2.5 `verkauf-lieferungen-liste` - Lieferungen-Übersicht
- **Pattern:** ListReport
- **MCP-Intent:** `list-deliveries`

#### 7.2.6 `verkauf-lieferschein-erstellen` - Lieferschein erstellen
- **Pattern:** Wizard
- **MCP-Intent:** `create-delivery`

#### 7.2.7 `verkauf-rechnungen-liste` - Rechnungs-Übersicht
- **Pattern:** ListReport
- **MCP-Intent:** `list-invoices`

#### 7.2.8 `verkauf-rechnung-erstellen` - Rechnung erstellen
- **Pattern:** Wizard
- **MCP-Intent:** `create-invoice`

---

### 7.3 Verkaufs-Controlling (6 Masken)

#### 7.3.1 `verkauf-umsatzuebersicht` - Umsatzübersicht
- **Pattern:** OverviewPage
- **KPIs:** Umsatz, Marge, Top-Kunden, Top-Artikel
- **MCP-Intent:** `overview-sales`

#### 7.3.2 `verkauf-deckungsbeitraege` - Deckungsbeitrags-Rechnung
- **Pattern:** OverviewPage
- **MCP-Intent:** `calculate-contribution-margin`

#### 7.3.3 `verkauf-provisionen` - Provisions-Abrechnung
- **Pattern:** ObjectPage
- **MCP-Intent:** `calculate-commissions`

#### 7.3.4 `verkauf-kundenwert` - Customer-Lifetime-Value
- **Pattern:** OverviewPage
- **MCP-Intent:** `calculate-clv`

#### 7.3.5 `verkauf-absatzprognose` - Absatzprognose (AI)
- **Pattern:** OverviewPage
- **Features:** Zeitreihen-Analyse, Saisonalität, Trends
- **MCP-Intent:** `forecast-sales`

#### 7.3.6 `verkauf-kennzahlen` - Verkaufs-Kennzahlen
- **Pattern:** OverviewPage
- **KPIs:** Auftragseingang, Stornoquote, Liefertreue
- **MCP-Intent:** `sales-kpis`

---

## 💶 MODUL 8: FINANZEN (14 Masken)

### 8.1 Debitoren-Management (4 Masken)

#### 8.1.1 `fibu-debitoren-liste` - Debitoren-Übersicht
- **Pattern:** ListReport
- **MCP-Intent:** `list-debtors`

#### 8.1.2 `fibu-offene-posten` - Offene Posten
- **Pattern:** ListReport
- **MCP-Intent:** `list-open-items`

#### 8.1.3 `fibu-mahnwesen` - Mahnwesen
- **Pattern:** Worklist
- **Features:** Mahnstufen, Mahnläufe, Inkasso
- **MCP-Intent:** `dunning-process`

#### 8.1.4 `fibu-zahlungseingaenge` - Zahlungseingänge
- **Pattern:** Worklist
- **Features:** Bank-Import, Auto-Matching, Differenzen
- **MCP-Intent:** `process-payments`

---

### 8.2 Kreditoren-Management (4 Masken)

#### 8.2.1 `fibu-kreditoren-liste` - Kreditoren-Übersicht
- **Pattern:** ListReport
- **MCP-Intent:** `list-creditors`

#### 8.2.2 `fibu-verbindlichkeiten` - Verbindlichkeiten
- **Pattern:** ListReport
- **MCP-Intent:** `list-payables`

#### 8.2.3 `fibu-zahlungsvorschlaege` - Zahlungsvorschläge
- **Pattern:** Worklist
- **Features:** Skonto-Optimierung, Liquiditätsplanung
- **MCP-Intent:** `suggest-payments`

#### 8.2.4 `fibu-zahlungslaeufe` - Zahlungsläufe
- **Pattern:** Wizard
- **Features:** SEPA-Export, Datev-Export
- **MCP-Intent:** `payment-runs`

---

### 8.3 Buchungswesen (6 Masken)

#### 8.3.1 `fibu-buchungen-liste` - Buchungs-Übersicht
- **Pattern:** ListReport
- **MCP-Intent:** `list-postings`

#### 8.3.2 `fibu-manuelle-buchung` - Manuelle Buchung
- **Pattern:** Wizard
- **MCP-Intent:** `manual-posting`

#### 8.3.3 `fibu-buchungsvorlagen` - Buchungsvorlagen
- **Pattern:** ListReport
- **MCP-Intent:** `manage-posting-templates`

#### 8.3.4 `fibu-kontenplan` - Kontenplan
- **Pattern:** ListReport
- **MCP-Intent:** `manage-chart-of-accounts`

#### 8.3.5 `fibu-kostenstellen` - Kostenstellen-Management
- **Pattern:** ListReport
- **MCP-Intent:** `manage-cost-centers`

#### 8.3.6 `fibu-budget-controlling` - Budget-Controlling
- **Pattern:** OverviewPage
- **KPIs:** Plan, Ist, Abweichung, Prognose
- **MCP-Intent:** `budget-controlling`

---

## 👥 MODUL 9: CRM (12 Masken)

### 9.1 Kontakt-Management (4 Masken)

#### 9.1.1 `crm-kontakte-liste` - Kontakte-Übersicht
- **Pattern:** ListReport
- **MCP-Intent:** `list-contacts`

#### 9.1.2 `crm-kontakt-profil` - Kontakt-Profil
- **Pattern:** ObjectPage
- **MCP-Intent:** `view-contact-profile`

#### 9.1.3 `crm-aktivitaeten` - Aktivitäten-Historie
- **Pattern:** ListReport
- **Features:** Anrufe, E-Mails, Besuche, Aufgaben
- **MCP-Intent:** `list-activities`

#### 9.1.4 `crm-wiedervorlagen` - Wiedervorlagen
- **Pattern:** Worklist
- **MCP-Intent:** `manage-follow-ups`

---

### 9.2 Kampagnen & Marketing (4 Masken)

#### 9.2.1 `crm-kampagnen-liste` - Kampagnen-Übersicht
- **Pattern:** ListReport
- **MCP-Intent:** `list-campaigns`

#### 9.2.2 `crm-kampagne-designer` - Kampagnen-Designer
- **Pattern:** Wizard
- **Features:** Zielgruppe, Channels, Timing, Budget
- **MCP-Intent:** `design-campaign`

#### 9.2.3 `crm-newsletter` - Newsletter-Manager
- **Pattern:** ObjectPage
- **MCP-Intent:** `manage-newsletter`

#### 9.2.4 `crm-kampagnen-analyse` - Kampagnen-Analyse
- **Pattern:** OverviewPage
- **KPIs:** Öffnungsrate, Klickrate, Conversion, ROI
- **MCP-Intent:** `analyze-campaigns`

---

### 9.3 Landwirt-spezifisch (4 Masken)

#### 9.3.1 `crm-betriebsprofile` - Betriebsprofile (Landwirte)
- **Pattern:** ObjectPage
- **Features:** Flächen, Kulturen, Tierbestand, Maschinen
- **MCP-Intent:** `view-farm-profile`

#### 9.3.2 `crm-flaechen-management` - Flächen-Management
- **Pattern:** ListReport
- **Features:** Schlag-Kartei, Geo-Koordinaten, Fruchtfolge
- **MCP-Intent:** `manage-fields`

#### 9.3.3 `crm-duengeplanung` - Düngeplanung-Service
- **Pattern:** Wizard (AI-gestützt)
- **Features:** Bodenanalyse, Empfehlung, DüV-Konformität
- **MCP-Intent:** `plan-fertilization`

#### 9.3.4 `crm-pflanzenschutz-beratung` - PSM-Beratungs-Service
- **Pattern:** Wizard (AI-gestützt)
- **Features:** Schadbilder-Erkennung, Mittelempfehlung, Zulassung
- **MCP-Intent:** `advisory-plant-protection`

---

## ✅ MODUL 10: COMPLIANCE & QS (14 Masken)

### 10.1 Zulassungen & Lizenzen (4 Masken)

#### 10.1.1 `compliance-zulassungen-register` - Zulassungsregister
- **Pattern:** ListReport
- **Features:** PSM (BVL), Saatgut (BSA), Dünger (DüMV)
- **MCP-Intent:** `manage-approvals`

#### 10.1.2 `compliance-ablauf-monitoring` - Ablauf-Monitoring
- **Pattern:** Worklist
- **Features:** Fristen, Erinnerungen, Verlängerung
- **MCP-Intent:** `monitor-expiry`

#### 10.1.3 `compliance-sachkunde-verwaltung` - Sachkunde-Register
- **Pattern:** ListReport
- **Features:** Mitarbeiter, Kunden, Schulungen, Ablauf
- **MCP-Intent:** `manage-expertise`

#### 10.1.4 `compliance-lizenzen` - Lizenzen-Verwaltung
- **Pattern:** ListReport
- **Features:** Sortenschutz, Nachbaugebühren, Z-Saatgut
- **MCP-Intent:** `manage-licenses`

---

### 10.2 QS-Systeme (4 Masken)

#### 10.2.1 `qs-qs-milch-management` - QS-Milch-Management
- **Pattern:** ObjectPage
- **Features:** Lieferanten, Aflatoxin, Zertifikate
- **MCP-Intent:** `manage-qs-milk-system`

#### 10.2.2 `qs-vlog-system` - VLOG-System
- **Pattern:** ObjectPage
- **Features:** GVO-Status, Zertifikate, Monitoring
- **MCP-Intent:** `manage-vlog-system`

#### 10.2.3 `qs-qs-lieferanten` - QS-Lieferanten-DB
- **Pattern:** ListReport
- **Features:** QS-Nummer, Status, Audits, Bewertung
- **MCP-Intent:** `manage-qs-suppliers-db`

#### 10.2.4 `qs-zertifikate-verwaltung` - Zertifikate-Zentrale
- **Pattern:** ListReport
- **Features:** Upload, Gültigkeit, Verknüpfungen, Archiv
- **MCP-Intent:** `manage-certificates`

---

### 10.3 Nachhaltigkeit (6 Masken)

#### 10.3.1 `nachhaltigkeit-eudr-compliance` - EUDR-Compliance-System
- **Pattern:** OverviewPage
- **Features:** Entwaldungsfreiheit, Geo-Koordinaten, Sorgfaltserklärung
- **MCP-Intent:** `manage-eudr`

#### 10.3.2 `nachhaltigkeit-raps` - Nachhaltig-Raps-System
- **Pattern:** ObjectPage
- **Features:** Landnutzung, ISCC, REDcert, Zertifikate
- **MCP-Intent:** `manage-sustainable-rape`

#### 10.3.3 `nachhaltigkeit-co2-bilanz` - CO2-Bilanzierung
- **Pattern:** OverviewPage
- **Features:** Scope 1/2/3, Reporting, Reduktion
- **MCP-Intent:** `calculate-carbon-footprint`

#### 10.3.4 `nachhaltigkeit-gis-integration` - GIS-Integration
- **Pattern:** ObjectPage
- **Features:** Anbauflächen, Entwaldungshistorie, Satellitenbilder
- **MCP-Intent:** `gis-integration`

#### 10.3.5 `nachhaltigkeit-biodiversitaet` - Biodiversitäts-Monitoring
- **Pattern:** OverviewPage
- **MCP-Intent:** `monitor-biodiversity`

#### 10.3.6 `nachhaltigkeit-reporting` - Nachhaltigkeits-Reporting
- **Pattern:** OverviewPage
- **Features:** CSRD, ESG, GRI-Standards
- **MCP-Intent:** `sustainability-reporting`

---

## ⚙️ MODUL 11: ADMINISTRATION (10 Masken)

### 11.1 Benutzerverwaltung (3 Masken)

#### 11.1.1 `admin-benutzer-liste` - Benutzer-Übersicht
- **Pattern:** ListReport
- **MCP-Intent:** `list-users`

#### 11.1.2 `admin-rollen-verwaltung` - Rollen & Berechtigungen
- **Pattern:** ObjectPage
- **MCP-Intent:** `manage-roles`

#### 11.1.3 `admin-audit-log` - Audit-Log
- **Pattern:** ListReport
- **MCP-Intent:** `view-audit-log`

---

### 11.2 Systemeinstellungen (4 Masken)

#### 11.2.1 `admin-standorte` - Standort-Verwaltung
- **Pattern:** ListReport
- **MCP-Intent:** `manage-sites`

#### 11.2.2 `admin-nummernkreise` - Nummernkreis-Verwaltung
- **Pattern:** ObjectPage
- **MCP-Intent:** `manage-number-ranges`

#### 11.2.3 `admin-schnittstellen` - Schnittstellen-Konfiguration
- **Pattern:** ObjectPage
- **Features:** API, EDI, OCR, GIS, Waagen
- **MCP-Intent:** `configure-interfaces`

#### 11.2.4 `admin-parameter` - System-Parameter
- **Pattern:** ObjectPage
- **MCP-Intent:** `configure-parameters`

---

### 11.3 Wartung & Monitoring (3 Masken)

#### 11.3.1 `admin-system-health` - System-Health-Dashboard
- **Pattern:** OverviewPage
- **KPIs:** CPU, Memory, Disk, DB, API-Response
- **MCP-Intent:** `monitor-system-health`

#### 11.3.2 `admin-backup-verwaltung` - Backup-Management
- **Pattern:** ObjectPage
- **MCP-Intent:** `manage-backups`

#### 11.3.3 `admin-log-verwaltung` - Log-Verwaltung
- **Pattern:** ListReport
- **MCP-Intent:** `manage-logs`

---

## 📊 MODUL 12: REPORTS & ANALYTICS (14 Masken)

### 12.1 Standard-Reports (6 Masken)

#### 12.1.1 `reports-umsatz` - Umsatz-Report
- **Pattern:** OverviewPage
- **MCP-Intent:** `report-sales`

#### 12.1.2 `reports-lagerbestand` - Lagerbestands-Report
- **Pattern:** OverviewPage
- **MCP-Intent:** `report-inventory`

#### 12.1.3 `reports-offene-posten` - Offene-Posten-Report
- **Pattern:** ListReport
- **MCP-Intent:** `report-open-items`

#### 12.1.4 `reports-deckungsbeitrag` - Deckungsbeitrags-Report
- **Pattern:** OverviewPage
- **MCP-Intent:** `report-contribution-margin`

#### 12.1.5 `reports-kunden-abc` - Kunden-ABC-Analyse
- **Pattern:** OverviewPage
- **MCP-Intent:** `report-customer-abc`

#### 12.1.6 `reports-artikel-abc` - Artikel-ABC-Analyse
- **Pattern:** OverviewPage
- **MCP-Intent:** `report-article-abc`

---

### 12.2 Analytics & BI (4 Masken)

#### 12.2.1 `analytics-dashboard-designer` - Dashboard-Designer
- **Pattern:** Wizard
- **Features:** Drag & Drop, Widgets, KPIs, Filters
- **MCP-Intent:** `design-dashboard`

#### 12.2.2 `analytics-data-explorer` - Data-Explorer
- **Pattern:** OverviewPage
- **Features:** Ad-hoc-Analysen, Pivot, Export
- **MCP-Intent:** `explore-data`

#### 12.2.3 `analytics-prognose-modelle` - Prognose-Modelle (AI)
- **Pattern:** OverviewPage
- **Features:** Absatz, Lagerbestand, Liquidität, Preise
- **MCP-Intent:** `forecast-models`

#### 12.2.4 `analytics-anomalie-erkennung` - Anomalie-Erkennung (AI)
- **Pattern:** Worklist
- **Features:** Preis-Anomalien, Qualitäts-Anomalien, Betrug
- **MCP-Intent:** `detect-anomalies`

---

### 12.3 Compliance-Reports (4 Masken)

#### 12.3.1 `reports-qs-milch` - QS-Milch-Report
- **Pattern:** OverviewPage
- **MCP-Intent:** `report-qs-milk`

#### 12.3.2 `reports-eudr` - EUDR-Konformitäts-Report
- **Pattern:** OverviewPage
- **MCP-Intent:** `report-eudr`

#### 12.3.3 `reports-nachhaltigkeit` - Nachhaltigkeits-Report
- **Pattern:** OverviewPage
- **Features:** CSRD, ESG, CO2
- **MCP-Intent:** `report-sustainability`

#### 12.3.4 `reports-audit-trail` - Audit-Trail-Report
- **Pattern:** ListReport
- **MCP-Intent:** `report-audit-trail`

---

## 🎯 ZUSAMMENFASSUNG

### Statistik nach SAP Fiori Pattern:

| Pattern | Anzahl | Prozent |
|---------|--------|---------|
| **ListReport** | 68 | 37% |
| **ObjectPage** | 54 | 30% |
| **Wizard** | 32 | 18% |
| **OverviewPage** | 22 | 12% |
| **Worklist** | 16 | 9% |
| **GESAMT** | **192** | 100% |

### Prioritäten-Matrix:

**Phase 1 (MVP - 3 Monate):** 60 Masken
- Agrarprodukte: Stammdaten, Listen, Bestellungen
- Futtermittel: Stammdaten, Mischungen, QS
- Chargenverwaltung: Basis-Features
- Waagen: Grundfunktionen
- Lager: Basis-Bewegungen
- Einkauf/Verkauf: Kernprozesse
- Finanzen: Debitoren, Kreditoren

**Phase 2 (Erweitert - 3 Monate):** 62 Masken
- Compliance: QS-Systeme, Zulassungen
- Nachhaltigkeit: EUDR, Nachhaltig-Raps
- Logistik: Tourenplanung, Tracking
- CRM: Kontakte, Landwirt-Profile
- Reports: Standard-Reports

**Phase 3 (Komplett - 3 Monate):** 60 Masken
- Analytics: AI-Features
- Administration: Vollständig
- Advanced Reports: BI, Prognosen
- Optimierungen: AI-gestützte Tools

---

## 📋 NÄCHSTE SCHRITTE

1. **Sofort:** Priorisierung Phase 1 Masken (60 Stück)
2. **Woche 1:** SAP Fiori Pattern-Components implementieren (ListReport, ObjectPage, etc.)
3. **Woche 2:** Erste 10 Agrar-Masken implementieren
4. **Woche 3:** Chargenverwaltung (18 Masken)
5. **Woche 4:** Futtermittel-Basis (10 Masken)

**Status:** ✅ Katalog komplett - Bereit für Implementierung!

---

**🌾 LANDHANDEL-SPEZIFISCHER MASKEN-KATALOG: 192 MASKEN DEFINIERT! 📊**

