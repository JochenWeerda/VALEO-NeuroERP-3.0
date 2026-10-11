---
title: Dauerhafte WhatsApp-Vorbereitung und Schutz der Kanalauftraege
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-11
description: Echte SQL- und HTTP-Abnahme von Persistenz, Audit, Replay, Rollback und reserviertem Kanal-Namensraum.
---

# WhatsApp-Vorbereitungsauftraege

## Umsetzung

Die fluechtige _OUTBOX entfällt. Beide Benachrichtigungsfunktionen erfordern
eine DB-Session, Urheber und Idempotenzschluessel. Sie schreiben gemeinsam mit
dem Audit in die bestehenden domain_shared.channel_process_threads und
channel_thread_audit_items. Keine neue Tabelle/Migration und kein Memoryfallback.
Die HTTP-Handler uebernehmen den Urheber aus dem verifizierten Token, committen
gemeinsam und behandeln Replay-Konflikte als 409. Ein fehlender/leerer
Schluessel ist 422. Die DB-Arbeit laeuft in synchronen FastAPI-Handlern.

Die Auftrags-ID bindet Mandant, Benachrichtigungstyp und Schluessel.
Transaktionssperre, Inhaltsfingerprint und gespeicherter Urheber verhindern
zweite Anlage oder Umdeutung. Auditfehler rollen den gemeinsamen Savepoint
zurueck; kein scheinbarer Erfolg. Lesen ist mandantengebunden, Default 50,
maximal 200 Eintraege; Request-Kopien aendern die Persistenz nicht.

Die allgemeine Kanalansicht las bisher dieselbe Tabelle. Daher schliesst das
persistente Kanalrepository den reservierten Namensraum bereits im SQL-Lesen
aus und verweigert generische Anlage/Ersetzung. Auch der historische
Memory-Lesefallback gibt diesen Namensraum nicht heraus. Damit kann die
generische Freigabeoberflaeche keine Benachrichtigung in einen Prozess umdeuten.
Normale persistente Kanalauftraege bleiben les- und schreibbar.

Zwei tote Lieferschein-/Rechnungs-Placeholder entfernt: customer_phone ist
kein Feld des Anlegemodells, der Rechnungsweg bestand nur aus pass. Vier
oberflaechliche Memory-Service-Tests aus Wave101 sind durch echte DB-Vertraege
ersetzt. Vorhandene Template-/HTTP-Guardtests nutzen jetzt einen ausdruecklichen
Speicher-Boundary-Double; diese beweisen keine SQL-Wirkung.

## Abnahme und Grenzen

79 WhatsApp-Vertraege gruen: 63 Template-/Vorbereitungs-/HTTP-Guardtests plus
16 echte PostgreSQL-Vertraege; finale Fassung 3,89 Sekunden. SQL-Pruefung auf vorhandenem valeo_probe,
Revision audit_urheber_20261011; nur eindeutig eigene Mandanten/Auftraege/Audits
angelegt und gezielt entfernt. Kein Reset, keine neue DB/Container/Migration.

Echt geprueft: Commit und neue Session, Original-Replay, anderer Inhalt/Urheber,
gleicher Schluessel in zwei Mandanten, Rollback mit wiederverwendbarem Schluessel,
Auditfehler nach realem Insert, zwei konkurrierende Transaktionen, getrennte
Aktionen, ungueltige Schluessel, begrenztes Lesen, generischer Lese-/Schreibschutz
und normaler ORM-Kanalauftrag. Ein echter HTTP-Vertrag prueft Commit, 409/422,
Tokenurheber statt Rumpfwert und Outbox-Ergebnis an derselben Datenbank.
OIDC-Provider bleibt im HTTP-Test ein Boundary-Double; keine reale Tokensignatur
oder Browser-Sitzung damit abgenommen.

Ein isolierter Lauf zweier vorhandener Wave71/73-Dateien war wegen der fehlenden
Root-Fixture require_db nicht ausfuehrbar (13 Setupfehler); diese 13 gelten nicht
als bestanden. Der normale persistente Kanalpfad wird im eigenen SQL-Vertrag
ausgefuehrt. Keine fremden Standard-Testmandanten beschrieben.

Drei Code-Inventare, Architekturindex (939/939) und fuenf Agent-Handbuch-
Artefakte auf isoliertem HEAD plus eigenen Hunks aktuell. Im Tabellenkatalog
sind exakt die Verbraucher der zwei bestehenden Tabellen nachgezogen;
Tabellen/Spalten/Schluessel unveraendert. Fremdes physisches Katalog-WIP bleibt
im Arbeitsbaum und wird nicht in den eigenen Commit aufgenommen.

Entscheidung/Integration: [ADR-081](../adr/adr-081-whatsapp-browser-notification-persistence.md).
pending_browser bleibt Vorbereitung. Kontobindung, Fachreferenz-/Empfaengerpruefung,
Browser-Lease, Abbruchabgleich, wirklicher Versand und Zustellnachweis sind offen.
Auch allgemeine Kanal-Mandantenisolation ausserhalb des reservierten Namensraums
und separate Meta-/Bestellwege sind nicht durch diesen Fix abgenommen.
