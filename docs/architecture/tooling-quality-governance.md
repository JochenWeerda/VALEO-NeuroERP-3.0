# Quality & Governance Tooling — Einführungsplan

**Status:** Accepted
**Datum:** 2026-04-04

## 1. Entscheidung

VALEO NeuroERP führt drei externe Governance-Tools ein:

| Tool | Zweck | Phase |
|------|-------|-------|
| **SonarCloud** | Statische Analyse, Quality Gates, technische Schulden | Sofort |
| **CodeRabbit** | AI-gestütztes PR-Review, inkrementell bei Commits | Sofort |
| **Sourcegraph** | Codebase-Suche, Cross-Repo-Kontext, Cody AI-Assistenz | Phase 2 |

**Nicht eingeführt:**
- Qodo (Alternative zu CodeRabbit, nicht parallel)
- Weitere Scanner (Scan-Abdeckung ist bereits dicht; Engpass = Gates + Priorisierung)

## 2. Begründung

Das Repo ist mehrsprachig (Python/TypeScript), breit aufgestellt (12+ Domains, 18 Workflows)
und hat an mehreren Stellen advisory-only Checks (`|| true`, `continue-on-error: true`):

- `ci.yml`: Bandit, Safety, ESLint, Playwright — alle mit `|| true`
- `security-scan.yml`: ZAP, Trivy, Grype, Bandit, Safety — alle `continue-on-error: true`
- `quality-gate.yml`: pip-audit, pnpm audit — `continue-on-error: true`

**Der Engpass ist nicht fehlende Scan-Abdeckung, sondern fehlende harte Gates.**
SonarQube schließt diese Lücke mit Quality Gates auf neuem Code.
CodeRabbit bringt kontextbezogenes Review-Feedback direkt in den PR-Flow.

## 3. SonarCloud

### 3.1 Setup-Schritte

1. **SonarCloud aktivieren**: https://sonarcloud.io → GitHub-App installieren → Repo importieren
2. **Secret anlegen**: Repository Settings → Secrets → `SONAR_TOKEN` aus SonarCloud-Account
3. **Dateien committed** (bereits vorhanden):
   - `sonar-project.properties` — Projektdefinition, Quellen, Ausschlüsse
   - `.github/workflows/sonarcloud.yml` — CI-Workflow mit Backend-Coverage + Frontend-Coverage

### 3.2 Quality Gate (empfohlen: "Sonar way")

Auf **neuem Code** (seit letztem Commit auf Main):
- 0 neue Bugs
- 0 neue Vulnerabilities
- 0 neue Security Hotspots (reviewed)
- Coverage ≥ 60%
- Duplicated Lines ≤ 3%

### 3.3 Was SonarCloud abdeckt, was die bestehenden Scanner nicht tun

| Fähigkeit | Bestehend | SonarCloud |
|-----------|-----------|------------|
| Bug-Erkennung (Null-Pointer, Dead Code, Logic Errors) | Nein | Ja |
| Code Smell / Maintainability Rating | Nein | Ja |
| Duplicated Code Detection | Nein | Ja (cross-file) |
| Quality Gate als PR-Status-Check | Nein | Ja |
| Trend-Analyse über Zeit | Nein | Ja (Dashboard) |
| Multi-Language in einem Report | Nein | Ja (Python + TS + SQL) |
| Security Hotspot Review Workflow | Nein | Ja |

### 3.4 Konfiguration

```
sonar-project.properties          # Quellen, Tests, Ausschlüsse, Coverage-Pfade
.github/workflows/sonarcloud.yml  # CI: pytest --cov → coverage.xml, vitest --coverage → lcov
```

Besonderheiten für dieses Repo:
- **Alembic-Migrationen** ausgeschlossen (generierter Code)
- **UI-Primitives** (`components/ui/*.tsx`) von Duplikaterkennung ausgeschlossen (Radix-Wrapper)
- **Models/Schemas** von CPD ausgeschlossen (strukturelle Ähnlichkeit ist Absicht)
- **Seeds/Scripts/Tools** von Coverage ausgeschlossen

## 4. CodeRabbit

### 4.1 Setup-Schritte

1. **CodeRabbit aktivieren**: https://coderabbit.ai → GitHub-App installieren → Repo autorisieren
2. **Konfiguration committed** (bereits vorhanden): `.coderabbit.yaml`
3. CodeRabbit reviewed automatisch ab dem nächsten PR

### 4.2 Konfiguration

```yaml
# .coderabbit.yaml — Kernpunkte:
language: de-DE                    # Deutsches Feedback
reviews.auto_review.enabled: true  # Automatisch bei jedem PR
reviews.auto_review.drafts: false  # Keine Draft-Reviews
reviews.profile: assertive        # Klar, nicht passiv
reviews.instructions: |            # VALEO-spezifische Regeln:
  - Tenant-Isolation prüfen
  - Mass Assignment prüfen
  - Information Disclosure prüfen
  - SSRF prüfen
  - XSS prüfen
  - SQL Injection prüfen
  - Fachliche Konsistenz (Dokumentketten)
  - API-URL-Konsistenz
```

### 4.3 Was CodeRabbit abdeckt, was SonarCloud nicht tut

| Fähigkeit | SonarCloud | CodeRabbit |
|-----------|------------|------------|
| Fachliche Review-Kommentare (ERP-Domäne) | Nein | Ja (via instructions) |
| Inkrementelles Review bei Folge-Commits | Nein | Ja |
| PR-Summary + High-Level-Zusammenfassung | Nein | Ja |
| GitHub Checks → Review-Kommentare | Nein | Ja |
| Cross-File-Kontext im Review | Begrenzt | Ja (AI) |
| Tenant-Isolation als Review-Regel | Nein | Ja (custom instruction) |

## 5. Sourcegraph

### 5.1 Setup-Schritte

1. **Sourcegraph Cloud**: https://sourcegraph.com → GitHub-Konto verbinden → Repo indexieren
   **ODER Self-Hosted**: Docker/Kubernetes-Deployment (empfohlen ab 50+ Repos)
2. **Ignore-Datei committed** (bereits vorhanden): `.sourcegraph/ignore`
3. **Cody IDE-Extension** installieren (VS Code / JetBrains)
4. Optional: Webhook in GitHub konfigurieren für schnellere Index-Updates

### 5.2 Konfiguration

```
.sourcegraph/ignore  # Dateien die nicht in der Code-Suche erscheinen
```

Sourcegraph-Konfiguration ist **instanz-zentriert**, nicht repo-zentriert. Die Ignore-Datei
ist die einzige Repo-Level-Konfiguration.

### 5.3 Was Sourcegraph abdeckt, was die anderen Tools nicht tun

| Fähigkeit | SonarCloud | CodeRabbit | Sourcegraph |
|-----------|------------|------------|-------------|
| Repo-weite Code-Suche (Regex, Structural) | Nein | Nein | Ja |
| Cross-Repo-Referenzen | Nein | Nein | Ja |
| Code Intelligence (Go-to-Definition, Find-References) | Nein | Nein | Ja |
| Cody AI-Chat mit vollem Repo-Kontext | Nein | Nein | Ja |
| Batch Changes (automatisierte Refactorings) | Nein | Nein | Ja |
| Code Ownership / Contributor-Graph | Nein | Nein | Ja |

### 5.4 Empfohlener Einsatz für VALEO

- **Code-Suche**: „Wo wird `tenant_id` NICHT in einer Query gefiltert?" — strukturelle Suche
- **Refactoring**: Batch Changes für systematische Umstellungen (z.B. alle `|| true` entfernen)
- **Cody**: AI-Assistenz mit vollem ERP-Kontext für neue Entwickler / Onboarding
- **Architecture**: Code-Graph für Abhängigkeitsanalyse zwischen Domains

## 6. Zusammenspiel der drei Tools

```
Developer öffnet PR
      │
      ├──→ CodeRabbit: AI-Review (fachlich + Security)
      │     └──→ Kommentare direkt im PR
      │
      ├──→ SonarCloud: Statische Analyse + Quality Gate
      │     └──→ PR-Status-Check (blockierend bei Verletzung)
      │
      └──→ Sourcegraph Cody: AI-Chat für Kontext-Fragen
            └──→ "Was macht diese Funktion?" / "Wo wird das sonst verwendet?"

PR wird gemerged
      │
      ├──→ SonarCloud: Trend-Dashboard aktualisiert
      └──→ Sourcegraph: Index aktualisiert (via Webhook)
```

## 7. Migration bestehender `|| true` Checks

Nach SonarCloud-Einführung schrittweise die bestehenden advisory-only Checks härten:

| Workflow | Check | Aktuell | Ziel |
|----------|-------|---------|------|
| `ci.yml` | ESLint | `\|\| true` | SonarCloud ESLint-Regeln (hart) |
| `ci.yml` | Bandit | `\|\| true` | SonarCloud Security Hotspots (hart) |
| `ci.yml` | Safety | `\|\| true` | `quality-gate.yml` pip-audit (hart nach Baseline) |
| `ci.yml` | Playwright | `\|\| true` | Separate E2E-Pflicht erst nach E2E-Stabilisierung |
| `security-scan.yml` | Alle Jobs | `continue-on-error` | Advisory belassen (weekly Scan ≠ Gate) |
| `quality-gate.yml` | pip-audit | `continue-on-error` | Hart nach Vulnerability-Baseline |
| `quality-gate.yml` | pnpm audit | `continue-on-error` | Hart nach Vulnerability-Baseline |

**Reihenfolge**: SonarCloud Quality Gate zuerst → dann bestehende `|| true` schrittweise entfernen

## 8. Referenzen

- [SonarCloud Docs](https://docs.sonarsource.com/sonarcloud/)
- [CodeRabbit Docs](https://docs.coderabbit.ai/)
- [Sourcegraph Docs](https://docs.sourcegraph.com/)
- [ADR-007 Agent-Tool-Contract-Governance](../adr/adr-007-agent-tool-contract-governance.md)
