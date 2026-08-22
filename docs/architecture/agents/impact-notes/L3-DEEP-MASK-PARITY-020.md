---
title: Impact Note L3-DEEP-MASK-PARITY-020
type: reference
audience: [architektur, frontend, backend, qa, agent]
owner: architecture
status: aktiv
last_reviewed: 2026-08-22
version: 1.0.0
---

# Impact Note L3-DEEP-MASK-PARITY-020

## Scope

Schliesst die live bestaetigten L3-Untermenue-Gaps ueber zentrale native
Maskenvertraege, feste Reporting-Projektionen und auditierte Operatoraktionen.

## Architekturartefakte

- Migration `l3_deep_mask_parity_20260822`
- 30 feste Report-Spezifikationen und unveraenderliche Bonuslaeufe
- tenantgebundene DMS-Suche und Terrorschutzprotokolle
- tenantgebundene Chargen-Operatorfunktion mit zentraler Tabellen-Auswahl
- kanonische Feldbuch-N/P2O5/K2O-Auswertung
- gespeicherte Belegkontroll-Sichten ohne duplizierten Statusautomaten

## Sicherheits- und Auditwirkung

Chargenfreigaben verlangen Qualitaetsfreigabe und menschlichen Grund.
Bonuskorrekturen erzeugen neue Laeufe. DMS, Sanktionen, Bonus und Chargen
filtern serverseitig nach Tenant. Externe DMS-Vorschau bleibt gegated.

## UI-Vertrag

Alle neuen Masken kompilieren ueber die Meridian-Kette. Die neue deklarative
`bulkActions`-Eigenschaft wird zentral in Schema, RenderPlan und
`FastTableRenderer` umgesetzt und uebergibt nur explizit ausgewaehlte Zeilen.
