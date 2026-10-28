---
title: QA URHEBER-AUS-TOKEN-20261028
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-28
version: 1.0.0
description: Fuenf Wege nahmen den Urheber aus dem Anfragekoerper; jetzt aus der geprueften Anmeldung. Der Identitaetsvertrag uebersah sie wegen eines fehlerhaften Docstring-Filters und camelCase-Feldern.
---

# QA URHEBER-AUS-TOKEN-20261028

**Basis:** `claude/tenant-fallback-abbau-20261027` (#82). Keine Migration.

## Befunde

| Weg | Befund | Korrektur |
|---|---|---|
| `POST/PUT /business-partners` | `created_by`/`updated_by` aus `payload.audit` | Anlage: beide aus dem Token; Aenderung: `updated_by` aus dem Token, `created_by` bleibt |
| `POST /api/contracts/{id}/amendments` | `created_by` aus `createdBy`, Mandant `body.tenantId or …`; der Vertrag wurde **nicht** darauf geprueft, ob er dem Mandanten gehoert | Urheber und Mandant aus der Anmeldung, Vertrag ueber `get_contract` im Mandanten (sonst 404); Felder entfernt |
| `POST /personal/payroll-exports` | `created_by` aus `createdBy` | Token; Feld entfernt |
| `POST /finance/buchungsuebergabe-export` | GoBD-Artefakt mit `created_by=body.bediener` — das ist der **Filter**, wessen Buchungen exportiert werden (oft leer) | wer exportiert, aus dem Token |
| `POST /finance/open-items/{id}/actions/mahnen` | Mahnstufe mit Bearbeiter `payload.get("operator")`, sonst `"Maske"` | Token |

**Vertragstest `tests/test_keine_client_identitaet.py`:** Sein Docstring-Filter zaehlte dreifache Anfuehrungszeichen nur am
Zeilenanfang. Ein `text("""` mitten in der Zeile verschob die Zaehlung, der Code dahinter galt als Docstring — so blieb
`payload.createdBy` im Lohnexport und `payload.get("operator")` in der Mahnung unentdeckt. Jetzt bestimmt der
Syntaxbaum Docstrings (mit Selbsttest); das Muster erkennt auch `createdBy`/`updatedBy`/`updated_by` und
`payload.audit.*`; geprueft werden auch die Router unter `app/routers`.

## Nachweise

```
pytest tests/test_urheber_aus_token.py tests/test_keine_client_identitaet.py -> 12 passed, 0 skipped
Gegenprobe alter Code (5 Dateien)                                           -> 8 rot
36 betroffene Bestandsmodule (Pakete zu 20)                                  -> 1726 passed, 4 rot
   (test_meridian_beleg_systemweit 4, auf der Basis #82 gleich rot), 0 neu rot
Code-Inventare, RLS-Matrix, Systemlesen aktuell; OpenAPI nur Nachtrag und Lohnexport
ruff: keine neuen Befunde
```

## Offen

- Rahmenvertraege (`RV-…`, `domain_ops.ops_rahmenvertraege`) haben keinen Mandanten; `GET /api/contracts/RV-…` liefert jeden
  Rahmenvertrag. Teil von RLS-DOMAIN-OPS (Tabellen ohne Mandant, Live-Daten muessen zugeordnet werden).
