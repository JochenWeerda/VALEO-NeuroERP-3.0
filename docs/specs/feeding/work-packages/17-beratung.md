---
title: "Arbeitspakete 161–170 — Beratungsfall und Beobachtung"
type: plan
audience: [produkt, architektur, entwickler, qa, agent]
owner: domain/agrar
status: geplant
last_reviewed: 2026-07-15
version: 1.0.0
generated_by: scripts/generate_feeding_work_packages.py
---

# Beratungsfall und Beobachtung

Requirements: FEED-CONS-001. Paketstatus und TDD-Laufnachweis werden bei Claim im Workboard/Slice gefuehrt; dieses Dokument bleibt der stabile Liefervertrag.

## FEED-WP-161 — Beratungsfall und Beobachtung: Vertrag und erste Journey

**Nutzen:** Im Bereich Beratungsfall und Beobachtung ein kleinster realer Nutzerfall funktioniert Ende-zu-Ende; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-CONS-001. **Abhaengig von:** FEED-WP-160. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Beratungsanlass und Entscheidung bilden eine Akte; Happy Path mit persistiertem Ergebnis und sichtbarer Herkunft. Nachweis ueber FEED-T161 und FEED-T028.

**Red:** Contract-/Domain-Test fuer den ersten Nutzerfall schlaegt fehl; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** kleinsten Domain-, API- und Meridian-Pfad implementieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Begriffe und Grenzen am Domainmodell ausrichten, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** fokussierte Domain-, API- und Screen-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-162 — Beratungsfall und Beobachtung: Grenzen und Validierung

**Nutzen:** Im Bereich Beratungsfall und Beobachtung ungueltige oder unvollstaendige Eingaben werden sicher erklaert; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-CONS-001. **Abhaengig von:** FEED-WP-160, FEED-WP-161. **Aufwand:** S (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Beratungsanlass und Entscheidung bilden eine Akte; Grenz-, Missing- und Conflict-Faelle liefern stabile Fehler. Nachweis ueber FEED-T162 und FEED-T029.

**Red:** Boundary-/Property-Test reproduziert die ungeschuetzte Grenze; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Validierung und ProblemDetails minimal ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Validierungsregeln zentralisieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Happy Path plus Boundary-/Property-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-163 — Beratungsfall und Beobachtung: Tenant und Berechtigung

**Nutzen:** Im Bereich Beratungsfall und Beobachtung nur berechtigte Personen sehen und aendern den fachlichen Scope; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-CONS-001. **Abhaengig von:** FEED-WP-160, FEED-WP-162. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Beratungsanlass und Entscheidung bilden eine Akte; Tenant, Rolle und Business-Grant werden serverseitig erzwungen. Nachweis ueber FEED-T163 und FEED-T030.

**Red:** negativer Isolation-/403-Test zeigt den Zugriff; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Policy am Application-Service/Endpoint schliessen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Policy-Duplikate in zentralen Guard ueberfuehren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Authz-, Enumeration- und Tenant-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-164 — Beratungsfall und Beobachtung: Version und Audit

**Nutzen:** Im Bereich Beratungsfall und Beobachtung Entscheidungen bleiben zeitlich und fachlich nachvollziehbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-CONS-001. **Abhaengig von:** FEED-WP-160, FEED-WP-163. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Beratungsanlass und Entscheidung bilden eine Akte; Aenderung erzeugt Version/Audit statt historischen Stand zu ueberschreiben. Nachweis ueber FEED-T164 und FEED-T031.

**Red:** Workflow-/Repository-Test zeigt verlorene Historie; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Versionierung und Auditereignis minimal persistieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Event- und Auditnamen vereinheitlichen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Lifecycle-, Migration- und Audit-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-165 — Beratungsfall und Beobachtung: Fehler und Wiederaufnahme

**Nutzen:** Im Bereich Beratungsfall und Beobachtung Nutzer koennen nach Konflikt oder Teilausfall sicher fortsetzen; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-CONS-001. **Abhaengig von:** FEED-WP-160, FEED-WP-164. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Beratungsanlass und Entscheidung bilden eine Akte; Retry ist idempotent und Fehlerzustand handlungsorientiert. Nachweis ueber FEED-T165 und FEED-T032.

**Red:** Idempotenz-/Recovery-Test erzeugt Doppelwirkung oder Sackgasse; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Idempotency Key, Journal oder Resume-Punkt ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Fehlerklassen und Kompensation schaerfen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Failure-, Retry- und Concurrency-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-166 — Beratungsfall und Beobachtung: Meridian UX und Accessibility

**Nutzen:** Im Bereich Beratungsfall und Beobachtung die Aufgabe ist auf Desktop und mobil zugaenglich bedienbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-CONS-001. **Abhaengig von:** FEED-WP-160, FEED-WP-165. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Beratungsanlass und Entscheidung bilden eine Akte; native ScreenDefinition, Tastatur, Focus, Empty/Error/Loading und WCAG sind abgedeckt. Nachweis ueber FEED-T166 und FEED-T033.

**Red:** Component-/axe-Test zeigt fehlenden Bedienvertrag; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** ScreenDefinition/RenderPlan und kleinstes Domain-Overlay ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** freie UI-Logik in Runtime-Vertrag zurueckfuehren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Component-, axe-, Keyboard- und Route-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-167 — Beratungsfall und Beobachtung: Events und Integration

**Nutzen:** Im Bereich Beratungsfall und Beobachtung nachgelagerte Prozesse erhalten ein stabiles, nachweisbares Signal; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-CONS-001. **Abhaengig von:** FEED-WP-160, FEED-WP-166. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Beratungsanlass und Entscheidung bilden eine Akte; Outbox/Event oder neutraler Port ist schemafest und genau-einmal-wirksam. Nachweis ueber FEED-T167 und FEED-T034.

**Red:** Contract-/Replay-Test zeigt Drift oder Doppelwirkung; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Event/Port plus Idempotenz minimal implementieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Mapping und Provideradapter trennen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Schema-, Replay-, Outbox- und Connector-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-168 — Beratungsfall und Beobachtung: Performance und Beobachtbarkeit

**Nutzen:** Im Bereich Beratungsfall und Beobachtung der Nutzerfall bleibt unter realer Last steuerbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-CONS-001. **Abhaengig von:** FEED-WP-160, FEED-WP-167. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Beratungsanlass und Entscheidung bilden eine Akte; Budget, Metriken, Traces und fachliche Alarmgrenzen sind nachgewiesen. Nachweis ueber FEED-T168 und FEED-T035.

**Red:** Benchmark verletzt bewusst das vereinbarte Budget; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Query/Cache/Batching und Metrik minimal optimieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Optimierung ohne Semantikaenderung isolieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Benchmark-, Explain-, Resilience- und SLO-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-169 — Beratungsfall und Beobachtung: Migration und Kompatibilitaet

**Nutzen:** Im Bereich Beratungsfall und Beobachtung Bestandsdaten und bestehende Konsumenten wechseln ohne Bruch; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-CONS-001. **Abhaengig von:** FEED-WP-160, FEED-WP-168. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Beratungsanlass und Entscheidung bilden eine Akte; Upgrade, Backfill, Dual-Read/Switch und Forward-Fix sind geprueft. Nachweis ueber FEED-T169 und FEED-T036.

**Red:** Migrations-/Aequivalenztest zeigt Drift zum Bestand; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** additive Migration und idempotenten Backfill liefern; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Kompatibilitaetsadapter befristen und dokumentieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Upgrade-, Backfill-, Golden- und API-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-170 — Beratungsfall und Beobachtung: Release-Journey und Betriebsabnahme

**Nutzen:** Im Bereich Beratungsfall und Beobachtung die Capability ist fuer den Pilotbetrieb abnahmefaehig; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-CONS-001. **Abhaengig von:** FEED-WP-160, FEED-WP-169. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Beratungsanlass und Entscheidung bilden eine Akte; E2E-Journey, Security, A11y, Runbook, Flag und Rollback sind gruen. Nachweis ueber FEED-T170 und FEED-T037.

**Red:** Release-Journey scheitert am letzten offenen Nutzerergebnis; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** fehlende vertikale Luecke ohne Scope-Ausweitung schliessen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** tote Adapter/Flags entfernen und Doku synchronisieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** vollstaendige Capability-, Playwright- und Release-Gates sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.
