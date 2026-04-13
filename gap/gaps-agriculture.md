# GAP-Analyse: Agriculture Management

**Domain:** Agrar / Landwirtschaft
**Referenz:** Community ERP Agriculture Management Module
**Status:** In Progress
**Erstellt:** 2025-11-27

---

## ðŸ“‹ Ãœbersicht

### Community ERP Agriculture Management Features (Referenz)

| Feature | Beschreibung | PrioritÃ¤t |
|---------|-------------|-----------|
| Kulturverwaltung | Planung und Verfolgung verschiedener Kulturen, Dokumentation von Kulturtypen und PflanzplÃ¤nen, Ãœberwachung von Wachstumsstadien | P0 |
| Inventarverfolgung | Verwaltung von Saatgut, DÃ¼ngemitteln, Pestiziden mit Echtzeit-Ãœberwachung und automatischer Nachbestellung | P1 |
| Feldoperationen | Planung, Terminierung und Aufzeichnung aller FeldaktivitÃ¤ten (PflÃ¼gen, SÃ¤en, JÃ¤ten, Ernten) mit Mapping-Tools | P0 |
| BewÃ¤sserungsmanagement | Planung und Ãœberwachung von BewÃ¤sserungssystemen mit IoT-Integration | P2 |
| Viehverwaltung | Detaillierte Aufzeichnungen Ã¼ber Tiere, Zuchtprogramme, FÃ¼tterungsplÃ¤ne, GesundheitsÃ¼berwachung | P3 |
| Vertrieb und Verkauf | Preisgestaltung, Auftrags- und Liefermanagement, E-Commerce-Integration | P1 |
| Finanzmanagement | Budgetierung, Finanzberichterstattung, Kostenverfolgung | P1 |
| Compliance und Berichterstattung | Regulatorische Compliance, Umweltbewertungen, SubventionsantrÃ¤ge | P0 |
| Personalmanagement | Gehaltsabrechnung, ZeitplÃ¤ne, Leistungsbeurteilungen | P2 |
| Technologieintegration | Drohnen, autonome Traktoren, KI-Modelle | P3 |
| Feldbesuche | Dokumentation von Feldbesuchen und Inspektionen | P1 |
| Kulturkrankheiten | Verfolgung von Krankheiten und Behandlungen | P1 |

---

## ðŸŽ¯ Spezifische Anforderungen VALEO NeuroERP

### Kernmodul: Ackerschlagkartei (Feldbuch)

**Anforderung:** Multi-Tenant Ackerschlagkartei fÃ¼r Dienstleister

- **Hintergrund:** Als Dienstleister fÃ¼hren wir DÃ¼ngen und PSM-Behandlungen fÃ¼r unsere Kunden aus und dokumentieren dies in kundenspezifischen Ackerschlagkarteien (Feldbuch)
- **MandantenfÃ¤higkeit:** Jeder Kunde (Landwirt) ist ein eigener Tenant mit eigenen SchlÃ¤gen und MaÃŸnahmen
- **Feldblockfinder-Integration:** VerknÃ¼pfung mit dem deutschen Feldblockfinder per iframe

---

## ðŸ“Š GAP-Matrix

### AGR-FLD: Feldverwaltung

| ID | Capability | Subcapability | Status | Gap-Beschreibung | LÃ¶sungstyp | PrioritÃ¤t |
|----|-----------|---------------|--------|------------------|------------|-----------|
| AGR-FLD-01 | Schlagverwaltung | SchlÃ¤ge anlegen/bearbeiten | Partial | Basis vorhanden, keine API-Anbindung | Type B | P0 |
| AGR-FLD-02 | Schlagverwaltung | MandantenfÃ¤higkeit | No | Keine Multi-Tenant-UnterstÃ¼tzung fÃ¼r KundenschlÃ¤ge | Type C | P0 |
| AGR-FLD-03 | Feldblockfinder | iframe-Integration | No | Kein Feldblockfinder integriert | Type B | P0 |
| AGR-FLD-04 | Feldkarten | GIS-Visualisierung | Partial | Basis Kartendarstellung vorhanden | Type C | P1 |
| AGR-FLD-05 | Feldgrenzen | Polygon-Erfassung | No | Keine Polygon-Erfassung mÃ¶glich | Type C | P2 |

### AGR-OPS: Feldoperationen

| ID | Capability | Subcapability | Status | Gap-Beschreibung | LÃ¶sungstyp | PrioritÃ¤t |
|----|-----------|---------------|--------|------------------|------------|-----------|
| AGR-OPS-01 | MaÃŸnahmen-Dokumentation | Erfassung DÃ¼ngung/PSM | Partial | Basis vorhanden, keine API | Type B | P0 |
| AGR-OPS-02 | MaÃŸnahmen-Dokumentation | MandantenfÃ¤higkeit | No | Keine Zuordnung zu Kunden-Tenants | Type C | P0 |
| AGR-OPS-03 | MaÃŸnahmen-Dokumentation | Mitarbeiter-Zuordnung | No | Keine Dienstleister-Mitarbeiter-Zuordnung | Type C | P1 |
| AGR-OPS-04 | Feldkalender | Planung/Terminierung | No | Kein Planungskalender vorhanden | Type C | P1 |
| AGR-OPS-05 | GPS-Tracking | Maschinen-Position | No | Keine GPS-Integration | Type B | P3 |

### AGR-INV: Betriebsmittelverwaltung

| ID | Capability | Subcapability | Status | Gap-Beschreibung | LÃ¶sungstyp | PrioritÃ¤t |
|----|-----------|---------------|--------|------------------|------------|-----------|
| AGR-INV-01 | DÃ¼ngemittel | Bestandsverwaltung | Partial | Stammdaten vorhanden, keine BestandsfÃ¼hrung | Type A | P1 |
| AGR-INV-02 | Pflanzenschutzmittel | PSM-Register | Partial | Stammdaten vorhanden, PSM-Auflagen fehlen | Type A | P1 |
| AGR-INV-03 | Saatgut | Sortenregister | Partial | Basis vorhanden | Type A | P2 |
| AGR-INV-04 | Automatische Nachbestellung | Mindestbestand-Warnung | No | Keine automatische Nachbestellung | Type B | P2 |

### AGR-COM: Compliance & Berichterstattung

| ID | Capability | Subcapability | Status | Gap-Beschreibung | LÃ¶sungstyp | PrioritÃ¤t |
|----|-----------|---------------|--------|------------------|------------|-----------|
| AGR-COM-01 | DÃ¼ngebilanz | Stoffstrombilanz | No | Keine DÃ¼ngebilanz-Berechnung | Type C | P0 |
| AGR-COM-02 | PSM-Dokumentation | Spritztagebuch | Partial | Basis vorhanden, nicht compliant | Type A | P0 |
| AGR-COM-03 | Cross-Compliance | CC-Berichte | No | Keine Cross-Compliance-Berichte | Type C | P1 |
| AGR-COM-04 | GQS/QS-Export | QualitÃ¤tssicherung | No | Kein QS-Export | Type B | P2 |
| AGR-COM-05 | LEA-Export | FÃ¶rderantrÃ¤ge | No | Kein LEA-Export | Type B | P2 |

---

## ðŸ—ï¸ Implementierungsplan

### Phase 1: MandantenfÃ¤hige Ackerschlagkartei (P0) - 4-6 Wochen

#### 1.1 Backend: Multi-Tenant Datenmodell
- [ ] Tenant-Erweiterung fÃ¼r Agrar-EntitÃ¤ten (SchlÃ¤ge, MaÃŸnahmen)
- [ ] Kunden-Schlag-Zuordnung
- [ ] Dienstleister-MaÃŸnahmen-Dokumentation

#### 1.2 Frontend: Mandantenauswahl
- [ ] Kundenauswahl-Komponente in Schlagkartei
- [ ] Filterung nach Kunden-Tenant
- [ ] MaÃŸnahmen-Zuordnung zu Kunden

#### 1.3 Feldblockfinder-Integration
- [ ] iframe-Komponente fÃ¼r Feldblockfinder
- [ ] URL-Konfiguration pro Bundesland
- [ ] Schlag-Ãœbernahme aus Feldblockfinder

### Phase 2: Compliance-Module (P0-P1) - 3-4 Wochen

#### 2.1 DÃ¼ngebilanz
- [ ] Stoffstrombilanz-Berechnung
- [ ] NÃ¤hrstoffvergleich
- [ ] Export (PDF/CSV)

#### 2.2 PSM-Dokumentation
- [ ] Spritztagebuch gemÃ¤ÃŸ PflSchG
- [ ] Anwenderschutz-Dokumentation
- [ ] AuflagenprÃ¼fung

### Phase 3: Erweiterte Features (P1-P2) - 4-6 Wochen

- [ ] Feldkalender mit Planung
- [ ] GIS-Integration erweitern
- [ ] QS/LEA-Export
- [ ] Automatische Nachbestellung

---

## ðŸ”— Feldblockfinder-Integration

### VerfÃ¼gbare Feldblockfinder nach Bundesland

| Bundesland | URL | Hinweise |
|------------|-----|----------|
| Niedersachsen | https://sla.niedersachsen.de/mapbender_sla/frames/login_flink.php | FLINK-Viewer |
| Bayern | https://www.lfl.bayern.de/iab/bodenschutz/019127/index.php | iBalis |
| Schleswig-Holstein | https://www.schleswig-holstein.de/DE/landesregierung/ministerien-behoerden/LLUR/Aufgaben/Boden/feldblockfinder.html | - |
| NRW | https://www.landwirtschaftskammer.de/foerderung/flaechenidentifizierung/ | - |

### iframe-Integration

```tsx
// Komponente: FeldblockfinderIntegration.tsx
interface FeldblockfinderProps {
  bundesland: string;
  onSchlagSelected?: (schlagData: SchlagData) => void;
}

const FELDBLOCKFINDER_URLS: Record<string, string> = {
  'niedersachsen': 'https://sla.niedersachsen.de/mapbender_sla/frames/login_flink.php',
  'bayern': 'https://www.lfl.bayern.de/iab/bodenschutz/019127/index.php',
  // ... weitere BundeslÃ¤nder
};
```

### Hinweise zur Integration

1. **Cross-Origin-Policy:** Einige Feldblockfinder blockieren iframe-Einbettung
2. **Alternative:** Link in neuem Tab Ã¶ffnen + manuelle DatenÃ¼bernahme
3. **Responsives Design:** iframe sollte sich an BildschirmgrÃ¶ÃŸe anpassen

---

## ðŸ“ˆ Status-Zusammenfassung

| Domain | Gesamt | Yes | Partial | No |
|--------|--------|-----|---------|-----|
| Feldverwaltung | 5 | 0 | 2 | 3 |
| Feldoperationen | 5 | 0 | 1 | 4 |
| Betriebsmittel | 4 | 0 | 3 | 1 |
| Compliance | 5 | 0 | 1 | 4 |
| **Gesamt** | **19** | **0 (0%)** | **7 (37%)** | **12 (63%)** |

---

## ðŸ“ NÃ¤chste Schritte

1. âœ… Gap-Analyse erstellt
2. âœ… Frontend: Mandantenauswahl in Schlagkartei implementiert
3. âœ… Frontend: Feldblockfinder iframe-Integration erstellt
4. âœ… Frontend: MaÃŸnahmen-Dokumentation mit Spritztagebuch erweitert
5. âœ… Navigation: Futtermittel-Routen verdrahtet
6. âœ… **Kundenportal komplett implementiert** (siehe unten)
7. âœ… **Compliance: DÃ¼ngebilanz-Modul / Stoffstrombilanz** implementiert
8. â³ Backend: Multi-Tenant Erweiterung fÃ¼r Agrar-EntitÃ¤ten (API)
9. â³ GIS: Erweiterte Kartenintegration mit Leaflet/OpenLayers

---

## âœ… Implementierte Features (2025-11-27)

### MandantenfÃ¤hige Ackerschlagkartei
- **Datei:** `packages/frontend-web/src/pages/agrar/feldbuch/schlagkartei.tsx`
- Multi-Tenant Kundenauswahl
- Filterung nach Kunde, Status, Kultur
- KPI-Dashboard mit Skeleton-Loading
- Tabs: Liste, Karte, KulturÃ¼bersicht

### Feldblockfinder-Integration
- **Datei:** `packages/frontend-web/src/components/agrar/FeldblockfinderIntegration.tsx`
- Bundesland-Auswahl fÃ¼r alle 16 BundeslÃ¤nder
- Fallback auf externen Link wenn iframe blockiert
- Manuelle Schlagdaten-Eingabe
- Dialog-Integration in Schlagkartei

### MaÃŸnahmen-Dokumentation / Spritztagebuch
- **Datei:** `packages/frontend-web/src/pages/agrar/feldbuch/massnahmen.tsx`
- Multi-Tenant Kundenzuordnung
- Spritztagebuch-Tab gemÃ¤ÃŸ Â§ 11 PflSchG
- PSM-Auflagen-Dokumentation
- Wetterdaten (Wind, Temperatur)
- Anwender/GerÃ¤te-Zuordnung

### Futtermittel-Navigation
- VollstÃ¤ndiges UntermenÃ¼ fÃ¼r Futtermittel
- Einzelfuttermittel, Mischfuttermittel
- Wareneingang, QualitÃ¤tskontrolle, Statistik

---

## ðŸ›’ Kundenportal (Implementiert 2025-11-28)

### Ãœbersicht
VollstÃ¤ndiges Self-Service-Portal fÃ¼r Kunden mit mobilem Zugang (Handy/Tablet)

**Route:** `/portal/*`
**Layout:** `CustomerPortalLayout.tsx` (separates, mobil-optimiertes Layout)

### Implementierte Module

#### 1. Portal Dashboard (`/portal`)
- **Datei:** `packages/frontend-web/src/pages/portal/index.tsx`
- Willkommens-Header mit Kundendaten
- KPI-Ãœbersicht (offene Bestellungen, VertrÃ¤ge, Rechnungen, Dokumente)
- Letzte Bestellungen mit Status-Badges
- Neue Dokumente zum Download
- Schnellzugriff-Karten fÃ¼r hÃ¤ufige Funktionen

#### 2. E-Shop (`/portal/shop`)
- **Datei:** `packages/frontend-web/src/pages/portal/shop.tsx`
- Produktkatalog mit Kategorien (Saatgut, DÃ¼nger, PSM, Futtermittel)
- Suchfunktion und Filterung
- Warenkorb mit MengenÃ¤nderung
- Bestellabschluss
- Anfrage-Dialog fÃ¼r individuelle Angebote
- Produktkarten mit Zertifikats-Badges

#### 3. Meine Bestellungen (`/portal/bestellungen`)
- **Datei:** `packages/frontend-web/src/pages/portal/bestellungen.tsx`
- BestellÃ¼bersicht mit Status-Filter
- Detailansicht mit Positionen
- Sendungsverfolgung (Trackingnummer)
- Rechnungs-Download
- KPIs: Offene, Unterwegs, Abgeschlossen

#### 4. Anfragen (`/portal/anfragen`)
- **Datei:** `packages/frontend-web/src/pages/portal/anfragen.tsx`
- Angebotsanfragen, Bestellanfragen, Dienstleistungen
- Status-Tracking (Offen â†’ In Bearbeitung â†’ Beantwortet â†’ Abgeschlossen)
- Dialog zum Erstellen neuer Anfragen
- Antwort-Anzeige vom VALEO-Team

#### 5. VertrÃ¤ge & Kontrakte (`/portal/vertraege`)
- **Datei:** `packages/frontend-web/src/pages/portal/vertraege.tsx`
- RahmenvertrÃ¤ge, LiefervertrÃ¤ge, Preiskontrakte
- VertragserfÃ¼llung mit Fortschrittsbalken
- Status: Aktiv, Auslaufend, Abgelaufen
- Vertragsvolumen und Preise
- PDF-Download

#### 6. Rechnungen (`/portal/rechnungen`)
- **Datei:** `packages/frontend-web/src/pages/portal/rechnungen.tsx`
- Offene und bezahlte Rechnungen
- ÃœberfÃ¤lligkeits-Warnung
- Zahlungsstatus und Teilzahlungen
- Brutto/Netto/MwSt-AufschlÃ¼sselung
- PDF-Download

#### 7. Dokumente (`/portal/dokumente`)
- **Datei:** `packages/frontend-web/src/pages/portal/dokumente.tsx`
- Kategorien: NÃ¤hrstoffbilanzen, Analysen, Deklarationen, Rechnungen, Lieferscheine
- Jahresfilter
- Schnellzugriff nach Dokumenttyp
- PDF/CSV/XLSX Download

#### 8. Zertifikate (`/portal/zertifikate`)
- **Datei:** `packages/frontend-web/src/pages/portal/zertifikate.tsx`
- GMP+, VLOG, QS, Bio, ISO, GLOBALG.A.P., AMA
- GÃ¼ltigkeitsstatus mit Auslauf-Warnung
- Aussteller und Beschreibung
- PDF-Download

#### 9. Ackerschlagkartei (`/portal/feldbuch`)
- **Datei:** `packages/frontend-web/src/pages/portal/feldbuch.tsx`
- SchlagÃ¼bersicht mit FLIK-Nummern
- MaÃŸnahmen-Dokumentation (DÃ¼ngung, PSM, Aussaat, Ernte)
- CSV-Export fÃ¼r SchlÃ¤ge und MaÃŸnahmen
- CSV-Import fÃ¼r DatenÃ¼bernahme
- VALEO-Dienstleistungen markiert

#### 10. NÃ¤hrstoffbilanzen (`/portal/naehrstoffbilanzen`)
- **Datei:** `packages/frontend-web/src/pages/portal/naehrstoffbilanzen.tsx`
- Stoffstrombilanz gemÃ¤ÃŸ DÃ¼V
- N-, P-, K-Salden mit GrenzwertprÃ¼fung
- 3-Jahres-Durchschnitt-Berechnung
- Schlagbezogene Ãœbersicht
- Compliance-Status (Grenzwerte eingehalten/Ã¼berschritten)
- Historische Bilanzen
- PDF-Download

### Technische Features
- **Responsives Design:** Optimiert fÃ¼r Mobile/Tablet
- **Bottom Navigation:** Touch-freundliche Navigation auf mobilen GerÃ¤ten
- **Skeleton Loading:** Platzhalter wÃ¤hrend Datenladung
- **Toast Notifications:** Feedback bei Aktionen
- **Dialoge:** Modale Dialoge fÃ¼r Details und Formulare

---

**Letzte Aktualisierung:** 2025-11-28



