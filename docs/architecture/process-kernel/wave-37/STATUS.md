# Wave-37 Status

## Scope
DMS + OCR + strukturierte Extraktion (Gap 045) + Offene Integrationsfähigkeit für Agenten (Gap 048)

## Zielbild

Wave 37 schließt zwei P1-Lücken:
Gap 045 (DMS + OCR — 60 % weniger manuelle Belegerfassung durch strukturierte Extraktion)
und Gap 048 (Offene Integrationsfähigkeit für Agenten — 10 externe Agent-Use-Cases live).

Die DMS-OCR-Contracts definieren typisierte Belegerkennungsregeln mit Schlagwort-Matching,
Confidence-Einstufung (HOCH/MITTEL/NIEDRIG/UNZUVERLÄSSIG) und automatische Statusbewertung
von OCR-Extraktionsergebnissen.
Die Agent-Integration-Contracts liefern ein vollständiges Tool-Manifest (10 Tools, 10 Use-Cases)
mit Capability-Matching, Autorisierungsstufen und Rate-Limit-Deklaration für externe Agenten.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/dms_ocr_contracts.py` | `DokumentTyp`, `BelegErkennungsRegel`, `confidence_stufe()`, `klassifiziere_dokument()`, `bewerte_ocr_ergebnis()` | abgeschlossen |
| AP2 | `app/core/dms_ocr_contracts.py` | `get_default_erkennungsregeln()` — 7 Regeln für Eingangsrechnung, Lieferschein, Wiegeschein, Kontrakt, Qualitätsprotokoll, Zertifikat, Gutschrift | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/dms/erkennungsregeln[?dokument_typ=]` + `POST /process/dms/classify` | abgeschlossen |
| AP4 | `app/core/agent_integration_contracts.py` | `AgentTool`, `AgentUseCase`, `match_capabilities()` mit VOLLSTAENDIGER/TEILWEISER/KEIN_MATCH | abgeschlossen |
| AP5 | `app/core/agent_integration_contracts.py` | `get_default_agent_tools()` (10 Tools) + `get_default_agent_use_cases()` (10 Use-Cases) | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/agent-tools[?kategorie=][?autorisierung=]` + `POST /process/agent-tools/match` | abgeschlossen |

## Abnahmekriterien

- `klassifiziere_dokument()` → case-insensitives Schlagwort-Matching, confidence = treffer/gesamt
- `manuell_pruefen=True` wenn beste Confidence < 30 %
- `bewerte_ocr_ergebnis()` → ERFOLGREICH ≥ 80 %, TEILWEISE ≥ 50 %, MANUELL_ERFORDERLICH ≥ 20 %, FEHLGESCHLAGEN < 20 %
- `match_capabilities()` → VOLLSTAENDIGER_MATCH nur wenn alle angefragten Capabilities abgedeckt
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave37_dms_agent.py` — 60 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave37_dms_agent.py -q --no-cov
# Ergebnis: 60 passed
```

## Status
`abgeschlossen`
