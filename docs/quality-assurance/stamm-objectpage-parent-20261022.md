---
title: StammObjectPageParent Pilot — QA
type: qa-evidence
audience: [agent, entwickler, qa]
owner: Cursor Composer
status: abgeschlossen
last_reviewed: 2026-10-22
version: 1.0.0
description: Nachweis UIX-STAMM-OBJECTPAGE-PARENT-20261022 — Parent-Factory und fuenf Pilot-Children.
---

# StammObjectPageParent Pilot (2026-10-22)

## Slice

`UIX-STAMM-OBJECTPAGE-PARENT-20261022` — Taxonomie-P1 ohne Codex Gate-D-Besitz.

## Geliefert

| Artefakt | Inhalt |
|---|---|
| `app/core/stamm_object_page_parent.py` | Factory `build_stamm_object_page` + Tab-/Source-Helfer |
| Pilot-Builder in `screen_definitions.py` | `agrar/duenger`, `agrar/saatgut`, `einkauf/supplier`, `finance/debitor`, `finance/kreditor` |
| `tests/test_stamm_object_page_parent.py` | Shared Shell, Child-Overrides, Parent-Guards |

## Parent-Vertrag (Shell)

- `mode=detail`, adapter native non-temporary
- `layout.floorplan=objectPage`, `sectionNavigation=anchors`, sticky header/footer
- `tabs[0].key=kopf`, dataSource `entity`
- Primaeraktion `edit` (safe); optionale `extra_actions`
- `identityField` + summary mit `kind=identity`
- `noWorkflowReason` Pflicht (Referenzstamm)

## Child-Overrides (erhalten)

| Screen | identityField | density / rail | Besonderheit |
|---|---|---|---|
| agrar/duenger | artikelnummer | compact / none | Tabs Verwendung, Preise |
| agrar/saatgut | artikelnummer | compact / none | Tabs Lager, Vertraege |
| einkauf/supplier | lieferantennummer | expertDense / combined | summaryEndpoint, Aktion neue_bestellung |
| finance/debitor | debitoren_nr | expertDense / audit | OP + Umsaetze |
| finance/kreditor | kreditoren_nr | expertDense / audit | OP + Bestellungen |

Create bleibt Legacy (UIX-057). Keine neuen Routen; Inventar-Delta 0 erwartet.

## Tests

```bash
python -m pytest tests/test_stamm_object_page_parent.py tests/test_meridian_party_objectpage.py -q -o addopts=
```

Ergebnis 2026-10-22: **10 + 5 bestanden** (ohne Coverage-addopts wegen lokaler Suite-Dauer).

## Abgrenzung

- Gate D Image/CI/Browser publiziert: weiter Codex `STUDIO-ENTITY-RELEASE`
- Belegfamilie / `screen_definitions_beleg.py`: unangetastet
- Touren/Training/Bestellvorschlag: unangetastet
- Folge: weitere Stamm-Children an Parent haengen; CLI-Siegel einer Parent-Maske nach Gate D

## Nebenbefund (nicht Slice-Scope)

Lokale WIP hatte `mask_action_runtime_service.py` (`_ergebnis`) und `docflow_return.py`
(`command_router`) gegen HEAD zurueckgesetzt — fuer Test-Import aus HEAD wiederhergestellt,
nicht als Slice-Commit.
