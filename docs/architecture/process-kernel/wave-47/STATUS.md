# Wave-47 Status

## Scope
Process State Machine Contracts + Workflow Delegation Contracts

## Zielbild

Wave 47 ergänzt den Process-Kernel um formale Verhaltenssteuerung und Aufgabenweitergabe:

1. **Process State Machine Contracts**: Formale Zustandsautomaten für Workflow-Prozesse mit
   Zuständen (START/NORMAL/WARTE/ENTSCHEIDUNG/ABSCHLUSS/FEHLER), Übergängen mit 5 Wächterbedingungen
   (IMMER/FELD_VORHANDEN/WERT_GLEICH/ROLLE_ERLAUBT/WERT_GROESSER) und priorisierter Ausführung.
   `fuehre_uebergang_aus()`: erste erlaubte Transition nach Priorität gewinnt; kein Match → erfolg=False.
   `Zustand.ist_endpunkt`: True für ABSCHLUSS und FEHLER.
   Standard-Automat `ZA-KONTRAKT-001` für Kontrakt-Freigabe: 6 Zustände, 6 Übergänge,
   4-Augen-Prinzip bei Beträgen > 10.000 EUR.

2. **Workflow Delegation Contracts**: Aufgaben-Delegation, Stellvertreterregeln und
   Eskalationsketten für Workflow-Tasks mit 4 Typen (DIREKT/STELLVERTRETER/ESKALATION/POOL).
   `loeseauf_delegation()`: ESKALATION hat höchste Priorität, dann nach Gültigkeitsbeginn absteigend;
   kein Match → Original-Subjekt bleibt zuständig (ist_delegiert=False).
   `DelegationsRegel.ist_gueltig()`: prüft Status AKTIV + Zeitfenster.
   `eskalations_zeitpunkt()`: erstellt_am + eskalations_nach_minuten.
   5 Standardregeln: DR-001 (Stellvertreter Urlaub), DR-002 (Eskalation nach 2h, STUFE_1),
   DR-003 (Eskalation nach 4h, STUFE_2), DR-004 (Pool-Zuweisung), DR-005 (WIDERRUFEN).

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/process_state_machine_contracts.py` | `Zustand` (ist_endpunkt), `Uebergang` (pruefe mit 5 Bedingungen), `UebergangsErgebnis` | abgeschlossen |
| AP2 | `app/core/process_state_machine_contracts.py` | `ZustandsAutomatDefinition` (start_zustand, endpunkt_ids, finde_uebergaenge), `fuehre_uebergang_aus()`, `get_default_zustandsautomat()` | abgeschlossen |
| AP3 | `app/core/workflow_delegation_contracts.py` | `DelegationsRegel` (ist_aktiv, ist_gueltig, gilt_fuer_aufgabe, eskalations_zeitpunkt), `DelegationsEntscheidung` | abgeschlossen |
| AP4 | `app/core/workflow_delegation_contracts.py` | `loeseauf_delegation()` (ESKALATION-Priorität, Default-kein-Match), `get_default_delegations_regeln()` (5) | abgeschlossen |
| AP5 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/state-machine/definition`, `POST /process/state-machine/uebergang` | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/delegation/regeln`, `POST /process/delegation/loeseauf` | abgeschlossen |

## Abnahmekriterien

- `Zustand.ist_endpunkt`: True nur für ABSCHLUSS und FEHLER
- `Uebergang.pruefe(WERT_GROESSER)`: False bei TypeError/ValueError (kein Crash)
- `fuehre_uebergang_aus()`: kein Match → `erfolg=False`, `zu_zustand_id==von_zustand_id`
- `loeseauf_delegation()`: ESKALATION gewinnt vor STELLVERTRETER bei gleichem Subjekt
- `loeseauf_delegation()`: WIDERRUFEN-Regeln werden ignoriert
- `loeseauf_delegation()`: leere `aufgaben_typen` = alle Aufgaben
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave47_state_machine_delegation.py` — 128 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave47_state_machine_delegation.py -q --no-cov
# Ergebnis: 128 passed
```

## Status
`abgeschlossen`
