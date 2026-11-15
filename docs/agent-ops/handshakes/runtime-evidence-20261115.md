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

Nachlauf: Strict-DB-Profil aus realem Erstfehler korrigiert (explizite gleiche TEST_DATABASE_URL, ein bestehender valeo_probe-Service, kanonische Rollen). Neue Herstellerbefunde gezielt gepatcht; separater BFF-Audit schliesst verschachtelte Manifestluecke. 42 lokale Sicherheits-/Consumervertraege gruen. Details security-langgraph-zod-20261115.md; GitHub-Nachlauf auf integriertem Folgecommit erforderlich, keine Gesamtfreigabe.

## Nachfolgeslices: O2C und lokaler Backendstart

Auf codex/o2c-real-contract-20261115 (Basis e8a2e92d5) sind zwei echte O2C-HTTP-Vertraege vorbereitet: signierte Fachrolle, eigener kanonisch angelegter/readback-gepruefter Kunde, serverseitiger Maskenkontext, Auftrag und Teil-Lieferschein mit Replay-/Versions-/Mengen-/Rollen-/Mandantenspoofing-Gegenproben. Scoped TypeScript und Collection (zwei Tests) gruen; echter HTTP-/CI-Lauf steht aus, keine Matrix-Statusanhebung.

Der bestehende lokale Backendcontainer war in einem Neustartzyklus, weil zwei bereits kanonisch migrierte optionale Lagerreferenzen fehlten. Ein enges Operationsskript mit 53 Unitfaellen, echtem vollstaendigem Rollback, Schema-Sicherung und Hashvergleich stellt diese ohne Rechte-/RLS-Aenderung wieder her. Danach wurden exakt sieben gesicherte, abhaengigkeitsgepruefte Alt-Testzeilen entfernt (zwei verwaiste Chargen, zwei mandantenwidrige Testbestellungen und drei Positionen). Alle anderen Bestellzeilen blieben unveraendert. Keine erfundenen Eltern/Mandanten oder Gate-Lockerungen.

Regulaeres Upgrade erreicht ruestlisten_tabelle_20261103 im noch eingebundenen alten Hauptbaum: 618 Tabellen mit RLS, beide validierten Mandanten-Verbund-FKs, Backend als valeo_app ohne privilegierte Rollenflags. Container gesund, /health HTTP200 und unauthentifiziertes DocFlow HTTP401; erneuter Operationsplan leer. Dies ist keine Bereitstellung des aktuellen Artifact-Quellstands oder positive Browser-/OIDC-Abnahme. Vollstaendige lokale Sicherungsinhalte bleiben ignoriert und werden nicht gepusht. QA inventory-reference-drift-20261115.md und action-matrix-o2c-http-20261115.md.
