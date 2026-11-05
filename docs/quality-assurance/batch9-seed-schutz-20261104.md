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
Seed-Loeschung dieser Tabelle. Testreste ART-TEST-001 und QS-2025-9999 werden
mangels eindeutiger Herkunft nicht geloescht. Verbleibende Zeilen folgen der
bestehenden Altbestand-Mandantenregel.

Bei zu entfernenden Tabellen blockiert jede nicht sicher erkannte Zeile den
Drop; SQL `IS NOT TRUE` erfasst auch NULL. Gleiche Dispositions-Signaturen
mit unterschiedlichen IDs blockieren ebenfalls. Eine leere zweite Tabelle
kann entfernt werden, jede Zeile darin blockiert den Drop.

Nachweis: `tests/test_batch9_seed_schutz_pg.py`, PostgreSQL `valeo_probe`,
Rolle `valeo_agent`, ausschliesslich TEMP-Tabellen in zurueckgerollter
Transaktion: **1 passed** (5,50 s). Je Register ein urspruenglicher Seed,
jedes Geschaeftsfeld einzeln geaendert und NULL; ferner vorhandener Mandant,
abweichender Bestand, NULL, Testrest, doppelte Signatur, sicherer Drop und
Schutz der zweiten Tabelle. Erster Lauf scheiterte durch einen Fehler im
Testaufbau und wurde korrigiert. Revision vor/nachher
`ruestlisten_tabelle_20261103`, keine weiteren Sitzungen; kein Migrationsstempel.
Der Test prueft nicht alle einzelnen Seedvarianten oder eine vollstaendige
Migration; diese bleiben Gegenstand der CI und fachlichen Datenpruefung.
