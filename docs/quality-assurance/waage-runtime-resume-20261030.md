---
title: Waage Runtime Wiederaufnahme 2026-10-30
type: reference
audience: [entwickler, qa]
owner: Codex
status: abgenommen
last_reviewed: 2026-10-30
version: 1.0.0
description: Gezielte Mandanten-, Kalibrierungs- und Importreparatur samt noch auszufuehrender Abnahme.
---

# Waage Runtime Wiederaufnahme

Vorher: Waagenstamm ohne Mandantenschluessel; impliziter Legacy-Wiegungsspeicher, ASCII-Import in nicht belegte agrar-Wiegetabelle, globale Fehlerqueue und Kalibrierung aus unbewiesener Paralleltabelle. Begonnener Zwischenstand schloss diese Wege mit 503. Jetzt: verifizierter Waagenstamm, erhaltene NULL-Altbestaende, kanonische Eichdaten, persistenter mandantengebundener ASCII-Eingangs-/Fehlernachweis und ausschliesslich kanonische Wiegescheine. Legacy-Wiegungs-CRUD wird mit 410 ersetzt; aktive UI nutzt kanonische Wiegescheine. [ADR](../adr/adr-waage-tenant-import-20261030.md) beschreibt Quelle, Rechte und Grenzen.

Neu vorbereitet: datenbankfreie Negativvertraege fuer nichtendliche/negative/falsche Gewichte, Datum, doppelte Quelle, Q-Zuordnung, fremde registrierte Waagen in Einzel-/Doppelanlage und unveraenderte Eichdaten nach abgelehntem Patch. Bestehende Tests an die tatsaechlichen kanonischen Vertraege angepasst; keine unmandantierte Scheinpersistenz als Erfolg pruefen.

Der opt-in SQL-Vertrag `tests/test_waage_tenant_postgres.py` erweitert den bestehenden vollstaendigen Rollback-Pruefstand um echte Eichmetadaten, strikten Dateirollback, tolerante Fehlerpersistenz, Wiederholung, Retry, Verwerfen, Fremdqueue-Verweigerung und Anwendungsrollen-RLS inklusive enger Referenzfunktion. Identitaeten sind ausdrueckliche Mini-App-Testattrappen. Der Lauf wendet CRM-Vorgaenger und Waagenmigration nur innerhalb einer aeusseren Transaktion an; er benoetigt unveraenderten passenden Ausgangsstand und `valeo_probe`. Keine neue Datenbank, kein Reset, keine dauerhaften GRANTs.

Abnahme 31.10.2026: 104 gezielte datenbankfreie Vertraege aus den sechs Waagen-/Import-/Wiegedomaenensuiten bestanden (50,88 s). Der verstaerkte echte PostgreSQL-/HTTP-Vertrag bestand anschliessend (2,84 s). Fremde registrierte Waagen werden sowohl in kanonischer Einzelanlage als auch Doppelwiegung vor einem Ticketwrite verweigert. NOT-VALID-Constraint verweigert neue NULL-Mandanten und Aenderungen unzugeordneter Altzeilen. Nach vollstaendigem aeusseren Rollback sind Alembic-Revision, temporaere Tabelle/Funktion und eigene Testzeilen nachweislich unveraendert. Waagenschema und GRANTs wurden nicht dauerhaft angewandt. Ein Starlette/httpx-Deprecationhinweis im Unitlauf ist keine fehlgeschlagene Fachpruefung. Der vorherige WIP-Nachweis bleibt datierte Historie, keine aktuelle Abnahme dieser erweiterten Fassung. Vor SQL zuerst `python scripts/pruefstand_db.py --status`; Tests im abgestimmten Fenster und mit `WAAGE_TENANT_SQL_TEST=1`. Root-/Fremdarbeitskopie unveraendert.
