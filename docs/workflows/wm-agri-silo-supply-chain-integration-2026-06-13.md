# WM-AGRI-SILO-001 — Integration: Prozessketten, Tools, Gap-Abschluss

**Stand:** 2026-06-19 (Ist-Abgleich Code ↔ Doku)
**Ziel:** Agrar-**Materialfluss** und **Silozellen** fachlich und navigierbar an die bestehenden **Lieferketten-** und **Logistik-Prozessketten** anbinden; offene Medienbruch-Punkte **benennen** vs. **repo-seitig geschlossen** (Doku + UI-Sprünge).

---

## 0. Code-Ist (2026-06-19)

| Komponente | Status im Repo | Nachweis |
|------------|----------------|----------|
| Stammdaten Siloanlage / Silozelle / Knoten / Kante | **Implementiert** | `AgriSiloMaterialFlowService`, API `/lager/wms/agri/*`, UI `lager/materialfluss` |
| Route-Validierung (QS-Sperre, Verschleppungshinweis) | **Implementiert** | `validate_route`, UI „Route prüfen“ |
| Live-Graph (React Flow) | **Implementiert** | `material-flow-display.ts`, Demo nur ohne Lagerwahl |
| Silozellen PATCH (Material, Lot, QS, Layout, VK) | **Implementiert** | API + Tabellen in `materialfluss.tsx` |
| `current_stock_kg` auf Silozellen | **Implementiert** | Migration `wms_material_flow_stock_link_20260619`, UI Spalte **Ist kg** |
| `layout_x` / `layout_y` / `updated_at` | **Implementiert** | Migration `agri_silo_cells_layout_20260619`, Visualisierungs-Editor |
| Materialtransfer kg-Buchung | **Implementiert** (Slice **WMS-FLOW-001**) | `book_material_transfer`, `POST …/material-flow/transfer`, Transfer-Card UI |
| Supply-Chain-Events bei Mutationen | **Implementiert** (Slice **WM-AGRI-CHAIN-002**) | `supply_chain_events` + Outbox `inventory.material_flow.*` |
| Transfer-Hooks in einer Transaktion | **Implementiert** | `commit()` nach `_emit_material_flow_hooks`; Test `test_transfer_commits_after_trace_hooks` |
| Lot-/Bestands-Sync `silo_lots` ↔ Graph | **Offen** | Folge-Slice **WM-AGRI-LOT-LINK** |
| Bird-View / Hofplan MapLibre | **Offen** | **WM-AGRI-MAP-001** |
| PLC / OPC-UA Live-Anlagen | **Offen** | **WM-AGRI-PLC-005** (Architektur only) |

---

## 1. Bezug zu DOM-SUPPLY-004 (Rückverfolgbarkeit)

| Thema | DOM-SUPPLY-004 | WM-AGRI-SILO-001 |
|--------|----------------|------------------|
| Rückgrat | Wiegeschein `weighing_tickets` → Annahme → `silo_lots` → Settlement | **Parallel:** digitales **Anlagen-/Fördermodell** (`material_flow_nodes`/`edges`, `silo_cells`) je **Warehouse** + **Tenant** |
| QS / Sperre | Lot-Folgeaktionen, Event-Log (`supply_chain_events`) | `qs_status` auf **Silozelle**, Knoten-`status`, Kanten-`status`; **validate-route** prüft u. a. QS-Sperre am Ziel |
| Mengen / Schwund | Trace-Service: Mengen-Konsistenz Stufe-zu-Stufe | **WMS-FLOW-001:** kg-Transfer zwischen Silozellen → `inventory_stock_movements` + `current_stock_kg`; kein automatischer Abgleich mit `silo_lots` |
| UI | `lager/rueckverfolgbarkeit` | `lager/materialfluss`, `lager/materialfluss-visualisierung` |

**Gap (bewusst offen, nächste Wellen):** Es gibt noch **keine** automatische Verknüpfung `silo_lots` ↔ `material_flow_nodes` (Lot-Update / Bestands-Sync). Folge-Slice **WM-AGRI-LOT-LINK** (CHAIN-002 deckt Event-Log + Outbox ab).

**Repo-seitig geschlossen (2026-06-13):** Fachliche **Zuordnung** und **Operator-Sprung**: Materialfluss-Toolbar → **Rückverfolgbarkeit**; Doku-Verweise (diese Datei, `docs/warehouse/README.md`, Handbuch-Inventar).

**Repo-seitig geschlossen (2026-06-19):** **Materialtransfer** inkl. Lagerbuchung und UI (Slice **WMS-FLOW-001**).

---

## 2. Bezug zur physischen Kette (Logistik-Welle)

Siehe [wave-physical-chain-logistics-audit-2026-06-12.md](./wave-physical-chain-logistics-audit-2026-06-12.md): **Waage → … → Lieferschein → Tour/Fracht → Traceability (read)**.

| Schnittstelle | Status |
|---------------|--------|
| `delivery_note_ref` auf Tour-Stops, Read-Spine LS | umgesetzt (LOG-SPINE-*) |
| Fracht simulate + Traceability-Tickets | Ketten-Test LOG-CHAIN-001 |
| **Lager-intern: Silo-Förderweg** vor Verladung | **Modell** WM-AGRI-SILO-001; **Ereignisse** WM-AGRI-CHAIN-002; **kg-Buchung** WMS-FLOW-001 |

---

## 3. Tool-Integration (KI / MCP / Bediener)

| Mechanismus | Nutzen |
|-------------|--------|
| `PageToolbar` **`mcpContext`** (`pageDomain`, `availableActions`) | KI-gestützte Aktionen können Kontext „inventory / materialfluss“ nutzen (`PageToolbar.tsx`, MCP-Metadaten) |
| Toolbar **Overflow** „Rückverfolgbarkeit“ | Schnellwechsel zur **DOM-SUPPLY-004**-Oberfläche ohne URL-Kopieren |
| Externes **Handbuch** `C:\Handbuch` | [handbuch-c-inventar.md](../warehouse/handbuch-c-inventar.md) — Warenflussdiagramm Brandhub als **Soll-Prozess** zum Abgleich mit dem digitalen Graph |

---

## 4. Gap-Matrix (Abschluss-Status)

| ID / Thema | Vorher | Nach Stand 2026-06-19 |
|------------|--------|------------------------|
| Kein dokumentierter **Ketten-Bezug** SILO ↔ SUPPLY-004 | Medienbruch in Köpfen | **Geschlossen** (diese Workflow-Datei + Warehouse-README) |
| Kein UI-Sprung **Materialfluss ↔ Rückverfolgbarkeit** | separate Silos | **Geschlossen** (Overflow-Aktion) |
| **Ereignis-/Trace-Kopplung** Förderkante ↔ `supply_chain_events` + Outbox | fehlend | **Geschlossen** (Slice **WM-AGRI-CHAIN-002**, 2026-06-13) |
| **kg-Transfer** Silozelle ↔ `inventory_stock_movements` | fehlend | **Geschlossen** (Slice **WMS-FLOW-001**, 2026-06-19): Backend + UI + Mobile-Sync |
| **Lot-Bestand** ↔ Silozelle im Graph (automatisch) | fehlend | **Offen** (WM-AGRI-LOT-LINK) |
| Bird-View Luftbild | offen | **Offen** (WM-AGRI-MAP-001) |
| PLC / Live-Anlagen | offen | **Offen** (WM-AGRI-PLC-005) |

---

## 5. `current_material_id` / `current_lot_id` / `current_stock_kg` auf Silozellen

**Ist (Stammdaten + Buchung):**

- `current_material_id`, `current_lot_id`: optional, per PATCH und UI pflegbar (keine Auto-Sync aus WE/Waage).
- `current_stock_kg`: wird bei **WMS-FLOW-001**-Transfer aktualisiert; in UI als **Ist kg** sichtbar (neben **Kap. kg** = `capacity_kg`).
- Umbuchung / Silo-Umfüllung: über Transfer-Card auf `lager/materialfluss` (Operator-gesteuert, auditierbar via Bewegungen + CHAIN-002-Events).

**Soll (spätere Integration, WM-AGRI-LOT-LINK):**

| Quelle / Ereignis | Erwartetes Mapping |
|-------------------|--------------------|
| Annahme / WE | Material und Lot der angenommenen Partie als Vorschlag für Ziel-Silozelle (Operator-Bestätigung) |
| Waage / Wiegeschein | Verknüpfung über Trace-Spine (`weighing_tickets`, DOM-SUPPLY-004); Lot-ID aus Ticket → `current_lot_id` + kg |
| QS-Freigabe / Sperre | `qs_status` steuert Routen/Kanten; Lot bleibt referenziert, bis Umbuchung oder Entladung |
| Mischauftrag / MMX | Verbrauchsmaterial aus Zelle → Auftrag; `current_*` nach Abschluss aktualisieren |

**Bereits vorhanden:** Rückverfolgbarkeit `lager/rueckverfolgbarkeit`, Supply-Chain-Events (CHAIN-002), Transfer-API (WMS-FLOW-001). **Fehlend:** Regel-Engine „Ticket/Lot → Silozelle“ als konsistente Transaktion ohne manuelle Eingabe.

---

## 6. Verweise

- Slice Stammdaten/Graph: [WM-AGRI-SILO-001](../agent-ops/slices/WM-AGRI-SILO-001.yaml)
- Slice Transfer/Buchung: [WMS-FLOW-001](../agent-ops/slices/WMS-FLOW-001.yaml)
- Slice Events/Outbox: [WM-AGRI-CHAIN-002](../agent-ops/slices/WM-AGRI-CHAIN-002.yaml)
- DOM-SUPPLY-004: [dom-supply-004-traceability-2026-06-10.md](../dom-supply-004-traceability-2026-06-10.md)
- Logistik-Audit: [wave-physical-chain-logistics-audit-2026-06-12.md](./wave-physical-chain-logistics-audit-2026-06-12.md)
- Futtermittel-Kette (parallel): [wave-physical-chain-feed-production-audit-2026-06-12.md](./wave-physical-chain-feed-production-audit-2026-06-12.md)
- Design: [EMPFEHLUNG.md](../design/EMPFEHLUNG.md) (PageToolbar)
