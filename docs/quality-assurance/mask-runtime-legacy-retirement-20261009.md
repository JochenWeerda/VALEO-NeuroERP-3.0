---
title: Kanonische Masken-Runtime und atomare Fachdelegation 2026-10-09
type: reference
audience: [agent, entwickler, qa]
owner: Codex-01a0f3fc
status: abgeschlossen
last_reviewed: 2026-10-09
---

# Eine Masken-Runtime mit atomarer Fachdelegation

Der ungenutzte run_mask_action samt ExecuteFn und _default_propose ist entfernt.
Verbraucherpruefung in app/tests/config/scripts und relevanter Doku: produktive
Aufrufer nutzen bereits run_delegated_mask_action; einzig die alte Atomizitaetssuite
pruefte noch den ungenutzten Weg. Deren Nachweise sind auf die echte Runtime
uebertragen und erweitert. Kein Ersatzadapter oder konkurrierender Speicher.

## Fachcommit bleibt Teil der aeusseren Einheit

Audit und Outbox werden in der aeusseren SQLAlchemy-Sitzung vorbereitet.
Der echte Fachdelegat bekommt eine eigene Session auf derselben Verbindung mit
join_transaction_mode=create_savepoint. Ein innerer Fachcommit gibt nur seinen
Savepoint frei; erst die Runtime committet Mutation, Audit und Ereignis gemeinsam.
Auch Fachwege ohne eigenen Commit geben ihren Savepoint vor Sitzungsende frei.
Eine spaetere Ablehnung oder ein fehlerhafter aeusserer Commit rollt alles zurueck.

Die Originalgegenprobe mit echtem SQLite-Fachcommit und anschliessender Ablehnung
meldete success=false, liess aber den Fachwert after dauerhaft stehen.
Die Reparatur fordert before und leere Audit/Outbox. Positive Nachweise mit und
ohne Fachcommit pruefen alle drei gespeicherten Wirkungen und exakten Ergebnis-IDs.
Ein neuer echter PostgreSQL-Zahlaufvertrag fuehrt approve_payment_run mit dessen
Commit aus, lehnt danach gezielt ab und fordert draft/approved_by=NULL sowie
keine Freigabe-Audit-/Ereigniszeile. Bestehende positive HTTP-Freigaben bleiben echt.

## Begrenzte Datenbankfehler, klare Fachgruende

SQLAlchemy-Fehler und HTTP-Serverfehler ab500 werden in Ergebnis und Warnmeldung
als nicht bestaetigte Speicherung/Pruefung angezeigt. SQL, Tabellen-/Spaltennamen
und gebundene Personalwerte werden nicht durchgereicht. Erwartete Fachablehnungen
wie HTTP409 wegen Vier-Augen-Prinzip bleiben sichtbar. Vier Originalfaelle in
Mutation/Audit/Outbox/Commit belegten SQL-Detaillecks. Zusaetzliche Vertraege pruefen
auch in HTTP500/503 verpackte Datenbankdetails und die Warnmeldungen.

## CI-Fixture mit belegter Freigabe

GitHub CI37843747893 auf7090c4a54: genau ein Fehler bei16758 bestandenen Tests,
Coverage70,66 ueber unveraenderter60er-Schwelle. Der Wave-1-Test verwendete
(run-1,None) als vermeintliche Status-/Erstellerzeile und erwartete dennoch
Freigabe. Der zentrale echte Guard verlangt draft und belegten anderen Ersteller.
Die Fixture liefert fuer den SELECT jetzt (draft,maker), fuer das UPDATE nur
den zurueckgegebenen run-1. Leerer Request bleibt erlaubt; Freigeber kommt aus
dem authentifizierten Nutzer api. Testname entsprechend nachgezogen. Keine
Freigaberegel geschwaecht, kein Test entfernt oder uebersprungen.

## Abnahme und Betrieb

Original neue Runtime-Nachweise: fuenf Fehler/18 gruen (vier Detaillecks und
verbliebener Altweg); zusaetzlich echte innere-Commit-Gegenprobe rot.
Finaler isolierter Lieferstand: 100 Tests ohne Skip:63 Runtime-/Wave-1-Vertraege in6,35s und37 Zahlungs-/Rations-/echte PG-Vertraege in29,80s gruen..
Nur vorhandener valeo_probe, Revision postfach_microsoft_20261008. PostgreSQL-
Tests verwenden bestehende eigene UUID-Testmandanten und raeumen nur ihre Daten
auf. SQLite-Nachweise sind In-Memory, keine Dateien, Datenbankserver oder Container.
Keine Schemaaenderung, Migration, Ruecksetzung oder neue PostgreSQL-Datenbank.

Ein kombinierter instrumentierter lokaler Lauf97 endet mit nativer Windows-
Access-Violation in inspect und ist kein akzeptierter Nachweis. Finale Gruppen
laufen ohne nativen Trace-Timer in getrennten Prozessen; alle Tests bleiben aktiv.
Ein erster Reparaturtest fand fehlenden Savepoint-Abschluss bei nicht committendem
Fachweg, nun mit positiven Faellen fuer beide Commit-Varianten korrigiert.

Lokale Evidenz: ci-mask-retirement-original.log, ci-mask-retirement-inner-commit-original.log,
ci-mask-retirement-wave1.log und ci-mask-retirement-business-final.log unter artifacts/.
Eine fremde gleichzeitig hinzugefuegte Tenant-Payload-Bereinigung im Dateikopf
bleibt als Arbeitsbaum-Hunk erhalten; sie ist kein ungepruefter Bestandteil dieses
isolierten Meilensteins. Eigene Quellhunks separat integriert, fremde Commits/WIP
nicht rueckgesetzt. GitHub-Folgeabnahme nach Push offen.

## Handshake und Grenzen

Neue Masken-Fachcommands nutzen den bestehenden delegierten Weg und echte
Mandantenservices. Historische Empfehlungen fuer run_mask_action sind ersetzt.
Keine neue API, ScreenDefinition, MCP-Registry oder Domänengrenze.

FIN-CLOSE/ADR-076, Zahlauf-MCP open_high und21 fehlende HTTP-Fachcommands bleiben
eigene offene Fachaufgaben. Dieser Slice schliesst die Runtime-Altlast, atomaren
Commit-Durchbruch, SQL-Detaillecks und die konkret rote CI-Fixture.
