---
card_id: P2P-010
chain: procure-to-pay
chain_step: 0
card_type: overview
related_cards: [P2P-020, P2P-040, P2P-041, P2P-050]
flow_spine: flow-spine-procure-to-pay
workflow_doc: docs/workflows/p2p-001-procure-to-pay-direktbestellung.md
overlaps: [SEC-008, INT-SG-057]
---

# P2P-010 — Procure-to-Pay (Card)

**Slice:** P2P-010 | **Lane:** Procure-to-Pay | **Owner:** Cursor | **Datum:** 2026-06-26
**Status:** abgeschlossen (Overview; Detail-Slices P2P-020+)

---

## 1. Zweck

End-to-End-Übersicht der Beschaffungskette: Flow-Spine-Vorgang → Direktbestellung /
Vorbelegung → Bestellung → Wareneingang → Match → Zahlung. Diese Card ist der
**Overview-Einstieg** (Step 0) in der Ketten-Registry
[`docs/_internal/workflow-chains.md`](../_internal/workflow-chains.md).

## 2. Prozesskette (Cards)

| Step | Card | Rolle |
|------|------|-------|
| 0 | **P2P-010** (diese Card) | Overview / Gesamtkette |
| 1 | [P2P-020](../einkauf/P2P-020-direktbestellung-standardmaske.md) | Direktbestellung Standardmaske |
| 2 | [P2P-040](../einkauf/P2P-040-vorbelegung-standardmaske.md) | Vorbelegung Standard |
| 3 | [P2P-041](../einkauf/P2P-041-vorbelegung-aus-anfrage-und-vertrag.md) | Vorbelegung Anfrage/Vertrag |
| — | [P2P-050](../einkauf/P2P-050-wizard-schrittvalidierung.md) | Querschnitt Wizard-Validierung |

## 3. Betroffene Dateien (Kernpfad)

- `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx` — Standardmaske
- `packages/frontend-web/src/pages/workflow/flow-spine-procure-to-pay.tsx` — Flow-Spine
- `docs/workflows/p2p-001-procure-to-pay-direktbestellung.md` — Workflow-Analyse

## 4. API-Endpoints (Auszug)

| Endpoint | Methode | Zweck |
|---|---|---|
| `/api/v1/procurement/orders` | GET/POST | Bestell-CRUD |
| `/api/v1/procurement/requisitions` | GET/POST | Bedarfsmeldungen |
| `/api/v1/process/flow-spines/procure-to-pay/instances` | POST | Spine-Instanz |

## 5. Offene Folgearbeit

| ID | Thema | Priorität |
|----|-------|-----------|
| P2P-020-FU | Inline-Fehler pro Wizard-Schritt | P3 |
| P2P-030 | Bestellung speichern → Arbeitsliste (Workflow-Doku) | P3 |

## 6. Verweise

- Workflow: [p2p-001-procure-to-pay-direktbestellung.md](../../workflows/p2p-001-procure-to-pay-direktbestellung.md)
- Ketten-Registry: [workflow-chains.md](../_internal/workflow-chains.md)
- Inventar: [cards-inventory.md](../_internal/cards-inventory.md)

*Erstellt im Rahmen CARD-AUDIT-001 / DOC-CARD-FRONTMATTER-001 — 2026-06-26*
