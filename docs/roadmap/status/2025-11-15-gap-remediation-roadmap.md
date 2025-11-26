# Must-Have Gap Remediation Roadmap – 15.11.2025

## Zielbild

Die in `docs/roadmap/status/2025-11-13-must-have-gap-audit.md` identifizierten Must-Haves werden sequenziell geschlossen, damit a.eins-Parität und Compliance erreicht werden. Die Reihenfolge folgt dem Prinzip „Compliance & Finanzkern zuerst“, anschließend Supply-Chain-Transparenz und finale Audit-Automatisierung.

| Reihenfolge | Gap / Capability                           | Aktueller Stand                 | Nächster Meilenstein                               |
|-------------|-------------------------------------------|---------------------------------|----------------------------------------------------|
| 1           | InfraStat Produktiv-Rollout               | Deploy-ready (Helm + Runbook)   | Go-Live Monitoring & IDEV Secrets                  |
| 2           | Zoll- & Exportkontrolle                   | Deploy-ready (Secrets + Alerts) | Workflow-Rollen im UI finalisieren                 |
| 3           | Inventory-Service (Mehrlager/Chargen)     | Frontend + Workflow live        | KPI-Dashboards & Alerts erweitern                  |
| 4           | Finance-Service (GoBD)                    | Domain + Gateway vorhanden      | Python-Service, Ledger, GoBD-Tests                 |
| 5           | Lieferkettentracking & Eventing           | Domain + UI vorhanden           | Persistenz/Event-Pipeline/Alerts                   |
| 6           | Audit-Domain End-to-End CI                | Hash-Chain & Tests vorhanden    | CI-Workflow Workflow→Audit→Archiv                  |

## Vorgehen (Rolling Wave)

1. **InfraStat Produktiv-Rollout (läuft)**  
   - Helm/Secrets/Alerts produktionsreif.  
   - Runbook enthält IDEV-Verifikation (Port-Forward + Smoke-Test).  
   - Ticket-Links: INFR-001, INFR-002, INFR-003.

2. **Zoll/Exportkontrolle**  
   - Nach Fertigstellung InfraStat sofortiger Fokuswechsel.  
   - Abhängigkeiten: Keycloak-Rollen, Secrets für OFAC/EU-API.  
   - Ticket-Links: ZOLL-005, ZOLL-008.

3. **Inventory-Service Produktiv machen**  
   - Ziel: `/api/v1/inventory` in Frontend eingebunden, Events Richtung Workflow.  
   - Ticket-Links: INV-010 ff.

4. **Finance-Service GoBD**  
   - Umsetzung Microservice (siehe `docs/specs/fibu_architektur_spezifikation.md`).  
   - Gateway + Frontend nutzen `/api/v1`.  
   - Ticket-Links: FIN-020 ff.

5. **Lieferkettentracking operationalisieren**  
   - EPCIS-Persistenz, ETA/Alerting, GraphQL/REST.  
   - Ticket-Links: LCT-011 ff.

6. **Audit-Domain CI**  
   - End-to-End-Testfall im CI (`.github/workflows/ci.yml`).  
   - Ticket-Links: AUD-007.

## Reporting

- Fortschritt je Stream wird in `docs/roadmap/status/2025-11-13-must-have-gap-audit.md` ergänzt.  
- Deployment-Artefakte (Helm Overrides, Runbooks) liegen unter `docs/deployment/**`.  
- Jede abgeschlossene Stufe dokumentiert Smoke-/Integration-Tests (siehe Runbooks). 

