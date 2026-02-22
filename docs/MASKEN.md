# VALEO NeuroERP - Eingabemasken Standard

**Version:** 1.0.0  
**Datum:** 2025-01-16  
**Status:** ✅ Aktiv

## 📋 Übersicht

Dieses Dokument definiert die **Pflicht-Funktionalitäten** und **Design-Prinzipien**, die in **allen Eingabemasken** des VALEO NeuroERP Systems implementiert werden müssen. Diese Standards gewährleisten eine konsistente Benutzererfahrung, ermöglichen vollautomatische UAT-Tests und folgen dem **Gewohnheits-Prinzip** für ähnliche Belege.

## 🎯 Gewohnheits-Prinzip (Konsistenz-Prinzip)

### Grundsatz

**Ähnliche Belege in einer Belegfolge müssen sich im Design, Layout und in den grundsätzlichen Funktionalitäten möglichst ähneln**, damit sich Benutzer schnell zurechtfinden können.

### Belegfolgen

#### Verkauf (Sales)
1. **Auftrag** → 2. **Lieferschein** → 3. **Rechnung**
   - Alle drei Belege haben ähnliche Struktur:
     - Header-Bereich (oben links): Beleg-Nr., Niederlassung, Vertreter, Bediener, Datum, etc.
     - Kunden-Bereich (oben rechts): Debitor-Kto., Kundenadresse, Tabs (KUNDE, LIEFER-ANSCHR., etc.)
     - Positionen-Grid (Mitte): Tabelle mit Artikeln
     - Positions-Details (unten): Aktuelle Position bearbeiten
     - Summen-Bereich: Netto, MWSt, Brutto
     - Bottom-Toolbar: Aktionen (Drucken, Speichern, Schließen)

#### Einkauf (Procurement)
1. **Angebot** → 2. **Bestellung** → 3. **Wareneingang** → 4. **Rechnung**
   - Ähnliche Struktur wie Verkauf, aber mit Lieferanten statt Kunden

#### Lager (Inventory)
1. **Lagerbuchung** → 2. **Inventur** → 3. **Umlagerung**
   - Gemeinsame Elemente: Artikel-Auswahl, Mengen, Lagerorte

### Gemeinsame Layout-Struktur

Alle Belege in einer Belegfolge müssen folgende **gemeinsame Bereiche** haben:

```
┌─────────────────────────────────────────────────────────┐
│ HEADER-BEREICH (oben links)                            │
│ - Beleg-Nr. + Browse-Button                            │
│ - Niederlassung, Vertreter, Bediener                   │
│ - Datum, Uhrzeit                                       │
│ - Status-Felder (gedruckt, ausgeliefert, fakturiert)  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ KUNDEN/LIEFERANTEN-BEREICH (oben rechts)              │
│ - Debitor-Kto./Kreditor-Kto. + "..."-Button           │
│ - Adress-Anzeige                                       │
│ - Tabs: KUNDE, LIEFER-ANSCHR., RECHN.-ANSCHRIFT, etc. │
│ - "wie vorheriger Beleg (F11)"-Link                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ POSITIONEN-GRID (Mitte)                                │
│ - Tabelle mit Spalten: Pos.-Nr., Artikel, Menge, etc.  │
│ - Grüne Zeile = aktive Position                        │
│ - Statusbar unten: Letzter Bezugspreis, etc.           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ POSITIONS-DETAILS (unten)                              │
│ - Pos.-Nr., Artikel-Nr. + "..."-Button                │
│ - Bezeichnung, Menge, Einheit                         │
│ - Listenpreis, Rabatt, Netto-Preis, Betrag            │
│ - Buttons: Zeile OK, Details, etc.                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ SUMMEN-BEREICH                                         │
│ - Netto Gesamt, MWSt, Brutto, EUR                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ BOTTOM-TOOLBAR                                         │
│ - Links: Beleg-spezifische Aktionen                    │
│ - Rechts: Speichern, Schließen                         │
└─────────────────────────────────────────────────────────┘
```

### Gemeinsame Funktionalitäten

Alle Belege in einer Belegfolge müssen folgende **gemeinsame Funktionalitäten** haben:

#### 1. Navigation & Auswahl
- ✅ **Kunden-/Lieferanten-Auswahl:** Strg+F1 → Dialog mit Suche, Filtern, Tabs
- ✅ **Artikel-Auswahl:** Strg+F2 → Dialog mit Matchcode, Filtern, Tabs
- ✅ **Position OK:** Strg+F3 → Position in Grid übernehmen

#### 2. Beleg-Aktionen
- ✅ **Speichern:** Strg+F4 → Beleg speichern (Draft-Status)
- ✅ **Drucken:** Strg+F5 → Druck-Dialog → Beleg buchen
- ✅ **Löschen:** Strg+F6 → Beleg löschen (nur Draft)
- ✅ **Schließen:** Strg+F7 → Zurück navigieren

#### 3. Kopier-Funktionen
- ✅ **Wie vorheriger Beleg (F11):** Kopiert ALLE Daten (Kunde + Positionen)
- ✅ **Wie vorheriger (Strg+F8):** Kopiert nur Positionen (Kunde bleibt)

#### 4. Status-Management
- ✅ **Draft** → **Gedruckt** → **Ausgeliefert** → **Fakturiert**
- ✅ Status-Änderungen nur mit Attestation (GoBD-konform)

#### 5. Berechnungen
- ✅ **Netto-Preis** = Listenpreis × (1 - Rabatt/100)
- ✅ **Netto-Betrag** = Netto-Preis × Menge
- ✅ **MWSt** = Netto-Betrag × MWSt-Prozent/100
- ✅ **Brutto** = Netto + MWSt

### Design-Konsistenz

#### Farben & Icons
- **Aktive Position:** Grüne Hintergrundfarbe
- **Gedruckt:** Checkbox mit grünem Häkchen
- **Ausgeliefert:** Checkbox mit grünem Häkchen
- **Fakturiert:** Textfeld mit Rechnungsnummer

#### Button-Positionen
- **Kunden-Auswahl:** "..."-Button rechts neben Debitor-Kto.
- **Artikel-Auswahl:** "..."-Button rechts neben Artikel-Nr.
- **Speichern:** Rechts unten in Toolbar
- **Schließen:** Rechts unten in Toolbar (neben Speichern)

#### Tastatur-Navigation
- **Tab:** Durch Felder navigieren
- **Enter:** Position OK (wenn in Positions-Details)
- **Esc:** Dialog schließen / Abbrechen

### Implementierungs-Regeln

1. **Layout-Template verwenden:**
   - Kopiere Layout-Struktur von `lieferschein-erfassung.tsx`
   - Passe nur beleg-spezifische Felder an

2. **Gleiche Komponenten verwenden:**
   - `CustomerSelectionDialog` für Kunden-Auswahl
   - `ArtikelSuchDialog` für Artikel-Auswahl
   - `LieferscheinDruckDialog` als Basis für Druck-Dialoge
   - `AttestationDialog` für Status-Änderungen

3. **Gleiche Shortcuts:**
   - Alle Belege verwenden die gleichen Shortcuts (Strg+F1-F12)
   - Keine beleg-spezifischen Shortcuts ohne Dokumentation

4. **Gleiche State-Struktur:**
   ```typescript
   type BelegState = {
     id: string | null
     belegNr: string
     niederlassung: number
     vertreter: string
     bediener: string
     datum: string
     uhrzeit: string
     customer: Customer | null
     positionen: Position[]
     aktivePositionIndex: number | null
     // ... beleg-spezifische Felder
   }
   ```

5. **Gleiche Workflows:**
   - Öffnen → Kunde wählen → Artikel hinzufügen → Positionen bestätigen → Speichern/Drucken → Buchen

### Checkliste für neue Belege

Bei Erstellung eines neuen Belegs in einer Belegfolge:

- [ ] Layout-Struktur entspricht anderen Belegen der Folge
- [ ] Alle gemeinsamen Bereiche vorhanden (Header, Kunde, Positionen, Summen, Toolbar)
- [ ] Gleiche Komponenten verwendet (CustomerSelectionDialog, ArtikelSuchDialog, etc.)
- [ ] Gleiche Shortcuts implementiert (Strg+F1-F12)
- [ ] Gleiche State-Struktur verwendet
- [ ] Gleiche Berechnungs-Logik (Netto, MWSt, Brutto)
- [ ] Gleiche Status-Übergänge (Draft → Gedruckt → etc.)
- [ ] Gleiche Button-Positionen und Icons
- [ ] Gleiche Farben für Status-Indikatoren
- [ ] Dokumentation: Abweichungen von Standard begründet

---

## ✅ Pflicht-Funktionalitäten für alle Masken

### 1. Sidebar-Toggle (Strg+B)

**Beschreibung:** Ein-/Ausklappen der linken Seitenleiste

**Implementierung:**
- ✅ **Automatisch verfügbar** über `AppShell` Komponente
- ✅ **Icon in TopBar:** `PanelLeft` Icon (oben rechts im Menü-Band)
- ✅ **Keyboard-Shortcut:** `Strg+B` (oder `Ctrl+B` auf Mac)
- ✅ **Funktionalität:** Toggle zwischen eingeklappt/ausgeklappt

**Technische Details:**
- Wird automatisch von `AppShell` bereitgestellt
- Keine zusätzliche Implementierung in einzelnen Masken erforderlich
- State wird in `AppShell` verwaltet (`sidebarCollapsed`)

**Verwendung:**
```typescript
// Automatisch verfügbar - keine Implementierung nötig
// Icon ist bereits in TopBar.tsx integriert
// Shortcut wird in AppShell.tsx gehandelt
```

---

### 2. Shortcuts-Liste Toggle (Strg+N)

**Beschreibung:** Ein-/Ausblenden der Shortcuts-Hilfe-Liste (rechtes Panel)

**Implementierung:**
- ✅ **Automatisch verfügbar** über `GlobalShortcutProvider`
- ✅ **Icon in TopBar:** `Keyboard` Icon (oben rechts im Menü-Band)
- ✅ **Keyboard-Shortcut:** `Strg+N` (oder `Ctrl+N` auf Mac)
- ✅ **Zyklische Schaltlogik:**
  1. **1. Klick:** `always` → Panel immer sichtbar
  2. **2. Klick:** `hover` → Panel nur bei Hover sichtbar
  3. **3. Klick:** `hidden` → Panel ausgeblendet
  4. **4. Klick:** zurück zu `always` (Zyklus)

**Technische Details:**
- Wird automatisch von `GlobalShortcutProvider` bereitgestellt
- State wird in `GlobalShortcutProvider` verwaltet (`displayMode`)
- Icon zeigt visuell den aktuellen Modus an (Opacity: 100% / 75% / 50%)
- Tooltip zeigt aktuellen Modus: "Shortcuts-Liste: [Modus] (Strg+N)"

**Verwendung:**
```typescript
// Automatisch verfügbar - keine Implementierung nötig
// Icon ist bereits in TopBar.tsx integriert
// Shortcut wird in AppShell.tsx gehandelt
// Schaltlogik ist in GlobalShortcutProvider.tsx implementiert
```

---

## 🎯 Standard-Keyboard-Shortcuts

Alle Masken müssen die folgenden **globalen Shortcuts** unterstützen:

| Shortcut | Aktion | Kategorie | Status |
|----------|--------|-----------|--------|
| **Strg+F1** | Kundenauswahl öffnen | Navigation | ✅ Standard |
| **Strg+F2** | Artikelauswahl öffnen | Navigation | ✅ Standard |
| **Strg+F3** | Position OK | Aktionen | ✅ Standard |
| **Strg+F4** | Beleg speichern | Aktionen | ✅ Standard |
| **Strg+F5** | Beleg drucken | Aktionen | ✅ Standard |
| **Strg+F6** | Beleg löschen | Aktionen | ✅ Standard |
| **Strg+F7** | Beleg schließen | Navigation | ✅ Standard |
| **Strg+F8** | Wie vorheriger (nur Positionen) | Aktionen | ✅ Standard |
| **Strg+F9** | Sofort-Rechnung | Aktionen | ✅ Standard |
| **Strg+F10** | Unterlagen | Navigation | ✅ Standard |
| **F11** | Wie vorheriger Beleg | Aktionen | ✅ Standard |
| **Strg+F12** | Information | Navigation | ✅ Standard |
| **Esc** | Abbrechen | Navigation | ✅ Standard |
| **Strg+B** | Seitenleiste ein-/ausklappen | Navigation | ✅ Standard |
| **Strg+N** | Shortcuts-Liste ein-/ausblenden | Navigation | ✅ Standard |

**Implementierung:**
- Shortcuts werden automatisch über `GlobalShortcutProvider` bereitgestellt
- Masken registrieren Handler über `useGlobalShortcuts()` Hook
- Siehe: `packages/frontend-web/src/lib/shortcuts/global-shortcuts.ts`

---

## 📐 Implementierungs-Checkliste für neue Masken

### ✅ Automatisch verfügbar (keine Implementierung nötig)

- [x] Sidebar-Toggle (Strg+B) - Icon in TopBar
- [x] Shortcuts-Liste Toggle (Strg+N) - Icon in TopBar
- [x] GlobalShortcutProvider - Bereitstellung der Shortcut-Infrastruktur
- [x] ShortcutHelpPanel - Rechtes Panel mit Shortcut-Übersicht

### ⚠️ Muss in jeder Maske implementiert werden

- [ ] **Shortcut-Handler registrieren:**
  ```typescript
  import { useGlobalShortcuts } from '@/lib/shortcuts/global-shortcuts'
  
  function MyMaskPage() {
    useGlobalShortcuts({
      'open-customer-selection': () => setShowCustomerDialog(true),
      'save-document': () => void handleSave(),
      'print-document': () => void handlePrint(),
      // ... weitere Handler
    })
  }
  ```

- [ ] **Buttons mit ShortcutHintButton wrappen:**
  ```typescript
  import { ShortcutHintButton } from '@/components/shortcuts/ShortcutHelpPanel'
  
  <ShortcutHintButton action="save-document" onClick={handleSave}>
    <Save className="h-4 w-4" />
    Speichern
  </ShortcutHintButton>
  ```

- [ ] **Masken-spezifische Shortcuts dokumentieren** (falls vorhanden)

---

## 🔧 Technische Komponenten

### AppShell
**Datei:** `packages/frontend-web/src/components/navigation/AppShell.tsx`

- Verwaltet Sidebar-State (`sidebarCollapsed`)
- Handled Strg+B für Sidebar-Toggle
- Handled Strg+N für Shortcuts-Toggle
- Stellt `onSidebarToggle` und `onShortcutsToggle` Props für TopBar bereit

### TopBar
**Datei:** `packages/frontend-web/src/components/navigation/TopBar.tsx`

- **Sidebar-Toggle Icon:** `PanelLeft` Icon mit Tooltip "Seitenleiste ein-/ausklappen (Strg+B)"
- **Shortcuts-Toggle Icon:** `Keyboard` Icon mit dynamischem Tooltip basierend auf Modus
- Icons sind nur auf Desktop sichtbar (`hidden md:inline-flex`)

### GlobalShortcutProvider
**Datei:** `packages/frontend-web/src/components/shortcuts/GlobalShortcutProvider.tsx`

- Verwaltet `displayMode` State für ShortcutHelpPanel
- Implementiert zyklische Schaltlogik (`always` → `hover` → `hidden` → `always`)
- Exportiert Funktionen für externen Zugriff:
  - `window.__cycleShortcutDisplayMode()` - Zyklus durchlaufen
  - `window.__getShortcutDisplayMode()` - Aktuellen Modus abfragen

### ShortcutHelpPanel
**Datei:** `packages/frontend-web/src/components/shortcuts/ShortcutHelpPanel.tsx`

- Rechtes Panel mit Shortcut-Übersicht
- Drei Anzeige-Modi: `always`, `hover`, `hidden`
- Automatisches Expandieren bei Wechsel zu `always` Modus

---

## 📚 Weitere Dokumentation

- **Masken-Referenz (Lieferschein):** `docs/masken-referenz-lieferschein.md` ⭐ **NEU - Vollständige Referenz für neue Masken**
- **Global Shortcuts System:** `docs/global-shortcuts-system.md`
- **Shortcuts F8/F11 Unterschied:** `docs/shortcuts-f8-f11-unterschied.md`
- **Lieferschein Keyboard Shortcuts:** `docs/lieferschein-keyboard-shortcuts.md`

---

## ✅ Beispiel-Implementierung

### Vollständige Referenz-Dokumentation

**📖 Siehe:** `docs/masken-referenz-lieferschein.md` für eine **vollständige Referenz-Dokumentation** der Lieferschein-Erfassungsmaske:

- ✅ Architektur & Struktur
- ✅ Datenstrukturen (Frontend & Backend)
- ✅ API-Integrationen (alle Endpoints)
- ✅ UI-Komponenten
- ✅ Keyboard-Shortcuts
- ✅ State-Management
- ✅ Validierungen & Business-Logic
- ✅ Best Practices
- ✅ Code-Beispiele
- ✅ Checkliste für neue Masken

### Code-Referenz

**📁 Datei:** `packages/frontend-web/src/pages/verkauf/lieferschein-erfassung.tsx`

**Features:**
- ✅ Alle globalen Shortcuts registriert
- ✅ Buttons mit ShortcutHintButton gewrappt
- ✅ Konsistente UX mit anderen Masken
- ✅ Vollständige CRUD-Funktionalität
- ✅ Preisberechnung mit API
- ✅ Gefahrgut-Punkte Validierung
- ✅ Gewichtsberechnung
- ✅ "Wie vorheriger Beleg" Funktionalität

---

## 🚀 Nächste Schritte

Bei Erstellung neuer Masken:

1. **Prüfe Belegfolge:** Zu welcher Belegfolge gehört der neue Beleg?
2. **Kopiere Struktur** von `lieferschein-erfassung.tsx` (Referenz-Implementierung)
3. **Passe beleg-spezifische Felder an**, behalte aber Layout-Struktur bei
4. **Registriere Shortcut-Handler** mit `useGlobalShortcuts()`
5. **Wrappe Buttons** mit `ShortcutHintButton`
6. **Verwende gleiche Komponenten** (CustomerSelectionDialog, ArtikelSuchDialog, etc.)
7. **Teste alle Shortcuts** (Strg+F1-F12, Esc, Strg+B, Strg+N)
8. **Vergleiche mit anderen Belegen** der gleichen Belegfolge
9. **Dokumentiere Abweichungen** von Standard (falls notwendig)

---

**Wichtig:** Diese Funktionalitäten sind **Pflicht** für alle Eingabemasken. Sie gewährleisten:
- ✅ Konsistente Benutzererfahrung
- ✅ Vollautomatische UAT-Tests möglich
- ✅ Einheitliche Navigation und Bedienung
- ✅ Barrierefreiheit und Accessibility

