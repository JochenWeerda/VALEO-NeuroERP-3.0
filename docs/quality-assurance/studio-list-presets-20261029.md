---
title: Studio-Listenpresets und begrenzter Vollabruf
type: reference
audience: [entwickler, agent, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-29
version: 1.0.0
description: Zentraler Listenvertrag und belastbare Abnahmegrenzen vor der CRM-Aktivitaetenmigration.
---

# Studio-Listenpresets und begrenzter Vollabruf

Registrierte `listExperience.presets` deklarieren Auswahl-, Kalender- und
Zustaendigkeitsfilter. REST, MCP und CLI verwenden denselben Projektor.
Unbekannte Filter oder nicht registrierte Werte scheitern vor dem Quellabruf.
`mine` ermittelt die Kennung und bestehende Namens-/E-Mail-Zuordnung nur aus
der geprueften Identitaet, nicht aus Aufrufparametern. Dies ist ein Listenfilter,
keine neue Berechtigung; Fachrechte und Mandantenbindung bleiben am Quellweg.

`complete=true` verlangt eine deklarierte Tabelle und Seite 1. Die Antwort
enthaelt den vollstaendigen passenden Bestand bis maximal 5.000 Zeilen;
`data.size` ist dann 5.000. Die aeusseren `page`/`limit` spiegeln den Aufruf,
die inneren Tabellenmetadaten den Projektor. Bestehende seitenweise Aufrufe
bleiben unveraendert. Quellseiten werden weiterhin unter den bestehenden
Zeit-, Mengen- und Bytebudgets gelesen. Keine stillen Teilantworten.
Serverseitig paginierte Fachquellen ohne gemeinsamen Vollbestandsvertrag
lehnen Vollabruf und Presets ab.

Kalenderfilter verwenden die zentrale Betriebszeitzone und Wochen ab Montag.
Zeitstempel ohne Zone gelten wie bei `business_date_at` als UTC. Ueberfaellig
bedeutet vor Beginn des heutigen Geschaeftstags und nicht abgeschlossen.
Fehlende Termine bleiben fehlend. Die Activity-Leseprojektion erlaubt daher
`date=null`; die Neuanlage verlangt weiterhin einen Termin.

Die zentrale Human-Runtime rendert beschriftete NativeSelect-Felder aus der
Definition, setzt beim Wechsel Seite 1 und liest den begrenzten Bestand einmal.
Weitere Browserseiten, Suche und Export verwenden diesen Bestand. Beim Wechsel
auf eine noch nicht geladene Auswahl wird der exportierbare Altbestand geleert.
CLI: `daten ... --tabelle list --vollstaendig --preset owner=mine`.

## Geprueft

- 33 neue Backendfaelle: strikte Metadaten/Requestgrenzen, Kalender und UTC-
  Tageswechsel, offene/abgeschlossene/undatierte Eintraege, verifizierter Bearbeiter,
  unbekannte Auswahl vor HTTP, 130 Quellzeilen in genau drei Fachseiten mit
  65 passenden Zeilen in einer Projektorantwort, CLI-Parameter und harte 5.000er-Grenze.
- Abschliessende gemeinsame gezielte Suite: 92 bestanden, zwei SQL-Verhaltenstests
  bewusst nicht ausgefuehrt (`not signed`). Keine Datenbank-/Containeranlage, kein Reset, keine Fachwrites.
- Zehn zentrale Frontendfaelle gruen: Selektoren, kombinierter Auswahlwechsel,
  Seitenreset, gleiche Transportparameter und negative Definitionsvertraege inklusive Nullwert ohne Validatorabsturz.
  Neun bestehende Collector-/Debitoren-Runtimefaelle im gemeinsamen Lauf bestanden.
- Vollstaendige Frontend-Typpruefung und Produktionsbuild in vorhandener
  isolierter Patchinstallation gruen. Keine persoenlichen Daten oder Tokens
  ausgegeben oder versioniert. Die Windows-pyreadline-Aufraeumwarnung nach
  pytest ist unabhaengig; die Testprozesse endeten mit Status 0.

## CRM: noch keine Fachfreigabe

Die Aktivitaetenliste ist in diesem Meilenstein noch nicht umgestellt.
Die Codepruefung belegt konkurrierende Modelle:

1. `/api/v1/crm/activities` liefert die lokale subject/contact-Liste.
2. `/api/v1/crm/activities/` liefert den paginierten CRM-Core-Vertrag.
3. Der API-Router wird in `main.py` vor dem lokalen CRM-Router registriert;
   beim gleichen Detailpfad liegt damit der Proxy zuerst. OpenAPI kann fuer
   doppelt registrierte Pfade spaetere Metadaten zeigen.
4. Der Frontend-Service erwartet bei seiner Collection ohne Slash bereits
   `items/total`. Die bestehende native Detaildefinition erwartet dagegen
   `subject/activity_type/due_date`, die Proxy-Antwort liefert `title/type/date`.
5. Der Legacy-Anlageweg verwendet teilweise camelCase, waehrend das API-Schema
   snake_case verlangt. Eine blosse Listenumschaltung waere keine Fachparitaet.

Diese Widersprueche muessen vor der Listenfreigabe zusammen mit Detail, Anlage,
Unterlisten und ihren realen Fach-/Rechtevertraegen geschlossen werden.
Keine SQL-Datenquelle erfunden, keine bestehenden Daten still migriert,
keine fremden Routen entfernt. Keine Browser-/Vier-Augen-/SQL-Gesamtabnahme
behauptet. Gates unveraendert A/B/C 851, E 804/851: **47 Runtime-Punkte offen**.

## Architecture Impact Note

Additive Leseoptionen und deklarative Metadaten innerhalb bestehender Masken-
Endpunkte (Minor); keine neuen Container, Domänengrenzen, Rollen oder Fachwrites.
OpenAPI und MCP-Referenz werden aus ihren Quellen synchron erzeugt. Der
Architekturindex und die C4-Struktur bleiben inhaltlich unveraendert.
