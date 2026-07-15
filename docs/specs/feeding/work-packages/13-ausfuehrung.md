---
title: "Arbeitspakete 121–130 — Ist-Fuetterung und Rueckmeldung"
type: plan
audience: [produkt, architektur, entwickler, qa, agent]
owner: domain/agrar
status: geplant
last_reviewed: 2026-07-15
version: 1.0.0
generated_by: scripts/generate_feeding_work_packages.py
---

# Ist-Fuetterung und Rueckmeldung

Requirements: FEED-ACT-001/002/004. Paketstatus und TDD-Laufnachweis werden bei Claim im Workboard/Slice gefuehrt; dieses Dokument bleibt der stabile Liefervertrag.

## FEED-WP-121 — Ist-Fuetterung und Rueckmeldung: Vertrag und erste Journey

**Nutzen:** Im Bereich Ist-Fuetterung und Rueckmeldung ein kleinster realer Nutzerfall funktioniert Ende-zu-Ende; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-ACT-001/002/004. **Abhaengig von:** FEED-WP-120. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Plan und tatsaechliche Fuetterung sind abgleichbar; Happy Path mit persistiertem Ergebnis und sichtbarer Herkunft. Nachweis ueber FEED-T121 und FEED-T188.

**Red:** Contract-/Domain-Test fuer den ersten Nutzerfall schlaegt fehl; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** kleinsten Domain-, API- und Meridian-Pfad implementieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Begriffe und Grenzen am Domainmodell ausrichten, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** fokussierte Domain-, API- und Screen-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-122 — Ist-Fuetterung und Rueckmeldung: Grenzen und Validierung

**Nutzen:** Im Bereich Ist-Fuetterung und Rueckmeldung ungueltige oder unvollstaendige Eingaben werden sicher erklaert; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-ACT-001/002/004. **Abhaengig von:** FEED-WP-120, FEED-WP-121. **Aufwand:** S (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Plan und tatsaechliche Fuetterung sind abgleichbar; Grenz-, Missing- und Conflict-Faelle liefern stabile Fehler. Nachweis ueber FEED-T122 und FEED-T189.

**Red:** Boundary-/Property-Test reproduziert die ungeschuetzte Grenze; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Validierung und ProblemDetails minimal ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Validierungsregeln zentralisieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Happy Path plus Boundary-/Property-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-123 — Ist-Fuetterung und Rueckmeldung: Tenant und Berechtigung

**Nutzen:** Im Bereich Ist-Fuetterung und Rueckmeldung nur berechtigte Personen sehen und aendern den fachlichen Scope; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-ACT-001/002/004. **Abhaengig von:** FEED-WP-120, FEED-WP-122. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Plan und tatsaechliche Fuetterung sind abgleichbar; Tenant, Rolle und Business-Grant werden serverseitig erzwungen. Nachweis ueber FEED-T123 und FEED-T190.

**Red:** negativer Isolation-/403-Test zeigt den Zugriff; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Policy am Application-Service/Endpoint schliessen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Policy-Duplikate in zentralen Guard ueberfuehren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Authz-, Enumeration- und Tenant-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-124 — Ist-Fuetterung und Rueckmeldung: Version und Audit

**Nutzen:** Im Bereich Ist-Fuetterung und Rueckmeldung Entscheidungen bleiben zeitlich und fachlich nachvollziehbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-ACT-001/002/004. **Abhaengig von:** FEED-WP-120, FEED-WP-123. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Plan und tatsaechliche Fuetterung sind abgleichbar; Aenderung erzeugt Version/Audit statt historischen Stand zu ueberschreiben. Nachweis ueber FEED-T124 und FEED-T191.

**Red:** Workflow-/Repository-Test zeigt verlorene Historie; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Versionierung und Auditereignis minimal persistieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Event- und Auditnamen vereinheitlichen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Lifecycle-, Migration- und Audit-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-125 — Ist-Fuetterung und Rueckmeldung: Fehler und Wiederaufnahme

**Nutzen:** Im Bereich Ist-Fuetterung und Rueckmeldung Nutzer koennen nach Konflikt oder Teilausfall sicher fortsetzen; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-ACT-001/002/004. **Abhaengig von:** FEED-WP-120, FEED-WP-124. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Plan und tatsaechliche Fuetterung sind abgleichbar; Retry ist idempotent und Fehlerzustand handlungsorientiert. Nachweis ueber FEED-T125 und FEED-T192.

**Red:** Idempotenz-/Recovery-Test erzeugt Doppelwirkung oder Sackgasse; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Idempotency Key, Journal oder Resume-Punkt ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Fehlerklassen und Kompensation schaerfen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Failure-, Retry- und Concurrency-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-126 — Ist-Fuetterung und Rueckmeldung: Meridian UX und Accessibility

**Nutzen:** Im Bereich Ist-Fuetterung und Rueckmeldung die Aufgabe ist auf Desktop und mobil zugaenglich bedienbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-ACT-001/002/004. **Abhaengig von:** FEED-WP-120, FEED-WP-125. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Plan und tatsaechliche Fuetterung sind abgleichbar; native ScreenDefinition, Tastatur, Focus, Empty/Error/Loading und WCAG sind abgedeckt. Nachweis ueber FEED-T126 und FEED-T193.

**Red:** Component-/axe-Test zeigt fehlenden Bedienvertrag; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** ScreenDefinition/RenderPlan und kleinstes Domain-Overlay ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** freie UI-Logik in Runtime-Vertrag zurueckfuehren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Component-, axe-, Keyboard- und Route-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-127 — Ist-Fuetterung und Rueckmeldung: Events und Integration

**Nutzen:** Im Bereich Ist-Fuetterung und Rueckmeldung nachgelagerte Prozesse erhalten ein stabiles, nachweisbares Signal; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-ACT-001/002/004. **Abhaengig von:** FEED-WP-120, FEED-WP-126. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Plan und tatsaechliche Fuetterung sind abgleichbar; Outbox/Event oder neutraler Port ist schemafest und genau-einmal-wirksam. Nachweis ueber FEED-T127 und FEED-T194.

**Red:** Contract-/Replay-Test zeigt Drift oder Doppelwirkung; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Event/Port plus Idempotenz minimal implementieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Mapping und Provideradapter trennen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Schema-, Replay-, Outbox- und Connector-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-128 — Ist-Fuetterung und Rueckmeldung: Performance und Beobachtbarkeit

**Nutzen:** Im Bereich Ist-Fuetterung und Rueckmeldung der Nutzerfall bleibt unter realer Last steuerbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-ACT-001/002/004. **Abhaengig von:** FEED-WP-120, FEED-WP-127. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Plan und tatsaechliche Fuetterung sind abgleichbar; Budget, Metriken, Traces und fachliche Alarmgrenzen sind nachgewiesen. Nachweis ueber FEED-T128 und FEED-T195.

**Red:** Benchmark verletzt bewusst das vereinbarte Budget; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Query/Cache/Batching und Metrik minimal optimieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Optimierung ohne Semantikaenderung isolieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Benchmark-, Explain-, Resilience- und SLO-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-129 — Ist-Fuetterung und Rueckmeldung: Migration und Kompatibilitaet

**Nutzen:** Im Bereich Ist-Fuetterung und Rueckmeldung Bestandsdaten und bestehende Konsumenten wechseln ohne Bruch; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-ACT-001/002/004. **Abhaengig von:** FEED-WP-120, FEED-WP-128. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Plan und tatsaechliche Fuetterung sind abgleichbar; Upgrade, Backfill, Dual-Read/Switch und Forward-Fix sind geprueft. Nachweis ueber FEED-T129 und FEED-T196.

**Red:** Migrations-/Aequivalenztest zeigt Drift zum Bestand; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** additive Migration und idempotenten Backfill liefern; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Kompatibilitaetsadapter befristen und dokumentieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Upgrade-, Backfill-, Golden- und API-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-130 — Ist-Fuetterung und Rueckmeldung: Release-Journey und Betriebsabnahme

**Nutzen:** Im Bereich Ist-Fuetterung und Rueckmeldung die Capability ist fuer den Pilotbetrieb abnahmefaehig; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-ACT-001/002/004. **Abhaengig von:** FEED-WP-120, FEED-WP-129. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Plan und tatsaechliche Fuetterung sind abgleichbar; E2E-Journey, Security, A11y, Runbook, Flag und Rollback sind gruen. Nachweis ueber FEED-T130 und FEED-T197.

**Red:** Release-Journey scheitert am letzten offenen Nutzerergebnis; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** fehlende vertikale Luecke ohne Scope-Ausweitung schliessen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** tote Adapter/Flags entfernen und Doku synchronisieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** vollstaendige Capability-, Playwright- und Release-Gates sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.
