# OTC-011 — Zahlungseingang und Abstimmung

**Slice:** OTC-011 | **Lane:** Order-to-Cash (Folge) | **Status:** abgeschlossen | **Owner:** Claude Sonnet 4.6
**Datum:** 2026-03-27

---

## A — Übersicht

Folgeslice zu **OTC-010**: Nach Rechnungsstellung verbindet OTC-011 die Rechnung mit dem
Debitoren-OP und ermöglicht Zahlungserfassung, Skonto, Ausgleich und Mahnstufenerhöhung.
Zusätzlich existiert eine separate `payment-matching.tsx`-Seite für Bankimport und automatisches
Matching. Die beiden Flows sind derzeit nicht verknüpft (offener Punkt OTC-011-P4).

### Beteiligte Masken

| Schritt | Datei | Hauptaktion |
|---|---|---|
| 4 | `sales/invoice-editor.tsx` | Button „OP / Zahlungseingang” — Deep-Link |
| 5 | `finance/op-debitoren.tsx` | OP laden, Zahlungen erfassen, Ausgleich buchen |
| 5b | `finance/payment-matching.tsx` | Bankimport CSV + Auto-Matching (isoliert) |

---

## B — Vollständige Card-Liste

1. `OTC-011-C1` Deep-Link von `invoice-editor` nach `/finance/op-debitoren?rechnungsnr=`
2. `OTC-011-C2` OP per Rechnungsnummer auflösen (`GET /finance/open-items?search=`)
3. `OTC-011-C3` Zahlungen manuell in `ZahlungenTable` erfassen (Zahlung, Skonto, Gutschrift, Storno)
4. `OTC-011-C4` Ausgleich buchen: jede Zahlung als `POST /finance/open-items/{id}/settle`
5. `OTC-011-C5` Ausgleichshistorie lesen: `GET /finance/open-items/{id}/settlements`
6. `OTC-011-C6` Mahnstufe erhöhen: `POST /finance/dunning/{id}/mahnung`
7. `OTC-011-C7` Bankimport + Auto-Matching: `payment-matching.tsx` (eigenständige Seite)

---

## C — Mermaid-Diagramm

```mermaid
flowchart TD
    A[invoice-editor.tsx\nRechnung gespeichert] -->|Button OP / Zahlungseingang\n?rechnungsnr=nr| B[op-debitoren.tsx]

    B --> C{?rechnungsnr\nvorhanden?}
    C -->|nein| D[Leere OP-Maske\nneu anlegen]
    C -->|ja| E[GET /finance/open-items\n?search=rechnungsnr\nOP-ID auflösen]

    E --> F{Treffer?}
    F -->|nein| G[Hinweis-Banner\nkein OP gefunden]
    F -->|ja| H[GET /finance/open-items/id\nOP laden + mapOpenItemApiToForm]

    H --> I[OP-Formular\nGrunddaten / Beträge / Mahnwesen]
    I --> J[ZahlungenTable\nZahlungen manuell erfassen]

    J -->|Aktion: zahlung| K[Zahlung mit offenem Betrag vorbelegen]
    J -->|Aktion: skonto| L[Skonto-Betrag als Zahlung eintragen]

    I -->|Aktion: ausgleich| M{Zahlungen\nvorhanden?}
    M -->|ja| N[POST /finance/open-items/id/settle\nje Zahlung]
    M -->|nein| O[saveData OP aktualisieren]
    N --> P[navigate /finance/op-debitoren]
    O --> P

    I -->|Aktion: mahnung| Q[POST /finance/dunning/id/mahnung\nraw fetch — Mahnstufe + 1]
    I -->|Tab: Ausgleichshistorie| R[GET /finance/open-items/id/settlements]

    S[payment-matching.tsx\nBankimport] -->|isoliert, kein Link zu OP-Debitoren| T[POST /finance/payments/import/csv]
    T --> U[POST /finance/payments/auto-match\noder manuelles Match]

    style A fill:#f59e0b
    style B fill:#6366f1,color:#fff
    style S fill:#94a3b8,color:#fff
```

---

## D — Soll-Ist-Abweichungen

| # | Soll | Ist nach OTC-011 | Bewertung |
|---|---|---|---|
| D-01 | Rechnung verlinkt direkt in Debitoren-OP | Button „OP / Zahlungseingang” navigiert mit `?rechnungsnr=` | behoben |
| D-02 | OP per Rechnungsnummer gefunden, nicht per manueller ID-Eingabe | `GET /open-items?search=` + exakter Match, Fallback auf erstes Ergebnis | behoben |
| D-03 | Zahlungen manuell erfassbar (Zahlung, Skonto, Gutschrift) | `ZahlungenTable` mit Edit/Add/Remove; offener Betrag wird live berechnet | behoben |
| D-04 | Ausgleich persistiert Zahlungen im Backend | `POST /open-items/{id}/settle` je Zahlung; Storno-Typ wird übersprungen | behoben |
| D-05 | Ausgleichshistorie lesbar | Tab „Ausgleichshistorie” mit `GET /open-items/{id}/settlements` | behoben |
| D-06 | Debitor-Auswahl aus CRM | `GET /crm/customers` dynamisch geladen, Dropdown zeigt Kunden-Nr + Name | behoben (P1) |
| D-07 | Mahnung nutzt einheitlichen `apiClient` | `apiClient.post()` von `@/lib/axios` — raw fetch entfernt | behoben (P2) |
| D-08 | Nach Ausgleich zu OP-Liste navigieren | `navigate('/finance/offene-posten')` + Toast mit OP-Nummer | behoben (P3) |
| D-09 | Bankimport und manuelle OP-Erfassung verbunden | Match-Toast mit „OP öffnen"-Button → `/finance/op-debitoren?opId=` | behoben (P4) |
| D-10 | `payment-matching.tsx` apiClient korrekt | Nutzt `@/lib/api-client` mit korrekter `{ data }` Destrukturierung | ok |

---

## E — UI/CRUD-Status

### `invoice-editor.tsx` (`@/lib/api-client` — AxiosResponse, korrekt mit `.data`)

| Funktion | Status |
|---|---|
| Deep-Link „OP / Zahlungseingang” bei gespeicherter Rechnung | OK — navigiert mit `?rechnungsnr=` |
| Button nur sichtbar wenn `docId` vorhanden und `invoice.number` gesetzt | OK |
| `nextTypes = []` — kein Docflow-Folgebeleg für OP | Design-Entscheidung; OP ist kein Docflow-Beleg |

### `op-debitoren.tsx` (`@/lib/axios` — unwrapped, kein `.data`-Bug)

| Funktion | Status |
|---|---|
| `?rechnungsnr=` auflösen via `GET /open-items?search=` | OK |
| OP laden via `GET /open-items/{id}` + `mapOpenItemApiToForm` | OK |
| Zahlungen manuell erfassen (ZahlungenTable) | OK |
| Skonto-Zahlung vorbelegen | OK |
| Ausgleich buchen (`POST /settle`) | OK |
| Ausgleichshistorie (`GET /settlements`) | OK |
| Mahnung eskalieren (`apiClient.post`) | OK — P2 behoben |
| Export (`POST /export/list`) | OK |
| Debitor-Dropdown (CRM-API) | OK — P1 behoben |

### `payment-matching.tsx` (`@/lib/api-client` — `.data` korrekt)

| Funktion | Status |
|---|---|
| Ungematchte Zahlungen laden | OK |
| CSV-Bankimport | OK |
| Match-Vorschläge laden | OK |
| Manuelles Match | OK |
| Auto-Match | OK |

---

## F — Risiken

### hoch

- keine (P1–P4 behoben)

### mittel

- keine

### niedrig

- `/finance/offene-posten` als Navigations-Ziel nach Ausgleich muss als Route existieren;
  falls sie fehlt, wird ein 404 angezeigt. Prüfen und ggf. Redirect einrichten.

---

## G — Empfehlungen

1. ~~**OTC-011-P1:**~~ behoben — Debitor-Dropdown aus CRM API.
2. ~~**OTC-011-P2:**~~ behoben — Mahnung nutzt `apiClient.post()`.
3. ~~**OTC-011-P3:**~~ behoben — Navigation zu `/finance/offene-posten` + Toast mit OP-Nummer.
4. ~~**OTC-011-P4:**~~ behoben — Match-Toast mit „OP öffnen"-Button.
5. **OTC-012:** Belegkette-Visualisierung — Auftrag → LS → Rechnung → OP → Zahlung als
   Timeline im Flow-Spine Cockpit.
6. Route `/finance/offene-posten` prüfen — muss als ListReport existieren oder Redirect auf
   bestehende OP-Übersicht einrichten.

---

*Erstellt von Claude Sonnet 4.6 — Slice OTC-011 — 2026-03-27*
