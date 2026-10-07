---
title: Abnahme User-Entscheidungen Lead und PDF
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-07
version: 1.0.0
---

# Lead, Ernte-PDF und Logistik

User-Entscheidungen umgesetzt gemaess [ADR-078](../adr/adr-078-canonical-lead-postgresql-pdf.md).
Lead-CRUD und Qualifizierung verwenden public.crm_leads statt crm-core mit festem
Mandanten. Die Qualifizierung verbindet einen vorhandenen eigenen Kunden mit
einer echten lokalen Opportunity. Drei verdeckte alte Lead-Router und die zwei konkurrierenden GET/POST-Wege
ohne Slash entfernt; beide Schreibweisen verwenden denselben kanonischen Service.

PDF-Inhalte werden in der bestehenden PostgreSQL-Dokumentablage gespeichert,
einschliesslich SHA-256, Belegreferenz, Version und authentifiziertem Ersteller.
Archivfehler werden weitergegeben; der Druckweg schreibt Inhalt, Audit und
Outbox gemeinsam. Download ist mandantengebunden und prueft die gespeicherten
Bytes. Beim echten Test aufgedeckte Altfehler ebenfalls korrigiert:
BusinessPartner verwendet partner_id/name_1, Artikelabfragen brauchen tenant_id.
Kein Erfolg fuer einen Hardwaredruck behauptet.

## Pruefung

Elf neue echte PostgreSQL-/HTTP-Vertraege bestanden: CRUD/Pagination,
Mandantenautoritaet, drei Vorschau-Modi ohne Mutation, lokale Opportunity,
Doppelqualifizierung, fremder Kunde/Lead, Leserechte, Fehlerruecknahme mit
Opportunity/Audit/Outbox, PDF-Bytes/Hash/Download/zwei Versionen, unveraenderliche
Inhalte/Loeschsperre und fehlgeschlagenes Archiv/Integritaetsfehler.
Insgesamt 106 neue und bestehende Fach-/Masken-/Routervertraege bestanden, ohne Skip.
Gemeinsamer valeo_probe; jede neue Testfunktion verwendet eine aeussere
Transaktion plus Savepoints. Endpoint-Commits schreiben keine permanenten
Testdaten. Keine neue Datenbank, Container oder pauschale Bereinigung.

Die additive Migration wurde nach Nutzungspruefung und gemeinsamem
Advisory-Lock angewandt. Die eigene Versions-Lesetransaktion wurde vor Alembic
beendet: andernfalls blockiert sie dessen ALTER der Versionstabelle.
Kein Reset und kein Eingriff in fremde Sitzungen.

## Fortlaufender Betrieb

Vor Codeaktivierung Migration anwenden. PostgreSQL-Backups enthalten BYTEA,
Header und Versionsmetadaten. Nach Restore ein archiviertes PDF ueber die
Downloadroute lesen und SHA-256 vergleichen. Archivfehler sind Betriebsfehler,
keine leeren erfolgreichen Ergebnisse. Alte Hash-only-Artefakte sind kein
wiederherstellbares PDF; Download gibt 404. Druckaktion erzeugt eine neue Version.

Die acht Logistikaktionen waren bereits im Meilenstein b2a63f451 geschlossen;
es werden keine zweiten Deklarationen angelegt. Bekannte FIBU-/Katalog- und
Abhaengigkeitsrestbefunde bleiben separat sichtbar; kein pauschales Alles-gruen.

Neue Tests tragen needs_live_db und laufen im bestehenden strikten PostgreSQL-CI-Job. CI nutzt dessen bereitgestellte Datenbank; lokale Laeufe verlangen TEST_DATABASE_URL. Alle neun Improvement-Checks auf stabilem Arbeitsbaum bestanden (15,344 s). OpenAPI: drei neue Pfade, keine entfernt; Doppelgruppen 33 -> 30.
