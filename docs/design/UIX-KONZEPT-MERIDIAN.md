# UIX-Konzept MERIDIAN — VALEO NeuroERP 3.0

> Stand: 2026-05-18 | Basis: MERIDIAN Design-System v1.0
> Zielgruppe: Agrarhandel-Genossenschaften, Landhandelsunternehmen

---

## 1. IST-Zustand UIX-Bewertung

### Stärken (bereits implementiert)

| Bereich | Status | Bewertung |
|---|---|---|
| MERIDIAN Design-Token-System | Vollständig | ★★★★★ |
| Sidebar-Navigation mit Collapse | Funktional | ★★★★☆ |
| ObjectPage / ListReport / Wizard Framework | Stabil | ★★★★☆ |
| Keyboard-Shortcuts (Strg+S, Strg+K) | Implementiert | ★★★★☆ |
| Touch-Targets ≥ 44px (Button h-10) | Erfüllt | ★★★★☆ |
| Favoriten / Pinned Tiles | Vorhanden | ★★★☆☆ |
| Dark-Mode-Tokens | Definiert | ★★★☆☆ |
| Skeleton-Loading (DataTable) | Neu | ★★★☆☆ |
| KPI-Cards mit Trendindikator | Neu | ★★★☆☆ |
| Fehlerbehandlung / Toast | Basisimplementierung | ★★★☆☆ |

### Schwächen (Gap-Analyse Ausgangspunkt)

| Bereich | Problem | Priorität |
|---|---|---|
| `aria-current="page"` | Fehlt auf aktiven NavLinks (WCAG A-02) | Hoch |
| Mobile/Tablet-Layout | Kein responsives Seitenkonzept für Terminal-Nutzer | Hoch |
| Leerzustände (Empty States) | Generisch, kein domänenspezifischer Kontext | Mittel |
| Inline-Validierung | Nur bei Submit, nicht beim Verlassen eines Feldes | Mittel |
| Formular-Entwürfe | Kein `localStorage`-basiertes Auto-Save | Mittel |
| Gespeicherte Tabellenansichten | Nicht persistiert (Spaltenbreite, Filter, Sortierung) | Mittel |
| Offline-Indikator | Nur POS-Terminal, nicht global | Mittel |
| Zoom 200% | Nicht getestet, potenzielle Layout-Brüche | Mittel |
| Rollenabhängige Navigation | Nur Feature-Flags, keine Rollen-Sichtbarkeit | Mittel |
| Usability-Tests | Keine durchgeführt | Offen |

### Kennzahlen IST

- **Anzahl Navigationsebenen:** 3 (Sektion → Gruppe → Item)
- **Klicks bis Auftrag erfassen:** ~4 (Dashboard → Verkauf → Aufträge → Neu)
- **Durchschn. Ladezeit (Dev):** ~800ms (keine Messungen in Prod)
- **WCAG-Konformität:** ~85% (4 bekannte Lücken)
- **Mobile-Nutzbarkeit:** 40% (grundlegend responsiv, nicht optimiert)

---

## 2. Soll-Zustand

### Vision

> VALEO NeuroERP ist das schnellste ERP für den deutschen Agrarhandel — messbar weniger Klicks als SAP S/4, messbar weniger Schulungsaufwand als Dynamics 365, vollständig barrierefrei nach WCAG 2.2 AA.

### Quantitative Ziele (18-Monats-Horizont)

| Metrik | IST | SOLL |
|---|---|---|
| Klicks bis "Auftrag erfassen" | 4 | ≤ 2 |
| Zeit für Wareneingang (Erstnutzer) | >5 Min | <2 Min |
| Keyboard-only Navigation (alle Screens) | 60% | 100% |
| WCAG 2.2 AA Konformität | 85% | 100% |
| Mobile-Nutzbarkeit (Touch-Score) | 40% | 90% |
| Fehlerrate bei Formular-Eingaben | ungemessen | <5% |
| User Satisfaction Score (SUS) | ungemessen | ≥ 80/100 |

### Design-Prinzipien

1. **Fachlichkeit vor Technik** — Domänenbegriffe dominieren, technische IDs sind versteckt
2. **Kontext bewahren** — Zurück-Navigation verliert keine Daten; Breadcrumbs sind immer sichtbar
3. **Fehler früh, nicht spät** — Inline-Validierung beim Verlassen eines Feldes
4. **Terminal-first, Desktop-optimiert** — Touch-Targets und Kontrast erfüllen auch Sonnenlicht/Handschuhe
5. **Geschwindigkeit schlägt Vollständigkeit** — Kritische Workflows in ≤ 3 Klicks erreichbar

---

## 3. GAP-Analyse

### 3.1 Personas & Nutzungsszenarien

| Persona | Rolle | Primäre Workflows | Gerät | Besondere Anforderungen |
|---|---|---|---|---|
| **Lagerist** | Warenannahme, Einlagerung, Kommissionierung | Wareneingang, Inventur, Auslagerung | Tablet/Scanner | Touch 56px, Offline, Scan-Support, Handschuhe |
| **Sachbearbeiter Einkauf** | Bestellvorschläge, Lieferantenmanagement | Bestellvorschlag, Bestellung, Auftragseingang | Desktop | Keyboard-first, Autocomplete, Massen-Aktionen |
| **Außendienst** | Kundentermine, Angebote, Kontrakterfassung | Auftrag, Kontrakt, Kundenakte | Tablet/Mobile | Offline-Modus, schnelle Eingabe, Unterschrift |
| **Disponent** | Fuhrplanung, Tourenoptimierung | Tourenplanung, LKW-Beladung, Fahrerwesen | Dual-Screen | Karten-Integration, Drag&Drop, Echtzeit-Updates |
| **Buchhalter** | Kontierung, Monatsabschluss, Berichte | Buchung, Kontenplan, Bilanz, GuV | Desktop | Tabellen-Massen-Import, Shortcut-Dense, Kontierungsvorlagen |
| **Geschäftsführung** | Kennzahlen, Berichte, Genehmigungen | Dashboard, KPI-Board, Freigaben | Tablet/Desktop | Dashboards, 1-Klick-Freigaben, keine Dateneingabe |
| **Externer Landwirt** | Anbauflächen, Lieferungen, Abrechnungen | Feldregister, Liefertermine, Jahresabrechnung | Mobile | Vereinfachte Ansicht, wenig Fachbegriffe, Mehrsprachig |

**GAPs:**
- Keine rollenabhängige Navigation vorhanden (alle sehen alle Module)
- Kein Landwirt-Portal-Modus (vereinfachte UI für externe Nutzer)
- Scanner-Integration (Barcode/QR) nur in POS, nicht im Lager

---

### 3.2 Top-10-Workflows (Klick-Analyse)

| # | Workflow | IST-Klicks | SOLL-Klicks | GAP |
|---|---|---|---|---|
| 1 | Auftrag erfassen | 4 | 2 | Strg+N global, Quick-Actions auf Dashboard |
| 2 | Wareneingang buchen | 5 | 2 | Scanner-Trigger direkt auf Lager-Startseite |
| 3 | Feldbuch-Maßnahme erfassen | 6 | 3 | Schlag-Kontext aus Karte direkt öffnen |
| 4 | Eingangsrechnung prüfen + buchen | 7 | 3 | OCR-Vorschlag, 1-Klick-Bestätigen |
| 5 | Kontrakt anlegen (Agrar) | 5 | 3 | Vorlagen-Bibliothek, Partner-Autocomplete |
| 6 | Bestandsabfrage (Artikel) | 3 | 1 | Global-Search zeigt Bestand direkt |
| 7 | Monatsabschluss vorbereiten | 10 | 5 | Guided Wizard mit Checkliste |
| 8 | LKW-Beladung planen | 8 | 4 | Drag&Drop Reihenfolge, Auto-Tour-Vorschlag |
| 9 | Reklamation erfassen | 6 | 3 | Auftrag-Kontext → direkt Reklamationsmaske |
| 10 | Jahresabrechnung Landwirt | 12 | 6 | Wizard statt manuelle Buchungsfolge |

**GAPs:**
- Kein globales `Strg+N` für "Neu"-Aktionen kontextabhängig
- Keine Quick-Actions auf dem Dashboard
- Global-Search zeigt nur Navigation, keine Datenobjekte (Kunden, Artikel, Aufträge)

---

### 3.3 Informationsarchitektur

**IST-Struktur:**
```
Sidebar (4 Sektionen)
├── Core (Dashboard, Suche, Favoriten)
├── Commercial (Verkauf, Einkauf, Agrar, CRM, Lager)
├── Finance (FIBU, Controlling, Compliance)
└── Operations (Lager-Ops, Fuhrpark, Personal, POS)
```

**SOLL-Ergänzungen:**

```
Sidebar
├── [Persona-Filter] — rollenbasierte Vorauswahl
├── Favoriten (max. 6, persistent)
├── Zuletzt verwendet (max. 5, Session)
├── Core / Commercial / Finance / Operations
└── Settings (immer am Boden)

Global Search (Strg+K)
├── Navigation (jetzt vorhanden)
├── Daten: Kunden, Artikel, Aufträge (NEU)
├── Aktionen: "Neuer Auftrag", "Wareneingang buchen" (NEU)
└── Hilfe: Dokumentation, Video-Tutorials (NEU)
```

**GAPs:**
- Zuletzt-verwendet-Liste fehlt
- Global-Search hat keinen Daten- oder Aktions-Layer
- Breadcrumbs existieren nicht konsistent auf allen Seiten
- Kein `aria-current="page"` → Screenreader kennen aktive Seite nicht (WCAG A-02)

---

### 3.4 Tabellen-UX Regelwerk

**SOLL-Standard für alle ListReport-Tabellen:**

| Feature | Status | Spezifikation |
|---|---|---|
| Sticky Header | Teilweise | `position: sticky; top: 0` immer aktiviert |
| Spalten-Sortierung | Vorhanden | Shift+Klick für Multi-Sort |
| Spalten-Resize | Fehlt | Drag-Handle mit min-width 80px |
| Spalten-Sichtbarkeit | Fehlt | Spalten-Picker-Dropdown (Persist in localStorage) |
| Filter | Vorhanden | Debounce 300ms, URL-Sync für Bookmarkability |
| Gespeicherte Ansichten | Fehlt | "Ansicht speichern als..." → Profil-gebunden |
| Massenauswahl | Teilweise | Shift+Klick Range-Select, Strg+A Alle |
| Inline-Editing | Fehlt | Doppelklick → Edit-Modus (für einfache Felder) |
| Export | Teilweise | CSV immer, XLSX + PDF je nach Domain |
| Leerzustand | Generisch | Domänenspezifisch mit Handlungsempfehlung |
| Pagination vs. Infinite Scroll | Gemischt | Default: Pagination 25/50/100; Infinite nur für Feeds |
| Zeilen-Höhe | 40px (h-10) | Kompakt-Modus: 32px (h-8) Toggle |

**GAPs:**
- Keine Spalten-Resize-Funktion
- Keine gespeicherten Ansichten
- Leerzustände sind nicht domänenspezifisch
- Kein Kompakt-Modus Toggle

---

### 3.5 Formular-UX Standards

**SOLL-Regelwerk:**

| Feature | Status | Spezifikation |
|---|---|---|
| Inline-Validierung | Submit-only | Validierung on-blur (beim Verlassen des Feldes) |
| Pflichtfeld-Markierung | `*` vorhanden | `aria-required="true"` + visueller `*` |
| Autocomplete | Teilweise | Alle Fremdschlüssel-Felder: Typeahead mit Debounce 300ms |
| Speichern-Status | Toast-only | Persistenter Indikator in der Toolbar (Saved / Unsaved) |
| Formular-Entwürfe | Fehlt | Auto-Save in `localStorage` alle 30s, expliziter Restore-Banner |
| Tabulatorreihenfolge | Nicht geprüft | Logische DOM-Reihenfolge = Tab-Reihenfolge |
| Numerische Eingaben | Teilweise | `inputmode="decimal"`, `lang="de"` Dezimalkomma |
| Datumsfelder | Nativ `<input type="date">` | + Kalender-Picker für Tastatur-Nutzer |
| Fehler-Zusammenfassung | Fehlt | Bei Submit mit Fehlern: Fehler-Summary am Formularanfang mit Sprunglinks |
| Ladezeit Autocomplete | Unbekannt | Max. 200ms bis erste Treffer erscheinen |
| Feld-Abhängigkeiten | Teilweise | Bedingte Sichtbarkeit/Pflicht klar kommunizieren |

**GAPs:**
- Keine on-blur-Validierung implementiert (nur handleSubmit)
- Kein Auto-Save für Formularentwürfe
- Kein Fehler-Summary-Block bei Submit-Fehler mit mehreren Feldern
- Autocomplete (Typeahead) für Kunden/Artikel/Partner-Felder fehlt weitgehend

---

### 3.6 Systemzustände

**Vollständige State-Map:**

| Zustand | IST | SOLL |
|---|---|---|
| **Leer (Empty)** | "Keine Einträge vorhanden." | Icon + Titel + Beschreibung + primäre Aktion ("Ersten Auftrag anlegen") |
| **Laden (Loading)** | Skeleton (DataTable), Spinner (ObjectPage) | Skeleton für alle Listen; Progress-Bar (top) für Seitenübergänge |
| **Fehler — Netzwerk** | Error-Toast | Inline-Fehler-Banner mit Retry-Button |
| **Fehler — Validierung** | Red border + Toast | on-blur inline + Fehler-Summary auf Submit |
| **Fehler — Server (5xx)** | Toast | Fehlerseite mit Incident-ID + Support-Link |
| **Fehler — Berechtigung (403)** | Keine | "Keine Berechtigung" Inline-Meldung mit Kontakt-Link |
| **Erfolg (Success)** | Toast "Gespeichert" | Toast + Dirty-Indicator reset + optionale Weiterleitung |
| **Offline** | POS-only | Globaler Offline-Banner (orange) + Queue-Indikator |
| **Konflikt (Concurrent Edit)** | Nicht behandelt | Optimistic-Lock-Fehler → Diff-Dialog "Änderungen zusammenführen" |
| **Session abgelaufen** | Keycloak-Redirect | Inpage-Modal "Sitzung abgelaufen — neu anmelden" (Daten erhalten) |
| **Keine Daten (Filter-Ergebnis)** | Generisch | "Keine Ergebnisse für [Filter]" + Filter-Reset-Link |
| **Lange Operation** | Spinner | Progress-Dialog mit Abbrechen-Option für >3s Operationen |

**GAPs:**
- 403-Zustand: keine Implementierung
- Concurrent-Edit-Konflikt: nicht behandelt
- Session-Ablauf: harter Redirect (Datenverlust möglich)
- Offline-Banner nur POS — fehlt global

---

### 3.7 Accessibility (über Kontrast hinaus)

**WCAG 2.2 AA Vollprüfliste:**

| Kriterium | Status | Maßnahme |
|---|---|---|
| **Tastatur-Navigation** | 80% | Alle Modals: Focus-Trap. DataTable: Arrow-Keys für Row-Navigation |
| **Fokus-Sichtbarkeit** (2.4.11) | Implementiert | `focus-visible:ring-2 focus-visible:ring-white/20` ✓ |
| **`aria-current="page"`** | FEHLT (A-02) | NavLink erhält `aria-current={isActive ? "page" : undefined}` |
| **`aria-label` auf Icons** | Teilweise | Alle Icon-only-Buttons brauchen `aria-label` |
| **`aria-invalid` + Fehlertext** | Teilweise | Fehler-`<p>` erhält `role="alert"` + `id` verknüpft via `aria-describedby` |
| **Zoom 200%** | Nicht getestet | Kein horizontales Scrolling auf Haupt-Layouts; geprüft in Chrome Dev Tools |
| **Farbblindheit** | Nicht getestet | Kein Info rein über Farbe (Symbole zusätzlich zu Farbe) |
| **Sprache** (`lang="de"`) | Zu prüfen | `<html lang="de">` in index.html |
| **Skip-Link** | Implementiert | `#main-content` Skip-Link in design-tokens-meridian.css |
| **Screenreader (NVDA/VoiceOver)** | Nicht getestet | Manueller Test nach MERIDIAN-Deployment (A-03) |
| **`<table>` Semantik** | Zu prüfen | `<th scope="col/row">` auf allen DataTables |
| **Formular-Labels** | Vorhanden | Alle Inputs haben `<label for>` oder `aria-label` |
| **Modalfokus** | Zu prüfen | Escape schließt, Fokus kehrt zum Trigger zurück |
| **Karussel/Auto-Play** | N/A | Keine auto-bewegenden Inhalte |

**Priorisierte Maßnahmen (Hoch):**
1. `aria-current="page"` in Sidebar.tsx (1 Zeile — sofort umsetzbar)
2. `role="alert"` auf Fehler-Paragraphen in ObjectPage.tsx
3. Arrow-Key-Navigation in DataTable (WCAG A-04)
4. `lang="de"` in index.html prüfen

---

### 3.8 Mobile / Tablet / Terminal-Konzept

**Geräteklassen:**

| Klasse | Beispiele | Auflösung | Besonderheiten |
|---|---|---|---|
| **Wareneingangs-Terminal** | Zebra TC52, Honeywell EDA52 | 480×800 | Scanner, Handschuhe, Sonnenlicht |
| **Außendienst-Tablet** | iPad Pro 11", Surface Pro | 1024×768 | Touch, Stift, gelegentlich offline |
| **Lager-Tablet** | Samsung Tab A8 | 800×1280 | Touch 56px, helles Umgebungslicht |
| **Büro-Desktop** | 1920×1080+ | — | Keyboard-first, Multi-Monitor |
| **Management-Tablet** | iPad Air | 1180×820 | Lesen-dominant, 1-Klick-Freigaben |

**SOLL-Breakpoints:**

```css
/* Mobile-first (Terminal/Handgerät) */
@media (max-width: 639px)   { /* sm: Stack-Layout, 56px Touch-Targets, vereinfachte Navigation */ }
@media (640px–1023px)       { /* md: Tablet-Layout, ausklappbare Sidebar */ }
@media (1024px+)            { /* lg: Desktop-Layout, Sidebar permanent sichtbar */ }
```

**Terminal-spezifische Anforderungen:**

| Anforderung | Status | Maßnahme |
|---|---|---|
| Touch-Target ≥ 56px | POS-only | `touch-numpad.tsx` als Standard im Lager-Modul |
| Kontrast bei Sonnenlicht | MERIDIAN-Tokens ausreichend | Test auf echtem Gerät ausstehend |
| Barcode/QR-Scanner | POS-only | `navigator.mediaDevices` Scanner-Komponente für Lager |
| Offline-Erste-Strategie | POS-only | Service Worker + IndexedDB für Lager-Modul |
| Handschuh-Navigation | Nicht implementiert | Größere Swipe-Zones, kein Hover-Feedback nötig |
| Vereinfachte Lager-Shell | Fehlt | Reduzierte Navigation: nur Lager-Modul + Logout |

**GAPs:**
- Kein dediziertes Lager-Terminal-Layout
- Keine Scanner-Komponente außerhalb POS
- Kein Service Worker für Lager-Offline-Betrieb
- Mobile Navigation (Sidebar als Bottom-Sheet oder Hamburger) fehlt

---

### 3.9 Usability-Testplan

**Methodik:** Aufgabenbasiertes Denken-Laut-Protokoll mit echten Nutzern.

**Teilnehmer:** 2 pro Rolle (Lagerist, Sachbearbeiter, Buchhalter) = 6 Personen.

**Test-Umgebung:** Staging-System mit Demodaten, Zoom-Recording, Think-Aloud.

#### Test T-01: Wareneingang (Lagerist)
- **Aufgabe:** "Sie haben gerade 500 kg Weizen angeliefert bekommen. Buchen Sie den Wareneingang für Lieferant 'Müller GbR', Artikel 'Weizen B-Qualität'."
- **Erfolgskriterium:** ≤ 3 Minuten, ≤ 5 Klicks, keine Fehlbuchung
- **Messpunkte:** Klickpfad, Fehlversuche, verbale Unsicherheiten

#### Test T-02: Kontrakt anlegen (Sachbearbeiter Einkauf)
- **Aufgabe:** "Legen Sie einen Einkaufskontrakt für 10.000 kg Raps, Ernte 2026, Preis 450 €/t, Lieferant Hofgut Schneider an."
- **Erfolgskriterium:** ≤ 4 Minuten, alle Pflichtfelder korrekt gefüllt
- **Messpunkte:** Suchverhalten (findet Kontrakt-Maske?), Feldreihenfolge, Validierungs-Reaktion

#### Test T-03: Monatsbuchung (Buchhalter)
- **Aufgabe:** "Buchen Sie die Eingangsrechnung RE-2026-0047 über 3.450 € von Müller Agrar GmbH auf Kostenstelle 'Fuhrpark'."
- **Erfolgskriterium:** ≤ 5 Minuten, korrekte Kontierung, keine doppelte Buchung
- **Messpunkte:** Kontensuche, Tastaturnutzung, Fehler bei Betragseingabe

#### Test T-04: Bestandsabfrage (Außendienst, unterwegs)
- **Aufgabe:** "Ein Kunde fragt Sie per Telefon: Wie viel Lagerbestand haben wir aktuell von 'Dünger Kalkammonsalpeter 27%'?"
- **Erfolgskriterium:** ≤ 60 Sekunden, korrekte Antwort
- **Messpunkte:** Suche vs. Navigation, Mobile-Nutzbarkeit

#### Test T-05: KPI-Dashboard (Geschäftsführung)
- **Aufgabe:** "Zeigen Sie mir den Umsatz des laufenden Monats und genehmigen Sie die drei offenen Bestellfreigaben."
- **Erfolgskriterium:** ≤ 2 Minuten, alle 3 Freigaben erledigt
- **Messpunkte:** Dashboard-Orientierung, Freigabe-Workflow, Klickzahl

#### Test T-06: Jahresabrechnung Landwirt (externer Nutzer)
- **Aufgabe:** "Sehen Sie sich Ihre Jahresabrechnung 2025 an und laden Sie sie als PDF herunter."
- **Erfolgskriterium:** ≤ 3 Minuten ohne Hilfe
- **Messpunkte:** Login-Hürde, Navigierbarkeit im Portal, Fachbegriff-Verständnis

#### Test T-07: Keyboard-only Navigation (Sachbearbeiter)
- **Aufgabe:** "Erfassen Sie einen Verkaufsauftrag, ohne die Maus zu benutzen."
- **Erfolgskriterium:** Vollständig möglich, alle interaktiven Elemente erreichbar
- **Messpunkte:** Fokus-Verluste, Fallen, Tab-Reihenfolge-Logik

#### Test T-08: Barrierefreiheit Screenreader (beliebige Rolle)
- **Aufgabe:** "Navigieren Sie mit NVDA zum Modul 'Einkauf > Bestellungen' und öffnen Sie den ersten Eintrag."
- **Erfolgskriterium:** Vollständig möglich, sinnvolle Screenreader-Ausgabe
- **Messpunkte:** aria-Attribute, Landmark-Navigation, Fehleransagen

---

### 3.10 Messbare UX-Metriken

**Primäre KPIs (monatlich messen):**

| Metrik | Messverfahren | Zielwert | Ampel |
|---|---|---|---|
| **Time-to-Task: Wareneingang** | Usability-Test T-01 | < 2 Min | 🟢 <2 / 🟡 2-4 / 🔴 >4 |
| **Time-to-Task: Auftrag erfassen** | Usability-Test T-02 | < 3 Min | 🟢 <3 / 🟡 3-5 / 🔴 >5 |
| **Klickzahl pro Workflow** | Analytics Event-Tracking | ≤ SOLL-Werte | je Workflow |
| **Formular-Fehlerrate** | Server-seitige Validierungsfehler / Submits | < 5% | 🟢 <5 / 🟡 5-15 / 🔴 >15 |
| **WCAG axe-core Violations** | CI-Test nach jedem Deploy | 0 | 🟢 0 / 🔴 >0 |
| **Keyboard-Navigation Coverage** | Playwright keyboard test | 100% der Routes | 🟢 100 / 🟡 <100 |
| **System Usability Scale (SUS)** | Fragebogen nach Tests | ≥ 80/100 | 🟢 ≥80 / 🟡 68-79 / 🔴 <68 |
| **Support-Tickets UX-Kategorie** | Helpdesk-Klassifizierung | < 10% aller Tickets | 🟢 <10 / 🟡 10-25 / 🔴 >25 |
| **Nutzung Favoriten** | Analytics: pinnedTileIds Count | > 60% der User nutzen ≥1 Favorit | 🟢 >60 |
| **Mobile-Session-Anteil** | Analytics: Viewport-Breakpoints | > 20% (Lager + Außendienst) | 🟢 >20 |

**Sekundäre KPIs (quartalsweise):**

| Metrik | Ziel |
|---|---|
| Zoom-200%-Tests bestanden | 100% der Hauptseiten |
| NVDA/VoiceOver Test bestanden | Alle kritischen Workflows |
| Lighthouse Performance Score | ≥ 90 (Prod-Build) |
| First Contentful Paint (FCP) | < 1.5s |
| Largest Contentful Paint (LCP) | < 2.5s |
| Cumulative Layout Shift (CLS) | < 0.1 |

---

## 4. Implementierungs-Roadmap

### Sprint 1 (sofort — 1-2 Tage)
- [ ] `aria-current="page"` in `Sidebar.tsx` NavLinks (WCAG A-02)
- [ ] `role="alert"` auf Fehler-Paragraphen in `ObjectPage.tsx`
- [ ] `lang="de"` in `index.html` prüfen/setzen
- [ ] axe-core Playwright-Test in CI einbinden (WCAG-AUDIT.md Setup)

### Sprint 2 (kurzfristig — 1 Woche)
- [ ] Inline-Validierung on-blur in `ObjectPage.tsx` (react-hook-form `mode: 'onBlur'`)
- [ ] Domänenspezifische Leerzustände (ListReport Empty-State-Prop: icon + title + description + action)
- [ ] Offline-Banner global (Zustand via `navigator.onLine` + Event-Listener)
- [ ] Spalten-Sichtbarkeit-Picker in DataTable

### Sprint 3 (mittelfristig — 2-4 Wochen)
- [ ] Global-Search erweitern: Daten-Layer (Kunden, Artikel, Aufträge)
- [ ] Gespeicherte Tabellenansichten (localStorage, pro Nutzer, pro Tabelle)
- [ ] Auto-Save Formular-Entwürfe (30s-Intervall, Restore-Banner)
- [ ] Arrow-Key-Navigation in DataTable (WCAG A-04)
- [ ] Mobile Navigation: Sidebar als Bottom-Sheet auf < 640px

### Sprint 4 (langfristig — 1-2 Monate)
- [ ] Lager-Terminal-Layout (vereinfachte Shell, 56px Touch-Targets)
- [ ] Scanner-Komponente (`navigator.mediaDevices`) für Lager-Modul
- [ ] Rollenabhängige Navigation (Feature-Flag pro Persona)
- [ ] Usability-Tests T-01 bis T-08 durchführen
- [ ] Service Worker für Lager-Offline-Betrieb

---

## 5. Entscheidungslog

| Datum | Entscheidung | Begründung |
|---|---|---|
| 2026-05-18 | MERIDIAN als Primär-Theme aktiviert | Höchste Barrierefreiheits-Score (9.1/10), Agrar-Domäne passt zu Ocean+Amber |
| 2026-05-18 | Button h-10 (40px) statt h-9 (36px) | WCAG 2.5.5 Touch-Target ≥ 44px mit Padding erfüllt |
| 2026-05-18 | Skeleton-Loading statt Spinner in DataTable | Reduziert Layoutsprünge (CLS), professionellerer Eindruck |
| 2026-05-18 | splitLayout als opt-in Prop in ObjectPage | Keine Breaking Change; golden ratio wo sinnvoll |
| TBD | Pagination vs. Infinite Scroll | Default Pagination: Büchhaltungs-Tabellen brauchen exakten Seitenkontext |
