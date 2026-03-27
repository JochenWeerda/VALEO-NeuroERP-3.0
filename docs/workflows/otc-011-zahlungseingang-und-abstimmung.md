# OTC-011 — Zahlungseingang und Abstimmung (Order-to-Cash Folgelane)

**Slice:** OTC-011 | **Lane:** Order-to-Cash (Folge) | **Status:** `in arbeit` — Erstanalyse  
**Owner:** Cursor Agent | **Datum:** 2026-03-27

---

## A — Einordnung

Folgeslice zu **OTC-010** (`docs/workflows/otc-010-order-to-cash.md`): Nach Rechnungsstellung und -verbuchung folgen **Zahlungseingang** (Debitoren) und **Abstimmung** mit offenen Posten. Diese Lane ist bewusst von der **Agrar-Lane (VK-013)** getrennt, damit Agenten nicht gleichzeitig dieselben Module bearbeiten.

**Referenz OTC-010 Abschnitt G:**

- Punkt 4: Zahlungseingangs-Flow, u. a. `POST /api/v1/finance/payment-runs` (im Kontext zu prüfen: bestehende Nutzung ist primär **Kreditoren-Zahlungslauf** in `zahlungslauf-kreditoren.tsx`).

---

## B — Abgrenzung

| Thema | Seite / Modul | Rolle für OTC-011 |
|--------|----------------|-------------------|
| Offene Debitoren-Posten | `finance/op-debitoren.tsx` | OP-Liste, Status `offen` / `teilbezahlt` — **Kern für Abstimmung** |
| Mahnwesen / Zahlung buchen | `finance/mahnwesen.tsx`, `dunning-editor.tsx` | Buchung „bezahlt“ auf Mahnlauf — **Teilprozess**, nicht vollständiger Bankimport |
| Kreditoren-Zahlungslauf | `finance/zahlungslauf-kreditoren.tsx` | Nutzt `/api/v1/finance/payment-runs` für **Ausgangszahlungen** — als technische Referenz für API-Muster, nicht als fachliche 1:1-Übernahme für Debitoren-Eingang |

---

## C — Zielbild (Soll)

1. Zahlungseingänge (Bank / manuell) den **richtigen offenen Rechnungen/OPs** zuordnen.
2. OP-Status bis **ausgeglichen** führen, konsistent mit Fibu/Docflow.
3. Optional: Verknüpfung zurück zur **Rechnung** (`invoice-editor` / Docflow-ID) für Nachvollziehbarkeit.

---

## D — Ist-Stand (kurz)

- `op-debitoren.tsx`: Masken-basierte OP-Erfassung mit Debitor, Betrag, Fälligkeit, Status — **Grundlage für „was ist offen“**.
- Vollständiger **Bankimport + automatische Zuordnung** ist in dieser ersten Ausbaustufe **nicht** als geliefert dokumentiert; Slice kann das als Gap benennen.

---

## E — Empfohlene nächste Umsetzungsschritte

1. API-Inventar: welche Endpoints buchen Zahlungen auf Debitoren-OPs (oder nur Mahnwesen)?
2. Einheitlicher `apiClient`-Pfad prüfen (`@/lib/axios` vs `@/lib/api-client`) analog OTC-010-Warnung.
3. Browser-Use-Checkliste unter `docs/quality-assurance/browser-use-checklists.md` ergänzen, wenn Flow testbar ist.

---

## F — Verweis

- Card: `docs/cards/finance/OTC-011-zahlungseingang-und-abstimmung.md`
- Parallele Arbeit: `docs/agent-ops/active-workboard.md` (Abschnitt **Parallele E2E-Lanes**)
