# Wave-21 Status

## Scope
Kontrakt-Preisformel-Engine + Settlement-Journal-Bridge (Gap 006, Gap 001)

## Zielbild

Wave 21 schließt zwei verbliebene P0-Luecken:
Gap 006 (Kontrakt-Preislogik Fix/Formel/Terminmarkt einheitlich,
0 ungeklaerte Preisabweichungen >24h) und vervollständigt Gap 001
(E2E Kontrakt→Settlement ohne Medienbruch) durch eine GoBD-konforme
Journal-Entry-Bridge vom genehmigten Settlement in die FiBu.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/price_formula_engine.py` | Preislogik-Engine: FixedPrice, FormulaPrice (Basis±Aufschlag), TerminmarktPrice (MATIF-Referenz); `evaluate_price()` gibt auditierbare PriceEvaluation zurueck | abgeschlossen |
| AP2 | `app/core/settlement_journal_bridge.py` | Bridge Settlement→FiBu: GoBD-konformer JournalEntryDraft (Soll/Haben-Saetze, Gegenkonto, Buchungsdatum, Prozessreferenz) | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/settlement/price-preview/{settlement_id}` — Preis-Preview mit Formel-Audit-Spur | abgeschlossen |
| AP4 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/settlement/journal-preview/{settlement_id}` — Buchungsvorschau vor Verbuchung | abgeschlossen |
| AP5 | `app/core/price_formula_engine.py` | Preisabweichungs-Alert: `PriceDeviationAlert` bei >5% Abweichung; `build_deviation_alert()` | abgeschlossen |
| AP6 | `app/core/settlement_e2e_reference.py` | E2E-Referenzkette Kontrakt→Annahme→Charge→Qualitaet→Settlement→Journal; `coverage_pct`, `missing_refs` | abgeschlossen |

## Abnahmekriterien

- `evaluate_price()` liefert fuer alle drei Preistypen (Fix, Formel, Terminmarkt) eine `PriceEvaluation` mit Audit-Spur
- `PriceDeviationAlert` wird ausgeloest wenn berechneter Preis um >5% vom Referenzpreis abweicht
- `JournalEntryDraft` traegt Soll/Haben-Saetze, Gegenkonto, Buchungsdatum und Prozessreferenz
- E2E-Referenzkette ist vollstaendig und maschinell pruefbar
- Alle Contracts tragen `schema_version=1`
- Keine Schichtverletzungen

## Tests

| Datei | Tests | Scope |
|-------|-------|-------|
| `tests/test_process_kernel_wave21_price_journal.py` | 37 | AP1/AP5: Preislogik (Fix/Formel/Terminmarkt + Alert); AP2: Journal-Bridge (Balance, GoBD-Felder, USt); AP6: E2E-Referenz (Coverage, missing_refs); AP3/AP4: API-Endpoints |

**Gesamt Wave 21: 37 Tests gruen**

## Gaps geschlossen

| Gap-ID | Beschreibung | Massnahme |
|--------|-------------|-----------|
| Gap 006 | Kontrakt-Preislogik Fix/Formel/Terminmarkt einheitlich | `price_formula_engine.py` mit `evaluate_price()` und `PriceDeviationAlert` |
| Gap 001 (teilweise) | E2E Kontrakt→Settlement ohne Medienbruch | `settlement_e2e_reference.py` + `settlement_journal_bridge.py` schliessen die Kette bis zum Journal-Entry |

## Status
`abgeschlossen` — 2026-03-14 — 1105 Tests Gesamtsuite gruen
