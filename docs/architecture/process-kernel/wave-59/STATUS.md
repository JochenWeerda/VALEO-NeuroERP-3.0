# Wave 59 — Consent Management + Workflow Trigger Contracts

**Status: ABGESCHLOSSEN**
**Datum: 2026-03-16**
**Tests: 142 grün, 0 Fehler**

## Scope

### Module

| Modul | Pfad | Beschreibung |
|-------|------|--------------|
| `process_consent_contracts` | `app/core/process_consent_contracts.py` | GDPR/DSGVO Consent Management und Datenverarbeitungsprotokolle |
| `workflow_trigger_contracts` | `app/core/workflow_trigger_contracts.py` | Workflow Trigger-Bedingungen und Aktivierungsregeln |

### Kernklassen

**process_consent_contracts:**
- `EinwilligungsTyp` — DATENVERARBEITUNG, MARKETING, ANALYSE, DRITTANBIETER, NOTWENDIG
- `EinwilligungsStatus` — ERTEILT, WIDERRUFEN, AUSSTEHEND, ABGELAUFEN
- `RechtsgrundlageTyp` — Art. 6(1)(a/b/c/f) DSGVO
- `Einwilligung` — mit `ist_aktiv()` und `aktueller_status()` Methoden (Ablaufprüfung)
- `VerarbeitungsProtokoll` — Audit-Trail für Datenverarbeitungsvorgänge
- `EinwilligungsRegister` — Sammlung mit Filterung nach Typ, Subjekt, Aktivstatus

**workflow_trigger_contracts:**
- `TriggerTyp` — ZEITPLAN, EREIGNIS, SCHWELLWERT, MANUELL, ABHAENGIGKEIT
- `TriggerStatus` — AKTIV, INAKTIV, AUSGELOEST, FEHLER
- `BedingungsOperator` — GLEICH, UNGLEICH, GROESSER, KLEINER, GROESSER_GLEICH, KLEINER_GLEICH, ENTHAELT
- `TriggerBedingung` — mit `pruefe(kontext)` für alle Operatoren, TypeError-safe
- `WorkflowTrigger` — mit `pruefe_bedingungen(kontext)`, INAKTIV=immer False, leer=immer True

### FastAPI Endpoints (4 neu)

| Method | Pfad | Beschreibung |
|--------|------|--------------|
| GET | `/api/v1/process/consent/register` | Default Einwilligungsregister mit Aktivstatus |
| POST | `/api/v1/process/consent/pruefe` | Prüfung ob Subjekt gültige Einwilligung hat |
| GET | `/api/v1/process/trigger/regeln` | Alle Workflow-Trigger-Regeln |
| POST | `/api/v1/process/trigger/pruefe-bedingungen` | Trigger-Bedingungen gegen Kontext prüfen |

### Testabdeckung

| Klasse | Tests |
|--------|-------|
| Enums (Typen, Status, Operatoren) | 8 |
| `Einwilligung.ist_aktiv()` | 11 |
| `Einwilligung.aktueller_status()` | 7 |
| `EinwilligungsRegister` Methoden | 8 |
| Default-Register Datenprüfung | 22 |
| `VerarbeitungsProtokoll` | 2 |
| `TriggerBedingung.pruefe()` alle Operatoren | 22 |
| `WorkflowTrigger.pruefe_bedingungen()` | 7 |
| Default-Trigger Verhalten | 18 |
| FastAPI Endpoints | 23 |
| **Gesamt** | **128 Unit + 14 API = 142** |

## Default-Daten Referenzzeit 2026-03-16 10:00:00

| ID | Subjekt | Typ | Status | Aktiv |
|----|---------|-----|--------|-------|
| EW-001 | KUNDE-001 | DATENVERARBEITUNG | ERTEILT | Ja (läuft 2027 ab) |
| EW-002 | KUNDE-001 | MARKETING | WIDERRUFEN | Nein |
| EW-003 | KUNDE-002 | NOTWENDIG | ERTEILT | Ja (kein Ablauf) |
| EW-004 | KUNDE-002 | ANALYSE | ERTEILT → ABGELAUFEN | Nein (35 Tage abgelaufen) |
| EW-005 | KUNDE-003 | DATENVERARBEITUNG | AUSSTEHEND | Nein |

| Trigger | Typ | Status | Bedingungen |
|---------|-----|--------|-------------|
| WT-001 | SCHWELLWERT | AKTIV | menge_tonnen >= 100 AND status == "GEPRUEFT" |
| WT-002 | EREIGNIS | AKTIV | ereignis_typ == "WAAGE_ABGESCHLOSSEN" |
| WT-003 | ZEITPLAN | AKTIV | (keine — immer True) |
| WT-004 | ABHAENGIGKEIT | INAKTIV | "settlement" in abgeschlossen_workflows |
| WT-005 | SCHWELLWERT | AKTIV | feuchte_pct > 15.0 |

## Regression

- 4331 bestehende Tests weiterhin grün
- 3 Fehler in `test_process_kernel_wave4_ap4_ap5_ap6.py` waren vor Wave 59 vorhanden (pre-existing `NameError` in `runtime_operations.py`)
