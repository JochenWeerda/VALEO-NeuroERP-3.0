# Quality & Governance Tooling — Einführungsplan

**Status:** Accepted
**Datum:** 2026-04-04

## 1. Entscheidung

VALEO NeuroERP führt drei externe Governance-Tools ein:

| Tool | Zweck | Phase |
|------|-------|-------|
| **SonarCloud** | Statische Analyse, Quality Gates, technische Schulden | Aktiv |
| **CodeRabbit** | AI-gestütztes PR-Review, inkrementell bei Commits | Aktiv |
| **Aider** | Terminal-basierte Multi-File-Refactorings mit Claude | Aktiv |
| **Continue.dev** | IDE-integriertes Codebase-Verständnis und Navigation | Aktiv |

**Nicht eingeführt / entfernt:**
- ~~Sourcegraph/Cody~~ — seit Juli 2025 nur Enterprise ($49/User/Monat), ersetzt durch Aider + Continue
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

## 5. Aider (Multi-File Refactoring)

### 5.1 Setup

```bash
# Installation
pip install aider-chat
# ODER mit uv (empfohlen)
uv tool install aider-chat

# API-Key setzen
export ANTHROPIC_API_KEY=<dein-key>

# Starten im Projektverzeichnis
cd VALEO-NeuroERP-3.0
aider
```

### 5.2 Konfiguration

```
.aider.conf.yml   # Modell, Git-Integration, Repo-Map, Read-Only-Dateien
```

Kernpunkte:
- **Modell**: Claude Sonnet als Architect + Editor
- **Repo-Map**: 4096 Tokens für Codebase-Kontext
- **Read-Only**: `CLAUDE.md` und `docs/MASKEN.md` als Kontext ohne Bearbeitungsrisiko
- **Auto-Commits**: Ein, für nachvollziehbare Refactoring-Schritte

### 5.3 Einsatz für VALEO

- **Multi-File-Refactorings**: `/add app/api/v1/endpoints/customers.py app/api/v1/schemas/crm.py` → Änderungen über mehrere Dateien planen und ausführen
- **Systematische Umstellungen**: z.B. alle `|| true` entfernen, URL-Patterns vereinheitlichen
- **Architect-Modus**: Erst planen, dann Code generieren — ideal für Domain-übergreifende Änderungen

### 5.4 Wichtige Befehle

| Befehl | Funktion |
|--------|----------|
| `/add <datei>` | Datei in Kontext aufnehmen |
| `/drop <datei>` | Datei aus Kontext entfernen |
| `/architect` | Planungsmodus (nur Reasoning) |
| `/code` | Code-Modus (Edits ausführen) |
| `/diff` | Aktuelle Änderungen anzeigen |
| `/undo` | Letzten Commit rückgängig machen |

## 6. Continue.dev (Codebase-Verständnis & Navigation)

### 6.1 Setup

1. **VS Code Extension**: Extensions → Suche „Continue" → Install
2. **API-Key**: Beim ersten Start nach Anthropic-Key gefragt, oder in `~/.continue/config.json`
3. **Projekt-Config**: `.continuerc.json` im Repo-Root (bereits committed)

### 6.2 Konfiguration

```
.continuerc.json    # Modelle, Context-Provider, Docs-Index
.continueignore     # Dateien die nicht indexiert werden (wie .gitignore)
```

Kernpunkte:
- **Chat-Modell**: Claude Sonnet mit 200k Kontext + Prompt-Caching
- **Autocomplete**: Claude Haiku für schnelle Tab-Completion
- **Context-Provider**: @Codebase (Embeddings-Suche), @Folder, @Terminal, @Diff, @Open
- **Docs-Index**: MASKEN.md und Architecture-Docs automatisch indexiert

### 6.3 Einsatz für VALEO

- **@Codebase-Fragen**: „Wo wird tenant_id NICHT in einer Query gefiltert?"
- **Navigation**: „Zeige alle Endpoints die sales_orders betreffen"
- **Verständnis**: „Erkläre den Flow von Auftragseingang bis Lieferschein"
- **Onboarding**: Neue Entwickler können Fragen zur Architektur stellen
- **Autocomplete**: Kontextbewusste Vorschläge beim Tippen

### 6.4 Wichtige Shortcuts (VS Code)

| Shortcut | Funktion |
|----------|----------|
| `Ctrl+L` | Chat öffnen |
| `Ctrl+I` | Inline-Edit |
| `@Codebase` | Gesamte Codebase durchsuchen |
| `@Folder` | Ordner als Kontext |
| `@Diff` | Aktuelle Änderungen als Kontext |

## 7. ~~Sourcegraph~~ (entfernt)

Sourcegraph/Cody ist seit Juli 2025 nur noch als Enterprise-Produkt verfügbar
($49/User/Monat). Die `.sourcegraph/ignore` bleibt im Repo für den Fall einer
späteren Enterprise-Evaluierung.

**Ersatz-Abdeckung:**

| Sourcegraph-Feature | Ersatz |
|---------------------|--------|
| Code-Suche (Regex, Structural) | Continue.dev @Codebase + GitHub Code Search |
| AI-Chat mit Repo-Kontext | Continue.dev Chat + Claude Code |
| Batch Refactorings | Aider Multi-File-Modus |
| Go-to-Definition | VS Code built-in + Continue.dev |

## 8. Zusammenspiel der vier Tools

```
Entwickler plant Refactoring
      │
      ├──→ Continue.dev: @Codebase — "Welche Dateien sind betroffen?"
      │     └──→ Codebase-Verständnis, Navigation, Kontext
      │
      └──→ Aider: Multi-File-Refactoring ausführen
            └──→ /add betroffene Dateien → Änderungen planen → Code generieren

Entwickler öffnet PR
      │
      ├──→ CodeRabbit: AI-Review (fachlich + Security)
      │     └──→ Kommentare direkt im PR
      │
      └──→ SonarCloud: Statische Analyse + Quality Gate
            └──→ PR-Status-Check (blockierend bei Verletzung)

PR wird gemerged
      │
      └──→ SonarCloud: Trend-Dashboard aktualisiert
```

## 9. Migration bestehender `|| true` Checks

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

## 10. Referenzen

- [SonarCloud Docs](https://docs.sonarsource.com/sonarcloud/)
- [CodeRabbit Docs](https://docs.coderabbit.ai/)
- [Aider Docs](https://aider.chat/docs/)
- [Aider Anthropic-Integration](https://aider.chat/docs/llms/anthropic.html)
- [Continue.dev Docs](https://docs.continue.dev/)
- [Continue.dev Anthropic-Setup](https://docs.continue.dev/customize/model-providers/top-level/anthropic)
- [ADR-007 Agent-Tool-Contract-Governance](../adr/adr-007-agent-tool-contract-governance.md)

## 11. AI-Harness-Governance

VALEO nutzt AI-Agenten nur innerhalb eines pruefbaren Harness:

- Slice-YAML mit fachlichem Vertrag, Architekturvertrag, Datenvertrag,
  Testvertrag, Security-Vertrag, Betriebsvertrag und Dokumentationsvertrag.
- Workboard-Dateibesitz vor Umsetzung.
- Doku-/Code-Sync fuer kritische Pfade.
- AI-Slice-Readiness-Check fuer neue oder geaenderte Slices.
- Nightly Documentation Drift Report ohne automatische Doku-Mutation.

Technische Artefakte:

| Artefakt | Zweck |
|----------|-------|
| `scripts/ai-slice-readiness-check.cjs` | Validiert Slice-YAML, Workboard-Bezug und AI-Harness |
| `scripts/docs-code-sync-check.cjs` | Erkennt kritische Codeaenderungen ohne passende Doku oder Ausnahme |
| `scripts/docs-drift-report.cjs` | Erzeugt Nightly-Report zu potenzieller Doku-Drift |
| `config/docs-code-sync-map.yaml` | Mapping von Codepfaden zu erwarteten Doku-Bereichen |
| `.github/workflows/ai-doc-sync.yml` | Nightly Drift Report als CI-Artefakt |
| `artifacts/ai-tool-compatibility-matrix.json` | Modell-/Tool-Fallbacks, Restriktionen und Datenklassen |

Diese Checks ersetzen kein Review. Sie verhindern, dass AI-Geschwindigkeit
neue nicht dokumentierte Architektur- oder Compliance-Schulden erzeugt.
