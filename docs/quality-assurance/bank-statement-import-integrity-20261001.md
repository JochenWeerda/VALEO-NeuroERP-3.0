---
title: Atomarer manueller Kontoauszugsimport
type: reference
audience: [agent, entwickler, qa, betrieb]
owner: Codex
status: aktiv
last_reviewed: 2026-10-01
---

# Kontoauszugsimport

Claims c19646386 und 3c1a0304f. Die DQ-Pruefung baute fuer die aktuelle
Zeile ein zweites Dictionary, obwohl die Duplikatregel die aktuelle Zeile
per Objektidentitaet aus dem Kontext ausschliesst. Damit galten gueltige
CSV-Zeilen sowohl im Parser als auch im Import als eigene Duplikate.
Beide Pruefungen verwenden jetzt das jeweilige Kontextobjekt.

Der manuelle Import schreibt Kopf und alle Zeilen in einer Transaktion.
SQL- und Commitfehler fuehren zu Rollback und einer generischen HTTP-500-
Antwort, ohne rohe Datenbankdetails. Die Antwort wird vor dem Commit
validiert. Gespeicherte Waehrung und Antwort verwenden den Importwert;
Betragspraezision und Waehrung werden vor DB-Zugriff geprueft. UUIDv7 ersetzt
die kollisionsanfaellige ID aus Zeitstempel und Kontopraefix.

## Verifikation

12 neue echte PostgreSQL-/HTTP-Vertraege und sechs bestehende DQ-Vertraege:
**18 bestanden**, auf dem vorhandenen valeo_probe ohne neue DB, Dockerinstanz,
Migration oder Reset. Eigene Importdaten werden nach jedem Test entfernt.
Log: artifacts/bank-statement-integrity-tests.log.
Ein zusaetzlicher Lauf ohne zentrale conftest-Fixtures ergab 17 bestanden
und einen HTTP-401 im bestehenden Bulk-HTTP-Test, dessen Auth-Testfixture
fehlte. Massgeblich ist der regulaere Lauf mit allen 18 bestandenen Tests;
die Authentisierung wurde nicht veraendert.

Nachgewiesen: gueltiger CSV-Import, Waehrung und Bestandszaehler, echte
PostgreSQL-Fehler bei Kopf/zweiter Zeile/Commit, reale Laengenbedingung,
kein Teilbestand nach Fehlern, echte Duplikate weiter abgewiesen,
Waehrungs-/Praezisionsfehler vor Writes, negative Bankbetraege erhalten,
unterschiedliche persistente Import-IDs und Rollback bei Antwortfehlern.
Ruff fuer neue Tests und Diff-Whitespacepruefung gruen.

Der bestehende Dead-Transaction-Scanner findet im bisherigen Import zwei
Fundstellen, nach Reparatur keine. Die projektweite Zahl ist wegen paralleler
Fremdarbeit eine Momentaufnahme, keine vollstaendige Gap-Schliessung.
Die bestehende Schwelle wird nicht angehoben.

## Automatischer Abgleich bleibt offen

Die bisher durch den DQ-Fehler praktisch blockierte Option auto_match las
alle zahlbaren offenen Posten ohne Mandantenfilter, setzte beim blossen
Referenztreffer auch Teilzahlungen auf null und speicherte keinen
Bankzeilenstatus. Nach Behebung der DQ waere dieser Pfad erreichbar geworden.
Deshalb wird auto_match jetzt vor jedem Datenbankzugriff mit HTTP 501
abgewiesen. Ein Vertrag sichert ab, dass dabei keine Importdaten entstehen.

Die atomare manuelle Importfunktion ist abgeschlossen. Fachlicher
Auto-Abgleich bleibt ein eigener Gap: tenantgebundene Kandidaten,
Betrag/Vorzeichen/Waehrung, Teilzahlungen, Mehrdeutigkeiten, persistente
Zuordnung, Sperren und Wiederholungsschutz sind gemeinsam abzusichern.
Authentisierung/Tenant-Query-Vertraege, CAMT-/MT940-Parserdetails und die
separate Zahlungs-Matching-API sind durch diesen Slice nicht vollstaendig
abgenommen. GitHub-CI und Integration bleiben externe Nachweise.
