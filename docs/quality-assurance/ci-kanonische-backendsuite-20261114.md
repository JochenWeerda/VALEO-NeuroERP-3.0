---
title: Kanonische Backend-Vollsuite und CI-Evidenz
type: qa
audience: [entwickler, qa, sicherheit]
owner: Codex
status: active
last_reviewed: 2026-11-14
---

# Kanonische Backend-Vollsuite und CI-Evidenz

Slice `CI-KANONISCHE-BACKENDSUITE-20261114`: Die Vollsuite laeuft einmal im
Quality-Gate-Backend. Dieser Job uebernimmt den strikten Datenbankmodus und
Inventory-Seed der bisherigen CI/CD-Suite. Migrations-, RLS-, Rollen-, Coverage-,
KI- und Sonar-Gates bleiben bestehen. CI/CD behaelt Test-Jobnamen, Mapping,
Codecov, Bandit und Safety sowie die Build-Abhaengigkeit, aber keine zweite
Postgres-Instanz oder Backend-Vollsuite.

Die Wiederverwendung verlangt einen erfolgreichen gesamten Quality-Gate-Lauf
mit demselben Repository, Event, Quellbranch und Head. Ein deterministischer
GitHub-Laufname bindet PR-Nummer, Head- und Basis-SHA beziehungsweise Push-Branch
und SHA schon bei der Kandidatenauswahl; parallele PRs mit demselben Head
koennen einander weder verdraengen noch einen fehlgeschlagenen Lauf verdecken.
Bei Pull Requests werden
PR-Nummer, Ereignisaktion, Absender und Basis-/Head-Kontext aus dem im Backend-Job erzeugten
`backend-context.json` gebunden; dessen Checkout-SHA ist der synthetische
Merge-Commit. Der vorhandene Coverage-Beleg prueft weiterhin SHA und Dateihash.
Die GitHub-API lieferte beim echten PR-134-Lauf 43599267829 ein leeres
`pull_requests`-Array; der Kontext wird deshalb nicht daraus erraten.

Nur der juengste passende Lauf innerhalb fuenf Minuten des ausloesenden
CI/CD-Laufs wird akzeptiert; bei Push werden auch Absender und vorheriger SHA
gebunden. Die Zeitgrenze ist bewusst fail-closed: stark verzoegerte oder
uneindeutige Ausloesung kann einen manuellen Nachlauf erfordern. Fehlende oder unvollstaendige Metadaten,
abweichender Kontext, fehlgeschlagene/abgebrochene Jobs oder Quality Gates,
abgelaufene Artefakte und Timeout blockieren. Ein reiner Sonar-Rerun darf
den erfolgreich erhaltenen Backend-Versuch wiederverwenden; bei Backend-Rerun
muss der Beleg dessen neuer Versuch sein. Artefakt-Overwrite ist ausschliesslich
auf den Namen `backend-coverage-xml` beschraenkt. API-Anfragen verwenden nur
`actions:read` und `contents:read`; signierte Download-URLs erhalten keinen
API-Token. Nur drei bekannte ZIP-Dateinamen und begrenzte Groessen sind erlaubt.

49 lokale No-DB-Vertraege bestanden, darunter falsche PR-/Repository-/Event-/
SHA-Kontexte, fehlender oder manipulierter Beleg, ZIP-Pfadversuch, fremder
Downloadhost, Fehler/Abbruch, Timeout und beide Wiederholungsarten. Die
GitHub-API-Struktur wurde am vorhandenen PR-134-Lauf lesend geprueft. Keine
neuen CI-Laeufe, Datenbanken oder Container wurden hier gestartet. Ein realer
GitHub-Nachlauf bleibt fuer Eventzuordnung, Artefaktdownload, Wartezeit und
gesamte Workflow-Integration erforderlich; bei uneindeutiger Herkunft bleibt
CI/CD rot statt auf aeltere Evidenz zurueckzufallen.


## Lead-Nachlauf 15.11.2026

Nach Review ergaenzt: ZIP-Gesamtgroesse begrenzt, Kontext-/Siegeldateien auf
64KiB begrenzt; Pollintervall 30 Sekunden zur API-Entlastung. Direkte Grant-
Factory-Aufrufe weisen unbekannte Datenrollen zurueck. Gemeinsamer lokaler
Nachlauf: 82 Consumer-/Rechte-/bestehende Improvement-Vertraege bestanden
(5,34 Sekunden); Docs-Governance gruen. Diese Laeufe werden nicht zu den
ueberlappenden Agentenzahlen addiert. Der echte GitHub-Produzent-/Consumer-
Nachweis auf dem neuen Commit ist separat erforderlich.
