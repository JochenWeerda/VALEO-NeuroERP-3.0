---
title: "Arbeitspakete 231–240 — KI-Agenten und Governance"
type: plan
audience: [produkt, architektur, entwickler, qa, agent]
owner: domain/agrar
status: geplant
last_reviewed: 2026-07-15
version: 1.0.0
generated_by: scripts/generate_feeding_work_packages.py
---

# KI-Agenten und Governance

Requirements: FEED-UI-003, FEED-NFR-SEC. Paketstatus und TDD-Laufnachweis werden bei Claim im Workboard/Slice gefuehrt; dieses Dokument bleibt der stabile Liefervertrag.

## FEED-WP-231 — KI-Agenten und Governance: Vertrag und erste Journey

**Nutzen:** Im Bereich KI-Agenten und Governance ein kleinster realer Nutzerfall funktioniert Ende-zu-Ende; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-UI-003, FEED-NFR-SEC. **Abhaengig von:** FEED-WP-200. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Agenten unterstuetzen erklaerbar innerhalb von Policies und Human Gates; Happy Path mit persistiertem Ergebnis und sichtbarer Herkunft. Nachweis ueber FEED-T031 und FEED-T098.

**Red:** Contract-/Domain-Test fuer den ersten Nutzerfall schlaegt fehl; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** kleinsten Domain-, API- und Meridian-Pfad implementieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Begriffe und Grenzen am Domainmodell ausrichten, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** fokussierte Domain-, API- und Screen-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-232 — KI-Agenten und Governance: Grenzen und Validierung

**Nutzen:** Im Bereich KI-Agenten und Governance ungueltige oder unvollstaendige Eingaben werden sicher erklaert; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-UI-003, FEED-NFR-SEC. **Abhaengig von:** FEED-WP-200, FEED-WP-231. **Aufwand:** S (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Agenten unterstuetzen erklaerbar innerhalb von Policies und Human Gates; Grenz-, Missing- und Conflict-Faelle liefern stabile Fehler. Nachweis ueber FEED-T032 und FEED-T099.

**Red:** Boundary-/Property-Test reproduziert die ungeschuetzte Grenze; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Validierung und ProblemDetails minimal ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Validierungsregeln zentralisieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Happy Path plus Boundary-/Property-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-233 — KI-Agenten und Governance: Tenant und Berechtigung

**Nutzen:** Im Bereich KI-Agenten und Governance nur berechtigte Personen sehen und aendern den fachlichen Scope; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-UI-003, FEED-NFR-SEC. **Abhaengig von:** FEED-WP-200, FEED-WP-232. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Agenten unterstuetzen erklaerbar innerhalb von Policies und Human Gates; Tenant, Rolle und Business-Grant werden serverseitig erzwungen. Nachweis ueber FEED-T033 und FEED-T100.

**Red:** negativer Isolation-/403-Test zeigt den Zugriff; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Policy am Application-Service/Endpoint schliessen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Policy-Duplikate in zentralen Guard ueberfuehren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Authz-, Enumeration- und Tenant-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-234 — KI-Agenten und Governance: Version und Audit

**Nutzen:** Im Bereich KI-Agenten und Governance Entscheidungen bleiben zeitlich und fachlich nachvollziehbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-UI-003, FEED-NFR-SEC. **Abhaengig von:** FEED-WP-200, FEED-WP-233. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Agenten unterstuetzen erklaerbar innerhalb von Policies und Human Gates; Aenderung erzeugt Version/Audit statt historischen Stand zu ueberschreiben. Nachweis ueber FEED-T034 und FEED-T101.

**Red:** Workflow-/Repository-Test zeigt verlorene Historie; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Versionierung und Auditereignis minimal persistieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Event- und Auditnamen vereinheitlichen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Lifecycle-, Migration- und Audit-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-235 — KI-Agenten und Governance: Fehler und Wiederaufnahme

**Nutzen:** Im Bereich KI-Agenten und Governance Nutzer koennen nach Konflikt oder Teilausfall sicher fortsetzen; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-UI-003, FEED-NFR-SEC. **Abhaengig von:** FEED-WP-200, FEED-WP-234. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Agenten unterstuetzen erklaerbar innerhalb von Policies und Human Gates; Retry ist idempotent und Fehlerzustand handlungsorientiert. Nachweis ueber FEED-T035 und FEED-T102.

**Red:** Idempotenz-/Recovery-Test erzeugt Doppelwirkung oder Sackgasse; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Idempotency Key, Journal oder Resume-Punkt ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Fehlerklassen und Kompensation schaerfen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Failure-, Retry- und Concurrency-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-236 — KI-Agenten und Governance: Meridian UX und Accessibility

**Nutzen:** Im Bereich KI-Agenten und Governance die Aufgabe ist auf Desktop und mobil zugaenglich bedienbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-UI-003, FEED-NFR-SEC. **Abhaengig von:** FEED-WP-200, FEED-WP-235. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Agenten unterstuetzen erklaerbar innerhalb von Policies und Human Gates; native ScreenDefinition, Tastatur, Focus, Empty/Error/Loading und WCAG sind abgedeckt. Nachweis ueber FEED-T036 und FEED-T103.

**Red:** Component-/axe-Test zeigt fehlenden Bedienvertrag; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** ScreenDefinition/RenderPlan und kleinstes Domain-Overlay ergaenzen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** freie UI-Logik in Runtime-Vertrag zurueckfuehren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Component-, axe-, Keyboard- und Route-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-237 — KI-Agenten und Governance: Events und Integration

**Nutzen:** Im Bereich KI-Agenten und Governance nachgelagerte Prozesse erhalten ein stabiles, nachweisbares Signal; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-UI-003, FEED-NFR-SEC. **Abhaengig von:** FEED-WP-200, FEED-WP-236. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Agenten unterstuetzen erklaerbar innerhalb von Policies und Human Gates; Outbox/Event oder neutraler Port ist schemafest und genau-einmal-wirksam. Nachweis ueber FEED-T037 und FEED-T104.

**Red:** Contract-/Replay-Test zeigt Drift oder Doppelwirkung; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Event/Port plus Idempotenz minimal implementieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Mapping und Provideradapter trennen, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Schema-, Replay-, Outbox- und Connector-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-238 — KI-Agenten und Governance: Performance und Beobachtbarkeit

**Nutzen:** Im Bereich KI-Agenten und Governance der Nutzerfall bleibt unter realer Last steuerbar; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-UI-003, FEED-NFR-SEC. **Abhaengig von:** FEED-WP-200, FEED-WP-237. **Aufwand:** M (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Agenten unterstuetzen erklaerbar innerhalb von Policies und Human Gates; Budget, Metriken, Traces und fachliche Alarmgrenzen sind nachgewiesen. Nachweis ueber FEED-T038 und FEED-T105.

**Red:** Benchmark verletzt bewusst das vereinbarte Budget; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** Query/Cache/Batching und Metrik minimal optimieren; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Optimierung ohne Semantikaenderung isolieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Benchmark-, Explain-, Resilience- und SLO-Suite sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-239 — KI-Agenten und Governance: Migration und Kompatibilitaet

**Nutzen:** Im Bereich KI-Agenten und Governance Bestandsdaten und bestehende Konsumenten wechseln ohne Bruch; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-UI-003, FEED-NFR-SEC. **Abhaengig von:** FEED-WP-200, FEED-WP-238. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Agenten unterstuetzen erklaerbar innerhalb von Policies und Human Gates; Upgrade, Backfill, Dual-Read/Switch und Forward-Fix sind geprueft. Nachweis ueber FEED-T039 und FEED-T106.

**Red:** Migrations-/Aequivalenztest zeigt Drift zum Bestand; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** additive Migration und idempotenten Backfill liefern; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** Kompatibilitaetsadapter befristen und dokumentieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** Upgrade-, Backfill-, Golden- und API-Regression sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.

## FEED-WP-240 — KI-Agenten und Governance: Release-Journey und Betriebsabnahme

**Nutzen:** Im Bereich KI-Agenten und Governance die Capability ist fuer den Pilotbetrieb abnahmefaehig; das Paket liefert bewusst einen vertikalen Pfad durch Fachlogik, Vertrag, Persistenz und Bedienung, soweit diese Schichten betroffen sind.

**Requirements:** FEED-UI-003, FEED-NFR-SEC. **Abhaengig von:** FEED-WP-200, FEED-WP-239. **Aufwand:** L (S=1–2, M=3–5, L=6–10 Personentage; Schaetzung vor Refinement).

**Akzeptanz:** Agenten unterstuetzen erklaerbar innerhalb von Policies und Human Gates; E2E-Journey, Security, A11y, Runbook, Flag und Rollback sind gruen. Nachweis ueber FEED-T040 und FEED-T107.

**Red:** Release-Journey scheitert am letzten offenen Nutzerergebnis; Fehler, Befehl und Testname werden im Slice als TDD-Evidenz gespeichert.

**Green:** fehlende vertikale Luecke ohne Scope-Ausweitung schliessen; keine spekulative Nebenfunktion und kein produktiver Mockpfad.

**Refactor:** tote Adapter/Flags entfernen und Doku synchronisieren, waehrend neue und relevante bestehende Tests gruen bleiben.

**Regression:** vollstaendige Capability-, Playwright- und Release-Gates sowie Markdown-/Traceability-Drift fuer betroffene Kapitel.

**Definition of Done:** Akzeptanz gruen; Tenant/RBAC/Audit geprueft; typisierte Vertraege; Meridian fuer neue UI; Migration/Observability soweit betroffen; Traceability, Workboard und Handbuch aktualisiert; offene externe Gates explizit und nicht durch Mocks ersetzt.
