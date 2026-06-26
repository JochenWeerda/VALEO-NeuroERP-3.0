# UX-Standard VALEO NeuroERP – einheitlich wie aus einem Guss

**Gültig für:** Alle Domänen (Finanz, Verkauf, Einkauf, Lager, FIBU Suite, CRM, …)  
**Prinzip:** Eine einheitliche Interaktionsschicht: **PageToolbar + Sprachsteuerung + Tastaturkürzel**. Kein Ribbon auf Maskenebene, keine abweichenden Toolbar-Patterns.

---

## 1. Das einheitliche Pattern

Jede Seite (Liste, Detail, Erfassung, Bericht) folgt **demselben** Aufbau:

| Element | Pflicht | Beschreibung |
|--------|--------|---------------|
| **PageToolbar** | Ja | Eine kontextuelle Toolbar pro Seite: Titel, optional Untertitel, 2–4 Primäraktionen (Buttons), weitere Aktionen im Overflow-Menü (⋯). Jede Aktion hat wo sinnvoll einen **Tastaturkürzel**. |
| **Tastaturkürzel** | Ja | Globale und seitenlokale Shortcuts. Standard: **Ctrl+K** = Command Palette, **Strg+F1–F12** für Belegaktionen (Kundenauswahl, Speichern, Drucken, …). Shortcuts in Toolbar-Buttons anzeigen (z. B. `Speichern (Strg+F4)`). |
| **Sprachsteuerung** | Ja | Aktionen und Navigation per Sprache auslösbar („Neue Rechnung“, „Speichern“, „Gehe zu Aufträge“). Technik: z. B. Web Speech API oder Anbindung an Assistenten/MCP; gleiche Intents wie Toolbar und Command Palette. |

Kein **Ribbon** (Register DATEI/ALLGEMEIN/AUSWERTUNGEN/…) auf Maskenebene. Keine domänenspezifischen Toolbar-Varianten – überall dieselbe PageToolbar-Komponente und dieselben Regeln für Shortcuts und Sprache.

---

## 2. PageToolbar

- **Komponente:** `@/components/navigation/PageToolbar`
- **Props:** `title`, `subtitle`, `primaryActions`, `overflowActions`, optional `rightSlot`, optional `mcpContext`
- **Primäraktionen:** Maximal 3–4 sichtbare Buttons (z. B. Neu, Export, Drucken). Jede `ToolbarAction` kann `shortcut` haben (z. B. `Ctrl+N`).
- **Overflow:** Alle weiteren Aktionen ins ⋯-Menü. Auch dort Shortcuts anzeigen.
- **Referenz:** `packages/frontend-web/src/pages/sales/orders-modern.tsx`, `components/patterns/ListReport.tsx`, `ObjectPage.tsx`, `OverviewPage.tsx`

FiBu-/Finance-Masken: Kein eigenes Ribbon mehr; stattdessen PageToolbar mit Aktionen wie Drucken, Export, BWA, Bilanz/GuV, Schnittstelle usw. als Primär- oder Overflow-Aktionen.

---

## 3. Tastaturkürzel

- **Globale Shortcuts:** `lib/shortcuts/global-shortcuts.ts` – `GLOBAL_SHORTCUTS`, `useGlobalShortcuts`, `globalShortcutManager`, `handleGlobalShortcutKeyDown`
- **Command Palette:** **Ctrl+K** – Suche, Navigation, Aktionen; `components/navigation/CommandPalette.tsx` bzw. Innendienst-`CommandPalette.tsx`
- **Provider:** `GlobalShortcutProvider` registriert die Key-Listener; `ShortcutHelpPanel` zeigt die Liste (Anzeige optional: always/hover/hidden)
- **Konvention:** Pro Aktion ein Shortcut; in der Toolbar und im Overflow als `(Strg+Fx)` bzw. `Ctrl+K` sichtbar machen

Neue Masken: Alle wichtigen Aktionen mit Shortcut definieren und in PageToolbar/Command Palette anbinden.

---

## 4. Sprachsteuerung

- **Ziel:** Dieselben Aktionen wie in PageToolbar und Command Palette per Sprache auslösbar („Neue Rechnung“, „Speichern“, „Aufträge öffnen“).
- **Umsetzung:** **Implementiert** — KI-Usability integriert im Haupt-Backend (`/api/v1/actions`, `/api/v1/voice/resolve`) sowie als Microservice (`services/ki-usability/`). Siehe [docs/architecture/KI-USABILITY-MICROSERVICES.md](architecture/KI-USABILITY-MICROSERVICES.md).
  - Einheitliche Intents/Befehle (gleiche Action-IDs wie Toolbar und Command Palette)
  - Backend: Microservice **ki-usability-api** (Action Registry, Voice-to-Intent, optional STT/TTS)
  - Frontend: Feature **ki-usability** (VoiceButton, useVoiceIntent, Action-Dispatcher), Anbindung Web Speech API und/oder Backend
  - Keine zweite UI – Sprache ist nur ein weiterer Zugang zu denselben Aktionen

---

## 5. Was entfällt

- **Ribbon auf Maskenebene** (Register DATEI, ALLGEMEIN, AUSWERTUNGEN, …): Nicht mehr verwenden. Bestehende FiBu-Masken bei Rebuild auf PageToolbar umstellen.
- **Suite-Navigation** (z. B. FIBU Suite: START + Links zu Hauptbuch, Debitoren, …): Bleibt erlaubt als **Navigation**, aber ohne Office-Ribbon-Optik; Bezeichnung z. B. „Suite-Navigation“ oder „Tab-Leiste“.

---

## 6. Umsetzung

- **Neue Seiten:** Nur noch PageToolbar + Shortcuts + (sobald vorhanden) Sprachsteuerung.
- **Bestehende Seiten mit Ribbon:** Bei nächstem größerem Refactoring auf PageToolbar umstellen; bis dahin Ribbon als Legacy führen.
- **Design System / FIBU-SUITE-TODO:** Verweis auf dieses Dokument; kein neues „Ribbon-Komponente“-Pattern mehr, sondern PageToolbar + Sprachsteuerung + Tastaturkürzel als Standard.

---

## 7. Referenzen

- PageToolbar: `packages/frontend-web/src/components/navigation/PageToolbar.tsx`
- Globale Shortcuts: `packages/frontend-web/src/lib/shortcuts/global-shortcuts.ts`
- Command Palette: `packages/frontend-web/src/components/navigation/CommandPalette.tsx`, `components/innendienst/CommandPalette.tsx`
- GlobalShortcutProvider / ShortcutHelpPanel: `packages/frontend-web/src/components/shortcuts/`
- FIBU-Suite und Ribbon-Abschaffung: [docs/FIBU-SUITE-TODO.md](FIBU-SUITE-TODO.md) (Abschnitt 0.1)
- KI Usability Microservices: [docs/architecture/KI-USABILITY-MICROSERVICES.md](architecture/KI-USABILITY-MICROSERVICES.md)
