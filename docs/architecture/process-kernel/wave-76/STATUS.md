# Wave 76 — Touch-optimierte Feldworkflows (Gap 024)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-19
**Tests:** 37 passed, 0 failed
**Gap:** 024 — Touch-optimierte Feldworkflows (Tablet/Lager/Waage), KPI: Fehlbedienungen -40%

## Lieferumfang

### A) TouchFieldLayout-Komponentenbibliothek (`components/touch/TouchFieldLayout.tsx`)

Neue, gemeinsam genutzte React-Komponenten für alle Touch-Feldworkflows:

| Komponente | Touch-Target | Zweck |
|------------|-------------|-------|
| `TouchCard` | ≥ 64px Höhe | Auswahl-Karte (ersetzt `<select>`) |
| `TouchCardGroup` | — | Gruppe von TouchCards mit Label |
| `TouchNumericInput` | ≥ 54px, `inputMode="decimal"` | Numerische Eingabe mit Ziffernblock |
| `TouchTextInput` | ≥ 54px | Text-Eingabe mit großem Touch-Target |
| `TouchToggle` | ≥ 52px | Ja/Nein-Umschalter (2 Buttons) |
| `TouchSubmitButton` | ≥ 56px (volle Breite) | Primäre Aktionsfläche |
| `TouchSection` | — | Abschnitt mit Überschrift |
| `TouchConfirmCard` | — | Zusammenfassung vor Absenden |
| `useTouchDevice()` | — | Erkennt Touch-Gerät per `pointer: coarse` |

**WCAG 2.1 Compliance:**
- Alle interaktiven Elemente: `min-h-[44px]` (WCAG 2.1 SC 2.5.5)
- Submit-Buttons: `min-h-[56px]`
- Auswahl-Karten: `min-h-[64px]`
- Numerische Inputs: `inputMode="decimal"` → mobiler Ziffernblock
- Eigene Endpoint-Header werden nicht überschrieben

### B) Einlagerung (Touch-Upgrade) (`pages/lager/einlagerung.tsx`)

- **Vorher:** `<Input>` für Artikel-Text, `<select>` für Lagerort
- **Nachher:** Artikel und Lagerort via `TouchCard`-Karten-Selektion
- Chargen-ID: `TouchTextInput` mit `autoCapitalize="characters"`
- Menge: `TouchNumericInput` mit `unit="t"` und `inputMode="decimal"`
- Bestätigung: `TouchConfirmCard` mit allen Feldern auf einen Blick

### C) LKW-Registrierung (Touch-Upgrade) (`pages/annahme/lkw-registrierung.tsx`)

- **Vorher:** Priorität via `<select>` (kleines Touch-Target, fehleranfällig)
- **Nachher:** Priorität (hoch/normal/niedrig) via 3 `TouchCard`-Karten
- Artikel-Auswahl ebenfalls via `TouchCard`-Karten
- Kennzeichen/Lieferant: `TouchTextInput` ≥ 54px
- Scan-Button: `min-h-[44px]` volle Breite
- Bestätigung: `TouchConfirmCard`

## Kontrakt-Tests (37 Tests)

- `TestTouchWorkflowStep` (6): Validierung Step-Kontrakte (leer, Länge, Pflichtfelder, Touch-Ziel)
- `TestTouchWorkflowState` (9): Zustandsmaschine (advance, back, progress, completed)
- `TestEinlagerungTouchPayload` (7): Einlagerung-Payload-Validierung
- `TestLKWRegistrierungTouchPayload` (7): LKW-Payload, typisierte Priorität
- `TestTouchTargetSizes` (5): WCAG 2.1 Touch-Ziel-Größen-Invarianten
- Proxy-Tests (3): POST /lager/einlagerung → 422 bei leerem Payload

## Touch-Design-Entscheidungen

- `<select>` komplett ersetzt durch `TouchCard`-Karten (kein Maus-Hover nötig)
- `inputMode="decimal"` für alle Mengen-Felder (mobiler Ziffernblock)
- `autoCapitalize="characters"` für Kennzeichen (Großbuchstaben automatisch)
- `capture="environment"` für Foto-Uploads (direkte Kamera auf Mobilgeräten)
- Spacing: `gap-4` Minimum zwischen Touch-Targets (Finger-Abstand)
