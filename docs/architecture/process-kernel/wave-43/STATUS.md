# Wave-43 Status

## Scope
Workflow Checkpoint Contracts + Cross-Domain Projection Contracts

## Zielbild

Wave 43 ergänzt den Process-Kernel um zwei Infrastruktur-Querschnittsthemen:

1. **Workflow Checkpoint Contracts**: Zustandssicherung für langläufige Workflows mit
   Intervallregeln (NACH_JEDEM_SCHRITT/ALLE_5/ALLE_10/MANUELL), Veralterungs-Erkennung
   (`ist_veraltet(max_alter_minuten)`) und Wiederherstellungs-Contract mit
   ERFOLGREICH/VERALTET/FEHLERHAFT-Ergebnis. 4 Standardregeln für kontrakt_annahme,
   ap_approval, settlement_freigabe und compliance_pruefung.

2. **Cross-Domain Projection Contracts**: Überwachung domainübergreifender Read-Model-
   Projektionen mit Lag-Klassifizierung (KEIN/GERING/MODERAT/KRITISCH), pessimistischem
   Gesamtstatus (FEHLERHAFT > VERALTET > VERZOEGERT > AKTUELL) und CrossDomainJoin-
   Contracts mit Konsistenzlevel. 5 Standardprojektionen über Agrar, Finance, Compliance
   und Audit.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/workflow_checkpoint_contracts.py` | `WorkflowCheckpoint` (alter_minuten, ist_veraltet, ist_gueltig), `CheckpointRegel` (pruefe_intervall), `CheckpointWiederherstellung` (kann_fortgesetzt_werden) | abgeschlossen |
| AP2 | `app/core/workflow_checkpoint_contracts.py` | `erstelle_checkpoint()`, `stelle_checkpoint_wieder_her()` (FEHLGESCHLAGEN→FEHLERHAFT, veraltet→VERALTET, sonst ERFOLGREICH), `get_default_checkpoint_regeln()` (4) | abgeschlossen |
| AP3 | `app/core/cross_domain_projection_contracts.py` | `DomainProjection` (lag_stufe, ist_aktuell), `CrossDomainJoin` (ist_stark_konsistent), `ProjectionGesundheit` (kritische_projektionen, gesamtstatus) | abgeschlossen |
| AP4 | `app/core/cross_domain_projection_contracts.py` | `berechne_lag_stufe()` (<1s→KEIN, <10s→GERING, <60s→MODERAT, ≥60s→KRITISCH), `erstelle_projektions_gesundheit()`, `get_default_projektionen()` (5) | abgeschlossen |
| AP5 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/checkpoints/regeln`, `POST /process/checkpoints/erstelle` | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/projections/gesundheit`, `POST /process/projections/pruefe-lag` | abgeschlossen |

## Abnahmekriterien

- `pruefe_intervall()`: MANUELL immer False; ALLE_5 nur bei Vielfachen von 5 (>0); NACH_JEDEM_SCHRITT ab Schritt 1
- `stelle_checkpoint_wieder_her()`: prüft FEHLGESCHLAGEN vor Veralterung
- `naechster_schritt` aus `zustand.get("naechster_schritt", schritt_id)` bei ERFOLGREICH
- `gesamtstatus`: FEHLERHAFT wenn irgendeine Projektion FEHLERHAFT; dann VERALTET; dann KRITISCH-Lag → VERZOEGERT
- `kritische_projektionen`: KRITISCH-Lag OR status in {FEHLERHAFT, VERALTET}
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave43_checkpoints_projections.py` — 73 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave43_checkpoints_projections.py -q --no-cov
# Ergebnis: 73 passed
```

## Status
`abgeschlossen`
