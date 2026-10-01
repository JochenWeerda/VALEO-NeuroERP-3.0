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

## Historischer Schutz und Nachzug

Die bisher durch den DQ-Fehler praktisch blockierte Option auto_match las
alle zahlbaren offenen Posten ohne Mandantenfilter, setzte beim blossen
Referenztreffer auch Teilzahlungen auf null und speicherte keinen
Bankzeilenstatus. Nach Behebung der DQ waere dieser Pfad erreichbar geworden.
Der manuelle Meilenstein sperrte auto_match vor jedem Datenbankzugriff mit
HTTP 501. Der Nachzug BANK-PAYMENT-MATCHING-INTEGRITY-20261001 ersetzt diese
Sperre durch den gemeinsamen sicheren Matching-Vertrag; aktuelle Abnahme:
[Bank- und Zahlungsabgleich](bank-payment-matching-integrity-20261001.md).

Die atomare manuelle Importfunktion ist abgeschlossen. Der damalige
Auto-Abgleich-Gap umfasste: tenantgebundene Kandidaten,
Betrag/Vorzeichen/Waehrung, Teilzahlungen, Mehrdeutigkeiten, persistente
Zuordnung, Sperren und Wiederholungsschutz sind gemeinsam abzusichern.
Dieser urspruengliche Slice allein nahm Tenant-/Matchingvertraege nicht
vollstaendig ab; ihr aktueller Stand und verbleibende Parser-/Fachgaps
stehen im verlinkten Nachzug. GitHub-CI und Integration bleiben externe Nachweise.
