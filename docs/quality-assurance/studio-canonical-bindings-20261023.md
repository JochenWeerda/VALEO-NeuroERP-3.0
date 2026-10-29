---
title: Studio-Stammdaten an kanonische Lesevertraege binden
type: reference
owner: Codex
status: teilweise abgeschlossen
last_reviewed: 2026-10-23
---

# Kanonische Studio-Stammdatenbindungen

Drei generierte Objektmasken verwiesen auf nicht existierende Detailpfade und erfundene Feldnamen. Hausbank verwendet jetzt den vorhandenen Hausbankvertrag mit bank_nr, IBAN und weiteren echten Feldern. Mengeneinheit verwendet einheit_kuerzel, Basiseinheit und Umrechnungsfaktor. Individuelle Artikelnummer verwendet id sowie Artikel-/Partnernummer und externe Kennung. Dieselben ScreenDefinitions werden von Human-, CLI- und MCP-Maskenlesezugriff verwendet; keine parallelen Masken oder Ersatz-Modelle.

Die bisherigen Fachrouter besassen fuer Mengeneinheiten und individuelle Artikelnummern keinen Detail-GET. Zwei eng begrenzte Lesewege liefern jetzt genau einen aktiven Datensatz und nehmen den Mandanten direkt aus der verifizierten Beareridentitaet. Fremde, inaktive und fehlende Eintraege ergeben404; Header-/Queryselector ersetzen die Identitaet nicht. Statische Umrechnungs- und Lookupwege behalten Vorrang. Keine neue Datenbank, Migration oder Containerinstanz.

Gate C verlangt fuer normale Datenquellen einen vorhandenen GET-Vertrag; ausdruecklich deklarierte POST-Berechnungsquellen prueft es gegen genau diese Methode. Das ist keine fachliche Schreibfreigabe. Konkrete Auswahlpfade werden nur aus explizit dokumentierten Path-Enums abgeleitet (auch referenzierte Schemas). Ein beliebiger ID-Platzhalter belegt keinen benannten Fachendpunkt; POST-only belegt keinen Leseweg. Keine Abschwaechung des negativen DATEV-/Wildcard-Vertrags.

## Nachweise

- 11 signierte HTTP-/SQL-Faelle bestanden: echte RSA-/JWKS-Pruefung, SQLite nur im Speicher, zwei Mandanten, falscher Token, fremder Selector,404-Gleichbehandlung, statische Routenvorrangigkeit. Redis-Sitzungsdurchsetzung ist in diesem begrenzten JWT-/Fachtest isoliert und hat eigene Systemtests.
- 21 Gate-/Migrations-Evidenzfaelle bestanden; keine DB-/HTTP-Authattrappe fuer einen behaupteten Live-Nachweis.
- 3 Definition-/Router-/Responsevertraege bestanden.

## Verbleibende Freigabegrenzen

Die Anlagenmaske ist damit noch nicht repariert: ihre API liefert eine verschachtelte Asset-Antwort. Fuer individuelle Artikelnummern fehlt weiterhin ein Update-Command; der Bearbeitenknopf ist sichtbar gesperrt. Hausbank und Mengeneinheit verwenden vorhandene autorisierte PUT-Vertraege mit vollstaendigen Payloadfeldern. Das belegt noch keine Domain-Command-/MCP-WRITE-/Freigabeabnahme. Create/Edit-Paritaet, echte CLI-Freigabe, Browser und Theme fuer diese Masken bleiben nachzuweisen; kein Made-by-Studio-Siegel durch diese Teilreparatur.

Breite historische UI-Fehlerzahlen sind kein Beleg fuer ebenso viele Runtimefehler: viele Tests lesen veraltete Seitentexte nach Zentralisierung. Diese Tests werden nicht pauschal geloescht. Reale Fach-, Layout- und Bedieninvarianten muessen im gemeinsamen Renderer nachgewiesen werden. Die272 frueheren page_no_route_or_nav-Meldungen umfassen auch Legacy-Hilfsmodule und sind keine Zahl ungepruefter Nutzerseiten.

## Kombinierte Abnahme

181 Parent-/Versions-/Bindungs-/signierte HTTP-Vertraege bestanden (Exit0). OpenAPI3246 Pfade, neue GET-Methoden an zwei bereits vorhandenen Detailpfaden; Rechteprojektion, Studio-Quellkatalog, Gatebericht, Agentenhandbuch und Codeinventare neu erzeugt. Architekturindexcheck gruen. Strenger GET-Vertrag zeigt23 offene C-Definitionen,54 E-Nachweise fehlen;5 Draft-Projektionen sauber. Kein Live-/Browser-/vollstaendiger Migrationsnachweis. Eine zitierte NoCommit-Notiz wurde zwischenzeitlich irrtuemlich als Nutzerstopp behandelt; der Nutzer hat die fortgeltende Commit-/Push-Freigabe ausdruecklich klargestellt.

## Methodenbezogener Endstand

Die absichtlich deklarierte POST-Steuervorschau ist kein fehlender GET. Methodenbezogener Abgleich und eigener Gate-C-Negativ-/Positivtest nachgezogen:23 gezielte Evidenz-/Methodenfaelle bestanden. Katalog und Gatebericht danach erneut erzeugt:857 Definitionen, A/B857, C835 (22offen), E803 (54offen);848 native Quellkatalogeintraege. Fuenf strukturellbereite Eintraege sind kein Live-Siegel. Fremde Root-Arbeitskopien des generierten Quellkatalogs/Gateberichts wurden erhalten; die neue gepruefte Artefaktfassung liegt in artifacts/migration-repair-source ; ihre Integration und Veroeffentlichung wird nach der Nutzerklarstellung fortgesetzt.
