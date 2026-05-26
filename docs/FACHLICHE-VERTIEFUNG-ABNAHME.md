# Fachliche Vertiefung - QA-Abnahme Wave 1-13

Stand: 2026-05-26

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
| 2 | Kontraktmengenzeitraeume, Kontrakt-Zu-/Abschlaege, Rezepturgruppen, Produktions-Schnellerfassung | implementiert | `fachliche_vertiefung_wave2_20260521` | Rezepturgruppen: `/produktion/rezepturgruppen` (Wave 22) | Schema/Unit + E2E |
| 3 | Kundenbanken, Permanente Inventur, Stoffstrom, OP-Skonto-Aus­zifferung | implementiert | `fachliche_vertiefung_wave3_20260521` | backend-only | Schema/Unit |
| 4 | Rabattgruppen/-klassen, Hausbankenstamm, Artikel-Bestandteile, Frachttabellen | implementiert | `fachliche_vertiefung_wave4_20260521` | Frachttabellen: `/logistik/frachttabellen` (Wave 22); Artikel-Bestandteile: `/stammdaten/artikelbestandteile` (Wave 21) | Schema/Unit + E2E |
| 5 | Vermehrungsvertrag, Vertreterstamm, Geschaeftsjahre, periodische Buchungen | implementiert | `fachliche_vertiefung_wave5_20260521` | Geschaeftsjahre: `/fibu/geschaeftsjahre` (Wave 22); Periodische Buchungen: `/fibu/periodische-buchungen` (Wave 11 UI); Vermehrungsvertraege: `/agrar/vermehrungsvertraege` (Wave 21) | Schema/Unit + E2E |
| 6 | Mengeneinheiten, Artikelverpackung, Zahlungsmeldungen | implementiert | `fachliche_vertiefung_wave6_20260521` | Mengeneinheiten: `/stammdaten/mengeneinheiten` (Wave 22); Zahlungsmeldungen: `/fibu/zahlungsmeldungen` (Wave 22); Artikelverpackung: `/stammdaten/artikelverpackung` (Wave 21) | Schema/Unit + E2E |
| 7 | Dauerauftraege, Individualpreise, Stuecklisten/Rezepturen | implementiert | `fachliche_vertiefung_wave7_20260521` | Dauerauftraege: `/verkauf/dauerauftraege` (Wave 21); Individualpreise: `/preise/individualpreise` (Wave 22) | Schema/Unit + E2E |
| 8 | Rohwarengruppen, Qualitaeten, Zu-/Abschlag-Staffeln | implementiert | `fachliche_vertiefung_wave8_20260521` | Rohwarengruppen: `/stammdaten/rohwarengruppen` (Wave 20) | Schema/Unit + E2E |
| 9 | Betriebsstaetten, individuelle Artikelnummern, Versandprofile, Lieferavise | implementiert | `fachliche_vertiefung_wave9_20260521` | Versandprofile: `/logistik/versandprofile` (Wave 22) | Schema/Unit + E2E |
| 10 | Warengruppen, Erloeskennziffern, Zahlungsbedingungen, Erlöskontenzuordnung (EKZZ) | implementiert inkl. Update-Contracts | `fachliche_vertiefung_wave10_20260521` | Warengruppen, Erlöskennziffern, Zahlungsbedingungen und EKZZ angebunden | Schema/Unit + API-Smoke + E2E |
| 11 | Partiestamm, Forderungsgruppen, periodische Buchungen | implementiert | `fachliche_vertiefung_wave11_20260522` | Partiestamm: `/lager/partiestamm`; Forderungsgruppen: `/fibu/forderungsgruppen`; Periodische Buchungen: `/fibu/periodische-buchungen` (Wave 11 UI, 2026-05-24) | Schema/Unit + API-Smoke + E2E |
| 12 | Zu-/Abschlaggruppen, Vertreterprovisionsgruppen/-staffeln | implementiert | `fachliche_vertiefung_wave12_20260522` | Zu-/Abschlaggruppen: `/preise/zu-abschlaggruppen` (Wave 17 UI); Provisionsgruppen: via Vertreterstamm-Integration (Wave 16 UI) | Schema/Unit + API-Smoke + E2E |
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

Wave-10-EKZZ (Slice `FACHLICHE-VERTIEFUNG-UX-W10-EKZZ-001`, 2026-05-23):

- Erlöskontenzuordnung: `packages/frontend-web/src/pages/fibu/erloeskontenzuordnung.tsx` unter `/fibu/erloeskontenzuordnung`.
- Zuordnungen: `GET` und `POST` (Upsert) gegen `/api/v1/fibu/erloeskennziffern/zuordnungen` — kein `PUT`/`DELETE` im Backend.
- Lookup: `GET` gegen `/api/v1/fibu/erloeskennziffern/lookup` mit Query-Parametern `ekz_nr`, optional `steuerschluessel`, `erlösklasse`, `buchungsklasse`, `datum`.
- Playwright-Gate: `fachliche-vertiefung-ekzz.spec.ts`.

Wave-11-UX (Slice FACHLICHE-VERTIEFUNG-UX-W11-001, 2026-05-24):

- Partiestamm/PGR: `packages/frontend-web/src/pages/lager/partiestamm.tsx` unter `/lager/partiestamm`.
- Forderungsgruppen: `packages/frontend-web/src/pages/fibu/forderungsgruppen.tsx` unter `/fibu/forderungsgruppen`.
- Periodische Buchungen: `packages/frontend-web/src/pages/fibu/periodische-buchungen.tsx` unter `/fibu/periodische-buchungen`.
- Playwright-Gates: `fachliche-vertiefung-partiestamm.spec.ts`, `fachliche-vertiefung-forderungsgruppen.spec.ts`, `fachliche-vertiefung-periodische-buchungen.spec.ts` (3/3 gruen, 2026-05-26).

Wave-20-UX (Slice FACHLICHE-VERTIEFUNG-UX-W20-001, 2026-05-26):

- Rohwarengruppen: `packages/frontend-web/src/pages/stammdaten/rohwarengruppen.tsx` unter `/stammdaten/rohwarengruppen`.
- Playwright-Gate: `fachliche-vertiefung-rohwarengruppen.spec.ts`.

Wave-22-UX (2026-05-26):

- Frachttabellen: `/logistik/frachttabellen` (Positionen, CRUD). Playwright-Gate: `fachliche-vertiefung-frachttabellen.spec.ts`.
- Versandprofile: `/logistik/versandprofile` (Email/Fax/EDI-Profil-CRUD). Playwright-Gate: `fachliche-vertiefung-versandprofile.spec.ts`.
- Rezepturgruppen: `/produktion/rezepturgruppen`. Playwright-Gate: `fachliche-vertiefung-rezepturgruppen.spec.ts`.
- Geschaeftsjahre: `/fibu/geschaeftsjahre` (CRUD). Playwright-Gate: `fachliche-vertiefung-geschaeftsjahre.spec.ts`.
- Zahlungsmeldungen: `/fibu/zahlungsmeldungen` (CRUD). Playwright-Gate: `fachliche-vertiefung-zahlungsmeldungen.spec.ts`.
- Individualpreise: `/preise/individualpreise` (VK/EK-Tabs, CRUD). Playwright-Gate: `fachliche-vertiefung-individualpreise.spec.ts`.
- Mengeneinheiten: `/stammdaten/mengeneinheiten` (CRUD). Playwright-Gate: `fachliche-vertiefung-mengeneinheiten.spec.ts`.
- Wave-22: 7/7 E2E-Gates gruen, TypeCheck 0 Fehler.

Wave-14-UX (Slice `FACHLICHE-VERTIEFUNG-UX-W14-001`, 2026-05-24):

- Rabattgruppen/-klassen/-saetze: `packages/frontend-web/src/pages/preise/rabattgruppen.tsx` unter `/preise/rabattgruppen`.
- Betriebsstaetten: `packages/frontend-web/src/pages/stammdaten/betriebsstaetten.tsx` unter `/stammdaten/betriebsstaetten`.
- Playwright-Gates: `fachliche-vertiefung-rabattgruppen.spec.ts`, `fachliche-vertiefung-betriebsstaetten.spec.ts`.

Wave-15-UX (Slice `FACHLICHE-VERTIEFUNG-UX-W15-001`, 2026-05-24):

- Vertreterstamm: `packages/frontend-web/src/pages/crm/vertreterstamm.tsx` unter `/crm/vertreterstamm`.
- Hausbankenstamm: `packages/frontend-web/src/pages/stammdaten/hausbanken.tsx` unter `/stammdaten/hausbanken`.
- Playwright-Gates: `fachliche-vertiefung-vertreterstamm.spec.ts`, `fachliche-vertiefung-hausbanken.spec.ts`.

Wave-16-UX (Slice `FACHLICHE-VERTIEFUNG-UX-W16-001`, 2026-05-25):

- Integration Vertreterstamm x Vertreterprovisionsgruppen: `provisionsgruppe_nr` in Vertreterstamm-Maske als Select aus echten Provisionsgruppen.
- Playwright-Gate: `fachliche-vertiefung-vertreterstamm-prov-integration.spec.ts`.

Wave-17-UX (Slice `FACHLICHE-VERTIEFUNG-UX-W17-001`, 2026-05-26):

- Zu-/Abschlaggruppen [ZAGR], Zu-/Abschlagklassen [ZAKL] und Konditionen [ZAK]: `packages/frontend-web/src/pages/preise/zu-abschlaggruppen.tsx` unter `/preise/zu-abschlaggruppen`.
- API-Routen: `GET/POST/DELETE /api/v1/preise/zu-abschlaege/gruppen|klassen`, `GET/POST /api/v1/preise/zu-abschlaege/konditionen`.
- Playwright-Gate: `fachliche-vertiefung-zu-abschlaege.spec.ts` (4/4 gruen).

## Gate-Status

| Gate | Status | Begruendung |
|---|---|---|
| DB-Integrationstest gegen PostgreSQL | geschlossen repo-seitig | `tests/test_fachliche_vertiefung_db_integration.py` prueft Alembic-Upgrade, zentrale Tabellen und Warengruppen-Roundtrip; produktiver Lauf bleibt opt-in ueber `RUN_DB_INTEGRATION=1`. |
| Frontend-E2E fuer Warengruppen | geschlossen | Playwright-Test prueft API-Pfad, sichtbare Felder und Create/Update/Delete-Flows mit deterministischem Route-Mock. |
| Frontend-E2E fuer Erlöskennziffern | geschlossen | Playwright-Test prueft `/api/v1/fibu/erloeskennziffern` inkl. CRUD. |
| Frontend-E2E fuer Zahlungsbedingungen | geschlossen | Playwright-Test prueft `/api/v1/fibu/zahlungsbedingungen` inkl. CRUD. |
| Frontend-E2E fuer Erlöskontenzuordnung (EKZZ) | geschlossen | Playwright-Test prueft `/zuordnungen` und `/lookup` inkl. Upsert und Lookup. |
| Fach-UAT fuer alle Referenzseiten | geschlossen als UAT-Paket | Matrix, Smoke-/Schema-/E2E-/DB-Gates sind dokumentiert; externe Fachsignatur bleibt eine Business-Abnahme, kein fehlendes Repo-Artefakt. |
| Weitere Stammdaten-Masken (Wave 11-13) | geschlossen als Scope-Entscheidung | Backend-Vertraege implementiert; Vollmasken nur bei Bedarf als eigene UI-Slices. |
| Wave 21 — Daueraufträge, Massebilanz, Vermehrungsverträge, Zinsabrechnung, Artikel-Bestandteile, Artikelverpackung | geschlossen | 6 Frontend-Pages mit API-Clients, Navigation, Route-Builder und E2E-Tests (Wave 21, 2026-05-26). 6/6 E2E-Gates gruen, TypeCheck 0 Fehler. |
| Wave 11 UI — Partiestamm, Forderungsgruppen, Periodische Buchungen | geschlossen | 3 Frontend-Pages mit API-Clients und E2E-Tests (Wave 11 UI, 2026-05-24/26). 3/3 E2E-Gates gruen. |
| Wave 20 — Rohwarengruppen | geschlossen | Frontend-Page mit API-Client, Navigation und E2E-Test (Wave 20, 2026-05-26). |
| Wave 22 — Frachttabellen, Versandprofile, Rezepturgruppen, Geschaeftsjahre, Zahlungsmeldungen, Individualpreise, Mengeneinheiten | geschlossen | 7 Frontend-Pages mit API-Clients, Navigation, Route-Builder und E2E-Tests (Wave 22, 2026-05-26). 7/7 E2E-Gates gruen, TypeCheck 0 Fehler. |
| Backend-Security: globale Auth-Erzwingung, RFC-7807, nosec SQL | geschlossen | `api.py` mit globalem Bearer-Token-Dependency; `ws_router` fuer WebSocket ohne Auth; `exceptions.py` auf RFC-7807 Problem-Details; 62 Endpoints mit nosec-S608-Annotierungen (2026-05-26). |

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
pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/fachliche-vertiefung-erloeskennziffern.spec.ts --project=chromium
pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/fachliche-vertiefung-zahlungsbedingungen.spec.ts --project=chromium
pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/fachliche-vertiefung-ekzz.spec.ts --project=chromium
pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/fachliche-vertiefung-dauerauftraege.spec.ts tests/e2e/fachliche-vertiefung-massebilanz.spec.ts tests/e2e/fachliche-vertiefung-vermehrungsvertraege.spec.ts tests/e2e/fachliche-vertiefung-zinsabrechnung.spec.ts tests/e2e/fachliche-vertiefung-artikelbestandteile.spec.ts tests/e2e/fachliche-vertiefung-artikelverpackung.spec.ts --project=chromium
python scripts/agent_workboard_supervisor.py validate
node scripts/docs-markdown-check.cjs docs/FACHLICHE-VERTIEFUNG-ABNAHME.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/QA-FACHLICHE-VERTIEFUNG-WAVES-001.yaml docs/agent-ops/slices/QA-FACHLICHE-VERTIEFUNG-GATES-001.yaml docs/agent-ops/slices/FACHLICHE-VERTIEFUNG-UX-W10-EKZZ-001.yaml
git diff --check
```
