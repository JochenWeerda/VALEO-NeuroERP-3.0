---
title: Typisierte schreibgeschuetzte Ernte-Regelprojektion
type: qa
audience: [entwickler, qa, agent]
owner: Codex
status: active
last_reviewed: 2026-10-15
version: 1.0.0
---

# Regelspalten im kanonischen Antwortvertrag

Die native Regeltabelle deklariert neun flache Spalten, die der Controller zuvor aus definition abgeleitet hat. Das API-Antwortmodell RuleVersionOut beschrieb diese Projektion jedoch nicht. Der globale Feldvertragscheck beanstandete zu Recht die fehlenden Spalten.

RuleVersionOut leitet die neun Anzeigefelder nun als Pydantic computed_field unmittelbar aus der unveraenderlichen HarvestDeductionRuleV1 ab. Jede dieser Eigenschaften ist im serialisierten OpenAPI-Vertrag readOnly und im Eingabeschema kein Regelparameter. Es gibt keinen zweiten gespeicherten Regelstand. Null Prozent und eine fehlende optionale Qualitaetsgrenze bleiben unveraendert; Inhaltsbindung und Originaldefinition werden nicht neu berechnet oder veraendert.

Vier gezielte Vertraege bestanden: alle Tabellenspalten in tatsaechlicher Antwort und Ausgabeschema, Schutz gegen widersprechende flache Werte, generierte Command-Paritaet sowie unveraenderte typisierte REST-Schreibvertraege. Zusaetzlich bestanden alle vier globalen Feldvertragspruefungen (test_mask_field_contracts): keine fehlenden Maskenfelder und keine neue untypisierte Kopf-/Tabellenquelle. Keine Datenbank oder Dockerinstanz erforderlich.

Die OpenAPI-Projektion wurde gegen die vollstaendige Produktionsanwendung main:app geprueft. Ausschliesslich die Komponente RuleVersionOut erhaelt neun readOnly-Eigenschaften; alle anderen kanonischen Pfade und Komponenten bleiben erhalten. Fremde aeltere OpenAPI-Arbeitskopien werden nicht vereinnahmt. Nachweise: artifacts/harvest-read-projection-tests.txt, harvest-read-openapi-proof.json und harvest-read-global-fields.txt.

## Uebriger CI-Handshake

Der fehlende Aktionskatalog ist als 5bf7e5b28 gepusht; der Abhaengigkeitsaudit dieses GitHub-Stands ist nach evidenzgebundener Review wieder gruen. Die weiteren Vollsuite-Tests bleiben im fremden CI-GRUEN-Claim. Konkret: historische Service-Doubles ohne locked-Parameter, direkte Ernte-Routenaufrufe ohne geprueften Actor, Meridian-Snapshot/Lookup-Pruefannahmen, ein Endpunkt-Matcher mit Querystring sowie weitere fachfremde Auth-/Snapshot-/DB-Testgrenzen. Bereits lokal geaenderte Testdateien wurden nicht committet oder ueberschrieben.

Die develop-Synchronisierung bleibt durch den Datenschutz-Push-Guard blockiert. Sowohl ein noch nicht enthaltenes historisches Commit als auch die aktuelle Fassung von scripts/ci/e2e_keycloak.sh enthalten kollidierende Bootstrap-Benutzerzuweisungen. Ein lokal ignorierter Kandidat ersetzt ausschliesslich zwei Zuweisungen durch eine eindeutige synthetische CI-Kennung und besteht den bestehenden Datenschutzcheck. Die Datei liegt im laufenden fremden CI-Claim; ihr gemeinsamer Arbeitsstand bleibt unangetastet. Kein Force-Push, keine historische Datenweitergabe und keine Abschwaechung des Guards. Nach Integration durch den Dateieigentuemer ist zudem die sichere Historien-/Baumsynchronisierung erneut zu pruefen.
