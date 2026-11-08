# Studio-Migrationsplaner, erster Funktionsmeilenstein

## Funktion

Der vorhandene Studio-Server bietet `POST /api/v1/studio/migration-plan` mit den
vorhandenen Bearbeitungsrollen und geprueftem aktiven Mandanten an. Die CLI nutzt
exakt diesen Weg: `studio migrationsentwurf auftrag.json --ausgabe plan.json`.

Der Planer ergaenzt fehlende Datenquellen-/Aktionsbindungen ausschliesslich aus
dem kuratierten Studio-Katalog. Existierende Konflikte und reduzierte
Gefahrenstufen/Agentensperren bleiben sichtbar und sperren. Der Plan enthaelt
Hashes fuer Definition, Katalog und kanonisches physisches Schemainventar; sein
Inhalt bindet ausserdem Mandant, Urheber, Compilerquellstand und Alembic-Head.
Es gibt keinen neuen Command-, Rechte- oder Geschaeftsdatenspeicher.

Typisierte Vorschlaege erzeugen ausfuehrbare additive Alembic-Quellen fuer neue
Tabellen oder optionale neue Spalten. Nur bekannte Domaenenschemas, feste
Bezeichner-/Typvertraege und bestehende mandantengebundene Erweiterungsziele sind
zulaessig. Neue Tabellen besitzen Mandanten-FK, zusammengesetzten Schluessel,
Version und Pflichturheber/Zeitpunkt. Kein freies SQL, keine entfernten Spalten,
kein Rueckbau vorhandener Daten und keine erfundenen Backfillwerte.

## Abnahme

Abschliessender Lauf:64 Faelle bestanden (Migrationsplaner, CLI und native
Uebernahme). Tests verwenden echten Planer und echten API-Router. Die erzeugte
Alembic-Quelle wird auf dem vorhandenen valeo_probe tatsaechlich ausgefuehrt:
Zwei Mandanten koennen denselben Objektbezeichner besitzen; ein nicht vorhandener
Mandant scheitert am FK. Der eigene Tabellen-/Datenbestand wird durch die aeussere
Transaktion vollstaendig zurueckgerollt. Kein Reset, keine neue Datenbank oder
Dockerinstanz. HTTP-Identitaet ist im Grenztest explizit ersetzt, daher kein neuer
OIDC-/MFA-Nachweis fuer diesen Planweg.

Negative Faelle: Identitaets-/Auditspalten, freie/fremde URLs, erfundene Commands,
reduzierte Agentensperren/Gefahrenstufen, SQL-/Typinjektion, doppelte Ziele/Spalten,
bereits vorhandene Tabellen/Felder, unbekannte Schemas, erforderliche Spalten ohne
Backfill, gefaelschter Urheber und fehlende Bearbeitungsrolle.

## Dreikanalvertrag und Betriebsgrenzen

Nutzerentscheid STUDIO-CHANNEL-001 ist in der Platform-Governance festgelegt:
Human-UI, CLI und MCP mit identischen Fachcommands, Rollen-/Datensatzrechten,
gepruefter Mandantenbindung und Wiederholungs-/Negativtests. Jeder neue Plan
liefert alle drei Kanalzustaende als not_verified und nennt diese Nachweise als
Blocker. Das ist keine vom Aufrufer bestaetigbare Berechtigung.

Dieser Meilenstein implementiert Planung und Artefakterzeugung. Er aktiviert
keine Maske und fuehrt im Vorschlagsaufruf keine DDL oder Fachcommands aus.
Noch offen sind die allgemeine CRUD-/Capability-Generierung, der UI-Editor fuer
Schemaaenderungen, die unveraenderliche Ablage/Auswertung des gesamten
Migrationsplans im Freigabeprozess sowie dessen vollstaendige Dreikanal-Abnahme.
Der vorhandene Studio-Freigabeweg wird nicht durch einen angeblich erfolgreichen
Plan ersetzt. Der laufende Backend-Mountbestand wurde nicht pauschal durch den
aktuellen Git-Stand ueberschrieben. Kein neuer lokaler Browsernachweis fuer die
neue Planungs-API; die reale115er-Baseline-Uebernahme ist separat dokumentiert.
