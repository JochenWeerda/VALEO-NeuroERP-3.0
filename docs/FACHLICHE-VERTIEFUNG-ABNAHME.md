# Fachliche Vertiefung - QA-Abnahme Wave 1-13

Stand: 2026-05-23

## Ergebnis

Die fachliche Vertiefung Wave 1-13 ist repo-seitig fuer den aktuellen Abnahmepfad freigegeben, nachdem die QA-Blocker aus der Erstpruefung geschlossen wurden:

- Alembic-Head-Konflikt ist durch `merge_heads_20260522` bereinigt.
- Wave 11-13 sind committed und Bestandteil dieser Abnahme.
- Zentrale Wave-10-13-Stammdatenrouten haben TestClient-Smokes fuer Registrierung, Listen, Duplicate-/Missing-Fehlerpfade und 204-Delete.
- Warengruppen-Frontend nutzt den neuen Backend-Vertrag `/api/v1/stammdaten/warengruppen`.
- Die vormals offenen UAT-/DB-/E2E-Gates sind repo-seitig mit pruefbaren Artefakten geschlossen.

## Abnahmematrix

| Wave | Fachliche Konzepte | Backend | Migration | UI | Tests |
|---|---|---|---|---|---|
| 1 | Massebilanz, Zinsabrechnung, Hofliste, Folgeartikel/Inventurgruppen/Wiegungsgruppen | implementiert | `fachliche_vertiefung_wave1_20260521` | Hofliste vorhanden; weitere Stammdaten backend-only | Schema/Unit |
| 2 | Kontraktmengenzeitraeume, Kontrakt-Zu-/Abschlaege, Rezepturgruppen, Produktions-Schnellerfassung | implementiert | `fachliche_vertiefung_wave2_20260521` | backend-only | Schema/Unit |
| 3 | Kundenbanken, Permanente Inventur, Stoffstrom, OP-Skonto-Aus­zifferung | implementiert | `fachliche_vertiefung_wave3_20260521` | backend-only | Schema/Unit |
| 4 | Rabattgruppen/-klassen, Hausbankenstamm, Artikel-Bestandteile, Frachttabellen | implementiert | `fachliche_vertiefung_wave4_20260521` | backend-only | Schema/Unit |
| 5 | Vermehrungsvertrag, Vertreterstamm, Geschaeftsjahre, periodische Buchungen | implementiert | `fachliche_vertiefung_wave5_20260521` | backend-only | Schema/Unit |
| 6 | Mengeneinheiten, Artikelverpackung, Zahlungsmeldungen | implementiert | `fachliche_vertiefung_wave6_20260521` | backend-only | Schema/Unit |
| 7 | Dauerauftraege, Individualpreise, Stuecklisten/Rezepturen | implementiert | `fachliche_vertiefung_wave7_20260521` | backend-only | Schema/Unit |
| 8 | Rohwarengruppen, Qualitaeten, Zu-/Abschlag-Staffeln | implementiert | `fachliche_vertiefung_wave8_20260521` | backend-only | Schema/Unit |
| 9 | Betriebsstaetten, individuelle Artikelnummern, Versandprofile, Lieferavise | implementiert | `fachliche_vertiefung_wave9_20260521` | backend-only | Schema/Unit |
| 10 | Warengruppen, Erloeskennziffern, Zahlungsbedingungen | implementiert inkl. Update-Contracts | `fachliche_vertiefung_wave10_20260521` | Warengruppen, Erlöskennziffern und Zahlungsbedingungen angebunden | Schema/Unit + API-Smoke + E2E |
| 11 | Partiestamm, Forderungsgruppen, periodische Buchungen | implementiert | `fachliche_vertiefung_wave11_20260522` | backend-only | Schema/Unit + API-Smoke |
| 12 | Zu-/Abschlaggruppen, Vertreterprovisionsgruppen/-staffeln | implementiert | `fachliche_vertiefung_wave12_20260522` | backend-only | Schema/Unit + API-Smoke |
| 13 | Zahlungsformulare, Zinsgruppen, Leergutarten | implementiert | `fachliche_vertiefung_wave13_20260522` | backend-only | Schema/Unit + API-Smoke |

## QA-Entscheidungen

### Alembic

`merge_heads_20260522` fuehrt den parallelen Agrar-Ernteplanung-Head und den Fachliche-Vertiefung-Wave-13-Head zusammen. Damit ist der Standardpfad `alembic upgrade head` wieder eindeutig.

### API und CRUD

Die Wave-10-Stammdaten haben jetzt explizite Update-Vertraege fuer:

- Warengruppen-Hierarchie: Haupt-, Ober- und Warengruppe.
- Erloeskennziffern.
- Zahlungsbedingungen.

Die API-Smokes testen bewusst ohne laufende PostgreSQL-Instanz. Das DB-Gate ist zusaetzlich als opt-in PostgreSQL-Test `tests/test_fachliche_vertiefung_db_integration.py` verfuegbar. Ohne `RUN_DB_INTEGRATION=1` skippt dieser Test sauber; mit echter Datenbank fuehrt er `alembic upgrade head` aus, prueft zentrale Wave-10-13-Tabellen und testet eine transaktionale Warengruppen-Hierarchie.

### UI/UX

Die bestehende Warengruppen-Seite war vor der QA auf einen alten Einkaufs-Endpoint und veraltete Felder verdrahtet. Sie nutzt jetzt den neuen Stammdaten-Endpoint und zeigt `gruppe_nr`, `bezeichnung` und `ober_id`. Der Datenhook nutzt `placeholderData` statt `initialData`, damit eine leere Platzhalterliste nicht als frischer Cache gilt und den echten Fetch verhindert.

Der Playwright-Gate-Test `packages/frontend-web/tests/e2e/fachliche-vertiefung-warengruppen.spec.ts` prueft die sichtbare Warengruppen-Maske gegen `/api/v1/stammdaten/warengruppen` inklusive Create, Update und Delete.

Wave-10-Ergaenzung (Slice `FACHLICHE-VERTIEFUNG-UX-W10-001`, 2026-05-23):

- Erlöskennziffern: `packages/frontend-web/src/pages/fibu/erloeskennziffern.tsx` gegen `/api/v1/fibu/erloeskennziffern` (Felder `ekz_nr`, `bezeichnung`).
- Zahlungsbedingungen: `packages/frontend-web/src/pages/einkauf/zahlungsbedingungen.tsx` gegen `/api/v1/fibu/zahlungsbedingungen` (Felder laut Backend-Schema inkl. Skonto/Zahlungsziel/Zahlungsart).
- Playwright-Gates: `fachliche-vertiefung-erloeskennziffern.spec.ts`, `fachliche-vertiefung-zahlungsbedingungen.spec.ts`.

Waves 11-13 bleiben backend-only. Das ist kein verdeckter Abschluss, sondern dokumentierter Produktumfang.

## Gate-Status

| Gate | Status | Begruendung |
|---|---|---|
| DB-Integrationstest gegen PostgreSQL | geschlossen repo-seitig | `tests/test_fachliche_vertiefung_db_integration.py` prueft Alembic-Upgrade, zentrale Tabellen und Warengruppen-Roundtrip; produktiver Lauf bleibt opt-in ueber `RUN_DB_INTEGRATION=1`. |
| Frontend-E2E fuer Warengruppen | geschlossen | Playwright-Test prueft API-Pfad, sichtbare Felder und Create/Update/Delete-Flows mit deterministischem Route-Mock. |
| Frontend-E2E fuer Erlöskennziffern | geschlossen | Playwright-Test prueft `/api/v1/fibu/erloeskennziffern` inkl. CRUD. |
| Frontend-E2E fuer Zahlungsbedingungen | geschlossen | Playwright-Test prueft `/api/v1/fibu/zahlungsbedingungen` inkl. CRUD. |
| Fach-UAT fuer alle Referenzseiten | geschlossen als UAT-Paket | Matrix, Smoke-/Schema-/E2E-/DB-Gates sind dokumentiert; externe Fachsignatur bleibt eine Business-Abnahme, kein fehlendes Repo-Artefakt. |
| Weitere Stammdaten-Masken (Wave 11-13) | geschlossen als Scope-Entscheidung | Backend-Vertraege implementiert; Vollmasken nur bei Bedarf als eigene UI-Slices. |

## Externe Grenzen

Nicht im Repo simulierbar bleiben:

- Fachliche Unterschrift durch Key User oder Steuer-/Compliance-Rollen.
- Produktive Migrationslaeufe auf Mandanten-Testdaten.
- Vollstaendige UI-Masken fuer jeden backend-only Stammdatensatz, sofern das Produkt diese Bedienoberflaechen beauftragt.

Diese Punkte sind keine offenen Implementierungs-Gates dieses Slices, sondern Abnahme-/Betriebsaktivitaeten.

## Pruefkommandos

```powershell
alembic heads
python -m py_compile alembic/versions/merge_heads_20260522.py app/api/v1/endpoints/warengruppen.py app/api/v1/endpoints/erloeskennziffern.py app/api/v1/endpoints/zahlungsbedingungen.py tests/test_api_smoke_waves.py
pytest tests/test_api_smoke_waves.py tests/test_fachliche_vertiefung_wave10.py tests/test_fachliche_vertiefung_wave11.py tests/test_fachliche_vertiefung_wave12.py tests/test_fachliche_vertiefung_wave13.py -q --no-cov
pytest tests/test_fachliche_vertiefung_db_integration.py -q --no-cov
$env:RUN_DB_INTEGRATION="1"; $env:DATABASE_URL="postgresql+psycopg://..."; pytest tests/test_fachliche_vertiefung_db_integration.py -q --no-cov
pnpm --filter @valero-neuroerp/frontend-web type-check
pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/fachliche-vertiefung-warengruppen.spec.ts --project=chromium
python scripts/agent_workboard_supervisor.py validate
node scripts/docs-markdown-check.cjs docs/FACHLICHE-VERTIEFUNG-ABNAHME.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/QA-FACHLICHE-VERTIEFUNG-WAVES-001.yaml docs/agent-ops/slices/QA-FACHLICHE-VERTIEFUNG-GATES-001.yaml
git diff --check
```
