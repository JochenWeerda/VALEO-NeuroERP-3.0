# KontrollWorklistParent — Abnahme 2026-10-22

Workstream **P1 KontrollWorklistParent** (Maskenfamilien-Taxonomie §2.4).

## Ziel

Expliziter Parent-Vertrag in `app/core/kontroll_worklist_parent.py` (`build_kontroll_worklist_screen`, `kontroll_from_legacy_definition`); **24** Queue-Worklists nutzen dieselbe Shell (Meridian `worklist`, `expertDense`, Audit-/Kontext-Rail, Queue-KPIs wo vorgesehen, virtualisierte Tabellen, `agentContract.testSelectors.summaryArea`). Kein `processRibbon`, keine `workflow.phases` (ProcessBand-Trennung).

## Geänderte / neue Dateien

| Datei | Änderung |
|---|---|
| `app/core/kontroll_worklist_parent.py` | Parent-Builder, Beleg-Kontrolle, Varianten, Sanktionen, `kontroll_from_legacy_definition` |
| `app/core/kontroll_worklist_legacy_payloads.py` | **neu** — eingefrorene Legacy-Payloads für Lift der §2.4-Kandidaten |
| `app/core/screen_definitions_kontrolle.py` | Prüfkorb, Beleg-Kontrolle, Sanktionen, 17 geliftete Worklists; `KONTROLL_WORKLIST_SCREEN_IDS` |
| `app/core/screen_definitions.py` | `**KONTROLLE_SCREEN_BUILDERS` am Ende von `_SCREEN_DEFINITIONS` (Override) |
| `tests/test_kontroll_worklist_parent.py` | Vertragstests für die gesamte Familie |
| `docs/quality-assurance/kontroll-worklist-parent-20261022.md` | diese Notiz |

Nicht angefasst (parallele Agenten): `screen_definitions_stamm.py`, `screen_definitions_listen.py`, Stamm-/Listen-Parents.

## Angeschlossene Worklist-Screen-IDs (24)

| Screen-ID | Mechanismus |
|---|---|
| `auswertungen/beleg-kontrolle` | `build_document_control_worklist` |
| `auswertungen/auftrags-kontrolle` | `build_document_control_variant` (`open_purchase_order`) |
| `auswertungen/lieferschein-kontrolle` | `uninvoiced_delivery_note` |
| `abrechnung/eb-lieferschein-kontrolle` | `missing_inbound_document` |
| `auswertungen/sanktionspruefung-personal` | `build_sanctions_kontroll_worklist` |
| `auswertungen/sanktionspruefung-kunden` | analog |
| `finance/pruefkorb` | `build_kontroll_worklist_screen` + Queue-Helfer |
| `docflow/dokumenten-ruecklauf` | `kontroll_from_legacy_definition` |
| `schnittstelle/mde-inbox` | Lift |
| `produktion/produktionsleitstand` | Lift |
| `lager/inventur-nebenlaeufe` | Lift |
| `finance/rechnungstapel` | Lift |
| `crm/mail-arbeitsplatz` | Lift |
| `lager/fremdware` | Lift |
| `schnittstelle/legacy-adapter-monitor` | Lift |
| `workspace/letzte-dokumente` | Lift (`contextRail`: `none`) |
| `auswertungen/l3-berichtskatalog` | Lift |
| `auswertungen/dms-volltext` | Lift |
| `auswertungen/aenderungshistorie` | Lift |
| `auswertungen/duengemittelmengen` | Lift (`contextRail`: `combined`) |
| `produktion/chargen-bearbeiten` | Lift |
| `auswertungen/bonus-berechnung` | Lift |
| `tankstelle/adapter-inbox` | Lift |
| `auswertungen/abfrage-center` | Lift |

## Abgrenzung

- **StammListenParent** (`compact`-Worklists in `screen_definitions_capture.py`, Listen-Module): bewusst nicht in diesem Slice.
- **`lager/leitstand`**: Floorplan `cockpit`, keine Kontroll-Worklist.
- **`crm/wiedervorlagen`**: liegt in `screen_definitions_listen.py` (fremder Dateibesitz).

## Tests

```text
python -m pytest tests/test_kontroll_worklist_parent.py -q -o addopts=
```

Ergebnis 2026-10-22 (Ausbau): **41 passed**, 1 Deprecation-Warning (Starlette/TestClient, unverändert).

## Offene Punkte

- Runtime-Browser-Abnahme der 24 Screens nicht in diesem Slice (reine ScreenDefinition-Verträge).
- Legacy-Payloads in `kontroll_worklist_legacy_payloads.py` sind Lift-Hilfsdaten; langfristig können einzelne Masken explizit als `build_kontroll_worklist_screen`-Children nachgezogen werden.
- Kein Git-Commit in dieser Session.
