---
title: CI-Katalogabgleich nach Postfach-Erweiterung
type: qa
audience: [entwickler, qa, agent]
owner: Codex-01a0f3fc
status: active
last_reviewed: 2026-10-08
version: 1.0.0
---

# CI-Katalogabgleich

## Bestaetigte Befunde

CI37758811063 auf 3ea5e3f6f: 16644 Tests bestanden, genau ein Fehler
im Vergleich des generierten Maskenaktionskatalogs. Die kanonische
Postfach-Aktion heisst jetzt `anmelden`; der versionierte Katalog nennt
noch `google`. Regenerierung aus committed Quelle: weiterhin 85 Aktionen
in 45 Masken, bestehende Ausfuehrungs- und Berechtigungsvertraege erhalten.

Quality Gate37758811757 scheitert am physischen Tabellenkatalog.
Der gemeinsame lokale Pruefstand `valeo_probe` steht auf
`postfach_microsoft_20261008`. Seine lesende Ernte stimmt jedoch mit dem
bisherigen Katalog ueberein: 661 Tabellen, keine hinzugefuegte, entfernte
oder geaenderte Tabellendefinition. Der lokale Nachweis ersetzt deshalb
keine Abnahme des frischen GitHub-Schemas. Fremde lokale Katalogfassungen
werden weder uebernommen noch verworfen.

## Nachweis und laufende Kontrolle

Aktionsgenerator und Tabellenkatalog `--check` aus committed Quelle gruen.
20 bestehende isolierte Katalog-/Lineage-Tests bestanden. Der bestehende
Consent-Schema-Vertrag wurde anschliessend direkt lesend am vorhandenen
Pruefstand ausgefuehrt; seine beiden getrennten Modelle und Verbraucher
sind korrekt. Keine neue Datenbank, kein Container, kein Reset oder Migration.

Der erste isolierte Testaufruf meldete bei diesem Integrationstest eine
fehlende `require_db`-Fixture, weil globale Fixtures bewusst nicht geladen
wurden. Der korrigierte Ablauf trennt die 20 isolierten Tests vom realen
lesenden Schema-Vertrag; keine Produkt- oder Testaussage abgeschwaecht.

Das bestehende Quality Gate bleibt verbindlich rot bei Schemaabweichung.
Nach ausdruecklicher Nutzer-Freigabe autorisiert:
Nur nach einem fehlgeschlagenen
Katalogvergleich erntet derselbe Job seine
bereits migrierte Datenbank und speichert beide Katalogdateien im Artefakt
`fresh-schema-table-catalog` fuer 14 Tage. Ein fehlgeschlagener Ernteschritt
laedt keinen alten Katalog als neuen Nachweis hoch. Daraus muss der genaue
Schemaunterschied geprueft werden, bevor ein neuer Katalog integriert wird.

Die automatische
Freigabepruefung hat den Commit mit Upload zweimal abgelehnt, weil der
frische Schemakatalog zusaetzliche bisher nicht veroeffentlichte Metadaten
enthalten koennte. Auch die belegte oeffentliche Version der bisherigen
Katalogdateien ersetzt diese Freigabe laut Pruefung nicht. Die Erweiterung
war lokal reviewbar in `.github/workflows/quality-gate.yml`. Auch ein erneuter
Versuch nach weiter wurde von der automatischen Pruefung abgelehnt. Erst die
anschliessende ausdrueckliche Nachricht "ich erlaube dir den Upload" hat die
Aktivierung freigegeben; der Commit wurde danach zugelassen.
Die genaue Ursache wurde anschliessend an der frischen Ernte nachgewiesen (siehe unten).

Auf 02ce0879c sind grosser CI37788113807, Docs Build37788113871,
Security Scan37788113995 und Smokes gruen. Quality Gate37788114327
bleibt am Tabellenkatalog rot. Die Diagnose erweitert nur dessen Nachweis;
kein Gate abgeschwaecht und keine weitere Datenbank erzeugt.

## Frische Schema-Ernte und Integration

Quality Gate37825542282 auf 3f3927045 hat den weiterhin roten Vergleich
korrekt gemeldet und Artefakt11572410712 erzeugt. Die autorisierte Ernte
enthaelt 670 Tabellen. Exakt neun Tabellen kommen gegenueber dem bisherigen
661er-Katalog hinzu; keine Tabelle fehlt und keine bestehende Definition
oder Verbraucherzuordnung unterscheidet sich:

- `domain_crm.contacts`
- `domain_inventory.article_alternative_eans`
- `domain_inventory.article_analyses`
- `domain_inventory.article_print_settings`
- `domain_inventory.article_units`
- `domain_inventory.nawaro_area_sheet_rows`
- `domain_inventory.nawaro_contract_sheet_rows`
- `domain_inventory.nawaro_raps_balances`
- `domain_inventory.nawaro_raps_certificates`

Dies sind exakt die zuvor rein lesend festgestellten ORM-Tabellen, die auf
dem lokalen migrationsbasierten Pruefstand fehlen. Der frische CI-Aufbau
fuehrt nach Alembic die vorhandene additive ORM-Initialisierung aus. Beide
generierten Katalogdateien stammen unveraendert inhaltlich aus diesem
Artefakt; JSON-Serialisierung und Markdown-Darstellung wurden erneut mit
dem kanonischen Generator verglichen. Keine manuellen Schemaannahmen,
keine Migration, kein Reset und keine zusaetzliche Datenbank oder Container.
Die fremden lokalen Katalog-Arbeitsfassungen bleiben erhalten.

Der lokale 661er-Pruefstand kann nach dieser Korrektur den physischen
670er-Katalog nicht mehr bestaetigen. Die Nachabnahme erfolgt deshalb im
bestehenden frischen GitHub-Job; sein Gate bleibt verbindlich.
