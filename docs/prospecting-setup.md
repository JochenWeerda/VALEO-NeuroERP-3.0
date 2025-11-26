# Prospecting Setup Guide

Die Prospecting-Kette (GAP → Snapshot → Customer-Analytics → UI) besteht aus mehreren Schritten. Diese Anleitung fasst alles zusammen, damit du die Pipeline lokal oder in einer Stage-Umgebung schnell aktivieren kannst.

## 1. Datenbank vorbereiten

1. **Analytics-Felder im Customer-Table**

   ```bash
   psql $DATABASE_URL -f database/analytics-customer-fields.sql
   ```

   Dadurch werden sämtliche `analytics_*`-Spalten (GAP-/Potenzial-Werte, Flags) einmalig angelegt.

2. **GAP-Basis-Tabellen**

   Falls noch nicht erfolgt, das komplette GAP-Schema einspielen:

   ```bash
   psql $DATABASE_URL -f database/analytics-gap.sql
   ```

## 2. GAP-Pipeline ausführen

Die CLI befindet sich unter `scripts/gap-cli.ts`. Ein kompletter Jahreslauf (Import → Aggregation → Matching → Snapshot → Hydrate) sieht so aus:

```bash
pnpm ts-node scripts/gap-cli.ts run-year \
  --year 2025 \
  --csv-path ./data/impdata2025.csv
```

Alternativ können die Schritte einzeln ausgeführt werden (`import`, `aggregate`, `match`, `snapshot`).

## 3. Customer Analytics hydratisieren

Zusätzlich zum TypeScript-Command gibt es eine SQL-basierte Version (`database/analytics-hydrate-customers.sql`). Beide Varianten nutzen denselben Filter:

- Nur `customer_potential_snapshot` für das angegebene Jahr.
- Nur Kunden, bei denen `analytics_block_auto_potential_update = FALSE`.

Ausführung via CLI:

```bash
pnpm ts-node scripts/gap-cli.ts hydrate-customers --year 2025
```

oder direkt per SQL (falls notwendig):

```bash
psql $DATABASE_URL -v year=2025 -f database/analytics-hydrate-customers.sql
```

## 4. Prospecting-UI aktivieren

1. `.env` (oder CI-Secret) um folgenden Eintrag ergänzen:

   ```
   VITE_ENABLE_PROSPECTING_UI=true
   ```

2. Frontend builden / dev-server neu starten, damit das Flag greift.

   - Das Flag steuert sowohl den Tab „Potential & Leaddaten“ in der Kundenmaske als auch die Route `/prospecting/leads` (Lead Explorer) inklusive Navigationsmenü.

## 5. UI prüfen

1. **Kundenmaske** öffnen → Tab „Potential & Leaddaten“:
   - Anzeigen: KPI-Karten, GAP-Herkunft, Produktpotenziale.
   - Switches testen („Stammkunde (geschützt)“, „Automatische Updates sperren“).
   - Für Tests ggf. Dummy-Werte direkt in `customers.analytics_*` setzen.

2. **Lead Explorer** (`/prospecting/leads`):
   - Filter (Jahr, Segment, Potenzial, Quelle, „Nur neue Prospekte“) verändern.
   - Aktionen testen („Lead anlegen“, „Kunde öffnen“, „Aufgabe“ – aktuell mit TODO-Handlern).

## 6. Tests / Sanity-Checks

- Es existiert ein kleiner Vitest (`packages/frontend-web/src/api/__tests__/prospecting.test.ts`), der sicherstellt, dass `fetchLeadCandidates` die Query-Parameter korrekt aufbaut.
- Für E2E- oder UI-Tests (Playwright/Cypress) können die gleichen Routen verwendet werden; ggf. Dummy-GAP-Daten in `gap_payments` und `customer_potential_snapshot` einspielen.

## 7. Zusammenfassung

1. `database/analytics-customer-fields.sql`
2. `database/analytics-gap.sql`
3. GAP-Pipeline (`scripts/gap-cli.ts run-year --year <Y> --csv-path <file>`)
4. `scripts/gap-cli.ts hydrate-customers --year <Y>`
5. `VITE_ENABLE_PROSPECTING_UI=true`
6. UI prüfen (Kunden-Tab + Lead Explorer)

Damit ist die Prospecting-Kette vollständig funktionsfähig.
