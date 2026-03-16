# Wave-44 Status

## Scope
Process Routing Contracts + Data Lineage Contracts

## Zielbild

Wave 44 ergänzt den Process-Kernel um zwei Querschnittsthemen:

1. **Process Routing Contracts**: Regelbasiertes Nachrichtenrouting mit priorisierten
   Routing-Regeln (niedrigere Zahl = höhere Priorität), 6 Bedingungstypen
   (IMMER/WERT_GLEICH/WERT_GROESSER/WERT_KLEINER/FELD_VORHANDEN/ROLLE_ERLAUBT),
   AND-Logik innerhalb einer Regel, DEAD_LETTER-Fallback bei keinem Match.
   6 Standardregeln für kontrakt_annahme (3) und ap_approval (3).

2. **Data Lineage Contracts**: Datenherkunftsgraph mit gerichteten Knoten
   (QUELLE/TRANSFORMATION/AGGREGATION/SENKE/ZWISCHENSPEICHER) und Transformationskanten
   (FILTER/PROJEKTION/ANREICHERUNG/BERECHNUNG/NORMALISIERUNG/ZUSAMMENFUEHRUNG),
   BFS-Pfadfindung und DFS-Zyklus-Erkennung.
   Standardgraph für Agrar-Annahme-Settlement-Prozess (5 Knoten, 5 Kanten, azyklisch).

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/process_routing_contracts.py` | `RoutingBedingung.pruefe()` (6 Typen, Fehlerresistenz), `RoutingRegel.pruefe_bedingungen()` (AND), `RoutingEntscheidung.wurde_geroutet` | abgeschlossen |
| AP2 | `app/core/process_routing_contracts.py` | `route_nachricht()` (Prioritätssortierung, erster Match gewinnt, DEAD_LETTER-Fallback), `get_default_routing_regeln()` (6) | abgeschlossen |
| AP3 | `app/core/data_lineage_contracts.py` | `LineageKnoten` (ist_quelle, ist_senke), `LineageKante`, `LineageGraph` (quellen, senken, hat_zyklus DFS, finde_pfad BFS) | abgeschlossen |
| AP4 | `app/core/data_lineage_contracts.py` | `erstelle_lineage_graph()`, `get_default_lineage_graph()` (5 Knoten, 5 Kanten, azyklischer DAG) | abgeschlossen |
| AP5 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/routing/regeln`, `POST /process/routing/route` | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/lineage/graph`, `POST /process/lineage/pfad` | abgeschlossen |

## Abnahmekriterien

- `route_nachricht()`: Regeln nach prioritaet sortiert; erster Match gewinnt; kein Match → DEAD_LETTER
- WERT_GROESSER/KLEINER: gibt False zurück bei TypeError/ValueError (keine Exception)
- `finde_pfad(A, A)` → [A] (Selbstreferenz)
- `finde_pfad(Senke, Quelle)` → [] (keine Rückwärtspfade in DAG)
- `hat_zyklus` = False für Standard-DAG; True wenn Rückwärtskante existiert
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave44_routing_lineage.py` — 60 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave44_routing_lineage.py -q --no-cov
# Ergebnis: 60 passed
```

## Status
`abgeschlossen`
