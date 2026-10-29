# ADR-085: Generierte Studio-Stammdatencommands

## Status

Proposed. Fortsetzung des beauftragten Studio-Migrationsmotors; keine neue
Containergrenze und kein allgemeines SQL-Werkzeug fuer Agenten.

## Kontext

Ein Schemaentwurf allein ergibt keine bedienbare Fachfunktion. UI, CLI und MCP
brauchen gleiche Commands, Typvertraege, Mandanten-/Rollenpruefungen, Wiederholung,
Nebenlaeufigkeitskontrolle und nachvollziehbare Geschaeftswirkungen.

## Entscheidung

Ein versionierter EntitySpec fuer neue Studio-Stammdaten erzeugt eine additive
Alembic-Migration, den gemeinsamen HTTP-Commandadapter, JSON-Schemas,
ScreenDefinition, Katalog- und Registrierungsfragmente. Der bestehende
Studio-Katalog nimmt generated_entities auf; daraus werden Quellen, Commands und
Routen beim Start abgeleitet. Keine zweite Rechteverwaltung. Bekannte CRM-,
Agrar- und Lagerrollen bleiben fuehrend. Ausschliesslich neue studio_-Tabellen
in den zugeordneten Domaenenschemas; bestehende Fach-/Buchungstabellen koennen
nicht uebernommen werden. Erweiterung bestehender generierter Vertrage und
weitere Domaenen benoetigen ausdrueckliche Versions-/Migrationsvertraege.

Die generierten Commands erlauben Anlegen, vollstaendiges versioniertes Ersetzen
und nachvollziehbares Deaktivieren. Festgeschriebene Buchungen, Bestand,
Zahlungen, Freigaben und andere spezifische Geschaeftsvorgaenge verbleiben in
ihren bestehenden Domaincommands. Fachreferenzen und beliebiges SQL sind kein
Bestandteil dieses Stammdatenvertrags. Systemfelder sind ausschliesslich serverseitig.

Je Entitaet werden Datentabelle und unveraenderbare Ereignis-/Wiederholungstabelle
im Domaenenschema erzeugt. Ein gemeinsamer Savepoint umfasst Datensatz, Beleg des
Wiederholungsauftrags, Vorher/Nachher-Audit und vorhandene Outbox. Der Adapter
committet gemeinsam. Schluessel bindet Tenant, Entitaet, Operation, Actor,
Vertragsversion, Inhalt, gelesene Version und Begruendung. Lock und Versionspruefung
verhindern verlorene Aktualisierungen; Wiederholung liefert den ersten Erfolg.
Outbox-Bereinigung entfernt keinen Wiederholungs-/Auditbeleg.

Die Migration markiert beide Tabellen mit dem Hash des EntitySpec und der
Laufzeitquellen. Der HTTP-Adapter prueft diese Markierung vor jedem Datenzugriff;
fehlende oder veraltete Bereitstellung sperrt. Das ist keine unabhaengige
vollstaendige Schemainventur. CLI und MCP verwenden die bestehenden Maskenadapter
und denselben authentifizierten HTTP-Command. Ausgaben bleiben deaktiviert,
Agentenrollen sind zusaetzlich explizit freizuschalten. Aus dem Paket ergibt sich
keine automatische Freigabe oder Simulationsevidenz.

## Konsequenzen

Keine DDL im Authoring-Request. Deployment erfolgt ueber die generierte Migration
und gepruefte Registrierung. Tests verwenden den bestehenden valeo_probe und
transaktionale eigene Tabellen; kein neuer Container/DB und kein Reset.
Der Stammdatenvertrag ersetzt weder eine unbekannte Fachregel noch den Nachweis
aller Finanz-, Beleg-, Lager- und Workflowketten. Das bisherige grain.v1-Profil
wird nicht pauschal fuer neue Schreibmasken geoeffnet. Nicht bestandene
Dreikanal-/Browser-/Fachkettenpruefungen bleiben Freigabevoraussetzung.


## Additive Weiterentwicklung registrierter Entitaeten

Der Erweiterungsauftrag enthaelt ausschliesslich Kennung, erwarteten
Basisfingerprint und neue nullable Spalten. Das bisherige Schema kommt aus
der geprueften serverseitigen Registrierung. Typwechsel, Entfernen, neue
Pflichtspalten ohne Backfill, reservierte Namen und fremde Tabellen bleiben
ausgeschlossen. Die Migration sperrt Daten-/Ereignistabelle und prueft beide
Basis-Markierungen vor dem ersten ALTER; neue Markierungen werden in derselben
Migration geschrieben. Bestehende Datensaetze und unveraenderliche Auditbelege
bleiben erhalten. Ein alter Runtimevertrag sperrt danach. Das neue Paket
setzt Schreibfreigabe und Agentenrollen erneut auf deaktiviert; Bereitstellung
und positive Abnahme sind ein expliziter Integrationsschritt. Die unveraenderte
Command-Schemaversion v1 wird nur um optionale Felder erweitert, die neue
Vertragsfassung besitzt einen anderen Inhaltsfingerprint und Migrationsstand.
Inkompatible Fach-/Schemaveraenderungen benoetigen einen eigenen versionierten
Domaincommand und sind nicht durch diesen Compiler freigegeben.
