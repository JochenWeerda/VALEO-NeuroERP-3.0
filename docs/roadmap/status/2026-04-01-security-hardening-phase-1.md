# Security Hardening Phase 1 - Status und Folgeplan (2026-04-01)

**Zweck:** Konsolidierter Status nach den abgearbeiteten Security-Slices `SEC-001` bis `SEC-013` sowie priorisierte Folgeplanung fuer die verbleibenden P1/P2-Funde.

## Ziel

- den aktuellen Security-Hardening-Stand in einer kompakten Roadmap-Statussicht festhalten
- die naechsten Security-Slices fuer Workboard und Folgeplanung klar priorisieren
- den Link zwischen operativer Triage und strategischem Leitplan dokumentieren

## Abgeschlossene Slices

| Slice | Fokus | Ergebnis |
|------|-------|----------|
| `SEC-001` | Repo-Secrets / Default-Credentials | harte Secrets entfernt, Defaults auf env-only / fail-fast gezogen |
| `SEC-002` | lokale zentrale Secret-Pflege | Vault + optionales OS-Keyring + CLI |
| `SEC-003` | Metrics + Copilot-WS | Auth-/Tenant-Bindung, kein Kontext-Spoofing |
| `SEC-004` | Supplier Portal | tenant-gebundene, parametrisierte Queries |
| `SEC-005` | Realtime-WebSockets | Bearer-Pflicht, tenant-spezifische Keys |
| `SEC-006` | Accounting Periods | Kontext-Tenant auf Create/List/Get/Update/Check |
| `SEC-007` | Creditors | keine freien Payload-/Query-/ID-basierten Tenant-Zugriffe |
| `SEC-008` | Einkauf-Router | Tenant-Isolation, Mass-Assignment-Whitelist, maskierte Fehler |
| `SEC-009` | Admin Mobile | SQL-Identifier-Whitelist |
| `SEC-010` | VIES | XML-Escaping im SOAP-Body |
| `SEC-011` | Documents Router | kein Information Disclosure via `str(e)` |
| `SEC-012` | Webhooks | SSRF-Block fuer localhost/private IPs |
| `SEC-013` | Print-/Export-Pfade | XSS-Schutz fuer `document.write`-basierte HTML-Interpolation |
| `SEC-014` | externer Vault | HashiCorp Vault + Production-Startup-Fail-Fast |
| `SEC-015` | Accruals / Provisions | tenant-gebundene Finance-Pfade |
| `SEC-016` | zentrale Egress-Policy | gemeinsame SSRF-/Outbound-Regel fuer Runtime-Pfade |
| `SEC-017` | CI-Sicherheitslane | feste Backend-/Frontend-Security-Regressionen |
| `SEC-018` | Frontend-HTML-Sinks | Inventur + Guard-Test fuer neue rohe HTML-Sinks |
| `SEC-019` | AP Approval Workflow | Tenant aus Kontext, Cross-Tenant-Invoices werden abgewiesen |
| `SEC-020` | Nebenbuch-Abstimmung | Reconciliation-/Export-Pfade sind tenant-gebunden |
| `SEC-021` | Tax Keys | CRUD und Lookup ziehen Tenant nur noch aus dem Kontext |

## Wirkungsbild

- Die ersten repoweiten CRITICAL/P1-Funde aus Secrets-, Backend-SAST- und Frontend-/Runtime-Hardening sind auf konkrete Slices heruntergebrochen und technisch verifiziert geschlossen.
- Besonders risikoreiche Muster sind jetzt systematisch reduziert:
  - freie Tenant-Zugriffe in Finance-/Einkauf-Routern
  - freie Finance-Query-Tenants in Approval-, Reconciliation- und Tax-Key-Routern
  - ungeschuetzte Realtime-/WS-Pfade
  - rohe Exception-Leaks
  - unkontrollierte Identifier-/XML-/HTML-Interpolation
  - unkontrollierte lokale Webhook-Ziele

## Verbleibende Hauptluecken

| Prioritaet | Thema | Warum noch offen |
|-----------|-------|------------------|
| `P0` | externer Produktions-Vault | lokales Keyring ist praktikabel fuer Dev, aber kein produktiver Secret-Store |
| `P1` | weitere Auth-/Tenant-Router | die SAST-Triage nannte breite Endpunktflaechen; bisher nur die hoechst priorisierten Router sind hart gemacht |
| `P1` | zentrale Egress-/SSRF-Policy | durch `SEC-016` geschlossen |
| `P1` | CI-Sicherheitslane | durch `SEC-017` geschlossen |
| `P2` | restliche Frontend-HTML-Pfade | durch `SEC-018` inventarisiert und als Guard-Test abgesichert |
| `P2` | Security-Observability | Verstoss- und Block-Events sind noch nicht als eigener Security-Dashboard-/Alerting-Pfad verdrahtet |

## Empfohlene Folge-Slices

1. `SEC-014` Externer Vault Adapter + Startup-Fail-Fast
2. `SEC-015` Weitere Auth-/Tenant-Router aus der SAST-Triage, jeweils einzeln und mit Dateibesitz
3. weiterer einzelner Backend-SAST-Slice mit klarem Dateibesitz
4. Security-Observability fuer Block-/Violation-Events
5. produktive Rollout-/Rotationsstrecke fuer den externen Vault

## Operative Regeln fuer die Folgephase

- keine Sammelpatches ueber mehrere Domains ohne klaren Dateibesitz
- pro Security-Slice mindestens ein direkter Regressionstest
- Workboard-, Open-Gaps- und Roadmap-Doku zusammen nachziehen
- fremde E2E-Artefakte und Generator-Diffs weiterhin nicht mit Sicherheits-Commits vermischen

## Verweise

- Strategischer Leitplan: [2026-03-31-strategic-next-steps.md](../2026-03-31-strategic-next-steps.md)
- Operativer Einstieg: [open-gaps-and-known-issues.md](../../project-context/open-gaps-and-known-issues.md)
- Slice-Status: [active-workboard.md](../../agent-ops/active-workboard.md)
