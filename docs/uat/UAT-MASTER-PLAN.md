# UAT-Masterplan — VALEO NeuroERP 3.0
**Version:** 1.0
**Stand:** 2026-05-18
**Klassifizierung:** Intern – Qualitätssicherung
**Verantwortlich:** Testmanager (Claude / QA-Beauftragter)
**Geltungsbereich:** Release 3.0 — Waves 2026-03 bis 2026-05-17

---

## 1. Zweck und Geltungsbereich

Dieser Masterplan regelt das User Acceptance Testing (UAT) für den VALEO NeuroERP 3.0-Release. Er definiert Methodik, Scope, Verantwortlichkeiten, Qualitätsziele und den Zeitplan gemäß folgender Standards:

| Standard | Anwendungsbereich |
|---|---|
| **ISO/IEC 25010:2023** | Qualitätsmerkmale (Funktionalität, Zuverlässigkeit, Performance, Sicherheit) |
| **ISO 31000:2018** | Risikobasiertes Testpriorisierungsmodell |
| **IEEE 829-2008** | Testdokumentationsstruktur |
| **ISTQB Foundation Level** | Testdesigntechniken, Teststufen, Defektmanagement |
| **BDD / Gherkin (Cucumber)** | Spezifikation durch Szenarien; lebende Dokumentation |
| **GoBD (2019)** | Revisionssicherheit und Nachvollziehbarkeit der Testprotokolle |

---

## 2. Methodologie

### 2.1 Risk-Based Testing (ISO 31000)

Jedes Feature erhält einen Risikowert aus der Kombination:

```
Risiko-Score = Wahrscheinlichkeit × Schadensausmaß
               (1–3)              (1–3)
```

**Risikoklassen und Testziele:**

| Risikoklasse | Score | Bezeichnung | Coverageziel | Automationsgrad |
|---|---|---|---|---|
| **P0 – Kritisch** | 7–9 | Kerngeschäftsprozess, gesetzlich | 100 % | ≥ 90 % automatisiert |
| **P1 – Hoch** | 4–6 | Wichtiger Geschäftsprozess | 90 % | ≥ 70 % automatisiert |
| **P2 – Mittel** | 2–3 | Unterstützungsprozess | 70 % | ≥ 50 % automatisiert |
| **P3 – Niedrig** | 1 | Nice-to-have | 50 % | manuell akzeptabel |

### 2.2 BDD / Gherkin

Alle Testfälle werden als Gherkin-Szenarien formuliert und in `.feature`-Dateien unter `docs/uat/features/` gepflegt. Die Szenarien dienen gleichzeitig als:
- Fachliche Anforderungsdokumentation (für Product Owner)
- Automatisierungsgrundlage (Playwright E2E, pytest BDD via `pytest-bdd`)
- Abnahmeprotokoll (Testsignaturen im CI-Artefakt)

### 2.3 Testdesigntechniken (ISTQB)

| Technik | Einsatz |
|---|---|
| Äquivalenzklassenanalyse | Eingabevalidierung (Gewichte, Preise, Mengen) |
| Grenzwertanalyse | Fristen (90-Tage-Regelung §17a UStDV), Kapazitätsgrenzen |
| Entscheidungstabellentest | Trocknungsregeln, Prämienberechnung, Risikoscoring |
| Zustandsbasiertes Testen | Workflow-Statusübergänge (Process Kernel) |
| Use-Case-Test | End-to-End-Geschäftsszenarien (Ernte-Annahme → Abrechnung) |
| Paarweises Testen | Konfigurationskombinationen (Mandant × Modul × Rolle) |

---

## 3. Scope-Matrix

### 3.1 Feature-Bereiche und Risikobewertung

| # | Feature-Bereich | Wave | Risiko | P-Level | Coverage | Automation |
|---|---|---|---|---|---|---|
| F01 | Ernte-Annahme (Harvest Acceptance) | 2026-03 | W:3 × S:3 = 9 | **P0** | 100 % | Playwright + pytest |
| F02 | Agrar-Kontrakte (Fix/Basis/Prämie) | 2026-03 | W:3 × S:3 = 9 | **P0** | 100 % | Playwright + pytest |
| F03 | Agrar-Abrechnung (Settlement) | 2026-03 | W:2 × S:3 = 6 | **P1** | 90 % | pytest |
| F04 | POS Tagesabschluss / DSFinV-K | 2026-04 | W:3 × S:3 = 9 | **P0** | 100 % | Playwright + pytest |
| F05 | POS Retoure | 2026-04 | W:2 × S:2 = 4 | **P1** | 90 % | Playwright |
| F06 | POS Offline-Queue | 2026-04 | W:2 × S:2 = 4 | **P1** | 90 % | Playwright |
| F07 | Gelangensbetätigung §17a UStDV | 2026-05-17 | W:3 × S:3 = 9 | **P0** | 100 % | pytest |
| F08 | Sanktionsprüfung (LKSG/EU-Embargo) | 2026-05-17 | W:3 × S:3 = 9 | **P0** | 100 % | pytest |
| F09 | LKSG Lieferanten-Risikobewertung | 2026-05-17 | W:2 × S:3 = 6 | **P1** | 90 % | pytest |
| F10 | Intrastat-Meldung | 2026-05-17 | W:2 × S:2 = 4 | **P1** | 90 % | pytest |
| F11 | GS1/SSCC Barcode-System | 2026-05-17 | W:2 × S:2 = 4 | **P1** | 90 % | pytest |
| F12 | eBilanz / XBRL-Export | 2026-05-17 | W:3 × S:3 = 9 | **P0** | 100 % | pytest |
| F13 | Genossenschaft (Mitgliederverwaltung) | 2026-05-17 | W:2 × S:2 = 4 | **P1** | 90 % | Playwright + pytest |
| F14 | Webshop-Integration (L3-Connect) | 2026-05-17 | W:2 × S:2 = 4 | **P1** | 90 % | pytest |
| F15 | Process Kernel (Workflow-Engine) | 2026-03 – 05 | W:3 × S:3 = 9 | **P0** | 100 % | pytest (903 Tests) |

### 3.2 Explizit ausgeschlossener Scope

- Infrastruktur-Tests (Load Balancer, Kubernetes-Autoscaling) → Betrieb
- Keycloak-Konfiguration → Security-Team
- Datenbankschema-Migrationen → Entwickler-Tests (Alembic)
- Drittanbieter-APIs (BrightSky, Open-Meteo) → Contract Tests separat

---

## 4. Entry / Exit Criteria

### 4.1 Entry Criteria (UAT-Startbedingungen)

Alle folgenden Bedingungen müssen erfüllt sein, bevor UAT gestartet wird:

- [ ] **EC-01** CI/CD-Pipeline grün (0 failing Tests in `main`)
- [ ] **EC-02** `alembic upgrade head` erfolgreich auf UAT-Datenbank durchgeführt
- [ ] **EC-03** Docker-Stack (`docker compose up -d`) startet ohne Fehler
- [ ] **EC-04** Alle P0-Smoke-Tests bestehen (siehe `docs/uat/SMOKE-RUNBOOK.md`)
- [ ] **EC-05** Testdaten-Seed erfolgreich (`pytest tests/fixtures/ -m seed`)
- [ ] **EC-06** UAT-Umgebung von Produktivdaten isoliert (eigener Tenant `uat-tenant-001`)
- [ ] **EC-07** Alle neuen Endpoints in `app/api/v1/api.py` registriert und erreichbar
- [ ] **EC-08** Zugangsdaten für alle Testrollen bereitgestellt (admin, manager, agrar_user, pos_operator, readonly)

### 4.2 Exit Criteria — Definition of Done für UAT

#### Pflichtziele (Blocker):
- [ ] **EX-01** Alle P0-Szenarien bestehen zu 100 % (kein offener P0-Defekt)
- [ ] **EX-02** Alle P1-Szenarien bestehen zu ≥ 90 %
- [ ] **EX-03** Kritische Defekte (Severity 1): 0 offen
- [ ] **EX-04** Hohe Defekte (Severity 2): 0 offen, alle mit Workaround dokumentiert
- [ ] **EX-05** Tenant-Isolation-Tests: 100 % Bestehen (kein Datenleck über Mandantengrenzen)
- [ ] **EX-06** Auth-Check-Tests: 100 % (jeder Endpoint prüft Bearer-Token und Tenant-ID)
- [ ] **EX-07** DSFinV-K-Export valide (Prüfsumme durch Kassensicherungsverordnung konform)
- [ ] **EX-08** Gelangensbetätigung-Workflow vollständig (§17a UStDV, 90-Tage-Frist korrekt)

#### Qualitätsziele (bedingt freigabefähig mit Dokumentation):
- [ ] **EX-09** Performance: P95 ≤ 200 ms auf Listendaten (bei ≤ 10.000 Datensätzen)
- [ ] **EX-10** Accessibility: WCAG 2.2 AA – 0 kritische Verstöße (axe-core-Scan)
- [ ] **EX-11** Defect Density ≤ 2 Defekte / Feature-Bereich (P1+P2)
- [ ] **EX-12** Regressionstest-Suite grün (keine neuen Failures gegenüber Baseline)

#### Dokumentation:
- [ ] **EX-13** Abnahmeprotokoll von Product Owner unterzeichnet
- [ ] **EX-14** Alle Test-Artefakte GoBD-konform archiviert (Datum, Tester, Ergebnis unveränderbar)
- [ ] **EX-15** Traceability-Matrix vollständig (100 % Requirements gecovert)

---

## 5. Qualitätsmetriken

### 5.1 Defektmetriken

| Metrik | Zielwert | Messung |
|---|---|---|
| Defect Density (P0-Features) | ≤ 1 Defekt / 100 Testfälle | JIRA / GitHub Issues |
| Defect Density (P1-Features) | ≤ 2 Defekte / 100 Testfälle | JIRA / GitHub Issues |
| Defect Detection Rate | ≥ 85 % (in UAT, nicht Produktion) | (UAT-Defekte) / (UAT + Prod-Defekte) |
| Mean Time to Fix (P0) | ≤ 24 Stunden | Issue-Timestamps |
| Mean Time to Fix (P1) | ≤ 72 Stunden | Issue-Timestamps |
| Retest Pass Rate | ≥ 95 % | Retest-Protokoll |

### 5.2 Coveragemetriken

| Ebene | Ziel | Messung |
|---|---|---|
| Requirement Coverage | 100 % (alle Anforderungen getestet) | Traceability-Matrix |
| Scenario Coverage P0 | 100 % Szenarien bestehen | pytest-bdd / Playwright |
| API Endpoint Coverage | ≥ 95 % aller Endpoints getestet | pytest parametrize |
| Branch Coverage (Backend) | ≥ 80 % | pytest-cov Report |
| UI Flow Coverage | ≥ 70 % kritischer User Journeys | Playwright |

### 5.3 ISO/IEC 25010 Qualitätsmerkmale

| Merkmal | Subcharacteristic | Messmethode | Zielwert |
|---|---|---|---|
| Functional Correctness | Accuracy | Gherkin-Szenarien | 100 % P0 |
| Performance Efficiency | Response Time | Locust / k6 Load Test | P95 ≤ 200 ms |
| Security | Confidentiality | Auth-Header-Test | 100 % der Endpoints |
| Reliability | Fault Tolerance | Chaos-Test (Redis-Ausfall) | Graceful Degradation |
| Usability | Accessibility | axe-core | WCAG 2.2 AA |
| Maintainability | Testability | Codecov | Backend ≥ 80 % |
| Portability | Installability | Docker Compose | Cold Start < 60 s |

---

## 6. Rollen und Verantwortlichkeiten

| Rolle | Person / System | Verantwortlichkeit |
|---|---|---|
| **Product Owner** | Fachbereich (Agrar, Finance, POS) | Fachliche Abnahme, Szenariensignatur |
| **Testmanager** | QA-Beauftragter / Claude | Planung, Koordination, Berichterstellung |
| **Automation Engineer** | Claude / CI-Pipeline | Playwright- und pytest-Skripte, CI-Ausführung |
| **Testdesigner** | Claude | Gherkin-Szenarien, Testdaten-Design |
| **Dev-Vertreter** | Entwicklung | Defektbehebung, technische Unterstützung |
| **Security Reviewer** | Security-Team | Penetrationstest, Auth-Checks |
| **Datenschutzbeauftragter** | DSB | DSGVO-Compliance-Review |
| **Steuerberater / GoBD-Prüfer** | Extern (bei Bedarf) | DSFinV-K, eBilanz, §17a UStDV Abnahme |

---

## 7. Testphasen und Zeitplan

### 7.1 Phasenübersicht

```
Phase 1: SMOKE          [Tag 1]     ← Basisverfügbarkeit aller Endpoints
Phase 2: FUNCTIONAL     [Tag 2–5]   ← Feature-by-Feature Gherkin-Szenarien
Phase 3: INTEGRATION    [Tag 6–8]   ← End-to-End Prozessketten
Phase 4: REGRESSION     [Tag 9]     ← Baseline-Vergleich, keine neuen Failures
Phase 5: PERFORMANCE    [Tag 10]    ← Lasttest, Response-Time-Messung
Phase 6: SECURITY       [Tag 11]    ← Auth-Checks, Tenant-Isolation, DSGVO
Phase 7: SIGN-OFF       [Tag 12]    ← Abnahmeprotokoll, Freigabeentscheidung
```

### 7.2 Detailplan

#### Phase 1 — Smoke Test (Tag 1)
**Ziel:** Alle kritischen Endpunkte erreichbar, Stack gesund
**Testfälle:** ~50 Health-Checks, Auth-Flow, DB-Konnektivität
**Tools:** `pytest -m smoke`, curl-Skript
**Exit:** 100 % der Smoke-Tests grün

#### Phase 2 — Funktionaler Test (Tag 2–5)
**Ziel:** Alle Gherkin-Szenarien für F01–F15 ausgeführt
**Testfälle:** ~280 Szenarien aus `.feature`-Dateien
**Tools:** `pytest-bdd`, Playwright, manuelle Exploration
**Priorität:** P0 zuerst, dann P1, dann P2

| Tag | Feature-Bereiche | Szenarien |
|---|---|---|
| Tag 2 | F01 Ernte-Annahme, F02 Agrar-Kontrakte | ~65 |
| Tag 3 | F03 Abrechnung, F15 Process Kernel | ~55 |
| Tag 4 | F04 POS DSFinV-K, F05 Retoure, F06 Offline | ~50 |
| Tag 5 | F07 Gelangensb., F08 Sanktion, F09 LKSG, F10 Intrastat, F11 GS1, F12 eBilanz, F13 Geno, F14 Webshop | ~110 |

#### Phase 3 — Integrationstest (Tag 6–8)

**End-to-End Prozessketten:**

| Kette | Beschreibung | Priorität |
|---|---|---|
| E2E-01 | LKW-Einfahrt → Qualitätsprüfung → Ernte-Annahme → Trocknung → Settlement → PDF → Buchung | P0 |
| E2E-02 | Kontrakt anlegen → Lieferung zuordnen → Prämie berechnen → Abrechnung → Ausschüttung | P0 |
| E2E-03 | POS-Verkauf → Tagesabschluss → DSFinV-K-Export → GoBD-Archivierung | P0 |
| E2E-04 | Lieferant anlegen → Sanktionsprüfung → LKSG-Bewertung → Freigabe/Sperre | P0 |
| E2E-05 | Auslandslieferung → Gelangensbetätigung → 90-Tage-Monitor → Mahnwesen | P0 |
| E2E-06 | Jahresabschluss → eBilanz → XBRL-Export → ELSTER-Upload | P1 |
| E2E-07 | Webshop-Bestellung → L3-Connect-Sync → ERP-Auftrag → Lieferschein | P1 |

#### Phase 4 — Regressionstest (Tag 9)
**Ziel:** Keine Regressions gegenüber letztem stabilem Release
**Testfälle:** Komplette Regressionssuites (automatisiert)
**Tools:** `pytest --tb=short -m regression`
**Exit:** 0 neue Failures; alle bekannten Skips dokumentiert

#### Phase 5 — Performancetest (Tag 10)
**Ziel:** Response-Time-Targets unter Last
**Szenarien:**

| Szenario | Last | Ziel |
|---|---|---|
| Listenanfragen (z. B. GET /agrar/contracts) | 100 parallele User | P95 ≤ 200 ms |
| Ernte-Annahme-Buchung (POST) | 50 parallele User | P95 ≤ 500 ms |
| DSFinV-K-Export (GET) | 10 parallele User | P95 ≤ 2.000 ms |
| eBilanz-XBRL-Generation | 5 parallele User | P95 ≤ 5.000 ms |

**Tools:** `locust` oder `k6`

#### Phase 6 — Security-Test (Tag 11)
**Prüfpunkte:**
- Alle 264 Endpoints: Bearer-Token-Pflicht (401 ohne Token)
- Alle Endpoints: Tenant-ID-Isolation (403 bei falschem Tenant)
- SQL-Injection-Scans (sqlmap auf Filterparameter)
- XSS-Scan (OWASP ZAP auf Frontend)
- DSGVO: PII in Logs (kein Name/Adresse in Stacktraces)
- Rate-Limiting auf Auth-Endpoints

#### Phase 7 — Sign-off (Tag 12)
- Defektstatusreview mit Product Owner
- Abnahmeprotokoll ausfüllen (siehe Abschnitt 10)
- Freigabeentscheidung (Go/No-Go)

---

## 8. Testumgebung

### 8.1 Umgebungskonfiguration

```yaml
UAT-Umgebung:
  tenant_id: "uat-tenant-001"
  database: "valeo_neuro_erp_uat"
  backend_url: "http://localhost:8000"
  frontend_url: "http://localhost:3001"
  redis_url: "redis://localhost:6379/1"  # DB 1, nicht Produktion
  nats_url: "nats://localhost:4222"
  api_dev_token: "<UAT-TOKEN>"

Testrollen (Benutzer):
  - admin_user: Alle Rechte
  - agrar_manager: Agrar-Modul komplett
  - agrar_user: Ernte-Annahme, Schläge (readonly+write)
  - pos_operator: POS-Terminal, Tagesabschluss
  - finance_user: FIBU, eBilanz, Intrastat
  - compliance_officer: Gelangensb., Sanktionen, LKSG
  - readonly_user: Nur GET-Rechte systemweit
```

### 8.2 Testdaten

| Datensatz | Quelle | Beschreibung |
|---|---|---|
| Agrar-Stammdaten | `tests/fixtures/agrar_seed.py` | 10 Schläge, 5 Sorten, 3 Trocknungsregeln |
| Kontrakte | `tests/fixtures/kontrakt_seed.py` | Fix, Basis, Prämien-Kontrakt je Mandant |
| Kunden/Partner | `tests/fixtures/partner_seed.py` | 20 Geschäftspartner inkl. Risikoklassen |
| POS-Artikel | `tests/fixtures/pos_seed.py` | 50 Artikel, 3 Kassenplätze |
| Finanzdaten | `tests/fixtures/finance_seed.py` | Kontierungsrahmen SKR04, Buchungsperioden |
| Compliance | `tests/fixtures/compliance_seed.py` | Sanktionslisten-Einträge (Testdaten) |

---

## 9. Defektmanagement

### 9.1 Severity-Klassifizierung

| Severity | Beschreibung | Beispiel | SLA Behebung |
|---|---|---|---|
| **S1 – Kritisch** | System nicht nutzbar, Datenverlust, Gesetzesverstoß | DSFinV-K falsche Beträge, Tenant-Datenleck | 24 Stunden |
| **S2 – Hoch** | Kernfunktion blockiert, kein Workaround | Ernte-Annahme speichert nicht | 48 Stunden |
| **S3 – Mittel** | Funktion beeinträchtigt, Workaround vorhanden | Filter funktioniert nicht korrekt | 5 Werktage |
| **S4 – Niedrig** | Kosmetisch, Usability-Verbesserung | Falscher Button-Text | Nächster Sprint |

### 9.2 Defektlebenszyklus

```
NEU → IN ANALYSE → BEHOBEN → RETEST → GESCHLOSSEN
                ↓
           ABGELEHNT (keine Abweichung)
           ZURÜCKGESTELLT (bekanntes Problem)
```

### 9.3 Defektfelder (IEEE 829)

Jeder Defektbericht enthält: ID, Titel, Severity, Priority, Feature-Bereich, Testfall-Referenz, Schritte zur Reproduktion, Erwartetes Ergebnis, Tatsächliches Ergebnis, Screenshots/Logs, Umgebung, Datum, Tester, Behoben-Datum, Fix-Beschreibung.

---

## 10. Sign-off Checkliste — Abnahmeprotokoll

```
VALEO NeuroERP 3.0 — UAT-Abnahmeprotokoll
==========================================
Release:        3.0.0
UAT-Periode:    _____________ bis _____________
Testumgebung:   uat-tenant-001 auf _______________

TESTPHASE-ERGEBNISSE
━━━━━━━━━━━━━━━━━━━━
[ ] Phase 1 Smoke:       Gesamt: ___  Bestanden: ___  Fehlgeschlagen: ___
[ ] Phase 2 Funktional:  Gesamt: ___  Bestanden: ___  Fehlgeschlagen: ___
[ ] Phase 3 Integration: Gesamt: ___  Bestanden: ___  Fehlgeschlagen: ___
[ ] Phase 4 Regression:  Gesamt: ___  Bestanden: ___  Fehlgeschlagen: ___
[ ] Phase 5 Performance: P95-Listendaten: ___ms  (Ziel ≤200ms)
[ ] Phase 6 Security:    Kritische Findings: ___  (Ziel: 0)

EXIT-CRITERIA
━━━━━━━━━━━━━
[ ] EX-01 P0-Szenarien: 100 % bestanden
[ ] EX-02 P1-Szenarien: ≥ 90 % bestanden
[ ] EX-03 S1-Defekte offen: 0
[ ] EX-04 S2-Defekte offen: 0
[ ] EX-05 Tenant-Isolation: 100 %
[ ] EX-06 Auth-Checks: 100 %
[ ] EX-07 DSFinV-K valide
[ ] EX-08 §17a UStDV korrekt

OFFENE PUNKTE (akzeptierte Restrisiken)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Aktualisierung 2026-05-18: Die repo-seitigen Auflagen M-001, M-002/M-003
und M-008 sind umgesetzt. Verbleibende Risiken sind externe Betriebsfreigaben
wie PCN-Portal/ECHA-Anbindung, produktive Browser-UATs und fachliche
Freigaben mit Echtdaten.

Nr. | Defekt-ID | Beschreibung | Risiko | Verantwortlich | Zieldatum
----|-----------|--------------|--------|---------------|----------
1   |           |              |        |               |
2   |           |              |        |               |

FREIGABEENTSCHEIDUNG
━━━━━━━━━━━━━━━━━━━
[ ] FREIGEGEBEN für Produktivbetrieb
[ ] FREIGEGEBEN mit Auflagen (siehe offene Punkte)
[ ] NICHT FREIGEGEBEN — Blocking Issues offen

UNTERSCHRIFTEN
━━━━━━━━━━━━━━
Product Owner (Agrar):    ________________  Datum: ____________
Product Owner (Finance):  ________________  Datum: ____________
Product Owner (POS):      ________________  Datum: ____________
Testmanager:              ________________  Datum: ____________
Datenschutzbeauftragter:  ________________  Datum: ____________
Geschäftsführung:         ________________  Datum: ____________
```

---

## 11. Testautomatisierung — Architektur

### 11.1 Backend-Tests (pytest + pytest-bdd)

```
tests/
├── uat/
│   ├── features/          # .feature-Dateien (Gherkin)
│   │   ├── agrar-kernprozesse.feature
│   │   ├── compliance-finanzen.feature
│   │   └── pos-kasse.feature
│   ├── step_defs/         # Python Step-Implementierungen
│   │   ├── agrar_steps.py
│   │   ├── compliance_steps.py
│   │   └── pos_steps.py
│   └── conftest.py        # Fixtures, Tenant-Setup
```

### 11.2 Frontend-Tests (Playwright)

```
tests/e2e/
├── agrar/
│   ├── ernte-annahme.spec.ts
│   ├── kontrakte.spec.ts
│   └── abrechnung.spec.ts
├── pos/
│   ├── tagesabschluss.spec.ts
│   ├── retoure.spec.ts
│   └── offline-queue.spec.ts
└── compliance/
    ├── gelangensbetaetigung.spec.ts
    └── sanktionspruefung.spec.ts
```

### 11.3 CI-Integration

```yaml
# .github/workflows/uat.yml (Auszug)
uat:
  needs: [unit-tests, integration-tests]
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Start UAT Stack
      run: docker compose -f docker-compose.uat.yml up -d --wait
    - name: Run UAT Smoke
      run: pytest -m smoke --tb=short
    - name: Run UAT Functional (BDD)
      run: pytest tests/uat/ --gherkin-terminal-reporter -v
    - name: Run Playwright E2E
      run: npx playwright test --reporter=html
    - name: Upload Test Artifacts
      uses: actions/upload-artifact@v4
      with:
        name: uat-report-${{ github.sha }}
        path: |
          pytest-report.xml
          playwright-report/
          htmlcov/
```

---

## 12. Referenzdokumente

| Dokument | Pfad |
|---|---|
| Smoke-Runbook | `docs/uat/SMOKE-RUNBOOK.md` |
| Abnahmekriterien | `docs/uat/ABNAHME-KRITERIEN.md` |
| Traceability-Matrix | `docs/uat/TRACEABILITY-MATRIX.md` |
| Agrar-Checkliste | `docs/uat/checklisten/AGRAR.md` |
| GoBD-Konformität | `docs/GOBD-COMPLIANCE.md` |
| Masken-Standard | `docs/MASKEN.md` |
| API-Dokumentation | `http://localhost:8000/docs` |
| Prozesskernel-Status | `docs/architecture/process-kernel/STATUS.md` |

---

*Erstellt gemäß IEEE 829-2008 / ISTQB / ISO/IEC 25010 / ISO 31000*
*Dieses Dokument ist versioniert und GoBD-konform zu archivieren.*
