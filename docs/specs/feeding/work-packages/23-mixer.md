---
title: "Arbeitspakete 221–230 — Mixer- und agrirouter-Austausch"
type: plan
audience: [produkt, architektur, entwickler, qa, agent]
owner: domain/agrar
status: geplant
last_reviewed: 2026-07-15
version: 1.0.0
generated_by: scripts/generate_feeding_work_packages.py
---

# Mixer- und agrirouter-Austausch

Requirements: FEED-PLAN-003, FEED-INT-002/003. Paketstatus und TDD-Laufnachweis werden bei Claim im Workboard/Slice gefuehrt; dieses Dokument bleibt der stabile Liefervertrag.

## FEED-WP-221 — Mixer- und agrirouter-Austausch: Vertrag und erste Journey

**Nutzen:** Im Bereich Mixer- und agrirouter-Austausch ein kleinster realer Nutzerfall funktioniert Ende-zu-Ende; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-PLAN-003, FEED-INT-002/003. **Abhaengig von:** FEED-WP-130. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Planexport und Rueckmeldung wirken genau einmal; Happy Path mit persistiertem Ergebnis und sichtbarer Herkunft. Nachweis ueber FEED-T021 und FEED-T088.

**Red:** Contract-/Domain-Test fuer den ersten Nutzerfall schlaegt fehl; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** kleinsten Domain-, API- und Meridian-Pfad implementieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Begriffe und Grenzen am Domainmodell ausrichten, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** fokussierte Domain-, API- und Screen-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-222 — Mixer- und agrirouter-Austausch: Grenzen und Validierung

**Nutzen:** Im Bereich Mixer- und agrirouter-Austausch ungueltige oder unvollstaendige Eingaben werden sicher erklaert; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-PLAN-003, FEED-INT-002/003. **Abhaengig von:** FEED-WP-130, FEED-WP-221. **Aufwand:** S (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Planexport und Rueckmeldung wirken genau einmal; Grenz-, Missing- und Conflict-Faelle liefern stabile Fehler. Nachweis ueber FEED-T022 und FEED-T089.

**Red:** Boundary-/Property-Test reproduziert die ungeschuetzte Grenze; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Validierung und ProblemDetails minimal ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Validierungsregeln zentralisieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Happy Path plus Boundary-/Property-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-223 — Mixer- und agrirouter-Austausch: Tenant und Berechtigung

**Nutzen:** Im Bereich Mixer- und agrirouter-Austausch nur berechtigte Personen sehen und aendern den fachlichen Scope; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-PLAN-003, FEED-INT-002/003. **Abhaengig von:** FEED-WP-130, FEED-WP-222. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Planexport und Rueckmeldung wirken genau einmal; Tenant, Rolle und Business-Grant werden serverseitig erzwungen. Nachweis ueber FEED-T023 und FEED-T090.

**Red:** negativer Isolation-/403-Test zeigt den Zugriff; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Policy am Application-Service/Endpoint schliessen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Policy-Duplikate in zentralen Guard ueberfuehren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Authz-, Enumeration- und Tenant-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-224 — Mixer- und agrirouter-Austausch: Version und Audit

**Nutzen:** Im Bereich Mixer- und agrirouter-Austausch Entscheidungen bleiben zeitlich und fachlich nachvollziehbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-PLAN-003, FEED-INT-002/003. **Abhaengig von:** FEED-WP-130, FEED-WP-223. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Planexport und Rueckmeldung wirken genau einmal; Aenderung erzeugt Version/Audit statt historischen Stand zu ueberschreiben. Nachweis ueber FEED-T024 und FEED-T091.

**Red:** Workflow-/Repository-Test zeigt verlorene Historie; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Versionierung und Auditereignis minimal persistieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Event- und Auditnamen vereinheitlichen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Lifecycle-, Migration- und Audit-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-225 — Mixer- und agrirouter-Austausch: Fehler und Wiederaufnahme

**Nutzen:** Im Bereich Mixer- und agrirouter-Austausch Nutzer koennen nach Konflikt oder Teilausfall sicher fortsetzen; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-PLAN-003, FEED-INT-002/003. **Abhaengig von:** FEED-WP-130, FEED-WP-224. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Planexport und Rueckmeldung wirken genau einmal; Retry ist idempotent und Fehlerzustand handlungsorientiert. Nachweis ueber FEED-T025 und FEED-T092.

**Red:** Idempotenz-/Recovery-Test erzeugt Doppelwirkung oder Sackgasse; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Idempotency Key, Journal oder Resume-Punkt ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Fehlerklassen und Kompensation schaerfen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Failure-, Retry- und Concurrency-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-226 — Mixer- und agrirouter-Austausch: Meridian UX und Accessibility

**Nutzen:** Im Bereich Mixer- und agrirouter-Austausch die Aufgabe ist auf Desktop und mobil zugaenglich bedienbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-PLAN-003, FEED-INT-002/003. **Abhaengig von:** FEED-WP-130, FEED-WP-225. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Planexport und Rueckmeldung wirken genau einmal; native ScreenDefinition, Tastatur, Focus, Empty/Error/Loading und WCAG sind abgedeckt. Nachweis ueber FEED-T026 und FEED-T093.

**Red:** Component-/axe-Test zeigt fehlenden Bedienvertrag; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** ScreenDefinition/RenderPlan und kleinstes Domain-Overlay ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** freie UI-Logik in Runtime-Vertrag zurueckfuehren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Component-, axe-, Keyboard- und Route-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-227 — Mixer- und agrirouter-Austausch: Events und Integration

**Nutzen:** Im Bereich Mixer- und agrirouter-Austausch nachgelagerte Prozesse erhalten ein stabiles, nachweisbares Signal; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-PLAN-003, FEED-INT-002/003. **Abhaengig von:** FEED-WP-130, FEED-WP-226. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Planexport und Rueckmeldung wirken genau einmal; Outbox/Event oder neutraler Port ist schemafest und genau-einmal-wirksam. Nachweis ueber FEED-T027 und FEED-T094.

**Red:** Contract-/Replay-Test zeigt Drift oder Doppelwirkung; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Event/Port plus Idempotenz minimal implementieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Mapping und Provideradapter trennen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Schema-, Replay-, Outbox- und Connector-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-228 — Mixer- und agrirouter-Austausch: Performance und Beobachtbarkeit

**Nutzen:** Im Bereich Mixer- und agrirouter-Austausch der Nutzerfall bleibt unter realer Last steuerbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-PLAN-003, FEED-INT-002/003. **Abhaengig von:** FEED-WP-130, FEED-WP-227. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Planexport und Rueckmeldung wirken genau einmal; Budget, Metriken, Traces und fachliche Alarmgrenzen sind nachgewiesen. Nachweis ueber FEED-T028 und FEED-T095.

**Red:** Benchmark verletzt bewusst das vereinbarte Budget; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Query/Cache/Batching und Metrik minimal optimieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Optimierung ohne Semantikaenderung isolieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Benchmark-, Explain-, Resilience- und SLO-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-229 — Mixer- und agrirouter-Austausch: Migration und Kompatibilitaet

**Nutzen:** Im Bereich Mixer- und agrirouter-Austausch Bestandsdaten und bestehende Konsumenten wechseln ohne Bruch; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-PLAN-003, FEED-INT-002/003. **Abhaengig von:** FEED-WP-130, FEED-WP-228. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Planexport und Rueckmeldung wirken genau einmal; Upgrade, Backfill, Dual-Read/Switch und Forward-Fix sind geprueft. Nachweis ueber FEED-T029 und FEED-T096.

**Red:** Migrations-/Aequivalenztest zeigt Drift zum Bestand; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** additive Migration und idempotenten Backfill liefern; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Kompatibilitaetsadapter befristen und dokumentieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Upgrade-, Backfill-, Golden- und API-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-230 — Mixer- und agrirouter-Austausch: Release-Journey und Betriebsabnahme

**Nutzen:** Im Bereich Mixer- und agrirouter-Austausch die Capability ist fuer den Pilotbetrieb abnahmefaehig; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-PLAN-003, FEED-INT-002/003. **Abhaengig von:** FEED-WP-130, FEED-WP-229. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Planexport und Rueckmeldung wirken genau einmal; E2E-Journey, Security, A11y, Runbook, Flag und Rollback sind gruen. Nachweis ueber FEED-T030 und FEED-T097.

**Red:** Release-Journey scheitert am letzten offenen Nutzerergebnis; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** fehlende vertikale Luecke ohne Scope-Ausweitung schliessen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** tote Adapter/Flags entfernen und Doku synchronisieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** vollstaendige Capability-, Playwright- und Release-Gates sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.
