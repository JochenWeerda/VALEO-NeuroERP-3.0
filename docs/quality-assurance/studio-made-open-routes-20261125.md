---
title: Studio-made offene Routen — Hebung
type: qa-evidence
audience: [agent, entwickler, qa]
owner: Cursor Cloud
status: aktiv
last_reviewed: 2026-11-25
description: Inventar und Create-Paritaet fuer Altmasken (Agrar, CRM, Finance).
---

# Studio-made offene Routen (2026-11-25)

## Inventar (main, `mask_route_migration_inventory.py`)

| Klasse | Anzahl |
|--------|--------|
| Routen gesamt | 1147 |
| runtime_wired | 1037 |
| legacy_wrapper (`createLegacyMaskPage`) | 35 |
| hand_built | 69 |
| legacy_mask_pattern (Routen) | 0 |
| ObjectPage/ListReport-Seiten (`*-legacy.tsx` u. a.) | 16 |

Qualitaetskatalog: [made-by-studio-qualitaetsversprechen.md](../architecture/uix/made-by-studio-qualitaetsversprechen.md).

## Erste Hebung

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `agrar/saatgut` (+ Stamm-Routen) | Detail native, Create → ObjectPage-Legacy | `creation` in SD + `createStammNativeDetailPage` ohne Legacy |
| `agrar/duenger` (+ Stamm-Routen) | wie oben | wie oben |
| `crm/lead-detail` Anlage | LeadMaskBuilder / LegacyLeadDetail | `UniversalNativeCreatePage` (`crm/lead`) |
| `finance/debitoren-stamm` | totgeladener Legacy-Import | native Detail + Capture `finance/debitoren/new` |

## Zweite Hebung (Batch 2)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `finance/bankkonto` (`bankkonten-stamm`) | Create → ObjectPage-Legacy (+ Client-IBAN-Lookup) | `creation` → POST `/api/v1/banken/konten`; IBAN-Pruefung serverseitig |
| `finance/kreditor` (`kreditoren-stamm`) | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/finance/creditors` (CreditorWrite-Felder) |
| `crm/opportunity` (`opportunity-detail`) | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/crm/opportunities/`; `tenant_id` optional im Schema |

Permission-Projektion (UI): `finance.bankkonto.*` / `finance.kreditor.*` → FINANCE_*; `crm.opportunity.*` → CRM_* / SALES_*.

## Dritte Hebung (Batch 3)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `einkauf/anfrage` (`anfrage-stamm`) | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/einkauf/anfragen` |
| `qualitaet/reklamation` | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/reklamationen` (`responseIdKey=reklamation_id`, Positionen-Tabelle) |
| `crm/kontakt` (`kontakt-detail`) | ScreenId `crm/kontakte/new` + Legacy | `crm/kontakt` + POST `/api/v1/crm/contacts/` (nested `data.id`) |
| `qualitaet/labor-detail` | Legacy-ObjectPage | `creation` → POST `/api/v1/qualitaet/labor-auftraege` |
| `service/anfrage-detail`, `service/anfrage/neu` | Legacy-ObjectPage | `creation` → POST `/api/v1/service/anfragen` |
| `crm/betriebsprofil` | fehlende ScreenId + Legacy | POST `/api/v1/crm/betriebsprofile` |
| `personal/mitarbeiter/neu` | Legacy | POST `/api/v1/personal/mitarbeiter` |
| `stammdaten/betriebsstaetten` | Legacy | POST `/api/v1/stammdaten/betriebsstaetten` (`responseIdKey=filial_nr`) |
| `stammdaten/hausbanken` | Legacy | POST `/api/v1/stammdaten/hausbanken` (`responseIdKey=bank_nr`) |
| `stammdaten/mengeneinheiten` | Legacy | POST `/api/v1/artikel/mengeneinheiten/stamm` |
| `crm/vertreter` (`vertreterstamm`) | fehlende ScreenId + Legacy | POST `/api/v1/crm/vertreter` (`responseIdKey=vertreter_nr`) |
| `UniversalNativeCreatePage` | nur `response.data.id` | `responseIdKey` + Defaults ausserhalb der Formularfelder + nested `data.id` |

## Sechste Hebung (Batch 6)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `stammdaten/artikelbestandteile` | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/artikel/bestandteile/stamm` (`responseIdKey=bestandteil_nr`); GET `/stamm/{nr}` |
| `stammdaten/artikelverpackung` | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/artikel/verpackungen` (`responseIdKey=verpackungs_nr`) |
| `stammdaten/artikel-stoffstrom` | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/artikel/stoffstrom`; GET `/{id}` |
| `stammdaten/individuelle-artikelnummern` | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/artikel/individuelle-nummern` |
| `verkauf/kunde-neu`, `verkauf/kunden-stamm-enhanced` | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/crm/customers/` → `/crm/customer-360/{id}` |

Permission-Projektion (UI): `stammdaten.stoffstrom|bestandteil|verpackung|indiv_artikel.*` → STAMMDATEN-Rollen; `verkauf.kunde.*` → CRM/SALES.

## Siebte Hebung (Batch 7)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `preise/individualpreise` | Legacy-ObjectPage | POST `/api/v1/preise/individualpreise` |
| `preise/rabattgruppen` | Legacy-ObjectPage | POST `/api/v1/preise/rabatte/gruppen` |
| `preise/zu-abschlaggruppen` | Legacy-ObjectPage | POST `/api/v1/kontrakte/zuabschlagsgruppen` |
| `verkauf/dauerauftraege` | Legacy-ObjectPage | POST `/api/v1/dauerauftraege` (`responseIdKey=da_nr`, Positionen-Tabelle) |
| `produktion/rezepturgruppen` | Legacy-ObjectPage | POST `/api/v1/produktion/mischfutter/rezepturgruppen` (`responseIdKey=gruppe_nr`) |

## Achte Hebung (Batch 8)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `fibu/geschaeftsjahre` | Legacy-ObjectPage | POST `/api/v1/fibu/geschaeftsjahre` (finance_admin) |
| `lager/massebilanz` | Legacy-ObjectPage | POST `/api/v1/massebilanz` |
| `lager/permanente-inventur` | Legacy-ObjectPage | POST `/api/v1/inventur/piv`; GET `/{id}` |

## Neunte Hebung (Batch 9)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `fibu/zahlungsmeldungen` | Legacy-ObjectPage | POST `/api/v1/fibu/zahlungsmeldungen` |
| `fibu/op-skonto-auszifferung` | Legacy-ObjectPage | POST `/api/v1/fibu/op-auszifferung` |
| `fibu/stammdaten` | Legacy-ObjectPage | POST `/api/v1/fibu/stammdaten/zahlungsformulare` |

## Zehnte Hebung (Batch 10)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `finance/bank-stamm` | Legacy-Factory | Alias auf `finance/bankkonto` Create |
| `agribusiness/field-service-task-neu` | Legacy + fehlende SD | neue SD + POST `/api/v1/agribusiness/field-service-tasks` |

## Elfte Hebung (Batch 11)

| Maske / Runtime | Vorher | Nachher |
|-----------------|--------|---------|
| `UniversalNativeCreatePage` | nur flaches POST | optional `payloadEnvelope` (z. B. `data`) |
| `personal/schulung-neu` | Legacy (Training `{data}`) | Native Create mit `payloadEnvelope=data` |

## Zwoelfte Hebung (Batch 12)

Ops-/Workspace-Masken vom falschen `createStammNativeDetailPage`-Factory geloest:
`admin/ai-approvals`, `admin/command-monitor`, `admin/agenten-integration` (spezialisiert),
`kontrakte/mengenzeitraeume` (pfadgebundenes Workspace).

## Dreizehnte Hebung (Batch 13)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `agrar/rohwarengruppen` | `createLegacyMaskPage` | SD + POST `/api/v1/rohware/gruppen` (`responseIdKey=gruppe_nr`); GET `/{nr}` |

## Vierzehnte Hebung (Batch 14)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `agrar/vermehrungsvertraege` | `createLegacyMaskPage` | SD + POST `/api/v1/saatzucht/vermehrungsvertraege` (`responseIdKey=vertrag_nr`) |

## Fuenfzehnte Hebung (Batch 15)

Alle verbleibenden `createLegacyMaskPage`-Wrapper (Admin-Suite, Admin-Ops, Agrar-Prozess,
Home, Konditionen, KIM-Panels) auf direkte Re-Exports umgestellt.
Inventar: `legacy_wrapper` **0** (vorher 35).

## Sechzehnte Hebung (Batch 16)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `fibu/abschluss-checklist-detail` | Factory+Legacy | POST `/api/v1/finance/closing-checklists` |

## Siebzehnte Hebung (Batch 17)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `einkauf/angebot` | Factory+Legacy (kein POST) | POST `/api/v1/einkauf/angebote` + SD `creation` |
| `einkauf/anlieferavis` | Factory+Legacy (kein POST) | POST `/api/v1/einkauf/anlieferavis` + SD `creation` |

Live `createStammNativeDetailPage` + `legacyImport`: **0**.

## Paritaets-Nachzug (Batch 17b) — verbindliche Invariante

Studio-made Masken duerfen gegenueber dem Vorgaenger **keine Funktionseinschränkung
und keine fehlenden Datenfelder** haben. Human, CI und MCP bedienen dieselben
`commandEndpoint`s (MCP-WRITE-015 / Made-by-Studio Gate C).

| Maske | Nachweis |
|-------|----------|
| `einkauf/angebot` | Legacy-Felder (Stammdaten/Angebot/Konditionen) + Aktionen pruefen/genehmigen/ablehnen/inBestellung + PUT; Test `tests/test_einkauf_studio_field_parity.py` |
| `einkauf/anlieferavis` | Legacy-Felder (Bestellung/Fahrzeug/Positionen/Bemerkungen) + senden/bestaetigen/stornieren (+ wareneingang additiv) + PUT; gleicher Test |

Inventar: `belegSeite(...)` zaehlt als `runtime_wired` (`mask_runtime_evidence`).

## Achtzehnte Hebung (Batch 18)

| Maske / Thema | Nachher |
|---------------|---------|
| `agrar/zinsabrechnung` | `NativeListPage` + SD mit Anlegen (alle Legacy-Formfelder) + buchen/stornieren/drucken |
| Kundenakte / Kontrakt-Detail | Universal-Mask Standard (Opt-out statt Opt-in) |
| Reine `<Navigate replace>`-Seiten | Inventar-Klasse `technical_page` (keine Altmasken) |

Inventar nach Batch 18: `hand_built`-Routen ~50 (Domain), `legacy_wrapper` 0.

## Neunzehnte Hebung (Batch 19) — Paritaet Human/CI/MCP

| Maske | Nachher |
|-------|---------|
| `agrar/sammelabrechnung` | `NativeListPage` + Create (alle Wizard-Felder inkl. `harvest_acceptance_ids`) + berechnen/buchen/löschen |
| `agrar/annahmen-qualitaet-nachtrag` | Worklist `missing_quality` + Zeilen-Nachtrag (`/qualitaetsprotokoll`) + Batch (`/quality-batch`, JSON-rows) |
| `kontrakte/mengenzeitraeume` | Stub-SD ersetzt: volle Aktionsmenge (Zeitraum anlegen/generieren/löschen, Gruppe, Abschlag); JSON-Body fuer `/generieren` |
| Redirects (`verkauf/kunden-stamm`, `crm/kunden-cockpit`, …) | Inventar `technical_page` via programmatisches `navigate(…, {replace:true})` |
| `NativeListPage` | Pfad-Platzhalter aus Eingabewerten (Header-Aktionen pfadgebunden) |

Inventar nach Batch 19: `runtime_wired` ~1088, `hand_built` ~38, `legacy_wrapper` 0.

## Zwanzigste Hebung (Batch 20)

| Maske / Fix | Nachher |
|-------------|---------|
| `agrar/erntefenster-konfig` | NativeListPage: Create aus Vorlage (alle Felder), Settlement-Nav, Sandbox-Nav, Backfill-Pfad-Alias |
| Inventar | `technical_page` nicht mehr in Handgebaut-Liste; Redirects sauber getrennt |

Inventar nach Batch 20: `hand_built` ~37.

## Noch offen (Folge)

- `hand_built` Prozessmasken (u. a. `annahme/rohware`, `lager/materialfluss`, Agrar-Ops-Legacy) — **nur mit Feld-/Aktionsparitaet**
- Gate D Browser/Image pro Maske; Permission-Projektion nach Generatorlauf nachziehen

## Tests

```bash
python -m pytest tests/test_studio_parity_batch19.py tests/test_zinsabrechnung_studio_parity.py \
  tests/test_einkauf_studio_field_parity.py -q --noconftest -o addopts=
cd packages/frontend-web && npx vitest run \
  src/__tests__/pages/mask-objectpage-stamm-native-route.test.ts \
  src/__tests__/bank-account-form-contract.test.tsx \
  src/__tests__/components/mask-builder/screen-permissions.test.ts
```
