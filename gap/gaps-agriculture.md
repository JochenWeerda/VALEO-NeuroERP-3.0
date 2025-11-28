***REMOVED*** GAP-Analyse: Agriculture Management

**Domain:** Agrar / Landwirtschaft
**Referenz:** Odoo Agriculture Management Module
**Status:** In Progress
**Erstellt:** 2025-11-27

---

***REMOVED******REMOVED*** 📋 Übersicht

***REMOVED******REMOVED******REMOVED*** Odoo Agriculture Management Features (Referenz)

| Feature | Beschreibung | Priorität |
|---------|-------------|-----------|
| Kulturverwaltung | Planung und Verfolgung verschiedener Kulturen, Dokumentation von Kulturtypen und Pflanzplänen, Überwachung von Wachstumsstadien | P0 |
| Inventarverfolgung | Verwaltung von Saatgut, Düngemitteln, Pestiziden mit Echtzeit-Überwachung und automatischer Nachbestellung | P1 |
| Feldoperationen | Planung, Terminierung und Aufzeichnung aller Feldaktivitäten (Pflügen, Säen, Jäten, Ernten) mit Mapping-Tools | P0 |
| Bewässerungsmanagement | Planung und Überwachung von Bewässerungssystemen mit IoT-Integration | P2 |
| Viehverwaltung | Detaillierte Aufzeichnungen über Tiere, Zuchtprogramme, Fütterungspläne, Gesundheitsüberwachung | P3 |
| Vertrieb und Verkauf | Preisgestaltung, Auftrags- und Liefermanagement, E-Commerce-Integration | P1 |
| Finanzmanagement | Budgetierung, Finanzberichterstattung, Kostenverfolgung | P1 |
| Compliance und Berichterstattung | Regulatorische Compliance, Umweltbewertungen, Subventionsanträge | P0 |
| Personalmanagement | Gehaltsabrechnung, Zeitpläne, Leistungsbeurteilungen | P2 |
| Technologieintegration | Drohnen, autonome Traktoren, KI-Modelle | P3 |
| Feldbesuche | Dokumentation von Feldbesuchen und Inspektionen | P1 |
| Kulturkrankheiten | Verfolgung von Krankheiten und Behandlungen | P1 |

---

***REMOVED******REMOVED*** 🎯 Spezifische Anforderungen VALEO NeuroERP

***REMOVED******REMOVED******REMOVED*** Kernmodul: Ackerschlagkartei (Feldbuch)

**Anforderung:** Multi-Tenant Ackerschlagkartei für Dienstleister

- **Hintergrund:** Als Dienstleister führen wir Düngen und PSM-Behandlungen für unsere Kunden aus und dokumentieren dies in kundenspezifischen Ackerschlagkarteien (Feldbuch)
- **Mandantenfähigkeit:** Jeder Kunde (Landwirt) ist ein eigener Tenant mit eigenen Schlägen und Maßnahmen
- **Feldblockfinder-Integration:** Verknüpfung mit dem deutschen Feldblockfinder per iframe

---

***REMOVED******REMOVED*** 📊 GAP-Matrix

***REMOVED******REMOVED******REMOVED*** AGR-FLD: Feldverwaltung

| ID | Capability | Subcapability | Status | Gap-Beschreibung | Lösungstyp | Priorität |
|----|-----------|---------------|--------|------------------|------------|-----------|
| AGR-FLD-01 | Schlagverwaltung | Schläge anlegen/bearbeiten | Partial | Basis vorhanden, keine API-Anbindung | Type B | P0 |
| AGR-FLD-02 | Schlagverwaltung | Mandantenfähigkeit | No | Keine Multi-Tenant-Unterstützung für Kundenschläge | Type C | P0 |
| AGR-FLD-03 | Feldblockfinder | iframe-Integration | No | Kein Feldblockfinder integriert | Type B | P0 |
| AGR-FLD-04 | Feldkarten | GIS-Visualisierung | Partial | Basis Kartendarstellung vorhanden | Type C | P1 |
| AGR-FLD-05 | Feldgrenzen | Polygon-Erfassung | No | Keine Polygon-Erfassung möglich | Type C | P2 |

***REMOVED******REMOVED******REMOVED*** AGR-OPS: Feldoperationen

| ID | Capability | Subcapability | Status | Gap-Beschreibung | Lösungstyp | Priorität |
|----|-----------|---------------|--------|------------------|------------|-----------|
| AGR-OPS-01 | Maßnahmen-Dokumentation | Erfassung Düngung/PSM | Partial | Basis vorhanden, keine API | Type B | P0 |
| AGR-OPS-02 | Maßnahmen-Dokumentation | Mandantenfähigkeit | No | Keine Zuordnung zu Kunden-Tenants | Type C | P0 |
| AGR-OPS-03 | Maßnahmen-Dokumentation | Mitarbeiter-Zuordnung | No | Keine Dienstleister-Mitarbeiter-Zuordnung | Type C | P1 |
| AGR-OPS-04 | Feldkalender | Planung/Terminierung | No | Kein Planungskalender vorhanden | Type C | P1 |
| AGR-OPS-05 | GPS-Tracking | Maschinen-Position | No | Keine GPS-Integration | Type B | P3 |

***REMOVED******REMOVED******REMOVED*** AGR-INV: Betriebsmittelverwaltung

| ID | Capability | Subcapability | Status | Gap-Beschreibung | Lösungstyp | Priorität |
|----|-----------|---------------|--------|------------------|------------|-----------|
| AGR-INV-01 | Düngemittel | Bestandsverwaltung | Partial | Stammdaten vorhanden, keine Bestandsführung | Type A | P1 |
| AGR-INV-02 | Pflanzenschutzmittel | PSM-Register | Partial | Stammdaten vorhanden, PSM-Auflagen fehlen | Type A | P1 |
| AGR-INV-03 | Saatgut | Sortenregister | Partial | Basis vorhanden | Type A | P2 |
| AGR-INV-04 | Automatische Nachbestellung | Mindestbestand-Warnung | No | Keine automatische Nachbestellung | Type B | P2 |

***REMOVED******REMOVED******REMOVED*** AGR-COM: Compliance & Berichterstattung

| ID | Capability | Subcapability | Status | Gap-Beschreibung | Lösungstyp | Priorität |
|----|-----------|---------------|--------|------------------|------------|-----------|
| AGR-COM-01 | Düngebilanz | Stoffstrombilanz | No | Keine Düngebilanz-Berechnung | Type C | P0 |
| AGR-COM-02 | PSM-Dokumentation | Spritztagebuch | Partial | Basis vorhanden, nicht compliant | Type A | P0 |
| AGR-COM-03 | Cross-Compliance | CC-Berichte | No | Keine Cross-Compliance-Berichte | Type C | P1 |
| AGR-COM-04 | GQS/QS-Export | Qualitätssicherung | No | Kein QS-Export | Type B | P2 |
| AGR-COM-05 | LEA-Export | Förderanträge | No | Kein LEA-Export | Type B | P2 |

---

***REMOVED******REMOVED*** 🏗️ Implementierungsplan

***REMOVED******REMOVED******REMOVED*** Phase 1: Mandantenfähige Ackerschlagkartei (P0) - 4-6 Wochen

***REMOVED******REMOVED******REMOVED******REMOVED*** 1.1 Backend: Multi-Tenant Datenmodell
- [ ] Tenant-Erweiterung für Agrar-Entitäten (Schläge, Maßnahmen)
- [ ] Kunden-Schlag-Zuordnung
- [ ] Dienstleister-Maßnahmen-Dokumentation

***REMOVED******REMOVED******REMOVED******REMOVED*** 1.2 Frontend: Mandantenauswahl
- [ ] Kundenauswahl-Komponente in Schlagkartei
- [ ] Filterung nach Kunden-Tenant
- [ ] Maßnahmen-Zuordnung zu Kunden

***REMOVED******REMOVED******REMOVED******REMOVED*** 1.3 Feldblockfinder-Integration
- [ ] iframe-Komponente für Feldblockfinder
- [ ] URL-Konfiguration pro Bundesland
- [ ] Schlag-Übernahme aus Feldblockfinder

***REMOVED******REMOVED******REMOVED*** Phase 2: Compliance-Module (P0-P1) - 3-4 Wochen

***REMOVED******REMOVED******REMOVED******REMOVED*** 2.1 Düngebilanz
- [ ] Stoffstrombilanz-Berechnung
- [ ] Nährstoffvergleich
- [ ] Export (PDF/CSV)

***REMOVED******REMOVED******REMOVED******REMOVED*** 2.2 PSM-Dokumentation
- [ ] Spritztagebuch gemäß PflSchG
- [ ] Anwenderschutz-Dokumentation
- [ ] Auflagenprüfung

***REMOVED******REMOVED******REMOVED*** Phase 3: Erweiterte Features (P1-P2) - 4-6 Wochen

- [ ] Feldkalender mit Planung
- [ ] GIS-Integration erweitern
- [ ] QS/LEA-Export
- [ ] Automatische Nachbestellung

---

***REMOVED******REMOVED*** 🔗 Feldblockfinder-Integration

***REMOVED******REMOVED******REMOVED*** Verfügbare Feldblockfinder nach Bundesland

| Bundesland | URL | Hinweise |
|------------|-----|----------|
| Niedersachsen | https://sla.niedersachsen.de/mapbender_sla/frames/login_flink.php | FLINK-Viewer |
| Bayern | https://www.lfl.bayern.de/iab/bodenschutz/019127/index.php | iBalis |
| Schleswig-Holstein | https://www.schleswig-holstein.de/DE/landesregierung/ministerien-behoerden/LLUR/Aufgaben/Boden/feldblockfinder.html | - |
| NRW | https://www.landwirtschaftskammer.de/foerderung/flaechenidentifizierung/ | - |

***REMOVED******REMOVED******REMOVED*** iframe-Integration

```tsx
// Komponente: FeldblockfinderIntegration.tsx
interface FeldblockfinderProps {
  bundesland: string;
  onSchlagSelected?: (schlagData: SchlagData) => void;
}

const FELDBLOCKFINDER_URLS: Record<string, string> = {
  'niedersachsen': 'https://sla.niedersachsen.de/mapbender_sla/frames/login_flink.php',
  'bayern': 'https://www.lfl.bayern.de/iab/bodenschutz/019127/index.php',
  // ... weitere Bundesländer
};
```

***REMOVED******REMOVED******REMOVED*** Hinweise zur Integration

1. **Cross-Origin-Policy:** Einige Feldblockfinder blockieren iframe-Einbettung
2. **Alternative:** Link in neuem Tab öffnen + manuelle Datenübernahme
3. **Responsives Design:** iframe sollte sich an Bildschirmgröße anpassen

---

***REMOVED******REMOVED*** 📈 Status-Zusammenfassung

| Domain | Gesamt | Yes | Partial | No |
|--------|--------|-----|---------|-----|
| Feldverwaltung | 5 | 0 | 2 | 3 |
| Feldoperationen | 5 | 0 | 1 | 4 |
| Betriebsmittel | 4 | 0 | 3 | 1 |
| Compliance | 5 | 0 | 1 | 4 |
| **Gesamt** | **19** | **0 (0%)** | **7 (37%)** | **12 (63%)** |

---

***REMOVED******REMOVED*** 📝 Nächste Schritte

1. ✅ Gap-Analyse erstellt
2. ✅ Frontend: Mandantenauswahl in Schlagkartei implementiert
3. ✅ Frontend: Feldblockfinder iframe-Integration erstellt
4. ✅ Frontend: Maßnahmen-Dokumentation mit Spritztagebuch erweitert
5. ✅ Navigation: Futtermittel-Routen verdrahtet
6. ✅ **Kundenportal komplett implementiert** (siehe unten)
7. ✅ **Compliance: Düngebilanz-Modul / Stoffstrombilanz** implementiert
8. ⏳ Backend: Multi-Tenant Erweiterung für Agrar-Entitäten (API)
9. ⏳ GIS: Erweiterte Kartenintegration mit Leaflet/OpenLayers

---

***REMOVED******REMOVED*** ✅ Implementierte Features (2025-11-27)

***REMOVED******REMOVED******REMOVED*** Mandantenfähige Ackerschlagkartei
- **Datei:** `packages/frontend-web/src/pages/agrar/feldbuch/schlagkartei.tsx`
- Multi-Tenant Kundenauswahl
- Filterung nach Kunde, Status, Kultur
- KPI-Dashboard mit Skeleton-Loading
- Tabs: Liste, Karte, Kulturübersicht

***REMOVED******REMOVED******REMOVED*** Feldblockfinder-Integration
- **Datei:** `packages/frontend-web/src/components/agrar/FeldblockfinderIntegration.tsx`
- Bundesland-Auswahl für alle 16 Bundesländer
- Fallback auf externen Link wenn iframe blockiert
- Manuelle Schlagdaten-Eingabe
- Dialog-Integration in Schlagkartei

***REMOVED******REMOVED******REMOVED*** Maßnahmen-Dokumentation / Spritztagebuch
- **Datei:** `packages/frontend-web/src/pages/agrar/feldbuch/massnahmen.tsx`
- Multi-Tenant Kundenzuordnung
- Spritztagebuch-Tab gemäß § 11 PflSchG
- PSM-Auflagen-Dokumentation
- Wetterdaten (Wind, Temperatur)
- Anwender/Geräte-Zuordnung

***REMOVED******REMOVED******REMOVED*** Futtermittel-Navigation
- Vollständiges Untermenü für Futtermittel
- Einzelfuttermittel, Mischfuttermittel
- Wareneingang, Qualitätskontrolle, Statistik

---

***REMOVED******REMOVED*** 🛒 Kundenportal (Implementiert 2025-11-28)

***REMOVED******REMOVED******REMOVED*** Übersicht
Vollständiges Self-Service-Portal für Kunden mit mobilem Zugang (Handy/Tablet)

**Route:** `/portal/*`
**Layout:** `CustomerPortalLayout.tsx` (separates, mobil-optimiertes Layout)

***REMOVED******REMOVED******REMOVED*** Implementierte Module

***REMOVED******REMOVED******REMOVED******REMOVED*** 1. Portal Dashboard (`/portal`)
- **Datei:** `packages/frontend-web/src/pages/portal/index.tsx`
- Willkommens-Header mit Kundendaten
- KPI-Übersicht (offene Bestellungen, Verträge, Rechnungen, Dokumente)
- Letzte Bestellungen mit Status-Badges
- Neue Dokumente zum Download
- Schnellzugriff-Karten für häufige Funktionen

***REMOVED******REMOVED******REMOVED******REMOVED*** 2. E-Shop (`/portal/shop`)
- **Datei:** `packages/frontend-web/src/pages/portal/shop.tsx`
- Produktkatalog mit Kategorien (Saatgut, Dünger, PSM, Futtermittel)
- Suchfunktion und Filterung
- Warenkorb mit Mengenänderung
- Bestellabschluss
- Anfrage-Dialog für individuelle Angebote
- Produktkarten mit Zertifikats-Badges

***REMOVED******REMOVED******REMOVED******REMOVED*** 3. Meine Bestellungen (`/portal/bestellungen`)
- **Datei:** `packages/frontend-web/src/pages/portal/bestellungen.tsx`
- Bestellübersicht mit Status-Filter
- Detailansicht mit Positionen
- Sendungsverfolgung (Trackingnummer)
- Rechnungs-Download
- KPIs: Offene, Unterwegs, Abgeschlossen

***REMOVED******REMOVED******REMOVED******REMOVED*** 4. Anfragen (`/portal/anfragen`)
- **Datei:** `packages/frontend-web/src/pages/portal/anfragen.tsx`
- Angebotsanfragen, Bestellanfragen, Dienstleistungen
- Status-Tracking (Offen → In Bearbeitung → Beantwortet → Abgeschlossen)
- Dialog zum Erstellen neuer Anfragen
- Antwort-Anzeige vom VALEO-Team

***REMOVED******REMOVED******REMOVED******REMOVED*** 5. Verträge & Kontrakte (`/portal/vertraege`)
- **Datei:** `packages/frontend-web/src/pages/portal/vertraege.tsx`
- Rahmenverträge, Lieferverträge, Preiskontrakte
- Vertragserfüllung mit Fortschrittsbalken
- Status: Aktiv, Auslaufend, Abgelaufen
- Vertragsvolumen und Preise
- PDF-Download

***REMOVED******REMOVED******REMOVED******REMOVED*** 6. Rechnungen (`/portal/rechnungen`)
- **Datei:** `packages/frontend-web/src/pages/portal/rechnungen.tsx`
- Offene und bezahlte Rechnungen
- Überfälligkeits-Warnung
- Zahlungsstatus und Teilzahlungen
- Brutto/Netto/MwSt-Aufschlüsselung
- PDF-Download

***REMOVED******REMOVED******REMOVED******REMOVED*** 7. Dokumente (`/portal/dokumente`)
- **Datei:** `packages/frontend-web/src/pages/portal/dokumente.tsx`
- Kategorien: Nährstoffbilanzen, Analysen, Deklarationen, Rechnungen, Lieferscheine
- Jahresfilter
- Schnellzugriff nach Dokumenttyp
- PDF/CSV/XLSX Download

***REMOVED******REMOVED******REMOVED******REMOVED*** 8. Zertifikate (`/portal/zertifikate`)
- **Datei:** `packages/frontend-web/src/pages/portal/zertifikate.tsx`
- GMP+, VLOG, QS, Bio, ISO, GLOBALG.A.P., AMA
- Gültigkeitsstatus mit Auslauf-Warnung
- Aussteller und Beschreibung
- PDF-Download

***REMOVED******REMOVED******REMOVED******REMOVED*** 9. Ackerschlagkartei (`/portal/feldbuch`)
- **Datei:** `packages/frontend-web/src/pages/portal/feldbuch.tsx`
- Schlagübersicht mit FLIK-Nummern
- Maßnahmen-Dokumentation (Düngung, PSM, Aussaat, Ernte)
- CSV-Export für Schläge und Maßnahmen
- CSV-Import für Datenübernahme
- VALEO-Dienstleistungen markiert

***REMOVED******REMOVED******REMOVED******REMOVED*** 10. Nährstoffbilanzen (`/portal/naehrstoffbilanzen`)
- **Datei:** `packages/frontend-web/src/pages/portal/naehrstoffbilanzen.tsx`
- Stoffstrombilanz gemäß DüV
- N-, P-, K-Salden mit Grenzwertprüfung
- 3-Jahres-Durchschnitt-Berechnung
- Schlagbezogene Übersicht
- Compliance-Status (Grenzwerte eingehalten/überschritten)
- Historische Bilanzen
- PDF-Download

***REMOVED******REMOVED******REMOVED*** Technische Features
- **Responsives Design:** Optimiert für Mobile/Tablet
- **Bottom Navigation:** Touch-freundliche Navigation auf mobilen Geräten
- **Skeleton Loading:** Platzhalter während Datenladung
- **Toast Notifications:** Feedback bei Aktionen
- **Dialoge:** Modale Dialoge für Details und Formulare

---

**Letzte Aktualisierung:** 2025-11-28

