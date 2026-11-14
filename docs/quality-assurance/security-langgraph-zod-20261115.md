---
title: LangGraph- und BFF-Abhaengigkeitssicherheit
type: qa
audience: [entwickler, qa, sicherheit]
owner: Codex
status: active
last_reviewed: 2026-11-15
---

# LangGraph- und BFF-Abhaengigkeitssicherheit

Slice `SECURITY-LANGGRAPH-ZOD-20261115`: Root- und AI-Service-Manifest setzen
`langgraph` 1.2.14 und `langgraph-checkpoint-sqlite` 3.1.2. Diese beheben laut
Hersteller den [SDK-Pfadbefund](https://github.com/langchain-ai/langgraph/security/advisories/GHSA-3fx2-cqw9-xr3c)
und die [SQLite-Namespace-Verwechslung](https://github.com/langchain-ai/langgraph/security/advisories/GHSA-6hmw-9432-67qq).
Die Paketmetadaten verlangen SDK >=0.4.6 und Checkpoint-Basis >=4.3.0; die
isolierte Aufloesung ergab SDK 0.4.14 und Checkpoint 4.3.2. Die bestehenden
SQLite-Saver der beiden Workflow-Factories bleiben erhalten.

Das eigenstaendig installierte BFF-Manifest pinnt `zod` auf 4.6.7 gegen
[GHSA-mrhx-c7xc-m3w5](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5).
Das BFF ist kein pnpm-Workspace-Importer; der Root-Lock blieb unveraendert.
Im gegenwaertigen BFF-Quellcode existiert kein Zod-Import oder Zod-Validator,
deshalb war keine Validator-Umschreibung angezeigt.

## Nachweis und Grenzen

- Python 3.11.13, wiederverwendete isolierte Sicherheitsumgebung: beide
  `pip-audit -r`-Laeufe fuer Root und `services/ai` meldeten keine bekannten
  Schwachstellen; `pip check` meldete keine Konflikte.
- Acht konkrete LangGraph-Vertraege bestanden: synchrone und asynchrone
  SDK-Pfadkodierung, vier SQLite-Batch-Namespace-Negativfaelle vor I/O,
  gueltiger Namespace und Graph-Kompilierung mit echtem `SqliteSaver` und
  simuliertem Verbindungsobjekt. Keine Datenbank wurde geoeffnet.
- BFF-Typecheck bestand vor und nach eigenstaendiger npm-Aufloesung; `npm ls`
  bestaetigte Zod 4.6.7 und eine begrenzte Arrayvalidierung bestand. Ein aus
  dem BFF-Manifest separat aufgeloester `npm audit --omit=dev` meldete null
  Produktionsbefunde. Dev-Abhaengigkeiten sind hierin nicht abgenommen.
- Der vorhandene `deepmerge`-Quellpatch bestand alle 21 CJS-, UMD- und
  Browser-Gegenproben. Das ist ein Nachweis fuer den lokalen Patch, keine
  Behauptung eines Herstellerfixes oder einer erneuerten Sicherheitsbewertung.

Kein globaler Paketwechsel, keine neue Datenbank, kein Container und keine
Scan-Ausnahme. CI-/Dependabot-Nachlauf fuer den integrierten Commit steht aus.

Der Security-Workflow prueft das eigenstaendig installierte BFF nun separat: nur Lock-Aufloesung ohne Installationsskripte, anschliessend blockierender Produktionsaudit und eigener JSON-Bericht. Dies schliesst die Inventarluecke des Root-pnpm-Audits; es wird keine Schwachstelle ausgenommen. GitHub-Nachlauf erforderlich.
