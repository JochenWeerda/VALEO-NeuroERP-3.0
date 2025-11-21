# Frontend – EPCIS Eventliste & KPI-Widget

## Übersicht
Die EPCIS-UI zeigt Events je Mandant und einfache KPIs (Anzahl, Top-biz_steps).

## Komponenten/Dateien
- Service: `packages/frontend-web/src/lib/services/inventory-service.ts`
- Seite: `packages/frontend-web/src/pages/inventory/epcis/index.tsx`

## Nutzung
- Tenant setzen im Eingabefeld (Standard `default`), Limit wählen (50/100/200).
- Filter: `biz_step`, `sku`.
- KPIs und Tabelle aktualisieren sich nach Reload.

## API-Zugriff
- `GET /api/v1/inventory/epcis/events` (Header `X-Tenant-Id`)
- `POST /api/v1/inventory/epcis/events` (Header `X-Tenant-Id`)

## Betrieb
- Rate-Limits und Circuit Breaker greifen serverseitig.
- Eskalationen bei anhaltenden Fehlern via Teams/E-Mail (Notifier).

## Tests (manuell)
1) Tenant `default` – Events anzeigen
2) Filter `biz_step=receiving` – Tabelle reduziert sich
3) SKU-Filter – Teilstring-Match
4) Reload – Daten neu laden



