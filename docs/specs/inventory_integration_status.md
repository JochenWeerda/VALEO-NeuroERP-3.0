# Inventory-Integration – Ist-Analyse (Stand 2025-11-14)

Ziel dieses Dokuments ist der Abgleich zwischen dem neuen Inventory-Service (`services/inventory`) und den bestehenden Frontend-/Domain-Integrationen. Grundlage: Task *inv-next-1* aus dem Must-Have-Plan.

---

## 1. Backend-Funktionalität (FastAPI)

| Endpoint | Datei | Schema | Status |
| --- | --- | --- | --- |
| `GET /api/v1/inventory/warehouses` | `app/api/v1/endpoints/warehouses.py` | `list[WarehouseRead]` | **Implementiert** |
| `POST /api/v1/inventory/warehouses` | s.o. | `WarehouseCreate → WarehouseRead` | **Implementiert** |
| `POST /api/v1/inventory/{warehouse_id}/locations` | `endpoints/locations.py` | `LocationCreate → LocationRead` | **Implementiert** |
| `GET /api/v1/inventory/lots` | `endpoints/inventory.py` | `LotListResponse` (Suchfilter) | **Implementiert** |
| `POST /api/v1/inventory/receipts` | s.o. | `ReceiptCreate → StockItemRead` | **Implementiert** |
| `POST /api/v1/inventory/transfers` | s.o. | `TransferCreate → StockItemRead` | **Implementiert** |
| `GET /api/v1/inventory/lots/{lot_id}` | s.o. | `LotTraceResponse` | **Implementiert** |

**Schemen (Auszug)**: `WarehouseCreate`, `LocationCreate`, `ReceiptCreate`, `TransferCreate`, `LotListResponse` etc. befinden sich in `services/inventory/app/schemas`.

**Mandantenkontext**: `resolve_tenant_id` (Header `X-Tenant-Id`, Fallback `settings.DEFAULT_TENANT`).

**EventBus**: optionaler NATS-Publisher über Dependency `get_event_bus()`.

---

## 2. Domain-Events aus dem Inventory-Service

Alle Events werden über `EventBus.publish` mit Prefix `settings.EVENT_BUS_SUBJECT_PREFIX` (Default `inventory`) gesendet. Payload-Struktur:

```jsonc
{
  "eventId": "uuid",
  "eventType": "<type>",
  "aggregateId": "<uuid>",
  "aggregateType": "<entity>",
  "eventVersion": 1,
  "occurredOn": "...",
  "tenantId": "<tenant>",
  "data": { ... }
}
```

### Bereits implementierte Eventtypen

| Event | Auslöser | Datenfelder |
| --- | --- | --- |
| `inventory.warehouse.created` | `InventoryService.create_warehouse` | `warehouseId`, `code`, `name`, `createdAt` |
| `inventory.location.created` | `add_location` | `locationId`, `warehouseId`, `code`, `locationType` |
| `inventory.goods.received` | `receive_stock` | `stockItemId`, `lotId`, `warehouseId`, `locationId`, `quantity`, `reference`, `receiptTimestamp`, `sku`, `lotNumber` |
| `inventory.stock.transferred` | `transfer_stock` | `sourceStockItemId`, `lotId`, `sourceWarehouseId`, `destinationWarehouseId`, `sourceLocationId`, `destinationLocationId`, `quantity`, `reference`, `transferTimestamp` |
| `inventory.lot.trace.requested` | `trace_lot` | `lotId`, `sku`, `lotNumber`, `transactionCount` |

**Gaps**: Es existiert noch kein Event-Consumer für eingehende Domain-Events (z. B. `purchase.receipt.posted`, `manufacturing.batch.completed`). Außerdem fehlen Saga-/Workflow-Hooks.

---

## 3. Frontend-/API-Verbrauch

### 3.1 React Query basierte API (`packages/frontend-web/src/lib/api/inventory.ts`)

| Hook | REST Endpoint | Backend-Status |
| --- | --- | --- |
| `useWarehouses` | `GET /api/v1/inventory/warehouses?is_active=` | **✅** (Filter wird direkt umgesetzt) |
| `useWarehouse` | `GET /api/v1/inventory/warehouses/{id}` | **✅** |
| `useCreateWarehouse` | `POST /api/v1/inventory/warehouses` | **✅** |
| `useUpdateWarehouse` | `PUT /api/v1/inventory/warehouses/{id}` | **✅** |
| `useDeleteWarehouse` | `DELETE /api/v1/inventory/warehouses/{id}` | **✅** |

### 3.2 Weitere Seiten/Hooks (Fetch)

| Frontend-Datei | Erwarteter Endpoint | Backend-Verfügbarkeit |
| --- | --- | --- |
| `features/inventory/StockManagement.tsx` | `/api/v1/inventory/articles`, `/warehouses`, `/stock-movements` | **✅** (Artikel- & Bewegungsendpunkte ergänzt) |
| `pages/inventory-reports.tsx`, `InventoryDashboard.tsx` | `/api/v1/inventory/reports/*` (stock-levels, alerts, replenishment, turnover) | **✅** (Turnover-Analyse aktuell noch Placeholder) |
| `pages/inventory.tsx`, `features/*` | Diverse Realtime-Feeds (WebSocket/MCP) | **nicht angebunden** |

**Offene Punkte**:
- Artikel-/Report-Daten nutzen vereinfachte SKU-Aggregate (keine Stammdatenpreise).
- Realtime-Feeds / SSE sind weiterhin offen.

---

## 4. Event/Workflow-Erwartungen anderer Domains

Basierend auf ursprünglicher Gap-Beschreibung:

| Erwarteter Event (extern) | Zweck | Ist-Zustand |
| --- | --- | --- |
| `inventory.stock.received` (exposed) | Trigger für Finance/Compliance | **Teilweise** (`inventory.goods.received` publiziert) |
| `inventory.stock.adjusted/reserved` | Integration mit Order- und Manufacturing-Domains | **Reserviert fehlt noch**, `inventory.stock.adjusted` existiert |
| `inventory.batch.tracked` | Mehrlager/Chargen-Tracking | **LotTrace event vorhanden**, Workflow-Hook über `inventory_inbound_flow` |
| Eingehend: `purchase.receipt.posted`, `sales.order.shipped`, `manufacturing.batch.completed` | Automatische Lagerbuchungen | **Teilweise** (purchase/sales angebunden, Manufacturing offen) |

### Neue Event-Consumer

| Subject | Verarbeitung | Ergebnis |
| --- | --- | --- |
| `purchase.receipt.posted` | `InventoryEventSubscribers._handle_purchase_receipt` | Erzeugt Wareneingänge via `ReceiptCreate` pro Zeile |
| `sales.shipment.confirmed` | `_handle_sales_shipment` | Reduziert Bestand via `issue_stock` |

Consumer werden beim Start automatisch aktiviert, sofern `INVENTORY_EVENT_BUS_ENABLED=true`. Weitere Subjects können analog ergänzt werden.

---

## 5. Zusammenfassung & Empfehlungen

1. **API-Lücken schließen**
   - Reports/Analytics weiter ausbauen (echte KPIs, Historie, Pagination).
   - Artikel-Response um Stammdatenfelder (Preis, Kategorie) ergänzen, sobald Master-Data-Service steht.
2. **Frontend-Abgleich**
   - Query-Hooks gegen neue Routen testen; ggf. Response-Mapper ergänzen, bis Stammdaten verfügbar sind.
3. **Domain-Events**
   - Event-Contracts in `packages/shared/contracts` formalisieren; weitere Subscriptions (Manufacturing, Reservations) hinzufügen.
4. **Workflow/Policy**
   - `inventory_inbound_flow` um Reservierungs-/Ausnahme-Transitions erweitern, sobald passende Events (`inventory.stock.reserved`) existieren.
5. **Monitoring**
   - Prometheus-Metriken/Alerts für Event-Consumer (Lag, Fehler) ergänzen.

Dieses Dokument dient als Referenz für die nächsten Tasks (`inv-next-2`, `inv-next-3`).

