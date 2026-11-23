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
