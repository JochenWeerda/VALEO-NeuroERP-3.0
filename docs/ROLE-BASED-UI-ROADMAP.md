# VALEO NeuroERP – Rollenbasierte UI Roadmap

**Erstellt:** 2026-02-06
**Verantwortlich:** Claude Code (Opus 4.5)
**Status:** ✅ Abgeschlossen

---

## Ziel

Transformation der VALEO ERP-Oberfläche zu einer **rollenbasierten, mobile-first Experience** für verschiedene Benutzergruppen:

1. **Landwirt (Kundenportal)** - Mobile 90%, Touch-first, Offline-fähig
2. **Lagerist (Warehouse)** - Scanner/MDE 99%, One-hand, Voice-optional
3. **Außendienst (Field Service)** - Tablet 60%, Offline-Sync, GPS
4. **Innendienst (CRM/Sales)** - Desktop 95%, Keyboard-first, Power-User
5. **Management (Executive)** - Desktop/Tablet 60%, KPI-focused

---

## Aktuelle Arbeit (Claude Code)

### Phase 1: Portal für Landwirte (Priorität 1)

**Betroffene Dateien:**
```
packages/frontend-web/src/
├── pages/portal/           # Alle Portal-Seiten
│   ├── index.tsx          # Dashboard
│   ├── shop.tsx           # Bestellungen
│   ├── bestellungen.tsx   # Bestellhistorie
│   └── ...
├── components/portal/      # NEU: Portal-spezifische Komponenten
├── hooks/useOfflineSync.ts # NEU: Offline-Sync Hook
└── lib/service-worker.ts   # Erweitern für Offline-Bestellungen
```

**Tasks:**
1. Portal-Dashboard Mobile-Redesign
2. Offline-Queue für Bestellungen
3. Voice-Ordering Integration
4. Quick-Reorder Cards
5. Big Touch Targets (48px minimum)

### Phase 2: Warehouse Terminal (Priorität 2) ✅

**Implementierte Dateien:**
```
packages/frontend-web/src/
├── pages/lager/terminal.tsx           # Warehouse Terminal Hauptseite
├── components/warehouse/
│   ├── index.ts                       # Export aller Warehouse-Komponenten
│   ├── WarehouseLayout.tsx            # Layout mit High-Contrast Theme
│   ├── ScannerInput.tsx               # Touch-optimiertes Scanner-Input
│   ├── ScanResult.tsx                 # Artikel-Info nach Scan
│   └── QuickActionGrid.tsx            # Große Aktions-Buttons
├── themes/warehouse-theme.ts          # High-Contrast Theme (Schwarz/Gelb)
├── hooks/useBarcodeScan.ts            # Keyboard & Kamera Scanner
└── hooks/useWarehouseTheme.ts         # Theme-Verwaltung
```

**Features:**
- High-Contrast Theme (Schwarz/Gelb) für industrielle Umgebungen
- 60px Touch Targets für Handschuh-Bedienung
- USB/Bluetooth Barcode-Scanner Integration (Keyboard-Emulation)
- Kamera-Scan für mobile Geräte (BarcodeDetector API)
- EAN-13, EAN-8, Code 128, Code 39, QR-Code Unterstützung
- Akustisches Feedback bei Scan

### Phase 3: Field Service App (Priorität 3) ✅

**Implementierte Dateien:**
```
packages/frontend-web/src/
├── components/field-service/
│   ├── index.ts                       # Export aller Field-Service-Komponenten
│   ├── LocationCard.tsx               # Kundenstandort mit Navigation
│   └── TourList.tsx                   # Tagestour mit Sortierung
└── hooks/useGeolocation.ts            # GPS-Integration
```

**Features:**
- GPS-Tracking mit Haversine-Distanzberechnung
- Sortierung nach Distanz, Zeit oder Priorität
- Integration mit Google Maps / Apple Maps Navigation
- TanStack Query für Daten-Management
- Metro Design für Tablet-Optimierung

### Phase 4: Innendienst / Power-User (Priorität 4) ✅

**Implementierte Dateien:**
```
packages/frontend-web/src/
├── components/innendienst/
│   ├── index.ts                       # Export aller Innendienst-Komponenten
│   ├── CommandPalette.tsx             # Ctrl+K Command Palette
│   ├── QuickSearch.tsx                # Globale Schnellsuche (Ctrl+/)
│   └── KeyboardShortcutsHelp.tsx      # Shift+? Shortcuts-Übersicht
└── hooks/useGlobalShortcuts.ts        # Bestehendes Shortcut-System
```

**Features:**
- Command Palette (Ctrl+K) für schnellen Zugriff auf alle Funktionen
- Globale Schnellsuche (Ctrl+/) über Kunden, Aufträge, Artikel
- Keyboard-Navigation mit G+X für Navigation, N+X für Neue Objekte
- Shift+? zeigt alle verfügbaren Tastenkürzel
- TanStack Query für Echtzeit-Suchergebnisse
- Letzte Suchen im LocalStorage

### Phase 5: Management / Executive Dashboard (Priorität 5) ✅

**Implementierte Dateien:**
```
packages/frontend-web/src/
├── pages/management/
│   └── executive-dashboard.tsx        # Hauptseite Executive Dashboard
├── components/management/
│   ├── index.ts                       # Export aller Management-Komponenten
│   ├── KPICard.tsx                    # KPI-Karten mit Trends & Sparklines
│   ├── AlertWidget.tsx                # Handlungsbedarf-Warnungen
│   └── TrendChart.tsx                 # Trend-Diagramme
```

**Features:**
- KPI-Cards mit Trend-Indikatoren und Ziel-Fortschritt
- Sparkline-Charts für schnelle Trend-Visualisierung
- Alert-Widget für kritische Handlungsempfehlungen
- Zeitraum-Filter (7d, 30d, 90d, Jahr)
- Top-Listen für Produkte und Kunden
- Export-Funktion
- Responsive für Desktop und Tablet

---

## Abgrenzung zu anderen Arbeiten

**Claude Code arbeitet an:**
- `packages/frontend-web/src/pages/portal/*`
- `packages/frontend-web/src/components/portal/*` (NEU)
- `packages/frontend-web/src/hooks/useOffline*.ts` (NEU)
- `packages/frontend-web/src/hooks/useVoice*.ts` (NEU)

**Bitte NICHT gleichzeitig bearbeiten:**
- Portal-Seiten (shop, bestellungen, index, etc.)
- Service Worker Konfiguration
- Voice-Button Komponente

**Kann parallel bearbeitet werden:**
- Backend-APIs
- Andere Frontend-Seiten (CRM, Finance, etc.)
- Dokumentation außerhalb dieses Bereichs

---

## Timeline

| Phase | Dauer | Status |
|-------|-------|--------|
| Quick Wins (Dark Mode, Touch, Error) | 2h | ✅ Fertig |
| Portal Mobile-Redesign | 2-3 Tage | ✅ Fertig |
| Offline-Sync | 2 Tage | ✅ Fertig |
| Voice-Ordering | 1-2 Tage | ✅ Fertig |
| Warehouse Terminal | 3-4 Tage | ✅ Fertig |
| Field Service App | 3-4 Tage | ✅ Fertig |
| Innendienst Power-User | 1-2 Tage | ✅ Fertig |
| Management Dashboard | 1-2 Tage | ✅ Fertig |

---

## Technische Entscheidungen

### Offline-First
- Service Worker mit Workbox (bereits via vite-plugin-pwa)
- IndexedDB für Offline-Queue (Bestellungen)
- Background Sync API für automatisches Senden

### Voice Integration
- Web Speech API (SpeechRecognition)
- Fallback: Manuelle Eingabe
- Kommandos: "Bestelle [Menge] [Artikel]", "Suche [Begriff]"

### Touch-Optimierung
- Minimum 48x48px Touch Targets (WCAG 2.1)
- Swipe-Gesten für häufige Aktionen
- Haptic Feedback wo verfügbar

### Warehouse Terminal
- High-Contrast Theme mit CSS Custom Properties
- Barcode-Scanner via Keyboard-Emulation (schnelle Tastenfolge = Scanner)
- BarcodeDetector API für Kamera-Scan (Chrome)
- EAN/UPC Prüfziffern-Validierung
- Akustisches Feedback via Web Audio API

### Field Service (GPS)
- Geolocation API mit High-Accuracy Mode
- Haversine-Formel für Distanzberechnung
- Native Navigation via Deep Links (Google Maps / Apple Maps)
- TanStack Query für Server-State
- Metro Design Pattern für Touch-Tablets

---

## Erstellte Komponenten (Übersicht)

### Portal (Landwirt)
- `OfflineIndicator` - Online/Offline Status Banner
- `QuickReorderCards` - 1-Tap Nachbestellung
- `PendingOrdersBanner` - Offline-Bestellungen Sync-Status
- `VoiceOrderButton` - Sprachbestellung mit Parser
- **CustomerPortalLayout:** "Zur Startseite"-Button für Anwender (admin/user/manager) – siehe `docs/portal-layout.md`

### Warehouse (Lagerist)
- `WarehouseLayout` - Layout mit Theme & Navigation
- `ScannerInput` - Touch-optimiertes Barcode-Input
- `ScanResult` - Artikel-Info nach Scan
- `QuickActionGrid` - Große Aktions-Buttons

### Field Service (Außendienst)
- `LocationCard` - Kundenstandort mit Navigation
- `TourList` - Sortierte Tagestour

### Innendienst (Power-User)
- `CommandPalette` - Ctrl+K Schnellzugriff
- `QuickSearch` - Globale Suche mit Recent
- `KeyboardShortcutsHelp` - Shift+? Hilfe-Overlay

### Management (Executive)
- `KPICard` + `KPIGrid` - Kennzahlen mit Trends
- `AlertWidget` + `AlertSummary` - Handlungsbedarf
- `TrendChart` + `TrendIndicator` - Zeitreihen-Visualisierung

---

## Status: ABGESCHLOSSEN ✅

Alle 5 Benutzerrollen sind implementiert:
1. ✅ Landwirt (Portal) - Mobile, Offline, Voice
2. ✅ Lagerist (Warehouse) - Scanner, High-Contrast
3. ✅ Außendienst (Field Service) - GPS, Navigation
4. ✅ Innendienst (CRM/Sales) - Keyboard-First, Command Palette
5. ✅ Management (Executive) - KPI Dashboard, Trends

---

*Letzte Aktualisierung: 2026-02-06 durch Claude Code*

