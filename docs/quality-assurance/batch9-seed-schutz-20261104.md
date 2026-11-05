---
title: Batch 9 Seed-Loeschschutz 2026-11-04
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-05
version: 1.1.0
---

# Batch 9: Seed-Loeschung und Tabellenentfernung

## Aktuelle Nutzerentscheidung fuer ausgemusterte Tabellen

Vorhandene Zeilen in `ops_disposition` und `ops_zertifikate_api` sind nach der
Nutzerentscheidung Testdaten. Beide ausgemusterten Tabellen duerfen nach Abbau
der Verbraucher auch mit diesen Zeilen entfernt werden. Die Dispositionsseiten
verwenden den Bestellvorschlag; der zweite Zertifikatsweg wurde entfernt. Die
Quelltextsuche in `app`, `services` und `packages` fand keine aktiven
Tabellenkonsumenten; `tests/test_compliance_register_batch9.py` prueft den
entfernten API-Weg und die Seitenverweise. Existenzpruefung und exklusiver Lock
bleiben erhalten; `DROP TABLE` erfolgt ohne CASCADE. Dabei werden die Daten der
beiden Tabellen unwiderruflich entfernt. Die fruehere Abbruchregel fuer
abweichende, NULL-haltige oder doppelte Zeilen gilt fuer diese Tabellen nicht mehr.

## Weiter genutzte Register

Die acht weiter genutzten Register behalten ihre vollstaendigen Seed-Signaturen:
Sie vergleichen alle im Git-Vorgaenger `a1f6fc19b^` gesetzten Geschaeftsfelder.
Eine bereits vorhandene Mandantenspalte verhindert jede Seed-Loeschung dieser
Tabelle. Im Zertifikatsregister bleibt der Testrest QS-2025-9999 mangels
eindeutiger Herkunft erhalten. Verbleibende Zeilen folgen der bestehenden
Altbestand-Mandantenregel.

IDs und Erstellungszeitpunkte wurden beim Seed zufaellig beziehungsweise zur
Laufzeit erzeugt; eine Herkunft laesst sich daraus nicht deterministisch
rekonstruieren. Eine identische Fachzeile ist deshalb technisch nicht von einer
Seed-Zeile unterscheidbar.

## Pruefstand und historischer Nachweis

Die bisherige PostgreSQL-Gegenprobe (1 passed, Revision unveraendert) pruefte
historisch die damaligen Register-Signaturen und die inzwischen ueberholte
Abbruchregel fuer den Tabellen-Drop. Sie ist kein Nachweis fuer die aktuelle
Entfernungsregel. Auch die frueheren Signaturen der drei Dispositions-Seeds
werden fuer die Entfernung der ausgemusterten Tabelle nicht mehr verwendet.

Der aktualisierte TEMP-Test prueft Drop mit Zeilen, fehlende Tabelle,
Abhaengigkeit ohne CASCADE und Rollback; **dieser aktualisierte Test steht noch
aus**, bis das Prueffenster frei ist. Er prueft je weiter genutztem Register
einen urspruenglichen Seed, nicht alle einzelnen Varianten oder eine
vollstaendige Migration. Keine Migration wurde hier gestempelt.
