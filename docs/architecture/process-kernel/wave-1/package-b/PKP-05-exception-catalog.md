# PKP-05 Ausnahmekatalog

## Zweck
- Reklamation, Abzug, Qualitätsabweichung und manuelle Sonderfälle in ein gemeinsames Regelmodell überführen

## Status
- erster Katalog im Backend angelegt
- Code-Artefakt: `app/core/exception_rules.py`

## Aktuelle Kategorien
- `complaint`
- `deduction`
- `quality-deviation`
- `manual-override`

## Kerngedanke
- jede Ausnahme besitzt Trigger, Entscheidungsweg und optionale Freigaberollen
- Ausnahmen bleiben nicht in impliziter UI-Logik hängen

## Nächster Schritt
- bestehende Settlement- und Qualitätsausnahmen auf diesen Katalog mappen
