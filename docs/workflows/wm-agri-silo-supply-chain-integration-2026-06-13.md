# WM-AGRI-SILO-001 â€” Integration: Prozessketten, Tools, Gap-Abschluss

**Stand:** 2026-06-13
**Ziel:** Agrar-**Materialfluss** und **Silozellen** fachlich und navigierbar an die bestehenden **Lieferketten-** und **Logistik-Prozessketten** anbinden; offene â€žMedienbruchâ€œ-Punkte **benennen** vs. **repo-seitig geschlossen** (Doku + UI-SprÃ¼nge).

---

## 1. Bezug zu DOM-SUPPLY-004 (RÃ¼ckverfolgbarkeit)

| Thema | DOM-SUPPLY-004 | WM-AGRI-SILO-001 |
|--------|----------------|------------------|
| RÃ¼ckgrat | Wiegeschein `weighing_tickets` â†’ Annahme â†’ `silo_lots` â†’ Settlement | **Parallel:** digitales **Anlagen-/FÃ¶rdermodell** (`material_flow_nodes`/`edges`, `silo_cells`) je **Warehouse** + **Tenant** |
| QS / Sperre | Lot-Folgeaktionen, Event-Log (`supply_chain_events`) | `qs_status` auf **Silozelle**, Knoten-`status`, Kanten-`status`; **validate-route** prÃ¼ft u. a. QS-Sperre am Ziel |
| Mengen / Schwund | Trace-Service: Mengen-Konsistenz Stufe-zu-Stufe | Materialfluss: **kein** kg-RÃ¼ckgrat (bewusst); Verschleppungs-**Hinweis** Ã¼ber `previous_material_id` bei Route |
| UI | `lager/rueckverfolgbarkeit` | `lager/materialfluss`, `lager/materialfluss-visualisierung` |

**Gap (bewusst offen, nÃ¤chste Wellen):** Es gibt noch **keine** automatische VerknÃ¼pfung `silo_lots` â†” `material_flow_nodes` (z. B. `ref_type=silo_cell` + Lot-Update). Das ist **Slice-Futter** (z. B. WM-AGRI-CHAIN-002), nicht Teil von SILO-001.

**Repo-seitig geschlossen (2026-06-13):** Fachliche **Zuordnung** und **Operator-Sprung**: Materialfluss-Toolbar â†’ **RÃ¼ckverfolgbarkeit**; Doku-Verweise (diese Datei, `docs/warehouse/README.md`, Handbuch-Inventar).

---

## 2. Bezug zur physischen Kette (Logistik-Welle)

Siehe [wave-physical-chain-logistics-audit-2026-06-12.md](./wave-physical-chain-logistics-audit-2026-06-12.md): **Waage â†’ â€¦ â†’ Lieferschein â†’ Tour/Fracht â†’ Traceability (read)**.

| Schnittstelle | Status |
|---------------|--------|
| `delivery_note_ref` auf Tour-Stops, Read-Spine LS | umgesetzt (LOG-SPINE-*) |
| Fracht simulate + Traceability-Tickets | Ketten-Test LOG-CHAIN-001 |
| **Lager-intern: Silo-FÃ¶rderweg** vor Verladung | **Modell** in WM-AGRI-SILO-001; **kein** zusÃ¤tzlicher Kernel-Event-Typ â€” Anbindung an `supply_chain_events` optional spÃ¤ter |

---

## 3. Tool-Integration (KI / MCP / Bediener)

| Mechanismus | Nutzen |
|-------------|--------|
| `PageToolbar` **`mcpContext`** (`pageDomain`, `availableActions`) | KI-gestÃ¼tzte Aktionen kÃ¶nnen Kontext â€žinventory / materialflussâ€œ nutzen (`PageToolbar.tsx`, MCP-Metadaten) |
| Toolbar **Overflow** â€žRÃ¼ckverfolgbarkeitâ€œ | Schnellwechsel zur **DOM-SUPPLY-004**-OberflÃ¤che ohne URL-Kopieren |
| Externes **Handbuch** `C:\Handbuch` | [handbuch-c-inventar.md](../warehouse/handbuch-c-inventar.md) â€” Warenflussdiagramm Brandhub als **Soll-Prozess** zum Abgleich mit dem digitalen Graph |

---

## 4. Gap-Matrix (Abschluss-Status)

| ID / Thema | Vorher | Nach Stand 2026-06-13 |
|------------|--------|-------------------------|
| Kein dokumentierter **Ketten-Bezug** SILO â†” SUPPLY-004 | Medienbruch in KÃ¶pfen | **Geschlossen** (diese Workflow-Datei + Warehouse-README) |
| Kein UI-Sprung **Materialfluss â†” RÃ¼ckverfolgbarkeit** | separate Silos | **Geschlossen** (Overflow-Aktion) |
| **Ereignis-/Trace-Kopplung** FÃ¶rderkante â†” `supply_chain_events` | fehlend | **Offen** (Slice-Vorschlag WM-AGRI-CHAIN-002 o. Ã¤.) |
| **Lot-Bestand** â†” Silozelle im Graph | fehlend | **Offen** (DomÃ¤nenmodellierung) |
| Bird-View Luftbild | offen | **Offen** (WM-AGRI-MAP-001) |

---

## 5. Verweise

- Slice: [WM-AGRI-SILO-001](../agent-ops/slices/WM-AGRI-SILO-001.yaml)
- DOM-SUPPLY-004: [dom-supply-004-traceability-2026-06-10.md](../dom-supply-004-traceability-2026-06-10.md)
- Logistik-Audit: [wave-physical-chain-logistics-audit-2026-06-12.md](./wave-physical-chain-logistics-audit-2026-06-12.md)
- Futtermittel-Kette (parallel): [wave-physical-chain-feed-production-audit-2026-06-12.md](./wave-physical-chain-feed-production-audit-2026-06-12.md)
- Design: [EMPFEHLUNG.md](../design/EMPFEHLUNG.md) (PageToolbar)
