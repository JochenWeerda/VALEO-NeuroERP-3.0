---
title: "Arbeitspakete 091–100 — Optimierung und Infeasibility"
type: plan
audience: [produkt, architektur, entwickler, qa, agent]
owner: domain/agrar
status: geplant
last_reviewed: 2026-07-15
version: 1.0.0
generated_by: scripts/generate_feeding_work_packages.py
---

# Optimierung und Infeasibility

Requirements: FEED-OPT-001/004/005. Paketstatus und TDD-Laufnachweis werden bei Claim im Workboard/Slice gefuehrt; dieses Dokument bleibt der stabile Liefervertrag.

## FEED-WP-091 — Optimierung und Infeasibility: Vertrag und erste Journey

**Nutzen:** Im Bereich Optimierung und Infeasibility ein kleinster realer Nutzerfall funktioniert Ende-zu-Ende; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-OPT-001/004/005. **Abhaengig von:** FEED-WP-060. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Solverlaeufe sind reproduzierbar und Konflikte erklaert; Happy Path mit persistiertem Ergebnis und sichtbarer Herkunft. Nachweis ueber FEED-T091 und FEED-T158.

**Red:** Contract-/Domain-Test fuer den ersten Nutzerfall schlaegt fehl; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** kleinsten Domain-, API- und Meridian-Pfad implementieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Begriffe und Grenzen am Domainmodell ausrichten, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** fokussierte Domain-, API- und Screen-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-092 — Optimierung und Infeasibility: Grenzen und Validierung

**Nutzen:** Im Bereich Optimierung und Infeasibility ungueltige oder unvollstaendige Eingaben werden sicher erklaert; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-OPT-001/004/005. **Abhaengig von:** FEED-WP-060, FEED-WP-091. **Aufwand:** S (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Solverlaeufe sind reproduzierbar und Konflikte erklaert; Grenz-, Missing- und Conflict-Faelle liefern stabile Fehler. Nachweis ueber FEED-T092 und FEED-T159.

**Red:** Boundary-/Property-Test reproduziert die ungeschuetzte Grenze; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Validierung und ProblemDetails minimal ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Validierungsregeln zentralisieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Happy Path plus Boundary-/Property-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-093 — Optimierung und Infeasibility: Tenant und Berechtigung

**Nutzen:** Im Bereich Optimierung und Infeasibility nur berechtigte Personen sehen und aendern den fachlichen Scope; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-OPT-001/004/005. **Abhaengig von:** FEED-WP-060, FEED-WP-092. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Solverlaeufe sind reproduzierbar und Konflikte erklaert; Tenant, Rolle und Business-Grant werden serverseitig erzwungen. Nachweis ueber FEED-T093 und FEED-T160.

**Red:** negativer Isolation-/403-Test zeigt den Zugriff; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Policy am Application-Service/Endpoint schliessen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Policy-Duplikate in zentralen Guard ueberfuehren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Authz-, Enumeration- und Tenant-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-094 — Optimierung und Infeasibility: Version und Audit

**Nutzen:** Im Bereich Optimierung und Infeasibility Entscheidungen bleiben zeitlich und fachlich nachvollziehbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-OPT-001/004/005. **Abhaengig von:** FEED-WP-060, FEED-WP-093. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Solverlaeufe sind reproduzierbar und Konflikte erklaert; Aenderung erzeugt Version/Audit statt historischen Stand zu ueberschreiben. Nachweis ueber FEED-T094 und FEED-T161.

**Red:** Workflow-/Repository-Test zeigt verlorene Historie; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Versionierung und Auditereignis minimal persistieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Event- und Auditnamen vereinheitlichen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Lifecycle-, Migration- und Audit-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-095 — Optimierung und Infeasibility: Fehler und Wiederaufnahme

**Nutzen:** Im Bereich Optimierung und Infeasibility Nutzer koennen nach Konflikt oder Teilausfall sicher fortsetzen; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-OPT-001/004/005. **Abhaengig von:** FEED-WP-060, FEED-WP-094. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Solverlaeufe sind reproduzierbar und Konflikte erklaert; Retry ist idempotent und Fehlerzustand handlungsorientiert. Nachweis ueber FEED-T095 und FEED-T162.

**Red:** Idempotenz-/Recovery-Test erzeugt Doppelwirkung oder Sackgasse; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Idempotency Key, Journal oder Resume-Punkt ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Fehlerklassen und Kompensation schaerfen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Failure-, Retry- und Concurrency-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-096 — Optimierung und Infeasibility: Meridian UX und Accessibility

**Nutzen:** Im Bereich Optimierung und Infeasibility die Aufgabe ist auf Desktop und mobil zugaenglich bedienbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-OPT-001/004/005. **Abhaengig von:** FEED-WP-060, FEED-WP-095. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Solverlaeufe sind reproduzierbar und Konflikte erklaert; native ScreenDefinition, Tastatur, Focus, Empty/Error/Loading und WCAG sind abgedeckt. Nachweis ueber FEED-T096 und FEED-T163.

**Red:** Component-/axe-Test zeigt fehlenden Bedienvertrag; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** ScreenDefinition/RenderPlan und kleinstes Domain-Overlay ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** freie UI-Logik in Runtime-Vertrag zurueckfuehren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Component-, axe-, Keyboard- und Route-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-097 — Optimierung und Infeasibility: Events und Integration

**Nutzen:** Im Bereich Optimierung und Infeasibility nachgelagerte Prozesse erhalten ein stabiles, nachweisbares Signal; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-OPT-001/004/005. **Abhaengig von:** FEED-WP-060, FEED-WP-096. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Solverlaeufe sind reproduzierbar und Konflikte erklaert; Outbox/Event oder neutraler Port ist schemafest und genau-einmal-wirksam. Nachweis ueber FEED-T097 und FEED-T164.

**Red:** Contract-/Replay-Test zeigt Drift oder Doppelwirkung; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Event/Port plus Idempotenz minimal implementieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Mapping und Provideradapter trennen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Schema-, Replay-, Outbox- und Connector-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-098 — Optimierung und Infeasibility: Performance und Beobachtbarkeit

**Nutzen:** Im Bereich Optimierung und Infeasibility der Nutzerfall bleibt unter realer Last steuerbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-OPT-001/004/005. **Abhaengig von:** FEED-WP-060, FEED-WP-097. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Solverlaeufe sind reproduzierbar und Konflikte erklaert; Budget, Metriken, Traces und fachliche Alarmgrenzen sind nachgewiesen. Nachweis ueber FEED-T098 und FEED-T165.

**Red:** Benchmark verletzt bewusst das vereinbarte Budget; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Query/Cache/Batching und Metrik minimal optimieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Optimierung ohne Semantikaenderung isolieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Benchmark-, Explain-, Resilience- und SLO-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-099 — Optimierung und Infeasibility: Migration und Kompatibilitaet

**Nutzen:** Im Bereich Optimierung und Infeasibility Bestandsdaten und bestehende Konsumenten wechseln ohne Bruch; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-OPT-001/004/005. **Abhaengig von:** FEED-WP-060, FEED-WP-098. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Solverlaeufe sind reproduzierbar und Konflikte erklaert; Upgrade, Backfill, Dual-Read/Switch und Forward-Fix sind geprueft. Nachweis ueber FEED-T099 und FEED-T166.

**Red:** Migrations-/Aequivalenztest zeigt Drift zum Bestand; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** additive Migration und idempotenten Backfill liefern; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Kompatibilitaetsadapter befristen und dokumentieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Upgrade-, Backfill-, Golden- und API-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-100 — Optimierung und Infeasibility: Release-Journey und Betriebsabnahme

**Nutzen:** Im Bereich Optimierung und Infeasibility die Capability ist fuer den Pilotbetrieb abnahmefaehig; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-OPT-001/004/005. **Abhaengig von:** FEED-WP-060, FEED-WP-099. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Solverlaeufe sind reproduzierbar und Konflikte erklaert; E2E-Journey, Security, A11y, Runbook, Flag und Rollback sind gruen. Nachweis ueber FEED-T100 und FEED-T167.

**Red:** Release-Journey scheitert am letzten offenen Nutzerergebnis; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** fehlende vertikale Luecke ohne Scope-Ausweitung schliessen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** tote Adapter/Flags entfernen und Doku synchronisieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** vollstaendige Capability-, Playwright- und Release-Gates sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.
