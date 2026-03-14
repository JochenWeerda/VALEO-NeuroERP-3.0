# PKP-01 Ziel-Command-Katalog

## Zweck
- vorläufiger Zielkatalog für die Kernprozesskette
- Ausgangspunkt für spätere Migration bestehender CRUD- und UI-Pfade

## Status
- erster technischer Katalog im Backend angelegt
- Code-Artefakt: `app/core/process_commands.py`

## Kerncommands
- `contract.create`
- `contract.update`
- `contract.allocate`
- `acceptance.register`
- `acceptance.capture`
- `acceptance.release`
- `quality.record`
- `quality.finalize`
- `settlement.preview`
- `settlement.create`
- `settlement.post`
- `workflow.simulate`
- `policy.evaluate`

## Nächster Schritt
- Result- und Error-Modelle pro Command weiter schärfen
- bestehende UI-/API-Pfade auf diese Zielcommands mappen
