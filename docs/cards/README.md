# Cards

## Zweck

Cards sind die kleinste fachlich pruefbare Einheit einer Workflow-Analyse.

## Granularitaetsregel

- Eine Card pro Hauptaktion, Entscheidung, Schleife, Ruecksprung oder Sonderfall.
- Wenn eine Card mehr als eine fachliche Hauptaktion enthaelt, zerlege sie weiter.
- Wenn Alternativpfade eigene UI-, Daten- oder Regellogik haben, erstelle eigene Cards.
- Wenn ein Schritt ohne eigene UI-, Daten- oder Entscheidungslogik auskommt, kann er mit Nachbar-Cards zusammengelegt werden.

## Pfadkonvention

Empfohlene Struktur:

- `docs/cards/verkauf/`
- `docs/cards/einkauf/`
- `docs/cards/lager-logistik/`
- `docs/cards/abrechnung/`
- `docs/cards/agrarportal/`
- `docs/cards/onlineshop/`

## Dateinamenschema

- `VK-010-auftrag-direkt-anlegen.md`
- `VK-020-direktlieferschein-ohne-angebot.md`
- `VK-031-teillieferung-anlegen.md`
- `EK-015-wareneingang-ohne-bestellung.md`
