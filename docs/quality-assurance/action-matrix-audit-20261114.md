---
title: Action-Matrix Nachweispruefung
status: aktiv
last_reviewed: 2026-11-14
owner: Codex
---

# Action-Matrix: deklarierte Einstufung und Nachweis

Der generierte Bericht zaehlt weiterhin alle 38 Aktionen: zwei `green`, vier
`partial`, 32 `gap` sind unveraenderte Angaben der acht YAML-Dateien. Diese
Einstufungen und Tags sind keine Testergebnisse. Die Matrix verknuepft derzeit
keine Aktion mit einem konkreten Testfall, CI-Lauf und Commit-SHA. Ein Tag oder
eine vorhandene Testdatei beweist keine ausgefuehrte oder bestandene Wirkung.
Auch eine kuenftige Referenz allein erhoeht keinen Status automatisch.

Konkreter Befund: Die angeblich gruenen `o2c-001` und `o2c-002` referenzieren
keine konkreten Tests. Die beiden `@critical`-Faelle in
`playwright-tests/specs/e2e-matrix/o2c-semantic-chain.spec.ts` pruefen GETs auf
alte `/api/v1/sales/orders` und `/api/v1/sales/delivery-notes`, akzeptieren
200, 404 und 422 und beweisen weder Anlage noch Umwandlung. Der alte
O2C-Smoke-Ablauf akzeptiert zudem 404, 422 und 503, nutzt Ersatz-IDs und
ueberspringt bei fehlenden IDs Folgeschritte. Der Auftrag wird mittlerweile
ueber DocFlow gefuehrt. Ein gruener Lauf dieser alten Tests wuerde deshalb die
fachlichen Aktionen nicht belegen. Auch die `partial`-Angaben fuer O2C, P2P und
WMS bleiben deklarativ; vorhandene Smoke-Faelle akzeptieren Fehlerantworten.

Der Strict-CI-Workflow verwendet `playwright.config.critical.ts` und selektiert
`@critical` API-Tests; die blosse Auswahl belegt keine Schreibwirkung. Fuer
eine kuenftige fachliche Abnahme sind je Aktion konkrete Testidentitaet,
passender kanonischer Vertrag und erfolgreicher CI-Lauf auf benanntem Commit
mit gepruefter Wirkung erforderlich. Authentifizierung, Mandant, Berechtigung,
Teilmenge und Fehlerfall sind dem Prozess entsprechend nachzuweisen. Es wurde
keine neue Abnahme oder Statusanhebung behauptet.

Der Generator lehnt unlesbares YAML, fehlende Pflichtstruktur, doppelte
Aktions-IDs und ungueltige Statuswerte ab. `--check` bleibt bei ungueltiger
Matrix, fehlender Zuordnung und Berichtsdrift sperrend. Die YAML-Statuswerte
wurden nicht geaendert. Es erfolgte kein Datenbank-, Browser- oder E2E-Lauf.

Gezielt geprueft: Generatorregeneration und --check erfolgreich; 11 Generator-
vertraege bestanden (38,45 s). Eine bestehende Starlette-Deprecation-Warnung
und ein pyreadline-Aufraeumhinweis nach erfolgreichem Testlauf traten auf.
