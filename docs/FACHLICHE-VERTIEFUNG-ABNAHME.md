# Fachliche Vertiefung - QA-Abnahme Wave 1-13

Stand: 2026-05-22

## Ergebnis

Die fachliche Vertiefung Wave 1-13 ist repo-seitig fuer den aktuellen Abnahmepfad freigegeben, nachdem die QA-Blocker aus der Erstpruefung geschlossen wurden:

- Alembic-Head-Konflikt ist durch `merge_heads_20260522` bereinigt.
- Wave 11-13 sind committed und Bestandteil dieser Abnahme.
- Zentrale Wave-10-13-Stammdatenrouten haben TestClient-Smokes fuer Registrierung, Listen, Duplicate-/Missing-Fehlerpfade und 204-Delete.
- Warengruppen-Frontend nutzt den neuen Backend-Vertrag `/api/v1/stammdaten/warengruppen`.
- Offene Vollabdeckungsgrenzen sind als UAT-/DB-/E2E-Gates ausgewiesen.

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
| 10 | Warengruppen, Erloeskennziffern, Zahlungsbedingungen | implementiert inkl. Update-Contracts | `fachliche_vertiefung_wave10_20260521` | Warengruppen-Liste angebunden | Schema/Unit + API-Smoke |
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

Die neuen API-Smokes testen bewusst ohne laufende PostgreSQL-Instanz. DB-Integration bleibt ein separates UAT-Gate.

### UI/UX

Die bestehende Warengruppen-Seite war vor der QA auf einen alten Einkaufs-Endpoint und veraltete Felder verdrahtet. Sie nutzt jetzt den neuen Stammdaten-Endpoint und zeigt `gruppe_nr`, `bezeichnung` und `ober_id`.

Alle weiteren Wave-1-13-Funktionen sind aktuell backend-only. Das ist kein verdeckter Abschluss, sondern ein dokumentierter Produktumfang: produktive Bedienoberflaechen fuer diese Stammdaten brauchen eigene UX-Slices mit Fachmasken, Rechte-/Rollenmodell, Validierungsfeedback und E2E-Tests.

## Restgates

| Gate | Status | Begruendung |
|---|---|---|
| DB-Integrationstest gegen PostgreSQL | offen | benoetigt migrierte Testdatenbank und echte Transaktionspruefung |
| Frontend-E2E fuer Warengruppen | offen | benoetigt laufendes Frontend/API-Setup |
| Fach-UAT fuer alle Referenzseiten | offen | 5.118 Hilfeseiten koennen nicht allein durch Schema-Smokes als fachlich voll gleichwertig bewiesen werden |
| Weitere Stammdaten-Masken | offen, nicht blocker fuer Backend-Abnahme | braucht separate UI-Slices je Domaene |

## Pruefkommandos

```powershell
alembic heads
python -m py_compile alembic/versions/merge_heads_20260522.py app/api/v1/endpoints/warengruppen.py app/api/v1/endpoints/erloeskennziffern.py app/api/v1/endpoints/zahlungsbedingungen.py tests/test_api_smoke_waves.py
pytest tests/test_api_smoke_waves.py tests/test_fachliche_vertiefung_wave10.py tests/test_fachliche_vertiefung_wave11.py tests/test_fachliche_vertiefung_wave12.py tests/test_fachliche_vertiefung_wave13.py -q --no-cov
pnpm --filter @valero-neuroerp/frontend-web type-check
python scripts/agent_workboard_supervisor.py validate
node scripts/docs-markdown-check.cjs docs/FACHLICHE-VERTIEFUNG-ABNAHME.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/QA-FACHLICHE-VERTIEFUNG-WAVES-001.yaml
git diff --check
```
