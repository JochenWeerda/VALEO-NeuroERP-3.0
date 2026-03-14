# E2E-Prozessketten-Report

Generiert durch `scripts/process_kernel/build_e2e_chain_report.py`

## Referenzkette

| Aggregat | Referenzfeld | Elternaggregat | Status |
|----------|-------------|----------------|--------|
| `HarvestAcceptance` | `contract_id` | `KonContract` | ✅ vorhanden |
| `QualityProtocol` | `acceptance_id` | `HarvestAcceptance` | ✅ vorhanden |
| `AgrarSettlement` | `protocol_id` | `QualityProtocol` | ✅ vorhanden |
| `AgrarSettlement` | `contract_id` | `KonContract` | ✅ vorhanden |
| `APInvoice` | `settlement_id` | `AgrarSettlement` | ✅ vorhanden |
| `JournalEntry` | `invoice_id` | `APInvoice` | ✅ vorhanden |

## Zusammenfassung

- Gesamt: 6 Referenzen
- Vorhanden: 6
- Fehlend: 0

## Ergebnis: Kette vollstaendig ✅