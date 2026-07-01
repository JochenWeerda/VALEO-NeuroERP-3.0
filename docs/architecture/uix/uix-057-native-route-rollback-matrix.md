---
title: UIX-057 — Native-Route Rollback- und Fallback-Matrix
type: reference
audience: [entwickler, qa, agent, betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-07-01
version: 1.0.0
description: Rückfallstrategie nach UIX-051 — alle 26 nativen Detailrouten mit Legacy-Fallback und Rollback-Methode.
---

# UIX-057 — Native-Route Rollback- und Fallback-Matrix

Stand nach **UIX-051** (alle 26 ScreenDefinitions mit `/:id`-Native-Routen). Legacy-ObjectPages sind **nicht gelöscht** — Rollback ist jederzeit über Alias-Priorität möglich.

## Rollback-Prinzip

1. **Sofort (Routing):** Native-Eintrag in `route-aliases.json` entfernen oder auf Legacy-`module` umstellen → `npm run routes:generate` → Deploy.
2. **Generator-Priorität:** `generate-tanstack-routes.mjs` bevorzugt `*-native` Aliase. Ohne nativen Alias gewinnt Legacy/auto.
3. **Redirect (optional):** `legacy-redirects.json` für URL-Umleitung ohne Code-Löschung.
4. **Feature-Flag (Pilot):** einzelne Masken weiterhin über Env-Flags in Pilot-Specs isolierbar.

## Risiko-Legende

| Level | Bedeutung |
|---|---|
| **low** | Stammdaten / Lesefokus, geringe Mutation |
| **medium** | Fachliche Mutation, reversibel |
| **high** | Zahlungs-/Freigabe-Risiko, Audit-Pflicht |
| **critical** | Massenzahlung, Agent gesperrt, 4-Augen |

## Matrix (26 native SDs)

| screenId | nativeRoute (primär) | legacyFallback (Modul) | risk | rollbackMethod |
|---|---|---|---|---|
| crm/customer-360 | `crm/kunden/:id` | `@/pages/crm/kunden-stamm-modern` | low | Alias entfernen → `kunden-stamm-modern` oder `kunden-stamm` |
| crm/lead | `crm/lead/:id` | `@/pages/crm/lead-detail` | low | Native-Alias löschen |
| crm/opportunity | `crm/opportunity/:id` | `@/pages/crm/opportunity-detail` | medium | Native-Alias löschen |
| einkauf/supplier | `einkauf/lieferanten/:id` | `@/pages/einkauf/lieferanten-stamm` | low | Native-Alias löschen |
| einkauf/purchase-order | `einkauf/bestellung/:id` | `@/pages/einkauf/bestellung-stamm` | medium | Native-Alias löschen |
| einkauf/anfrage | `einkauf/anfrage/:id` | `@/pages/einkauf/anfrage-stamm` | low | Native-Alias löschen |
| einkauf/angebot | `einkauf/angebot/:id` | `@/pages/einkauf/angebot-stamm` | medium | Native-Alias löschen |
| einkauf/anlieferavis | `einkauf/anlieferavis/:id` | `@/pages/einkauf/anlieferavis` | medium | Native-Alias löschen |
| einkauf/auftragsbestaetigung | `einkauf/auftragsbestaetigung/:id` | `@/pages/einkauf/auftragsbestaetigung` | low | Native-Alias löschen |
| finance/ap-invoice | `finance/ap-invoice/:id` | `@/pages/einkauf/rechnungseingang` | high | Native-Alias löschen; Freigabe-Endpoint prüfen |
| finance/ar-open-item | `finance/ar-open-item/:id` | `@/pages/finance/op-debitoren` (Detail) | high | Native-Alias löschen |
| finance/payment-run | `finance/payment-run/:id` | `@/pages/finance/zahlungslauf-kreditoren` | **critical** | **Nicht als normale Produktivroute freigeben** ohne 4-Augen; Alias entfernen + Ops-Freigabe |
| finance/debitor | `finance/debitor/:id` | `@/pages/finance/debitoren-stamm` | medium | Native-Alias löschen |
| finance/kreditor | `finance/kreditor/:id` | `@/pages/finance/kreditoren-stamm` | medium | Native-Alias löschen |
| finance/bankkonto | `finance/bankkonto/:id` | `@/pages/finance/bankkonten-stamm` | medium | Native-Alias löschen |
| lager/article-stock | `lager/artikel/:id` | — (kein separates Legacy-Detail) | low | Native-Alias löschen |
| lager/stock-movement | `lager/stock-movement/:id` | `@/pages/lager/lagerbewegungen` (Detail) | medium | Native-Alias löschen |
| sales/delivery-note | `sales/delivery-note/:id` | — | medium | Native-Alias löschen |
| sales/sales-order | `sales/sales-order/:id` | — | **high** | Native-Alias löschen; O2C-Kette prüfen |
| agrar/kontrakte | `agrar/kontrakt/:id` | — | **high** | Native-Alias löschen; Settlement-Kette prüfen |
| agrar/harvest-settlement | `agrar/harvest-settlement/:id` | `@/pages/agrar/sammelabrechnung` | **high** | Native-Alias löschen |
| agrar/duenger | `agrar/duenger/:id` | `@/pages/agrar/duenger-stamm` | low | Native-Alias löschen |
| agrar/saatgut | `agrar/saatgut/:id` | `@/pages/agrar/saatgut-stamm` | low | Native-Alias löschen |
| qualitaet/reklamation | `qualitaet/reklamation/:id` | `@/pages/qualitaet/reklamation-detail` | medium | Native-Alias löschen |
| futtermittel/einzelfuttermittel | `futtermittel/einzelfuttermittel/:id` | `@/pages/futtermittel/einzelfuttermittel-stamm` | low | Native-Alias löschen |
| futtermittel/mischfuttermittel | `futtermittel/mischfuttermittel/:id` | `@/pages/futtermittel/mischfuttermittel-stamm` | low | Native-Alias löschen |

## Kritische Masken — Ops-Hinweise

### finance/payment-run

- **Agent:** `forbiddenForAgents=True`, `humanApprovalRequired=True`, `freigeben` gestubt.
- **Produktivfreigabe:** erst nach AP+AR-Parity, 4-Augen-Freigabe und separate Ops-Freigabe.
- **Rollback:** Native-Alias `finance/payment-run/:id` entfernen → Legacy `zahlungslauf-kreditoren`.

### sales/sales-order

- **Kette:** Order-to-Cash — Regression in Lieferschein/Faktura prüfen.
- **Rollback:** Alias entfernen; Pilot `VITE_ENABLE_UNIVERSAL_MASK_SALES_ORDER` für isolierte Tests.

### finance/ap-invoice / finance/ar-open-item

- **Freigabe/Mahnung:** CommandEndpoints aktiv — Rollback nur mit Finance-Review.

### agrar/harvest-settlement / agrar/kontrakte

- **Kampagne/Settlement:** hoher fachlicher Schaden bei falscher Route — Smoke + E2E Pflicht.

## Verifikation nach Rollback

```bash
cd packages/frontend-web && npm run routes:generate
pytest tests/test_uix054_route_inventory_verification.py -m unit --no-cov
python scripts/generate_agent_handbuch.py --check
```

## Verweise

- [UIX-043 Masken-Inventur](uix-043-mask-migration-inventory.md)
- [Universal Mask Runtime Status](universal-mask-runtime-status.md)
- `packages/frontend-web/scripts/generate-tanstack-routes.mjs` — `candidatePriority`
