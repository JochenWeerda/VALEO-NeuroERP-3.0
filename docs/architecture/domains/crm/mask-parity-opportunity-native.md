---
title: CRM Opportunity — Native Parity-Matrix (UIX-039)
type: reference
audience: [entwickler, architektur, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-06-29
version: 1.0.0
description: Legacy-Opportunity vs. native ScreenDefinition crm/opportunity — Readiness und Restarbeit.
---

# UIX-039 — CRM Opportunity Native Parity-Matrix

Stand: 2026-06-29 · ScreenDefinition: `crm/opportunity` · `adapter.temporary: false`

## Ergebnis

Opportunity ist der **dritte native Rollout** nach CRM 360 und einkauf/supplier.
Alle 6 mandatory Readiness-Gates und alle 6 advisory Gates sind grün (`generatorReady=true`, `advisoryScore=1.0`).

## Tabs

| Bereich | Legacy | Native ScreenDefinition | Status |
|---------|--------|-------------------------|--------|
| Stammdaten | Opportunity-Detail | Tab `kopf` — opportunity_nr, bezeichnung, Phase, Betrag, Wahrscheinlichkeit | ✅ paritaetsnah |
| Aktivitäten | Tab / Liste | Tab `aktivitaeten`, serverPagination, Sort/Filter | ✅ paritaetsnah |
| Angebote | Tab / Quotes | Tab `angebote`, serverPagination, Sort/Filter | ✅ paritaetsnah |

## Actions

| Action | dangerLevel | permission | Status |
|--------|-------------|------------|--------|
| edit | safe | crm.opportunity.update | ⚠ UIX-042 Frontend |

## AgentMaskContract

| Feld | Status |
|------|--------|
| businessPurpose | ✅ explizit |
| examplePrompts | ✅ 3 Beispiele |
| sensitiveFields | ✅ umsatz, wahrscheinlichkeit |
| testSelectors.screenRoot | ✅ `[data-testid='crm-opportunity-360']` |

## Offene Restarbeit

| Priorität | Thema | Slice |
|-----------|-------|-------|
| P2 | Frontend `useUniversalMaskRuntime` auf Opportunity-Route | UIX-042 |
| P2 | Browser-E2E Legacy vs. Native | UIX-042 |

## Verweise

- ScreenDefinition: `app/core/screen_definitions.py` → `build_crm_opportunity_screen_definition()`
- Benutzerhandbuch: [Masken-Plattform — Rollout-Piloten](../../benutzerhandbuch/masken-plattform.md)
- CRM 360 Referenz: [UIX-034 Parity-Matrix](../../../adr/uix-034-crm360-native-parity-matrix.md)
