---
title: UIX-034 CRM 360 Native Parity Matrix
description: Legacy-Runtime vs. Native-Runtime Vergleich fuer das CRM 360 Cockpit (crm/customer-360)
type: reference
audience: [entwicklung, architektur, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-06-29
version: 1.1.0
---

# UIX-034 - CRM 360 Native Parity Matrix

**Status:** Accepted
**Date:** 2026-06-29

## Kontext

Nach UIX-028/029 nutzt CRM 360 bei `adapter.temporary === false` den nativen `useUniversalMaskRuntime`-Pfad. Vor Abbau des Legacy-Fallbacks muss fachliche und technische Parität gegen die bestehende CRM-Maske nachgewiesen werden. UIX-033 liefert verschärfte Readiness-Gates als objektive Checkliste.

## Entscheidung

1. Parity-Matrix Legacy vs. Native als Referenzdokument führen (Tabs, Felder, Actions, AgentContract, Readiness).
2. Legacy-Fallback bleibt aktiv, bis E2E-Verifikation und Finance-Tab abgeschlossen sind (UIX-034d).
3. Kein weiterer Rollout-Kandidat wird über UIX-034 auf `generator_ready` gesetzt.

## Konsequenzen

Positiv: Nachweisbare Promotions-Grundlage für CRM 360 und Vorlage für UIX-038 (einkauf/supplier).
Negativ: Zwei Runtime-Pfade bleiben temporär parallel; Finance-Tab und Lookup-DataSources sind noch Lücken.

---

Stand: 2026-06-29. ScreenDefinition: `crm/customer-360`. Native Runtime ist aktiv, wenn `adapter.temporary === false`.

## Ergebnis

Die CRM-360-Maske ist im nativen Runtime-Pfad technisch generator-ready. Die neue Readiness-Logik trennt harte Gates von advisory Gates:

- `generatorReady = true`, wenn alle mandatory Gates gruen sind.
- Advisory Gates bleiben sichtbar, blockieren aber keine technische Generator-Freigabe.
- Der Legacy-Fallback bleibt aktiv, falls die native ScreenDefinition nicht geladen wird.
- Kein weiterer Rollout-Kandidat wird durch UIX-034 auf `generator_ready` gesetzt.

## Tabs

| Bereich | Legacy | Native ScreenDefinition | Status |
|---|---|---|---|
| Stammdaten | `CUSTOMER_MASK_OBJECT_PAGE_CONFIG` + `mapCustomerToMask` | Tab `masterdata` mit Kundennummer, Firma, Branche, Segment, Kreditlimit, Zahlungsbedingungen, Notizen | paritaetsnah |
| Adresse & Kommunikation | Teil des Legacy-Mappers | Tab `address` mit Strasse, PLZ, Ort, Land, Telefon, Fax, E-Mail | paritaetsnah |
| Ansprechpartner | Lazy Tab-Tabelle | Tab `contacts`, `serverPagination`, `dataSourceKey=contacts`, sortierbare und filterbare Spalte | paritaetsnah |
| Finanzen | Legacy-Tabelle fuer offene Posten vorhanden, aber nicht im nativen SD-Tab ausmodelliert | Tab `finance` existiert als leerer Platzhalter | offen |
| Auftraege | Lazy Tab-Tabelle | Tab `auftraege`, `serverPagination`, Sort/Filter-Spalten | paritaetsnah |
| Aktivitaeten | Lazy Tab-Tabelle | Tab `aktivitaeten`, `serverPagination`, Sort/Filter-Spalten | paritaetsnah |
| Dokumente | Lazy Tab-Tabelle | Tab `dokumente`, `serverPagination`, sortierbare Datumsspalte | paritaetsnah |

## Mandatory Readiness Gates

| Gate | CRM 360 Status | Evidenz |
|---|---|---|
| `schema_valid` | gruen | `schemaVersion`, `id`, `domain`, `mode`, `title` gesetzt |
| `non_temporary` | gruen | `adapter.type=native`, `temporary=false` |
| `data_sources` | gruen | `entity`, `contacts`, `auftraege`, `aktivitaeten`, `dokumente` definiert |
| `table_data_source_bound` | gruen | alle serverseitig paginierten Tabellen haben passende `dataSourceKey` |
| `table_columns_complete` | gruen | alle Tabellen haben mindestens zwei fachliche Spalten |
| `actions_classified` | gruen | `edit` und `create_activity` haben `dangerLevel=safe` und Permission |

## Advisory Gates

| Gate | CRM 360 Status | Bewertung |
|---|---|---|
| `sort_whitelist` | weitgehend gruen | `contacts`, `auftraege`, `aktivitaeten`, `dokumente` besitzen sortierbare Spalten |
| `filter_columns` | teilweise gruen | `contacts`, `auftraege`, `aktivitaeten` besitzen Filterspalten; `dokumente` bleibt Sort-only |
| `agent_contract` | gruen | explizites `agentContract.businessPurpose` vorhanden |
| `workflow_declared` | gruen | `noWorkflowReason` dokumentiert Verwaltungsobjekt ohne eigenen Prozessstatus |
| `stable_test_selectors` | gruen | `agentContract.testSelectors.screenRoot` gesetzt |
| `table_query_contract` | gruen | keine generischen Sort-/Filterkeys wie `col1` |

## Agent Contract

Der native Screen liefert einen expliziten Agent-Kontext:

- `businessPurpose`: 360-Grad-Kundenstamm-Cockpit fuer Vertrieb und CRM.
- `examplePrompts`: Analyse, Aktivitaet anlegen, offene Auftraege anzeigen.
- `sensitiveFields`: `kreditlimit`, `zahlungsbedingungen`, `notizen`.
- `testSelectors`: `screenRoot`, `primaryAction`, `summaryArea`.

Die generierten `readableFields` und `editableFields` kommen aus den nativen `fields[]` der Tabs. Damit sind Stammdaten und Adresse fuer Human UI und Agentenvertrag aus derselben ScreenDefinition ableitbar.

## Restarbeit

| Prioritaet | Thema | Einordnung |
|---|---|---|
| P1 | Finance-Tab nativ ausmodellieren | offene Posten/Kreditdaten als native Tabelle oder Felder an `finance` binden |
| P1 | Backend-Command fuer `create_activity` | UIX-035: ActionRuntime produktiv ueber validate/dryRun/propose/execute fuehren |
| P2 | Lookup-DataSources | Land/Branche als echte Lookup-Felder statt Freitext |
| P2 | Browser-Paritaet mit Testdaten | Playwright-Smoke gegen native Runtime und Legacy-Fallback mit gleicher Fixture |
| Extern | Performance- und GitHub-Actions-Nachweis | UIX-032 muss CI-seitig gruen belegt werden |

## Abnahmebezug

- Backend: `tests/test_agent_mask_contract.py` prueft AgentContract und Readiness-Gates.
- Frontend: `packages/frontend-web/src/__tests__/components/mask-builder/runtime/generatorReadiness.test.ts` prueft mandatory/advisory Split.
- Lokale Gate-Ergebnisse werden in `docs/project-context/open-gaps-and-known-issues.md` und im Workboard nachgetragen.
