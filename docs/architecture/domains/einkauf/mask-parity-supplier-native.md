---
title: Einkauf Lieferant — Native Parity-Matrix (UIX-038)
type: reference
audience: [entwickler, architektur, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-06-29
version: 1.0.0
description: Legacy-Lieferantenmaske vs. native ScreenDefinition einkauf/supplier — Readiness und Restarbeit.
---

# UIX-038 — Lieferant Native Parity-Matrix

Stand: 2026-06-29 · ScreenDefinition: `einkauf/supplier` · `adapter.temporary: false`

## Ergebnis

Lieferantenstamm ist der **erste native Rollout nach CRM 360**. Alle 6 mandatory Readiness-Gates
und alle 6 advisory Gates sind grün (`generatorReady=true`, `advisoryScore=1.0`).

## Tabs

| Bereich | Legacy | Native ScreenDefinition | Status |
|---------|--------|-------------------------|--------|
| Stammdaten | Lieferanten-Stammmaske | Tab `kopf` — lieferanten_nr, firma, Adresse, Kontakt, Zahlungsbedingungen, Lieferzeit, Status | ✅ paritaetsnah |
| Bestellungen | Lazy Tab / Liste | Tab `bestellungen`, serverPagination, Sort/Filter | ✅ paritaetsnah |
| Ansprechpartner | Kontaktliste | Tab `kontakte`, serverPagination, Sort/Filter | ✅ paritaetsnah |

## Actions

| Action | dangerLevel | permission | commandEndpoint | Status |
|--------|-------------|------------|-----------------|--------|
| edit | safe | einkauf.lieferant.update | — (Stub) | ⚠ UIX-042 Frontend |
| neue_bestellung | safe | einkauf.bestellung.create | stubReason | ⚠ UIX-041 Backend |

## AgentMaskContract

| Feld | Status |
|------|--------|
| businessPurpose | ✅ explizit |
| examplePrompts | ✅ 3 Beispiele |
| sensitiveFields | ✅ zahlungsbedingungen, lieferzeit_tage |
| testSelectors.screenRoot | ✅ `[data-testid='einkauf-supplier-360']` |

## Offene Restarbeit

| Priorität | Thema | Slice |
|-----------|-------|-------|
| P1 | Frontend `useUniversalMaskRuntime` auf Lieferanten-Route (analog CRM) | UIX-042 |
| P2 | `neue_bestellung` commandEndpoint produktiv | UIX-041 |
| P2 | Browser-E2E Legacy vs. Native | UIX-042 |

## Verweise

- ScreenDefinition: `app/core/screen_definitions.py` → `build_supplier_screen_definition()`
- Benutzerhandbuch: [Lieferantenstamm 360°](../../benutzerhandbuch/einkauf.md#lieferantenstamm-360-native)
- Rollout-Report: [UIX-037](../../uix/uix-037-rollout-readiness-report.md)
