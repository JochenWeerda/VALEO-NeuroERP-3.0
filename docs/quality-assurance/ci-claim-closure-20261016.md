---
title: Uebernommener CI-Claim und versionierte Studio-Ausgangsfassungen
type: qa
audience: [entwickler, qa, sicherheit]
owner: Codex
status: active
last_reviewed: 2026-10-16
version: 1.0.0
---

# Uebernahme und Quellkorrekturen

Der Nutzer hat den ruhenden Claim CI-GRUEN-20261014 ausdruecklich an Codex uebergeben. Einzelvergleich mit HEAD zeigte sowohl alte physische Arbeitskopien als auch eine bereits vorbereitete Lock-Stub-Korrektur. Geliefert wird nur der kanonische Stand mit geprueften Aenderungen im isolierten Index.

## Testgrenzen

Mini-Apps fuer PCN deklarieren ihre Testidentitaet ausdruecklich. Direkte Ernte-Aufrufe erhalten einen ausgewiesenen verifizierten Test-Request; Signaturpruefung wird dadurch nicht behauptet. Query-Stubs modellieren die erforderliche Schreibsperre. Finanztests erkennen den vorhandenen gemeinsamen Pruefstand und die explizite CI-Job-Datenbank an; die Entwicklungsdatenbank bleibt verboten. Journaltests verwenden die erklaerte Job-Verbindung auch dann, wenn nur DATABASE_URL gesetzt ist.

206 bestehende Finanz-, Ernte-, DQ-, PCN- und Katalogvertraege bestehen. Der vorherige kanonische Gegenlauf reproduzierte zehn Fehler in den betroffenen Fach-, Snapshot- und Veroeffentlichungsvertraegen.

## Echte Quellfehler

Snapshot-Lesen und -Anlegen verwenden jetzt get_tenant_id statt tenant_id aus der Query. Anlegen verlangt die vorhandene admin-Rolle. Fuenf neue HTTP-Grenzvertraege sowie SQL-/Speicher-Pagination und bestehende Read-Model-Vertraege bestehen, insgesamt 69 Tests. Das Persistenzmodell ist fuer die regulaere additive Initialisierung registriert; die Unit-Tests verwenden eine ausdrueckliche Store-Dependency und akzeptieren keine 500 mehr als Erfolg.

Der Ernte-Regelarbeitsraum verwaltet mehrere Regelversionen und Annahmen. Er ist daher ein cockpit mit Auditkontext, keine ObjectPage eines einzelnen Belegs. 119 unveraenderte Meridian-/Aktionsvertraege bestehen. Die Endpunktmontagepruefung vergleicht den URL-Pfad ohne Queryparameter; fachlich erforderliche feste Queryparameter werden nicht aus den Commands entfernt.

Die neun genehmigten nativen Belegvarianten kommen aus ihrem geprueften Code und sind auf den bestehenden synthetischen Sichtpruefungsmandanten begrenzt. Das alte Skript erteilt keine kuenstlichen Studio-Freigaben mehr. 31 Beleg-/Variantenvertraege bestehen. Die Studio-Freigabesicherung wurde nicht geaendert.

## Studio-Migrationsbeginn

14 neue Importvertraege pruefen Quellhash, unbekannte/fremde Quellen, Rollen, manipulierte Identitaets-/Definitions-/Nachweisfelder, Dubletten, unveraenderte native Laufzeit und die fortbestehende Freigabesicherung. Darunter ein echter PostgreSQL-Vertrag: genau ein Entwurf und ein unveraenderbarer Historieneintrag trotz Wiederholung; vollstaendiger Quellsnapshot erhalten, eigene Daten per aeusserer Transaktion zurueckgerollt. Zusammen mit vier nativen Belegvertraegen: 18 bestanden.

Zwei neue UI-Pruefungen bestaetigen die Uebernahme des angezeigten Quellstands und denselben Idempotenzschluessel nach einem unklaren Netzfehler. Zusammen mit den Lookup-Vertraegen: neun bestanden. [Migrationsablauf und Grenzen](../architecture/studio-native-migration.md).

## Datenschutz und Nachlauf

Die CI-Bootstrapkennung wurde ausschliesslich durch eine synthetische Kennung ersetzt. Zwei geschuetzte Zuweisungen entfallen; der lokale Datenschutzguard und die Shellsyntaxpruefung bestehen. Kennwort und Token wurden nicht ausgegeben. Die historische problematische main-Abstammung darf nicht nach develop nachgeschoben werden; der Abgleich muss einen datenschutzgeprueften Snapshot mit gleicher Endfassung und erhaltener develop-Abstammung verwenden.

Service Security, Security Scan, PostgreSQL, E2E Smoke, E2E Critical, Security Agent und Doku des vorherigen Standes f2866ce87 sind gruen. Die geaenderten Quellen benoetigen einen neuen vollstaendigen GitHub-Nachlauf. Es wurde keine neue Datenbank und kein Container angelegt, kein Reset und keine Migration ausgefuehrt. Eine echte Modellabnahme bleibt von einem gueltigen lokal konfigurierten Anbieterschluessel abhaengig; Tests und Import geben keine solche Abnahme vor.
