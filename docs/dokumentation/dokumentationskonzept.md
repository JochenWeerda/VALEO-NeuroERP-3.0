---
title: Dokumentationskonzept VALEO NeuroERP 3.0
type: explanation
audience: [entwickler, product, qa, admin]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Dokumentationskonzept VALEO NeuroERP 3.0

Verbindliches Konzept für eine projektideale Software-Dokumentation. Es setzt auf
den bestehenden Assets auf (AI-Harness, `agent-ops/slices`, ADRs,
Process-Kernel-STATUS, Release-Compatibility-Matrix, MCP-Tool-Katalog,
AI-DOC-DRIFT-DASHBOARD) und überführt die organisch gewachsene Doku-Landschaft
in ein wartbares, versioniertes, agententaugliches System.

## 1. Ziele

Die Doku muss vier Realitäten gleichzeitig bedienen:

1. **Regulatorik** — GoBD, DSGVO, Audit-Fähigkeit: Doku ist Nachweis
   (revisionssicher, versioniert, datierbar).
2. **Multi-Mandanten-ERP** — gleiche Software, unterschiedliche
   Modulkonfiguration pro Tenant → Doku ist konfigurationsabhängig.
3. **Fachdomäne Landhandel/Agrar** — Endnutzer sind Sachbearbeiter:
   Deutsch, aufgabenorientiert.
4. **Agentische Entwicklung** — Coding- und Operator-Agents (Hermes) sind
   Leser **und** Autoren der Doku → Maschinenlesbarkeit ist Pflicht.

### Messbare Zielwerte

| Ziel | Kennzahl |
|---|---|
| Auffindbarkeit | Time-to-Answer < 2 min für Top-50-Aufgaben |
| Aktualität | 0 kritische Treffer im Nightly Doku-Code-Drift-Report |
| Abdeckung | 100 % produktive API-Endpoints + jede Wave/jeder Slice mit Pflichtdoku |
| Revisionssicherheit | unveränderlicher Doku-Snapshot je Release |
| Agent-Tauglichkeit | maschinenlesbarer Vertrag je Slice/Tool (`ai_harness`, MCP-Schema) |

## 2. Beteiligte / Zielgruppen

| Zielgruppe | Primärbedarf | Artefakt |
|---|---|---|
| Endnutzer (Annahme/Verkauf/Lager/FiBu) | „Wie erledige ich Aufgabe X?" | Benutzerhandbuch + In-App-Hilfe |
| Key-/Power-User | Prozessvarianten, Sonderfälle | How-to-Guides, Prozesslandkarten |
| Tenant-Admin | Module, RBAC, Nummernkreise, Stammdaten | Mandanten-Admin-Handbuch |
| Betrieb/System-Admin | Deploy, Backup, Monitoring, Incident, Skalierung | Betriebshandbuch/Runbooks |
| Entwickler | Architektur, Datenmodell, Setup, Konventionen | Developer-Docs, ADRs, CLAUDE.md/AGENTS.md |
| QA/Test | Soll-Ist, Testpläne, Browser-Use | QA-Bereich, UAT-Features |
| Security/Compliance/Auditor | GoBD, DSGVO-ROPA, Audit-Trail | Compliance-Doku, Audit-Evidence |
| Integratoren/Partner | API, Events, Webhooks, Auth | Schnittstellen-/Integrationshandbuch |
| KI-Agents (Hermes & Co.) | Fähigkeiten, Tools, Guardrails, Verträge | Agent-Capability-Katalog (maschinenlesbar) |
| Management/Product | Status, Roadmap, Reifegrad | Process-Kernel-STATUS, Roadmap |

## 3. Dokumentationsarten — Diátaxis

Jedes Dokument hat **genau einen** Typ:

```text
Tutorial      → Lernen       → "Erste Ernteannahme Schritt für Schritt"
How-to-Guide  → Aufgabe      → "Lieferschein in Rechnung umwandeln"
Reference     → Nachschlagen → API, Datenmodell, Maskenkatalog, CLI
Explanation   → Verstehen    → ADRs, Architektur, Gewohnheits-Prinzip
```

Status-/Reports sind kein Diátaxis-Typ → eigener Lebenszyklus (siehe §10/§11).

## 4. Schnittstellenbeschreibung

| Schnittstelle | Quelle | Format | Versionierung |
|---|---|---|---|
| REST-API | FastAPI → `openapi.json` | OpenAPI 3.1 (generiert) | je API-Contract |
| Event-Bus (NATS/Outbox) | Event-Schemas | AsyncAPI (neu) | je Event-Schema |
| MCP-Tools | `config/mcp_erp_tools.yaml` | JSON-Schema + Scope/Risiko | im Tool-Katalog |
| SSE-Streams | `sse_router` | Endpoint-Referenz | mit API |
| Webhooks (DMS/GS1) | Router | Payload-Verträge | mit API |
| Datenverträge | Slice `daten_vertrag` | Tabellen/Felder/Tenant | mit Migration |

**Prinzip: Single Source = Code.** OpenAPI/AsyncAPI werden generiert, nie
handgepflegt; Artefakte versioniert in `artifacts/`, eingebettet in die
Doku-Site. Verknüpfung mit der Release-Compatibility-Matrix.

## 5. Benutzerhandbuch

Aufgabenorientiert pro Fachdomäne (nicht nach Menüstruktur):

```text
benutzerhandbuch/
├── einstieg/            (Login, Mandant, Navigation, Tastatur)
├── annahme/             (LKW-Registrierung, Waage, Qualität, Annahme)
├── verkauf/             (Auftrag → Lieferschein → Rechnung)
├── einkauf/             (Bestellung → Wareneingang → Prüfung)
├── lager/               (Bestand, Umlagerung, Inventur, Silo)
├── finanzbuchhaltung/   (Debitoren, Mahnwesen, Zahlungen)
├── crm/                 (Kontakte, Leads, Hofprofile)
└── glossar/             (Fachbegriffe Landhandel/Agrar)
```

Je Aufgabe: Ziel → Voraussetzungen → Schritte (nummeriert, mit Screenshot) →
Ergebnis → häufige Fehler. Sprache Deutsch, Terminologie via Terminology-Registry.
In-App-Hilfe über kontextsensitive Deep-Links (Routen-IDs).

## 6. Admin-Handbuch (zweigeteilt)

- **Mandanten-Admin:** Module/Feature-Flags (`INSTALLED_MODULES`/
  `TENANT_MODULE_FLAGS`), RBAC, Nummernkreise, Stammdaten, Belegvorlagen,
  Übersetzungen.
- **Betriebs-/System-Admin:** Deployment (Docker Compose), Secrets,
  Backup/Restore, Alembic (Single-Head), Monitoring (Prometheus/SLO),
  Incident-Response, Skalierung (Worker, vgl. PERF-MULTIUSER-001),
  Production-Readiness-Gates.

## 7. KI-Agent-Dokumentation (Hermes & Co.)

Eigene, maschinenlesbare Schicht:

```text
agent-docs/
├── AGENTS.md             (Einstieg, Pflichtreihenfolge — vorhanden)
├── capability-catalog    (Hermes/Operator/Coding-Agents: Fähigkeiten)
├── tool-catalog/         (MCP-Tools: Schema, Scope, Idempotenz, Risiko)
├── guardrails            (Human-Approval HIGH-risk, fail-closed, RBAC)
├── contracts/            (Slice ai_harness: 7 Verträge als Schema)
├── skills/               (.cursor/skills, autogoal)
└── runbooks/             (Operator-Agent Proposal-Lifecycle)
```

Zwei Rollen je Agent klar trennen:

- **Agent als Leser:** strukturierte Verträge (`ai_harness`, MCP-JSON-Schema,
  OpenAPI).
- **Agent als Autor:** jeder Slice erzeugt Pflichtdoku (Workboard, Slice-YAML,
  Workflow-Doc); Doku-Update = Definition of Done. Drift wird nachts gemessen
  (AI-DOC-DRIFT-DASHBOARD).

## 8. Versionierung

| Ebene | Strategie |
|---|---|
| Doku-Quelle | Docs-as-Code: Markdown im Repo, gleicher PR/Commit wie der Code |
| Release-Snapshot | unveränderlicher Doku-Stand je Release (`mike`, Git-Tag); auditrelevant |
| API-Versionen | OpenAPI/AsyncAPI versioniert; Breaking Change → neue Contract-Version + Deprecation |
| ADRs | append-only, Status proposed/accepted/superseded |
| Changelog | „Keep a Changelog" + nutzerlesbare Release Notes (DE) |
| Kompatibilität | Verknüpfung mit `artifacts/release-compatibility-matrix.json` |
| Deprecation | Frist-Policy, sichtbar in Reference + Changelog |
| Versionswähler | Doku-Site mit Versions-Dropdown (`mike`) |

**Semantik: Doku-Version = App-Version** (kein eigener Doku-Versionsstrang).

## 9. Toolchain & Struktur

**MkDocs + Material for MkDocs** (Markdown-nativ → agententauglich,
Python-Stack, geringe Migrationskosten, `mike`-Versionierung, Volltextsuche,
Mermaid, OpenAPI-Einbettung).

```text
docs/
├── index.md
├── benutzerhandbuch/      (§5)
├── admin/                 (§6 — tenant + betrieb)
├── entwickler/            (Architektur, Setup, Konventionen)
├── schnittstellen/        (§4 — API/Events/MCP/Webhooks, generiert)
├── agent-docs/            (§7)
├── compliance/            (GoBD, DSGVO, Audit)
├── referenz/              (Masken, Datenmodell, CLI, Glossar)
├── adr/                   (bestehend)
├── architecture/          (bestehend, inkl. process-kernel STATUS)
└── _internal/             (Workboard, Slices, Reports — nicht in öffentliche Site)
```

## 10. Sprachstrategie

- **Deutsch (verbindlich):** Benutzerhandbuch, Admin/Mandant, Compliance.
- **Englisch (pragmatisch):** API-/Event-Referenz, Agent-Verträge, ADRs
  (code-nah, generiert).
- Keine vollständige Zweisprachigkeit (vermeidet Pflege-Drift).

## 11. Governance & Pflege

- CODEOWNERS je Doku-Bereich.
- Doku = Teil der Definition of Done (AGENTS.md/CLAUDE.md).
- CI-Gates: Link-Check, Markdown-Lint (`docs-governance-check.cjs`),
  Slice-Readiness, OpenAPI-Diff, Drift-Report, `mkdocs build`.
- Staleness: `last_reviewed`-Frontmatter; nach Frist ohne Review → Flag.
- Review-Frequenz: Benutzerhandbuch je Release, Architektur/ADR bei Änderung,
  Compliance quartalsweise.

### Frontmatter-Pflichtfelder

Siehe [Frontmatter-Standard](frontmatter-standard.md). Jede kuratierte
Doku-Seite trägt: `title, type, audience, owner, status, last_reviewed, version`.

## 12. Migration / Aufräumen

1. Archivieren: `archive/`, `*-COMPLETE.md`, `*-debugging.md`, datierte Reports
   → `_internal/archive/` (aus der öffentlichen Site ausgeschlossen, im Git erhalten).
2. Konsolidieren: doppelte/überlappende Themen zusammenführen.
3. Einordnen: nach Diátaxis-Typ + Zielgruppe.
4. Frontmatter erzwingen.

## 13. Umsetzung als Slices

| Slice | Inhalt |
|---|---|
| `DOC-FOUNDATION-001` | MkDocs-Material + `mike` + CI-Build, Taxonomie, Frontmatter-Standard |
| `DOC-INTERFACES-001` | OpenAPI/AsyncAPI-Generierung + Einbettung + Schnittstellenhandbuch |
| `DOC-USER-MANUAL-001` | Benutzerhandbuch-Skelett + In-App-Deep-Links + Terminologie |
| `DOC-ADMIN-OPS-001` | Mandanten-Admin- + Betriebshandbuch |
| `DOC-AGENT-CATALOG-001` | Hermes/Agent-Capability- + Tool-Katalog + Guardrails |
| `DOC-GOVERNANCE-001` | CODEOWNERS, Link-Check, Staleness, Release-Snapshot, Changelog |
| `DOC-MIGRATION-001` | Aufräumen/Archivieren der Altbestände |

## 14. Leitprinzip

**Docs-as-Code.** Doku reist im selben PR wie der Code; Doku-Update ist Teil der
Definition of Done; Drift wird nachts gemessen. Einziger Weg, der bei hohem Tempo
und Multi-Agent-Betrieb nicht wieder zerfasert.
