# Übergabe an Codex: E2E Full UAT aus M0-CI-GESAMTBASIS herausgelöst (23.11.2026)

Meilenstein M0. Absender: Cursor (M0-E2E-FULL-UAT-20261123).

## Anlass

Der Workflow „E2E Full UAT Tests“ ist auf main seit mindestens 09.11.2026 jeden Tag rot. `M0-CI-GESAMTBASIS-20261115`
ist seit 15.11. reserviert; an den betroffenen Specs gab es seither keinen Codex-Commit. Der Nutzer hat am 23.11. die
Umsetzung aller offenen Meilensteine beauftragt.

## Befund

Lauf 45156197226 (main `bbe18fb8f`): alle 21 roten `@full`-Tests – CRM 360 (16), Zahlungsabgleich (3),
POS-Fiskalisierung (2) – zeigen im Seitenabbild die SSO-Anmeldeseite. `.github/workflows/e2e-full.yml` startet weder
den Test-Keycloak noch Postgres/Redis, installiert keine Python-Abhängigkeiten und migriert nicht. Seit dem Wegfall des
Dev-Tokens am 12.10.2026 läuft der Workflow deshalb unangemeldet. `e2e-critical.yml` zeigt den richtigen Aufbau.

## Abgrenzung

- Cursor übernimmt nur E2E Full UAT (Dateibesitz im Workboard-Eintrag `M0-E2E-FULL-UAT-20261123`).
- Bei Codex bleiben: Sonar-Abdeckung neuer Zeilen (main 71,4 % statt 80 %) und Runtime API Sweep
  (`RUNTIME-FIVE-503-20261117`; im Lauf 45161980314 u. a. 503 auf `/agrar/psm/proplanta/*`,
  `/portal/handelspartner`, `/sustainability/nutrients/crop`, dazu SQL-Fehler `einkauf_retouren.created_at`).

Falls Codex E2E Full UAT selbst schon bearbeitet: bitte im Workboard melden, dann gibt Cursor den Claim zurück.

## Nachtrag 23.11.2026: Befund für CRM-ACTIVITY-CANONICAL-20261029 (P1)

„Aktivität anlegen“ aus der Kundenakte schlägt im Browser immer mit 422 fehl (Lauf 45275876249, Backend-Log:
`POST /api/v1/crm/customers/{id}/actions/create_activity` → 422; die Maske zeigt „Request failed with status code 422“).

Ursache: Kopf- und Fußaktionen der nativen Detailseite übergeben den Datensatzkontext als Payload
(`ActionFooterRenderer` → `UniversalNativeDetailPage.handleAction` → `useActionRuntime`; nur `responseAdapter`- und
`commandBinding`-Aktionen werden auf die deklarierten Eingaben beschränkt). `create_activity_action` in
`app/api/v1/endpoints/crm_360.py` lehnt seit f84db0298 jedes Feld außer `betreff, typ, datum, verantwortlich, notiz`
ab („Invalid activity action envelope“). Gleiches Muster in `mask_actions.py` (Verkaufschance, „Invalid activity mask
envelope“). Die Python-Tests rufen den Endpunkt nur mit den fünf Feldern auf und sehen den Fehler deshalb nicht.

Lösungswege (Entscheid bei Codex, Datei liegt in deinem Claim): Endpunkt übernimmt nur die fünf Felder und verwirft
den Kontext, oder die Aktion deklariert eine Payload-Beschränkung, die die Laufzeit auf die `inputFields` reduziert.
Abnahme: `test.fixme` „Aktivitaet anlegen erscheint im Abschnitt Aktivitaeten“ in
`playwright-tests/specs/crm/crm360-kundenakte.spec.ts` scharf schalten; er bedient die Maske gegen das echte Backend.
