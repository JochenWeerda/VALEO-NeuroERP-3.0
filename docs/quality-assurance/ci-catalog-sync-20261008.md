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
Vorbereitet, noch nicht veroeffentlicht: Nur nach einem fehlgeschlagenen
Katalogvergleich erntet derselbe Job seine
bereits migrierte Datenbank und speichert beide Katalogdateien im Artefakt
`fresh-schema-table-catalog` fuer 14 Tage. Ein fehlgeschlagener Ernteschritt
laedt keinen alten Katalog als neuen Nachweis hoch. Daraus muss der genaue
Schemaunterschied geprueft werden, bevor ein neuer Katalog integriert wird.

Offen: ausdrueckliche Freigabe des GitHub-Artefaktuploads, danach frische
CI-Ernte auswerten und den bestaetigten Drift schliessen. Die automatische
Freigabepruefung hat den Commit mit Upload zweimal abgelehnt, weil der
frische Schemakatalog zusaetzliche bisher nicht veroeffentlichte Metadaten
enthalten koennte. Auch die belegte oeffentliche Version der bisherigen
Katalogdateien ersetzt diese Freigabe laut Pruefung nicht. Die Erweiterung
bleibt lokal reviewbar in `.github/workflows/quality-gate.yml`; sie wird
ohne Freigabe weder committet noch aktiviert. Der lokale Pruefstand liefert
bisher keinen Beleg fuer die genaue Ursache des frischen Schema-Drifts.
