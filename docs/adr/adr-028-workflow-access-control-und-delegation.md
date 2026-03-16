# ADR-028: Workflow Access Control und Delegation

**Status:** Accepted
**Datum:** 2026-03-16
**Cluster:** Process Reliability / Process Core

---

## Kontext

Mit wachsender Prozesstiefe im Process-Kernel entstanden Anforderungen an feingranulare
Zugangskontrolle auf Workflow-Ressourcen und an flexible Aufgabenweitergabe:

- Nicht jede Rolle darf jeden Workflow-Schritt ausführen oder freigeben (4-Augen-Prinzip).
- Abwesenheitsvertretungen, Eskalationsketten und Pool-Zuweisung müssen systemisch abbildbar sein.
- Zustandsübergänge in Prozessen sollen formal verifizierbar sein (kein impliziter Statuswechsel).

## Entscheidung

1. **Workflow ACL Contracts** (`app/core/workflow_acl_contracts.py`): Feingranulare Zugangs­kontrolle
   per `AclRegel` (Ressource × Subjekt × Aktion). Auswertungslogik:
   - Sortierung nach `(prioritaet, 0=VERWEIGERN, 1=ERLAUBEN)` — Deny-Override bei gleicher Priorität.
   - Kein Match → Default-Deny (`angewandte_regel_id=""`).
   - Drei Aktionen: LESEN, SCHREIBEN, AUSFUEHREN, FREIGEBEN, ADMINISTRIEREN.

2. **Workflow Delegation Contracts** (`app/core/workflow_delegation_contracts.py`): Aufgaben­delegation
   über `DelegationsRegel` mit vier Typen (DIREKT/STELLVERTRETER/ESKALATION/POOL).
   - `loeseauf_delegation()`: ESKALATION hat höchste Priorität; WIDERRUFEN-Regeln werden ignoriert;
     leere `aufgaben_typen` = alle Aufgaben.
   - `eskalations_zeitpunkt()`: Konfigurierbare Frist in Minuten ab Erstellzeitpunkt.

3. **Process State Machine Contracts** (`app/core/process_state_machine_contracts.py`): Formale
   Zustandsautomaten mit fünf Wächterbedingungen (IMMER/FELD_VORHANDEN/WERT_GLEICH/ROLLE_ERLAUBT/
   WERT_GROESSER). Übergänge werden nach Priorität sortiert ausgeführt.

## Konsequenzen

- Positiv: Zugangsentscheidungen sind auditierbar, deterministisch und testbar ohne Datenbankzugriff.
- Positiv: Delegation und Eskalation sind in Kernlogik verankert, nicht in UI-Sonderlogik.
- Negativ: ACL-Regeln müssen konsistent mit dem Policy-Override-Modell (ADR-010) gehalten werden.
- Constraint: `app/core/`-Module dürfen weiterhin keine `app/api/`-Importe enthalten.

## Bezug zu anderen ADRs

- ADR-005 (Workflow-/Policy-Kern): State Machine ergänzt den bestehenden Workflow-Kern.
- ADR-010 (Policy-Override-Modell): ACL-Regeln arbeiten komplementär zu Policy-Overrides.
- ADR-023 (Governance Rollen- und Berechtigungsvererbung): ACL-Delegation implementiert das Vererbungsmodell.

## Implementierung

- Wave 46: `workflow_acl_contracts.py` (68 Tests)
- Wave 47: `process_state_machine_contracts.py` + `workflow_delegation_contracts.py` (128 Tests)
