# Security Hardening Phase 2 - Status und Folgeplan (2026-04-03)

**Zweck:** Konsolidierter Status fuer die nachgezogenen Sales-/Monitoring-Slices `SEC-031`, `SEC-032` und `SEC-034` sowie die naechste sinnvolle Folgeplanung.

## In dieser Runde geschlossen

| Slice | Fokus | Ergebnis |
|------|-------|----------|
| `SEC-031` | Sales Orders | freie Query-/Payload-Tenants entfernt; Item-Deletes, Re-Reads und Delivery-Mutationen tenant-gescoped |
| `SEC-032` | Sales Offers | freie Query-/Payload-Tenants entfernt; Update-/Delete-/Convert-Pfade und Item-Reset/Readback tenant-gescoped |
| `SEC-034` | Security Event Persistence | append-only JSONL-Persistenz fuer Security-Events; Monitoring und Admin-Summary lesen nach Restart weiter |

## Architekturwirkung

- Der Sales-Cluster folgt jetzt konsistent demselben Tenant-Hardening-Muster wie die bereits gehaerteten Delivery-Note-, Credit-Note- und Reporting-Router.
- Security-Observability ist nicht mehr rein fluechtig; Block-/Violation-Events ueberleben Prozessneustarts und bleiben fuer Dashboard, Monitoring und Triage sichtbar.
- Die Persistenz ist bewusst migrationsfrei gehalten: append-only JSONL statt neuer DB-Tabelle. Das reduziert Rollout-Risiko, ist aber nur ein Zwischenschritt.

## Verbleibende Hauptluecken

| Prioritaet | Thema | Warum noch offen |
|-----------|-------|------------------|
| `P1` | weitere einzelne Auth-/Tenant-Router | es bleiben weitere SAST-Funde ausserhalb des bisher gehaerteten Finance-/Sales-/Inventory-/Agrar-Clusters |
| `P1` | externer Vault Rollout | der Provider ist vorhanden, aber produktive Rotation, Onboarding und Betriebsroutine muessen noch nachgezogen werden |
| `P2` | DB-/Audit-Bridge fuer Security-Events | JSONL ist restart-stabil, aber noch keine relationale Auswertung oder zentrale Audit-Kette |
| `P2` | externes Security-Alerting | Dashboard zeigt Events, aber Weiterleitung an Mail/Webhook/ChatOps fehlt noch |

## Empfohlene naechste Slices

1. `SEC-035` weiterer einzelner Router ausserhalb Sales/Finance, z.B. `branches.py` oder `price_lists.py`
2. `SEC-036` DB-/Audit-Bridge fuer Security-Events
3. `SEC-037` externes Alerting fuer Security-Monitoring
4. `SEC-038` Vault-Rotations- und Betriebsstrecke

## Verweise

- Operativer Einstieg: [open-gaps-and-known-issues.md](../../project-context/open-gaps-and-known-issues.md)
- Slice-Status: [active-workboard.md](../../agent-ops/active-workboard.md)
- Vorheriger Security-Stand: [2026-04-01-security-hardening-phase-1.md](2026-04-01-security-hardening-phase-1.md)
