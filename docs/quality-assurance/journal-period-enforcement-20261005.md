---
title: Pflichtperiodenpruefung und koordinierter Abschluss
type: reference
audience: [qa, agent, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-10-05
version: 1.0.0
---

# Periodenpflicht im Journal

## Umsetzung

FinanceTransactionService.Create leitet YYYY-MM aus dem Buchungsdatum ab;
ein explizites period muss dazu passen. Post verwendet das gespeicherte
Buchungsdatum. Reverse prueft die neue Stornoperiode; eine alte abgeschlossene
Ursprungsperiode wird dadurch nicht wiedereroeffnet. Fehlendes period an
der direkten Prueffunktion ist ein Fehler, keine Freigabe. Die bestehende
Semantik bleibt: OPEN/ADJUSTING buchbar, CLOSED/unbekannt sperrt, keine Zeile
gilt als noch nicht abgeschlossene Periode. Eine vorhandene NULL-Zeile wird
als unbekannt abgewiesen, nicht mit fehlender Zeile verwechselt.

Der gemeinsame Helper nimmt eine Shared-Transaktionssperre je Tenant/Periode,
Close/Reopen und Perioden-API Create/Update eine Exclusive-Sperre desselben
Schluessels. PostgreSQL-Advisory-Lock gilt auch ohne vorhandene Zeile; diese
wird sonst nicht durch eine reine Zeilensperre geschuetzt. FOR SHARE schuetzt
die vorhandene Statuszeile auch gegen direkte Updates. READ COMMITTED ist
Pflicht, damit eine nach dem Warten neu angelegte Zeile nicht aus einem
alten Repeatable-Read-Snapshot verschwindet. Alle Sperren bleiben bis zum
Commit/Rollback bestehen, einschliesslich aeusserem Journal-Transaktionsmodus.

## Nachweise

371 Journal-/Periodenregressionen bestanden in 15.62 Sekunden sowie 25
bestehende Periodenstatusvertraege in 2.28 Sekunden. Neue 29 Vertraege,
davon 19 echte PostgreSQL-Faelle. Anlage/Post/Storno ohne optionales period
unter OPEN/ADJUSTING/CLOSED und fehlender Zeile; abweichendes Buchungsdatum,
Fremdtenant, malformed/missing Periode, widerspruechliches period, NULL/
unbekannter Status, unzulaessige Isolation und echter privater Schemafehler.

Vier echte Konkurrenzbelege mit pg_locks: Wartende Buchung liest nach
Abschluss CLOSED und schreibt nicht; erster Abschluss einer fehlenden
Periode wartet auf laufendes Journal; Perioden-API Create und Update warten
auf laufenden Journal-Reader. Der erste Abschluss verwendet den echten
FinancePeriodService; lediglich OP-Abschlussmetriken sind im privaten
Schema als leer isoliert. API-Faelle verwenden echte Handler und eigene
Tabellen, nur nachgelagerter Audit-Helper ist isoliert. Keine komplette
Audit-/API-Atomizitaetsbehauptung.

Bestehende Unit-Vertraege fuer Betrag/Hash/Lifecycle isolieren den neuen
Periodenguard explizit; er wird in dieser eigenen PostgreSQL-Suite real
geprueft. Alte check_period_open(None)-Freigabe durch Abweisung ersetzt.
Der alte Statusvertragstest mit ALTER der gemeinsamen Tabelle wurde
entfernt; derselbe Fail-Closed-Vertrag ist jetzt in der kleinen privaten
Tabellenfixture pruefbar, mit transaktionellem Rollback des eigenen DDL.
Keine Abnahme laesst eine gemeinsame Tabelle zeitweise unlesbar werden.

Vor Tests: vorhandener valeo_probe Revision wiegung_kanonisch_20261005.
Wiederverwendete kleine eigene Tabellenfixtures plus bestehende eigene
Status-Testzeilen mit gezieltem Cleanup. Keine neue Datenbank/Dockerinstanz,
gemeinsame Migration oder Reset. Logs: artifacts/journal-period-tests.log
und artifacts/journal-period-vocabulary.log. Neue Pythonanteile Ruff-sauber.
Ein bestehender F401 in finance_period_service.py und vier bestehende
API-Importbefunde bleiben ausserhalb der Sperrhunks; keine globale Lint-
oder CI-Gruenbehauptung. Eigene Whitespace-Pruefung sauber.

## Handoff

Claim 1238e843a. Minor-Bugfix im bestehenden Perioden-/Journalvertrag,
keine neue API/DTO/Spalte/Domain-Grenze. Andere rohe Journal-/OP-Schreiber
verwenden weiterhin teils ungesperrte Guards oder separate Commitwege;
sie brauchen dieselbe Integration. Die Abschlussreife umfasst bisher OP-
Metriken, keine komplette Journal/OP-Consumer-Atomizitaet. API-Fehlermapping,
Audit/Anchor-Atomizitaet, Schema/Hash/NULL-Waehrung und Cancel-Grund offen.
Keine globale Journal-/GoBD-Abnahme oder Gesamtprojektabschluss. Fremde
Logistik/Godfile- und UI-Arbeit bleibt unangetastet, keine Baseline angehoben.
