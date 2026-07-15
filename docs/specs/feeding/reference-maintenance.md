---
title: "Fuetterungsberatung — Pflegevertrag des Architektur-Referenzwerks"
type: reference
audience: [architektur, entwickler, fachlich, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Verbindliche Regeln, damit das 300–500-Seiten-Referenzwerk trotz Code-, OpenAPI- und Migrationsaenderungen eine verlaessliche Single Source of Truth bleibt.
---

# Pflegevertrag

## 1. Zweck

Das Referenzwerk soll Entscheidungen vorwegnehmen, ohne eine zweite technische
Wahrheit neben Code, Datenbank und generierter OpenAPI zu erzeugen. Es besteht aus
normativen Produktvertraegen, erklaerenden Architektursichten und generierten oder
quellengebundenen Inventaren.

## 2. Verbindlichkeitsklassen

| Klasse | Bedeutung | Beispiel | Konfliktregel |
|---|---|---|---|
| NORMATIV | fachliche oder architektonische Sollvorgabe | Statusautomat, Rollenmatrix, Invariante | Aenderung braucht Requirement-ID, Slice und Test |
| QUELLENGEBUNDEN | Abbild eines technischen Vertrags | Endpoint, Tabelle, Eventfeld | Code/OpenAPI/Migration ist Ausfuehrungsquelle; Doku-Drift muss im selben Slice korrigiert werden |
| ERKLAEREND | Begruendung, Beispiel, Lernpfad | Szenario, Begriffsbeispiel | darf normative Aussagen nicht erweitern |
| GEPLANT | noch nicht implementiertes Ziel | FEED-*-Arbeitspaket | muss Status und Abhaengigkeiten nennen |
| EXTERN BLOCKIERT | nicht repo-seitig lieferbar | DDW-Livevertrag | kein Mock darf als produktive Loesung gelten |

## 3. Quellenhierarchie

1. Fachliche Norm: freigegebene GfE-/DLG-Quelle und versionierter Golden-Test.
2. Produktanforderung: stabile `FEED-*`-ID im Lastenheft/Referenzwerk.
3. Architekturentscheidung: akzeptierter ADR und Domain Pack.
4. Laufzeitvertrag: Code, generierte OpenAPI, Alembic-Migration und Eventschema.
5. Bedienvertrag: ScreenDefinition/RenderPlan sowie Masken- und Workflowkatalog.
6. Planung: Workboard-Slice und Arbeitspaket.

Bei Widerspruch stoppt der umsetzende Slice, klassifiziert die Abweichung und
aktualisiert die hoeher priorisierte Quelle oder dokumentiert eine Migration.

## 4. Kapitelvertrag

Jedes Dokument 00–17 enthaelt:

- Owner, Status, Version und `last_reviewed`;
- normative IDs oder explizite Kennzeichnung als erklaerend;
- Quellen auf Code, ADR, OpenAPI, Migration oder Test;
- bekannte Abweichungen und naechste Arbeitspakete;
- keine erfundenen Endpunkte, Tabellen, Formeln oder Providerfaehigkeiten.

## 5. Aenderungsregeln je Artefakt

| Codeaenderung | Pflichtaktualisierung |
|---|---|
| neue/veraenderte Tabelle oder Index | 05 Datenmodell, Migrationsteil, Traceability, Tests |
| neuer/veraenderter Endpoint | 06 API, Domain Pack, OpenAPI-Beispiel, RBAC-Test |
| neue/veraenderte Maske | 07 Maskenkatalog, 10 UI/UX, Interaktions-/axe-Test |
| Status-/Prozesswechsel | 08 Workflow, 04 DDD, Event-/Audit-Test |
| neue Formel/Regel | 09 Regelwerk, Quellenreferenz, Golden-/Property-Test |
| neuer Agent oder Toolzugriff | 11 Agenten, Policy, Human-in-the-loop- und Halluzinationstest |
| neuer Connector | 12 Integrationen, Mapping, Quarantaene, Consent/Contract/Secret/Egress-Gates |
| neuer Slice | 17 Roadmap/Arbeitspaket, Workboard, Traceability |

## 6. Formel- und Regel-SSOT

Das Regelwerk beschreibt Eingaben, Einheiten, Gueltigkeit, Quellen, Randfaelle und
Testvektoren. Rechenformeln werden nur dann in Markdown ausgeschrieben, wenn sie
aus einer zitierbaren Norm stammen und exakt als Code-/Testreferenz verankert sind.
Die ausfuehrbare Wahrheit bleibt der versionierte Rechenkern plus Golden-Test.

## 7. API- und Datenmodell-SSOT

Der API-Katalog enthaelt fachliche Semantik und Beispiele. Feldlisten werden gegen
Pydantic/OpenAPI geprueft. Das Datenmodell enthaelt Zweck, Schluessel, Beziehungen,
Indizes, Tenant- und Historisierungsregeln; die physische Wahrheit bleibt Alembic.

## 8. Review- und Driftzyklus

- je Slice: betroffene Kapitel vor Abschluss aktualisieren;
- je Release: alle NORMATIV- und QUELLENGEBUNDEN-Kapitel reviewen;
- quartalsweise: externe Norm-/Providerquellen auf Version und Vertrag pruefen;
- Drift-Gate: tote Dateilinks, unbekannte Requirement-IDs, fehlende Testnachweise,
  Endpoint-/Tabellenabweichungen und veraltete `last_reviewed` blockieren;
- 300–500 Seiten sind Zielumfang, kein Qualitaetsmass: Duplikate werden entfernt,
  nicht durch Seitenzahl gerechtfertigt.

## 9. Verbindlicher TDD-Vertrag

Jede produktive Aenderung folgt **Red → Green → Refactor**. Dokumentation oder ein
nachtraeglich hinzugefuegter Happy-Path-Test ersetzt diesen Ablauf nicht.

1. **Test-ID waehlen:** Requirement, Invariante und betroffene Schicht benennen.
2. **Red:** kleinsten aussagekraeftigen Test zuerst schreiben und den erwarteten
   Fehler nachweisen. Ein Test, der vor der Implementierung bereits gruen ist,
   beweist die neue Anforderung nicht und muss geschaerft werden.
3. **Green:** kleinste fachlich korrekte Implementierung erstellen, die den Test
   bestehen laesst. Keine vorgezogene Nebenfunktion oder spekulative Abstraktion.
4. **Refactor:** Duplikate, Benennung, Grenzen und Architektur verbessern, waehrend
   der neue Test und die relevante Regression gruen bleiben.
5. **Regression:** fokussierte Tests, betroffene Domain-/Contract-/UI-Suite und die
   risikogerechten Repo-Gates ausfuehren.
6. **Nachweis:** Red-Fehler, Green-Befehl, Ergebnis, Test-ID und Artefakt im Slice
   oder Commit dokumentieren.

### 9.1 TDD je Aenderungsklasse

| Aenderung | Zuerst fehlschlagender Test |
|---|---|
| Domainregel/Invariante | Unit-, Boundary- oder Property-Test |
| GfE-/DLG-Regel | Golden- plus Boundary-Test gegen versionierte Quelle |
| API | Contract-/Auth-/ProblemDetails-Test vor Endpointcode |
| Migration/Repository | Schema-, Tenant-, Constraint- und Backfill-Test |
| ScreenDefinition/Maske | Compiler-/Component-Test; danach Playwright/A11y |
| Workflow | verbotener und erlaubter Zustandsuebergang samt Audit/Event |
| Connector | Contract-Fixture, Idempotenz, Delete/Move und Fehlerfall |
| Agent/Tool | Policy-/Schema-/Injection-Eval vor Prompt-/Toolfreigabe |
| Performancefix | reproduzierbarer Benchmark, der das Budget zunaechst verletzt |
| Bugfix | Regressionstest, der exakt den beobachteten Fehler reproduziert |

### 9.2 Ausnahmen

Reine Prosa-, Kommentar- oder Formatkorrekturen benoetigen keinen Red-Test, muessen
aber Markdown-/Governance-Gates bestehen. Explorative Spikes duerfen ohne TDD auf
einem wegwerfbaren Pfad arbeiten; kein Spike-Code wird produktiv uebernommen, bevor
der Vertrag durch Tests neu umgesetzt wurde. Externe Live-Gates koennen durch Mocks
nicht als gruen gelten.

### 9.3 Commit- und Reviewnachweis

Ein Arbeitspaket gilt nur dann als implementiert, wenn sein Nachweis mindestens
enthaelt:

```yaml
tdd_evidence:
  test_ids: [FEED-T...]
  red:
    command: "..."
    expected_failure: "..."
  green:
    command: "..."
    result: passed
  regression:
    commands: ["..."]
    result: passed
  refactor_notes: "..."
```

Der Red-Nachweis darf als lokaler Testlauf, CI-Artefakt oder bewusst separater
Testcommit vorliegen. Er muss keine absichtlich rote Hauptbranch-Pipeline erzeugen.

## 10. Status des Aufbaus

`FEED-SPEC-REFERENCE-038` baut die Kapitel in fachlich abhaengiger Reihenfolge auf:
Grundlagen -> DDD/Daten/API -> Masken/Workflows/Regeln -> Agenten/Integrationen/
Tests -> Migration/Rollout/Traceability/Roadmap. Jedes Kapitel wird erst als
`aktiv` markiert, wenn Quellen, IDs und mindestens ein Abnahmemechanismus vorhanden
sind; vorher bleibt es `in_arbeit`, nicht scheinbar abgeschlossen.

## 11. Maschinenpruefung des Arbeitsprogramms

Der 240-Pakete-Katalog wird deterministisch erzeugt und eingecheckt:

```powershell
python scripts/generate_feeding_work_packages.py
python scripts/generate_feeding_work_packages.py --check
pytest -q tests/test_feeding_reference_catalog.py
```

Der Check erkennt Generator-Drift; der Test verlangt alle Kapitel 00–17, exakt
240 eindeutige Pakete, die TDD-/DoD-Pflichtfelder und ausschliesslich bekannte
Akzeptanztest-IDs aus Kapitel 13. Paketstatus und reale Laufnachweise bleiben im
Workboard und Slice-YAML, damit generierte Liefervertraege nicht ueberschrieben
werden muessen.
