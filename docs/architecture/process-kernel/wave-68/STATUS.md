# Wave-68 Status

## Scope
Process Health Dashboard Contracts + Workflow Dependency Visualization Contracts

## Zielbild

Wave 68 ergänzt den Process-Kernel um Überwachungs- und Visualisierungsverträge:

1. **Process Health Dashboard Contracts**: Komponentenüberwachung mit 5 MetrikTypen
   (DURCHSATZ/LATENZ/FEHLERRATE/VERFUEGBARKEIT/AUSLASTUNG), schwellwertbasierte Status-Berechnung
   (GESUND/DEGRADIERT/KRITISCH/AUSGEFALLEN/UNBEKANNT), Dashboard-Aggregation mit
   `gesamtstatus()`, `kritische_komponenten()` und `verfuegbarkeits_pct()`.

2. **Workflow Dependency Visualization Contracts**: Graph-Modell mit 7 KnotenTypen und
   5 KantenStilen, `hat_zyklen()` (DFS), `kritischer_pfad()` (längster Pfad START→ENDE),
   `ebenen_layout()` (topologisches BFS), GraphExport für Mermaid/DOT/JSON.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/process_health_dashboard_contracts.py` | MetrikSchwellwert.bewerte(), DashboardKomponente.berechne_status(), HealthDashboard.gesamtstatus() | abgeschlossen |
| AP2 | `app/core/workflow_dependency_visualization_contracts.py` | VisualisierungsGraph.hat_zyklen(), kritischer_pfad(), ebenen_layout() | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | GET /process/health-dashboard/schwellwerte, POST /process/health-dashboard/pruefe-status | abgeschlossen |
| AP4 | `app/api/v1/endpoints/process_kernel_api.py` | POST /process/visualisierung/graph/analyse, GET /process/visualisierung/knoten-typen | abgeschlossen |

## Abnahmekriterien

- `bewerte()`: wert < warnung_ab → GESUND; warnung_ab ≤ wert < kritisch_ab → DEGRADIERT; wert ≥ kritisch_ab → KRITISCH
- `berechne_status()`: keine Metriken → UNBEKANNT; status_override hat Vorrang
- `gesamtstatus()`: keine Komponenten → UNBEKANNT; schlechtester Komponentenstatus gewinnt
- `hat_zyklen()`: False für DAG, True für Zyklus
- `kritischer_pfad()`: leere Liste wenn kein START/ENDE; längster Pfad bei mehreren Optionen
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave68_health_visualization.py` — 164 Tests, alle grün

## Status
`abgeschlossen`
