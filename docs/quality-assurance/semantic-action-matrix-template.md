# Semantic Action Matrix Template

## Zweck

Dieses Template beschreibt fachliche Klick- und Workflow-Vertraege fuer
Playwright- und modellbasierte Tests. Ziel ist nicht "Button klickbar", sondern
"fachlich richtige Aktion im richtigen Entity-Kontext".

## Mindestfelder

| Feld | Bedeutung |
|------|-----------|
| `screen` | Fachliche Maske oder Prozesssicht |
| `action_id` | Stabile technische ID fuer Tests |
| `label` | Sichtbares Label oder ARIA-Name |
| `technical_handler` | Handler, Route, API-Call oder Component-Event |
| `required_context` | Pflichtkontext wie `customerId`, `lotId`, `tenantId` |
| `expected_route` | Erwartete Zielroute oder modaler Kontext |
| `expected_content` | Erwarteter Seitentitel, Hauptinhalt oder Landmark |
| `entity_context` | Erwartete Entitaet und ID-Weitergabe |
| `crud_type` | `create`, `read`, `update`, `delete`, `process`, `print`, `export` |
| `back_target` | Erwarteter Ruecksprung nach Browser-Back oder UI-Zurueck |
| `workflow_category` | Fachlicher Prozesscluster |
| `must_not_404` | Muss immer `true` sein, ausser Legacy-Fallback wird bewusst getestet |
| `console_error_policy` | `none`, `known_allowlist`, `captured_warning` |
| `external_gate` | Reales oder simuliertes Pruefer-Gate, falls relevant |

## YAML-Beispiel

```yaml
screen: CRM360
action_id: crm360.offer.create
label: Angebot erstellen
technical_handler: navigateToCreateOffer
required_context:
  - customerId
expected_route: /sales/offers/new?customerId=:customerId
expected_content: Angebot erstellen
entity_context:
  entity: offer
  source_entity: customer
  source_id: customerId
crud_type: create
back_target: /crm/customer/:customerId
workflow_category: customer-to-revenue
must_not_404: true
console_error_policy: none
external_gate: not_applicable
```

## Playwright-Pruefpunkte

- Aktion ist sichtbar.
- Aktion ist fuer den Kontext enabled oder liefert fachlich begruendeten Disabled-State.
- Klick oeffnet erwartete Route, Maske, Modal oder Druckansicht.
- Entity-Kontext wird korrekt uebergeben.
- Keine 404-Seite.
- Keine unerwarteten Console Errors.
- CRUD-Operation schreibt/liest den erwarteten Datensatz oder mockt den Vertrag bewusst.
- Browser-Back und fachlicher Zurueck-Button fuehren zum erwarteten Ziel.
- Externe Gates werden als offen, simuliert oder real bestanden dokumentiert.

## Report-Kategorien

| Kategorie | Bedeutung |
|-----------|-----------|
| `OK` | Vertrag erfuellt |
| `MISSING_LINK` | Aktion sichtbar, aber nicht verdrahtet |
| `WRONG_TARGET` | Falsche Route, Maske oder Entity |
| `MISSING_CRUD` | Fachlicher CRUD-Flow fehlt oder ist nur UI |
| `BACK_BUG` | Zurueck fuehrt zu 404, falschem Kontext oder Datenverlust |
| `CONSOLE_ERROR` | Unerwarteter Browser-/Request-Fehler |
| `WORKFLOW_QUESTIONABLE` | Technisch moeglich, fachlich unplausibel |
| `EXTERNAL_GATE_OPEN` | Interne Simulation ok, reale Abnahme fehlt |

## VALEO-Prioritaet

1. POS/TSE und Tagesabschluss
2. WMS/Silo/Lot/QS/Trace
3. FiBu/Payroll/DATEV/Kanzlei-Export
4. CRM360 Customer-to-Revenue
5. QS/Reklamation/CAPA

