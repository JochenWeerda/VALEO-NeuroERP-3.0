# KIM L3 S2 Review

Stand: 2026-06-09

## Befunde und Korrekturen

- Das Ang./Auf.-Dropdown wich vom L3-Sollvertrag ab: Kaufangebote,
  Kaufabrechnungen und Fremdbestaende standen statt Anfrage und Bestellung im
  Menue. Das Menue entspricht jetzt dem Bauplan.
- Die Auswahl Uebersicht setzte nur den externen Override zurueck und liess
  dadurch die zuvor aktive Kategorie im Panel stehen. Der Belegtab ist jetzt
  kontrolliert; `ALL` zeigt alle Belege und deaktiviert die fachlich unklare
  Neuanlage.
- Anfrage und Bestellung besitzen stabile kundenbezogene Tabellenansichten und
  kanonische Neu-Ziele.
- Die dokumentierten Informations-Shortcuts F11, Strg+B und Strg+Z sind
  verdrahtet.
- Alle elf Informationsmodule und alle sechs Ang./Auf.-Menuepunkte werden im
  Browser geklickt und auf Kundenkontext, aktiven Zieltab und Fehlerfreiheit
  geprueft.

## Verifikation

- Frontend TypeScript: gruen
- Playwright TypeScript: gruen
- fokussierter ESLint: gruen
- CRM360 Playwright: 17 Tests bestanden
- Workboard-Supervisor und `git diff --check`: gruen

