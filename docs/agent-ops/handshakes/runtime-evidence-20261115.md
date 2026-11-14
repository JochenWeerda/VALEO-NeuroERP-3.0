---
title: Runtime-Nachweise und kanonische CI
status: aktiv
last_reviewed: 2026-11-15
owner: Codex
---

# Uebergabe

Branch codex/runtime-evidence-20261114, Basis ce82644ae (main/develop).
CI/CD und Sicherheitsnachlauf der Basis waren erfolgreich; einige weitere
Nachlaeufe waren abgebrochen. Kein blinder Wiederholungslauf gestartet.

Neu: enger Datenrechte-Planmodus mit Katalog-Nachbedingung und Rollback;
82 lokale Consumer-/Rechte-/Improvement-Vertraege gruen. Drei echte
PostgreSQL-Teilumwandlungsfaelle auf bestehendem valeo_probe ohne Skip gruen;
keine permanenten Grants/Testdaten/Schemaaenderungen. Dauerhafte breite ACL-
Vergabe war durch automatische Freigabepruefung abgelehnt, nicht ausgefuehrt;
die freigegebene Rollback-Alternative ist geprueft. Lokale Probe-Revision
psm_register_entfernt_20261104. Teilmengenvorschau, vier aus zehn, Rest sechs,
Replay, Gegenproben und RLS auch gegen gefaelschten Servicefilter belegt.

CI/CD konsumiert kuenftig den exakt korrelierten ganzen erfolgreichen
Quality-Gate-Lauf statt eine zweite Vollsuite/DB auszufuehren. Event/PR/Base/
Head/Checkout, echte Backend-Jobattempt und Coveragehash werden geprueft.
Parallele PRs desselben Branches sind durch deterministische Laufnamen getrennt.
Strict-Datenbankmodus und Inventory-Seed bleiben im kanonischen Produzenten.
Ein echter GitHub-Nachlauf muss diesen neuen Vertrag erst abnehmen.

Offen: Browser-/OIDC-Gesamtkette, weitere Matrixaktionen und verbleibende
Runtime46-Fachfunktionen; keine Gesamtfreigabe. QA: ci-kanonische-backendsuite-
20261114.md, probe-datenrechte-20261114.md, docflow-teilmengen-sql-20261115.md.
