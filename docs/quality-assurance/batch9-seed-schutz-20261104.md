---
title: Batch 9 Seed-Loeschschutz 2026-11-04
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-04
version: 1.0.0
---

# Batch 9: Seed-Loeschung und Tabellenentfernung

Die Signaturen der acht verbleibenden Register und der drei Dispositions-Seeds
vergleichen alle im Git-Vorgaenger `a1f6fc19b^` gesetzten Geschaeftsfelder.
IDs und Erstellungszeitpunkte wurden beim Seed zufaellig beziehungsweise zur
Laufzeit erzeugt; eine Herkunft laesst sich daraus nicht deterministisch
rekonstruieren. Eine identische Fachzeile ist deshalb technisch nicht von einer
Seed-Zeile unterscheidbar. Bereits vorhandene Mandantenspalte verhindert jede
Seed-Loeschung dieser Tabelle. Im weiter genutzten Zertifikatsregister bleibt der Testrest QS-2025-9999
mangels eindeutiger Herkunft erhalten. Verbleibende Zeilen folgen der
bestehenden Altbestand-Mandantenregel.

## Neue Nutzerentscheidung zu ausgemusterten Tabellen

Die Nutzerentscheidung vom 04.11.2026 ersetzt die fruehere Abbruchregel fuer
`ops_disposition` und `ops_zertifikate_api`: vorhandene Zeilen dieser beiden
Tabellen sind Testdaten und die ausgemusterten Tabellen duerfen nach Abbau der
Verbraucher entfernt werden. Die Dispositionsseiten verwenden den
Bestellvorschlag; der zweite Zertifikatsweg wurde entfernt. Die Quelltextsuche
in `app`, `services` und `packages` findet keine aktiven Tabellenkonsumenten;
`tests/test_compliance_register_batch9.py` prueft den entfernten API-Weg und
die Seitenverweise. Existenzpruefung und exklusiver Lock bleiben erhalten;
`DROP TABLE` erfolgt ohne CASCADE, Daten der beiden Tabellen werden dabei
unwiderruflich entfernt. Die acht weiter genutzten Register behalten ihre
vollstaendigen Signaturen und den Schutz vorhandener Mandantenspalten.

Die bisherige PostgreSQL-Gegenprobe (1 passed, Revision unveraendert) belegt den
alten Stand der Register-Signaturen. Der aktualisierte TEMP-Test prueft zusaetzlich
Drop mit Zeilen, fehlende Tabelle, Abhaengigkeit ohne CASCADE und Rollback;
**dieser aktualisierte Test steht noch aus**, bis das Prueffenster frei ist.
Er prueft je Register einen urspruenglichen Seed, nicht alle einzelnen Varianten
oder eine vollstaendige Migration. Keine Migration wurde hier gestempelt.
