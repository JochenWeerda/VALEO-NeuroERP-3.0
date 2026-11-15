# Sonar-Abnahmeprüfung 2026-11-13

## Bezug und Ergebnis

- Bezug: `main`-Commit `b310e13b5c43f04b58c82d904be3a4e035967919`, Quality-Gate-Lauf [42771235959](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/42771235959), Sonar-Job `129693663069` vom 10. November 2026.
- Das Sonar-Gate scheiterte. Die abgefragte Kennzahl für neuen Code betrug **70,8993 % Coverage** bei geforderten mindestens 80 %. Die Abfrage meldete 140.471 neue abzudeckende Zeilen und 38.397 davon ungedeckte Zeilen. Sonars Coverage berücksichtigt auch Bedingungen; aus Zeilenzahlen allein lässt sich die Gatewirkung nicht exakt berechnen.
- Nach Quellbereich: `app` 25.345/112.961, Frontend 12.533/25.712, `services` 447/1.174 und `modules` 72/624 ungedeckte/abzudeckende neue Zeilen. Innerhalb `services`: KI 214/907, Finance 57/57, CRM-Core 35/35. Diese Werte sind eine Momentaufnahme der Sonar-API, kein Nachweis für einen späteren Commit.

## Berichtskette und Grenzen

Der Job lud das Backend-Cobertura-Artefakt und das Frontend-LCOV-Artefakt desselben Laufs, prüfte deren Evidenz und importierte beide Berichte. Der Python-Import meldete zwei mehrdeutige Dateipfade und ignorierte deren Coverage; genannt wurde `agrar/__init__.py`. Der LCOV-Import meldete 24 nicht aufgelöste Pfade; das erste Beispiel `src/components/ui/LazyTabs.tsx` liegt im bereits bestehenden Sonar-Quellausschluss `packages/frontend-web/src/components/ui/*.tsx`. Das Log nennt nicht alle 24 Pfade; deren Ursache und Einfluss sind deshalb nicht pauschal bestimmbar. Der fehlende `test-results.xml` betrifft den konfigurierten xUnit-Ausführungsbericht, nicht die beiden Coverage-Berichte.

Der Scanner klassifizierte Testmuster laut Log getrennt von Quellen. Er fand 39 TypeScript-Konfigurationen; die beiden Konfigurationen unter `docs/_internal/archive/domains-ts-backend/` scheiterten an einer fehlenden referenzierten Archiv-Konfiguration. Die Frontend-Konfiguration analysierte 1.989 Dateien. Eine explizite Auswahl der Laufzeitkonfigurationen kann die automatische Discovery bereinigen, muss aber die Analyse aller produktiven TypeScript-Quellen nachweislich erhalten. Die Scannerwarnung zu ungültigem UTF-8 in `packages/frontend-web/src/config/mask-builder-customer.json` ist ein separater Befund.

Die Python-Standardsuite sucht Tests unter `tests/`; der KI-Service wird danach isoliert ausgeführt und seine Coverage zusammengeführt. Andere serviceeigene Tests werden dadurch nicht automatisch Teil dieses Sonar-Berichts. Einzelne Root-Tests können dennoch Service-Code ausführen. Für Finance bestehen ältere Tests mit SQLite-Datei und Schema-Reset; diese sind kein datenbankfreier Nachweis. Aussagekräftige zusätzliche Tests und ein erneuter vollständiger CI-/Sonar-Lauf sind erforderlich, um eine Verbesserung und die Gate-Abnahme zu belegen. Keine Schwelle, New-Code-Periode oder Coverage-Ausschlüsse wurden geändert.
