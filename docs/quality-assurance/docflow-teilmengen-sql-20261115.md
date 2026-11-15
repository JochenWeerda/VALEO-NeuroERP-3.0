---
title: DocFlow-Teilmengen gegen PostgreSQL und RLS
status: aktiv
last_reviewed: 2026-11-15
owner: Codex
---

# Reale Teilumwandlung ohne bleibende Testdaten

Der bestehende Pruefstand `valeo_probe` wurde vorab mit
`pruefstand_db.py --status` geprueft: Revision
`psm_register_entfernt_20261104`, keine andere aktive Sitzung.
Keine neue Datenbank, kein Container, kein Reset oder Tabellen-DDL.

Die automatische Freigabepruefung lehnte eine dauerhafte breite Vergabe an
`valeo_agent` ab. Diese Aktion wurde nicht ausgefuehrt. Die anschliessend
freigegebene Alternative verwendet ausschliesslich eine aeussere Transaktion:
Der bestehende Eigentuemer bereitet darin eng benannte Tabellenrechte vor;
alle Fachzugriffe laufen nach `SET LOCAL ROLE valeo_agent` ohne Superuser-,
Eigentuemer- oder BYPASSRLS-Recht. Die zentrale `tenant_scope`-/RLS-Anbindung
ist aktiv. Fachkommandos duerfen nur ihre Savepoints abschliessen, nie die
aeussere Transaktion. Danach werden Daten und Rechte zurueckgerollt.

Drei Tests in `tests/test_docflow_partial_conversion_postgres.py` bestanden:

- Preisfreie Optionsdaten, schreibfreie Vorschau und reale Uebernahme von vier
  aus zehn kg; Zielposition, Ursprungsbezug, Rest sechs und Version zwei
  werden aus PostgreSQL erneut gelesen. Outbox und verbindliches Kommando-
  protokoll sind vorhanden; der Service-Akteur verdraengt einen gefaelschten
  `created_by`-Eingabewert. Replay mit demselben Schluessel erzeugt keinen
  zweiten Beleg oder Event.
- Uebermenge, alte Version, anderer Inhalt mit gleichem Schluessel bei
  aktueller Version, Nullmenge und fremde Positionskennung werden abgewiesen.
  Nach jeder Abweisung bleiben die vorher gezahlten eigenen Wirkungen gleich.
- Ein fremder Mandantenkontext sperrt selbst einen manipulierten Service-
  Mandantenfilter sowie SQL ohne Mandantenpraedikat. Lesen/Umwandeln scheitern,
  ein fremdes Update betrifft null Zeilen und die Quelle bleibt unveraendert.

Nach jedem Test werden Tabellen-/Schema-ACLs, Eigentuemer, RLS- und Rollenflags
mit dem Vorzustand verglichen. Eigene Mandanten, Belege und Outboxzeilen sind
anschliessend nicht vorhanden. Uebliche PostgreSQL-Sequenzluecken durch
`nextval` koennen trotz Rollback entstehen; Sequenzen werden nicht resettiert.
Es wurde keine dauerhafte Rechtevergabe oder Bereinigung fremder Daten
vorgenommen.

Der erste Lauf fand einen Fehler der Testauswertung: Die lokale Outbox liefert
JSON als Text; dieser wird nun geparst und inhaltlich geprueft. Produktivcode
wurde dafuer nicht veraendert. Finaler gezielter Lauf: drei bestanden,
3,04 Sekunden, keine uebersprungenen Faelle. Lokales Testwerkzeug Python3.11.0;
der Nachweis ersetzt nicht die kanonische Linux-/Python-Abnahme der CI.

Die Quelle wird als synthetischer Auftrag direkt in der isolierten Transaktion
vorbereitet. Kundenanlage, komplette Auftragserfassung, OIDC-Anmeldung und
Browserbedienung sind damit nicht nachgewiesen. Die bestehenden HTTP-Rollen-
und Studio-Dialogvertraege bleiben getrennte Nachweise; die Action-Matrix
wird hierdurch nicht pauschal auf E2E-gruen gesetzt.
