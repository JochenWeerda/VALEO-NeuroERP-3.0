# Wave 7 Paket B Status

## Paket
- Name: `Reklamation, Ausnahmen, Preisabsicherung und Silo-Protokolle`
- Zugeordnete Aufgaben: `AP3`, `AP4`, `AP5`, `AP6`
- Status: `abgeschlossen`

## Ziel
Reklamationen und Ausnahmen werden als formale Prozess-Aggregate mit Zustandsmaschinen
modelliert. Preisabsicherung (MATIF-Hedge) und Silo-GoBD-Protokolle schliessen die
verbleibenden Luecken im Handelsprozess.

## Gelieferte Artefakte (Zielstand)

| Datei | Inhalt | Status |
|-------|--------|--------|
| `app/core/reklamation.py` | `Reklamation`, `ReklamationsZustandsmaschine`, `ReklamationStore`, CRM-/DMS-Referenzen, SLA-Status, Audit-Trail | umgesetzt |
| `app/core/exception_workflow_extension.py` | `AusnahmeAntrag`, `AusnahmeGenehmigungsregel`, `pruefe_ausnahme_notwendig()` | umgesetzt |
| `app/core/price_hedge.py` | `HedgeReference`, `KontraktHedgeBindung`, `berechne_hedge_quote()`, `HedgeStore` | umgesetzt |
| `app/core/silo_protokolle.py` | `SiloReinigungsprotokoll`, `TrocknungsProtokoll` | umgesetzt |
| `app/api/v1/endpoints/reklamation_api.py` | CRUD Reklamationen + Statuswechsel, CRM-/DMS-Verknuepfung, Audit- und SLA-Sichten | umgesetzt |
| `app/api/v1/endpoints/price_hedge_api.py` | CRUD HedgeReferences + Absicherungsquote | umgesetzt |
| `tests/test_process_kernel_wave7_domain.py` | 28 Tests | umgesetzt |
| `tests/test_process_kernel_wave8_complaint_e2e.py` | 3 Tests | umgesetzt |

## Testergebnis

```
31 passed in 27.72s
```

- Reklamation Tests: 8 gruen
- Ausnahme Tests: 5 gruen
- HedgeReference Tests: 8 gruen
- Silo-Protokoll Tests: 5 gruen
- API Tests: 2 gruen
- Complaint-E2E-Tests: 3 gruen

## Erweiterung Gap 008

- Reklamationen tragen jetzt CRM-Referenzen, DMS-Dokumentreferenzen, SLA-Status und einen audit-freundlichen Hash-Trace.
- Die API bietet Detail-, Audit-, CRM-Lookup-, DMS-Update- und Ueberfaelligkeits-Sichten.
- Reklamationsfaelle koennen dadurch bis zum CRM-/DMS-Kontext und zur Frist-/Statuslogik durchverfolgt werden.

## Abnahmekriterien (alle erfuellt)

- `ReklamationZustandsmaschine.transition()` wirft `ValueError` bei ungueltigem Uebergang — grueen
- `AusnahmeAntrag` wird ausgeloest wenn Command-Payload Schwellenwert ueberschreitet — grueen
- `berechne_hedge_quote()` gibt 0 fuer ungesichert, 100 fuer vollstaendig gesichert — grueen
- `SiloReinigungsprotokoll.ist_gobd_vollstaendig()` prueft alle Pflichtfelder — grueen
- `TrocknungsProtokoll.trocknungseffekt_pct` berechnet korrekt aus Eingang/Ausgang — grueen

## Abhaengigkeiten

- `app/core/command_dispatcher.py` (Wave 5 AP1) — Dispatcher-Integration fuer Ausnahmen
- `app/core/contract_pricing.py` (Wave 6 B) — `KonContractLot` fuer Hedge-Bindung
- `app/core/silo_operations.py` (Wave 6 B) — `SiloCell` fuer Protokoll-Anbindung
- `app/core/audit_evidence.py` (Wave 3 AP2) — GoBD-Beleg-IDs
