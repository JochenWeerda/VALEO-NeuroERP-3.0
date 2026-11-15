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

PR135-Erstlauf: Der separate Strict-DB-Job stellte nur DATABASE_URL bereit; die drei neuen verpflichtenden PostgreSQL-Vertraege lehnten die fehlende explizite TEST_DATABASE_URL korrekt ab. Korrektur: derselbe einzelne Job-Service heisst valeo_probe, beide URLs stimmen ueberein, kanonische Datenrollen werden nach init_db eingerichtet. Der lokale Profilvertrag besteht; echter CI-Nachlauf bleibt erforderlich.

## GitHub-Abnahme auf e8a2e92d5

PR 135 besteht mit allen 68 Checks. Die Nachweise beziehen sich auf den
geprueften PR-Kopf `e8a2e92d5`, nicht pauschal auf spaetere Commits.

| Nachweis | Ergebnis |
| --- | --- |
| Quality Gate 43653854329 | Erfolgreich, einschliesslich kritischer Coverage und Image-Smoke |
| Kanonische Backend-Vollsuite | 28.444 bestanden, 72 uebersprungen, einer abgewaehlt; 2.009,95 Sekunden |
| Gesamtdeckung | 76,10 Prozent; geforderte Schwelle 60 Prozent |
| Sonar-Job 132638443225 | Erfolgreich mit `sonar.qualitygate.wait=true` |
| CI/CD 43653854364 | Erfolgreich; echte Evidenzuebernahme ohne zweite Backend-Vollsuite oder eigene PostgreSQL-Instanz |
| Strict-DB 43653854377 | 701 bestanden, vier uebersprungen, 27.812 abgewaehlt; 145,68 Sekunden |

Der Consumer bestaetigt am 15.11.2026 um 00:20:13 UTC ausdruecklich:
`Canonical backend evidence verified for this checkout.` Ueberlappende
Testzahlen werden nicht addiert.

PR 135 wurde am 15.11.2026 um 00:22:20 UTC nach `main` integriert:
`e9ae5cab651d293c62e7a7b182dae4547408b8bc`. Nach Abstammungspruefung wurde
`develop` ohne Force auf denselben Commit vorgezogen. Alle Checks waren vor
Integration gruen. Der normale Merge war wegen der vorgeschriebenen externen
Review gesperrt; fuer diese Reviewausnahme wurden die vorhandenen
Administratorrechte genutzt. Keine Testanforderung oder Branchregel wurde
geaendert. Ein Nachlauf der Merge-SHA ist vom belegten PR-Lauf zu unterscheiden.
