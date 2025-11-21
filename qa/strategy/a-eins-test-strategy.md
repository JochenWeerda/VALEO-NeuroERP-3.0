# Teststrategie für a.eins-Erweiterung

## Ziele

- Sicherstellen, dass neue Funktionen (Compliance, Fertigung, Service, RAG) stabil, konform und performant ausgeliefert werden.
- Risiko-basierte Testabdeckung mit Fokus auf regulatorische Anforderungen und KI-gestützte Entscheidungen.
- Kontinuierliche Qualitätssicherung über alle Entwicklungsphasen (Shift-Left + Shift-Right).

## Test-Ebenen

1. **Unit & Modul-Tests**
   - Fokus auf Workflow-Engine, Compliance-Regeln, Berechnungslogik.
   - Pflicht: Branch-Coverage ≥ 80 %, Mutation Testing für kritische Services.
2. **API- & Contract-Tests**
   - Consumer-Driven Contracts zwischen Kern-Services, RAG-Gateway, Drittsystemen (EDI, Zoll).
   - Negative Tests für Validierungs- und Auth-Fälle.
3. **End-to-End & Szenario-Tests**
   - Lead-to-Cash, Procure-to-Pay, Service-to-Customer inkl. KI-Entscheidungen.
   - Data-Seeding über synthetische Szenarien (z. B. Zolltarifänderung, SLA-Verletzung).
4. **Compliance-Testfälle**
   - InfraStat-Meldeläufe (monatlich, Korrekturmeldungen).
   - Zoll/Exportkontrolle: Embargoprüfung, Präferenzkalkulation.
   - Audit Trails: Unveränderbarkeit, Berechtigungsnachweise.
5. **Nicht-funktionale Tests**
   - Performance (Lasttests für Workflow-/Event-Engine, RAG-Abfragen).
   - Sicherheit (Penetration, RBAC/ABAC, Data Leakage).
   - Resilienz (Chaos Tests, Event-Bus-Ausfälle, Fallbacks).
6. **KI-spezifische Validierung**
   - Offline-Evaluierung: Precision/Recall, Bias-Prüfungen.
   - Online-Monitoring: Drift Detection, Feedback-Loops.

## Testdaten-Strategie

- **Golden Records** für Finanz- und Compliance-Daten mit synthetischer Anreicherung.
- **Anonymisierte Produktionsdaten** unter DSGVO-konformen Verfahren.
- **Scenario Templates** für Lieferketten, Service-Cases, Exportfälle.
- **Data Contracts** definieren Pflichtfelder, Sensitivität, Löschfristen.

## Automatisierung & Tooling

- CI/CD-Integration (GitHub Actions): Stufen Unit → Integration → E2E → Compliance.
- Playwright/Cypress für UI, pytest/jest für API & Logik.
- Infrastructure-as-Code Tests (z. B. Terraform, Policy-as-Code).
- Observability Hooks (OpenTelemetry) für Test-Metriken.
- RAG-Test-Harness: Prompt-Regression, Antwortvalidierung, Toxicity/Leakage Checks.

## Qualitäts-Gates

- **Definition of Ready**: Akzeptanzkriterien inkl. Compliance-Anforderungen, Testfälle spezifiziert.
- **Definition of Done**: Tests bestanden, Dokumentation aktualisiert, RAG-Content gepflegt.
- **Release Gate**: Go/No-Go-Checkliste (Compliance, Performance, Monitoring).

## Rollen & Verantwortlichkeiten

- **QA Lead**: Gesamtkoordination, Teststrategie-Review, Reporting.
- **Domain QA**: Spezialisten für Finance/Compliance, Supply Chain, Service.
- **Automation Engineer**: Framework-Pflege, Pipelines, Testdaten-Skripte.
- **AI Validation Owner**: Modelltests, Drift-Monitoring, Ethik-Checks.

## Metriken & Reporting

- Test Coverage je Domäne, Fehlerrate pro Release.
- MTTR/MTTD für Produktionsvorfälle.
- Compliance Pass Rate (Meldungen, Audits).
- KI-Qualitätsmetriken (Precision@K, Feedback Score).
- Trendberichte in zentralem QA-Dashboard (Grafana/Superset).

## Continuous Improvement

- Regelmäßige QA/Compliance-Syncs.
- Root-Cause-Analysen bei Defects oder Audit Findings.
- Backlog für QA-Tech-Debt und Testwerkzeug-Optimierungen.
- Automatisiertes Wissens-Update in der RAG-Basis nach Abschluss von Tests/Audits.

