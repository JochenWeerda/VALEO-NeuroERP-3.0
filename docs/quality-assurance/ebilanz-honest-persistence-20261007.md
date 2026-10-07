---
title: eBilanz echte Entwurfspersistenz und gesperrte Scheinuebertragung
type: reference
audience: [entwickler, qa, agent, betrieb]
owner: Codex
status: aktiv
last_reviewed: 2026-10-07
version: 1.0.0
---

# eBilanz-Persistenz und wahrheitsgemaesse Antworten

## Befund und Reparatur

Die vorhandenen Request-Handler legten `domain_finance.ebilanz_exports` selbst
an und verschluckten Datenbankfehler. Erstellung bestaetigte trotzdem 201;
Validierung bestaetigte auch nicht vorhandene Exporte, ohne XBRL zu pruefen.
Ein ausschliesslich lokal verwendeter Simulator erzeugte ELSTER-Tickets,
meldete UEBERTRAGEN und beim Polling sogar ANGENOMMEN, ohne Empfangsquittung.
UStVA verwendete denselben Scheinerfolg.

Der Simulationsservice ist nach Verbraucherpruefung entfernt. Erstellung
speichert ausschliesslich reale tenantgebundene Entwurfsmetadaten, mit
Paketgroesse 0 und ausdruecklichem Hinweis auf fehlendes XBRL. Schreibfehler
liefern 503 mit Rollback. Listen und Status verschlucken keine Datenbankfehler.
Fehlende oder fremde Export-IDs liefern 404. Ohne vollstaendiges XBRL und echte
ERiC-Anbindung liefern Export-Validierung, Uebertragung und UStVA-Uebertragung
409; kein Ticket, Status-Update oder Datenbankeintrag wird erfunden.

Die Readiness nennt NOT_READY_EXTERNAL_GATE und repo_contract_ready=false.
Die lokale GCD-Pruefung weist leere Pflichtfelder zurueck und bezeichnet ihren
begrenzten Umfang. Sie ersetzt keine offizielle Taxonomie-/ERiC-Validierung.
Der bestehende Feldkatalog ist eine historische Teilmenge mit Zielversion 6.7,
keine aktuelle amtliche Volltaxonomie. Historische Simulations-Tickets werden
als NICHT_BESTAETIGT dargestellt; vorhandene Datensaetze bleiben unveraendert.
Historische UStVA-Eintraege bestaetigen ebenfalls keinen behoerdlichen Empfang.

Alle Wege verlangen die zentralen Finance-Leserechte. Erstellung/Validierung
verlangen Schreibrechte, die Uebertragungswege Finance-Admin. Rollen werden vor
Datenbankzugriff geprueft. Listen haben SQL-LIMIT und fetchmany; Paging ist
begrenzt, stabil sortiert und auf den Request-Mandanten beschraenkt.

## Schema und Betrieb

`ebilanz_persist_20261007` uebernimmt die bisherige Entwicklungstabelle in den
kanonischen Alembic-Lieferstand. Neue Installationen erhalten dieselben
verwendeten Spalten, Default-Paketgroesse 0 und einen Tenant-/Zeit-/ID-Index.
Bestehende Zeilen werden weder geloescht noch umgeschrieben. Keine Request-DDL.
Migration vor Aktivierung anwenden; Datenbankfehler bleiben sichtbare
Betriebsfehler, keine leere erfolgreiche Liste.

Gemeinsamer valeo_probe vorab kontrolliert und Migration unter Nutzungs- und
Advisory-Lock-Pruefung angewandt. Keine neue Datenbank, Container, Reset oder
pauschale Bereinigung. Neue Integrationstests verwenden aeussere Transaktion
und Savepoints, einschliesslich Endpoint-Commits. needs_live_db fuehrt sie im
bestehenden strikten PostgreSQL-CI-Job aus; dessen bereitgestellte DB wird
verwendet. Kein externer Steuer- oder ELSTER-Aufruf.

## Nachweise

84 neue/bestehende Fach-, SQL-Bind-, Kalender- und Paginierungsvertraege
bestanden ohne Skip (12,22 s). Darunter echte PG-/HTTP-Vertraege fuer Entwurf,
Mandanten-/Rollentrennung, historische Tickets, Fehler-Rollback, gesperrte
Validierung/Uebertragung, leere Pflichtfelder und Begrenzung. Vorheriger
Integrationslauf einschliesslich Phase-23-Routen: 38 Vertraege bestanden.
Alle neun Improvement-Pruefungen bestanden auf stabilem Arbeitsbaum (26,0 s).

Der SQL-Bind-Pruefer prueft jetzt getrackte und neue Quelldateien; von Git als
geloescht erkannte Pfade werden ausgespart. Nullseparierte Pfade erhalten
Leerzeichen. Unerwartete Lesefehler bleiben harte Fehler. Zwei echte temporaere
Git-Vertraege pruefen Rueckbau/neuen Code/Pfade mit Leerzeichen und Lesefehler.
Keine Datenbank oder Container fuer diese Scanner-Vertraege.
Baselines ausschliesslich gesenkt: drei eBilanz-.all-Abfragen entfernt, zwei
date.today-Stellen entfernt. Keine neue Ausnahme oder erhoehter Schwellwert.

## Explizit offen

Vollstaendiges, versioniertes XBRL mit Bilanz-/GuV-Daten, echte amtliche
Taxonomievalidierung und ERiC mit Zertifikat und nachweisbarer Empfangsquittung
sind noch nicht implementiert. Eine brauchbare steuerliche Meldung wird daher
nicht behauptet. Die eBilanz-Schemaquelle ist geschlossen; eine frische
Gesamtkatalog-Abnahme bleibt beim getrennten Katalog-Slice. Allgemeine
Finanzbuchungs-, Lead-Routing-, doppelte API- und Security-Restbefunde bleiben
separate Arbeit. Neue GitHub-Abnahme fuer diesen Commit bleibt erforderlich.
