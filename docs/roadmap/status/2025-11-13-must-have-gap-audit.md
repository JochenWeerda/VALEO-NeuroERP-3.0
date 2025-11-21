# Must-Have Gap Audit – 13.11.2025 (Update)

## Überblick

- Quelle: `docs/roadmap/a-eins-gap-backlog.md`
- Kontext: Prüfung der Verzeichnisstruktur und Implementierungsstände der **Must-Have**-Gaps zur a.eins-Parität.
- Ergebnis: InfraStat & Zoll-Service jetzt vorhanden (Integrationstests/Helm eingerichtet), übrige Must-Haves unverändert teil/offen. Konkrete Arbeitspakete siehe Abschnitt **Nächste Schritte**.

## Gap-Status im Detail

### InfraStat/Intrastat Meldewesen
- **Status:** Bereit für Produktiv-Rollout (15.11.2025)
- **Nachweis:** `services/compliance/infrastat/**` + Helm-Overrides mit IDEV-Referenzen (`docs/deployment/helm/infra/values-infrastat.yaml`), Prometheus-Alerts aktiviert (`alerts.infrastatEnabled`), Runbook `docs/deployment/runbook/infra/idev-setup.md` mit Port-Forward/Smoke-Test.
- **Restaufgaben:** Go-Live-Termin planen und produktive Credentials hinter `infrastat-idev` Secret legen; Monitoring dauerhaft beobachten.

### Zoll- & Exportkontrolle
- **Status:** Bereit für Produktiv-Rollout (15.11.2025)
- **Nachweis:** `services/compliance/zoll/**` (Screening mit OFAC/EU-Anbindung, Delta-Updates + Backoff, Prometheus-Metriken `zoll_*`), Helm-Overrides (`docs/deployment/helm/infra/values-zoll.yaml`), Runbook `docs/deployment/runbook/compliance/zoll-setup.md`.
- **Restaufgaben:** Erweiterte Workflow-Policies im UI sowie produktive Geheimnisse pflegen.

### Mehrlager- & Chargenverwaltung
- **Status:** Frontend & Workflow verdrahtet (15.11.2025)
- **Nachweis:** `services/inventory/` publiziert Events nach Workflow-Service (`emit_workflow_event`), React-Frontend nutzt `useLotTrace` + Stock-Hooks, Docker/Helm + Compose aktiviert EventBus real.
- **Restaufgabe:** KPI/Tracing-Dashboards weiter ausbauen (z. B. ETA-Berechnungen, Alerts im UI).

### Finanz- & Anlagenbuchhaltung (GoBD)
- **Status:** Teilweise (Domain vorhanden, Service fehlt)
- **Nachweis:** Umfangreiche Domain in `packages/finance-domain/**`, jedoch `services/finance/` lediglich Stub ohne Implementierung (`app/`-Package fehlt). Details zur Zielarchitektur siehe `docs/specs/fibu_architektur_spezifikation.md`.
- **Folgen:** Kein produktiver Finanzservice, keine GoBD-konforme Belegkette im Microservice-Verbund.

### Mandantenfähige Workflows/Policy-as-Code
- **Status:** Grundfunktion vorhanden
- **Nachweis:** `services/workflow/` mit Mandanten-Feld (`tenant`) in Definitionen/Instanzen, Policy- & Saga-Engine, NATS-/Postgres-Anbindung.
- **Restlücke:** Admin-Oberfläche/Konfig-API für Mandanten-Templates und Tests für Mandantenwechsel fehlen noch.

### Lieferketten-Tracking & Eventing
- **Status:** Teilweise (Domain & UI vorhanden)
- **Nachweis:** `packages/inventory-domain/src/services/traceability-service.ts` (EPCIS/Gs1), Frontend (`packages/frontend-web/src/pages/charge/rueckverfolgung.tsx`). Keine produktive Event-/Persistenzintegration.
- **Folgen:** Tracking-Daten nicht abrufbar, keine ETA-/Abweichungsalarme im System.

### Compliance-Archiv & Audit Trail
- **Status:** Weitgehend erfüllt
- **Nachweis:** `packages/audit-domain/**` (Hash-Chain, Events, Integritätsprüfungen), Vielzahl an Tests/Docs. Restaufgabe: End-to-End-Verifikation in CI.

## Nächste Schritte (Priorisierte ToDos)

1. **(Erledigt 15.11.2025) InfraStat Produktiv-Rollout**  
   - Helm-Overrides + Secrets + Alerts dokumentiert, Runbook ergänzt.  
   - Nächste Aktion: Go-Live-Fenster terminieren / Monitoring aktivieren.

2. **(Erledigt 15.11.2025) Zoll/Exportkontrolle**  
   - EU/OFAC Keys via Secrets, Delta/Backoff + Alerts umgesetzt, Runbook ergänzt.  
   - Offene Nacharbeiten: rollenbasierte Freigabe-Policies im Workflow-UI.

3. **(Erledigt 15.11.2025) Inventory-Service produktiv machen**  
   - API + EventBus + Workflow-Forwarding aktiv, Frontend `useLotTrace` nutzt Service.  
   - Rest: Dashboard-Optimierungen & KPI-Veredelung.

4. **Finance-Service produktiv machen**  
   - `services/finance/app/**` analog Workflow-Service: Ledger, Anlagenbuchhaltung, Audit-Hooks.  
   - GoBD-Test-Suite (`tests/compliance/test_gobd.py`) in CI aktivieren.

5. **Lieferkettentracking operationalisieren**  
   - Event-Pipeline (NATS Topics), Persistenz für EPCIS-Events, REST-/GraphQL-API.  
   - Alerts/ETA-Berechnungen in Workflow-Engine integrieren.

6. **Audit-Domain in CI verankern**  
   - End-to-End-Testfall (Workflow → Audit → Archiv) in `.github/workflows/ci.yml` ergänzen.

## Offene Fragen

- Welche Datenquellen stehen kurzfristig für InfraStat zur Verfügung (z. B. Warenwirtschaft-DB, Data Warehouse)?  
- Wie werden Finance/Inventory-Services produktiv geführt (Python vs. Node.js)?  
- Schnittstellen zu Zollbehörden (ELSTER, ATLAS) geplant oder Mock-Endpunkte nötig?

_Aktualisiert von GPT-5 Codex, 13.11.2025_

