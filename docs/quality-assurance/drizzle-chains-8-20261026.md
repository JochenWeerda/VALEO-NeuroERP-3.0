---
title: Drizzle-Migrationsketten fuer acht Domaenenpakete (2026-10-26)
type: qa
audience: [entwickler, qa, betrieb]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# Drizzle-Migrationsketten fuer acht Domaenenpakete (2026-10-26)

Slice `DRIZZLE-CHAINS-8-20261026`, Zweig `claude/drizzle-chains-8-20261026`, gestapelt auf
PR #44 ([drizzle-migrations-ops-20261025.md](drizzle-migrations-ops-20261025.md)).

## Ausgangslage

analytics, contracts, crm, pricing, quality, regulatory, scheduler und weighing hatten ein
Drizzle-Schema, aber keine eingecheckte Migration. Keine Ignore-Regel schloss Migrationen
aus (quality-`.gitignore` Zeile 44 ist ein durch fruehere Bereinigung verstuemmelter
Kommentar ohne Wirkung, `git check-ignore` leer).

## Aenderung

Je Paket Initialmigration, Journal und Snapshot mit drizzle-kit 0.31.11 aus dem aktuellen
Schema (`drizzle-kit generate` mit der Paketkonfiguration) sowie `migrate:apply`
(`drizzle-kit migrate`). Ausgabeordner und Praefix folgen der vorhandenen Konfiguration
(crm: `src/infra/db/migrations`; contracts, pricing, quality, regulatory, scheduler mit
Zeitstempelpraefix). Keine Schemaaenderung noetig: alle Schemata laden, keine
Duplikatwarnung.

| Paket | Migration | Anweisungen | Tabellen | Indizes | FK | Unique |
| --- | --- | --- | --- | --- | --- | --- |
| analytics | `0000_cynical_viper` | 55 | 15 | 40 | 0 | 0 |
| contracts | `20261026061352_unique_colossus` | 26 | 5 | 17 | 4 | 0 |
| crm | `0000_chilly_namora` | 26 | 4 | 18 | 4 | 1 |
| pricing | `20261026061357_luxuriant_killer_shrike` | 21 | 5 | 16 | 0 | 0 |
| quality | `20261026061400_large_the_hunter` | 33 | 5 | 27 | 1 | 2 |
| regulatory | `20261026061402_flippant_ultron` | 32 | 6 | 26 | 0 | 1 |
| scheduler | `20261026061404_wonderful_ikaris` | 32 | 5 | 24 | 3 | 0 |
| weighing | `0000_wooden_psynapse` | 49 | 7 | 42 | 0 | 0 |

## Pruefskript erweitert

`scripts/verify_drizzle_migrations_probe.cjs`:

- vergleicht zusaetzlich Fremdschluessel (Spalten, Ziel, ON DELETE/UPDATE) und
  Unique-Constraints; constraint-gestuetzte Indizes zaehlen nicht als freie Indizes;
- findet Snapshots mit Zeitstempelpraefix;
- drizzle-kit schreibt Fremdschluesselziele fest als `REFERENCES "public".`. Im Pruefschema
  werden genau diese Qualifizierer auf das Pruefschema umgelenkt und gezaehlt; jeder andere
  Schema-Qualifizierer bricht ab. Ein Fremdschluessel ausserhalb des Pruefschemas wuerde im
  Vergleich als `schema.tabelle` sichtbar. So kann kein Constraint an eine gleichnamige
  Tabelle im gemeinsamen `public` von valeo_probe binden.
- normalisiert ausschliesslich Schreibweisen: `timestamp` = `timestamp without time zone`,
  Leerzeichen in Typmodifikatoren (`numeric(15, 3)`), Schluesselreihenfolge in
  jsonb-Defaults. Erstlauf ohne diese Normalisierung: 129 Meldungen, klassifiziert
  62 Timestamp-Alias, 66 numeric-Leerzeichen, 1 jsonb-Reihenfolge, 0 sonstige.

## Abnahme

| Pruefung | Ergebnis |
| --- | --- |
| `drizzle-kit check` je Paket | "Everything's fine" (8/8) |
| `drizzle-kit generate` je Paket | "No schema changes" (8/8) |
| valeo_probe, je Paket eine Transaktion mit Rollback | 8 neue + 3 bestehende Ketten: alle Anweisungen angewendet, FK-Umlenkungen 4/4/1/3 (contracts/crm/quality/scheduler), **0 Abweichungen** |
| Negativprobe (contracts-Kopie: FK `cascade`->`set null`, `approved_at` ohne Zeitzone) | genau beide gemeldet; Zeitzonenunterschied bleibt trotz Normalisierung sichtbar |

Pruefstand: Wartungsfenster vom Nutzer am 2026-10-26 freigegeben; vorher und nachher
`pruefstand_db.py --status` Revision `loading_stop_fk_20261023`, keine fremde Sitzung,
Restkontrolle 0 (`drizzle`, `drizzle_chain_check`, `drizzle_restore_check`). Nur
Transaktionen mit Rollback, nichts festgeschrieben; kein Reset, keine neue DB, kein Container.

## Grenzen

- Die Ketten beschreiben das Schema, nicht bestehende Datenbanken: Eine Umgebung, deren
  Domaenentabellen frueher per `push` entstanden, braucht vor `migrate:apply` einen
  Abgleich (Tabellen vorhanden -> Initialmigration wuerde scheitern). Keine solche Umgebung
  im Repo belegt; nicht geprueft.
- hr bleibt ohne Drizzle-Kette (Handmigration, `TIMESTAMPTZ`-Abweichung offen).
- Keine Aussage ueber vollstaendige Sicherheit oder Gesamtfreigabe.

## CI-Abnahme

| Lauf | Commit | Ergebnis |
| --- | --- | --- |
| Security Scan 40279303829 | 8ff7bb483 | alle Jobs success |
| Quality Gate 40279300491 | 8ff7bb483 | Dependency Scan, Improvement integrity, FSX, Secret Scan, SBOM, WCAG, Production contract u. a. success; Frontend-Unit 214 Faelle mit identischer Fallmenge wie Basis-Lauf 40234161888 (0 neu); Doc-Drift 272 wie Basis |
