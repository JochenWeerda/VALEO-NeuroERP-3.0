# Phase 6 Completion Report — Agriculture Backend + Erweiterung

**Datum:** 2026-03-05
**Referenz:** `gap/gaps-agriculture.md`, `.cursor/plans/gap-closure_master_plan_ab0cb3b1.plan.md`
**Maturity-Fortschritt:** ~85% → ~88%

---

## 1. Implementierte Capabilities

| ID | Capability | Endpoint | Beschreibung |
|----|------------|----------|--------------|
| **AGR-OPS-04** | Feldkalender | `GET /agrar/feldbuch/calendar?von=&bis=` | Geplante und durchgeführte Maßnahmen nach Datum (Filter: customer_id, schlag_id) |
| **AGR-FLD-03** | Feldblockfinder | `GET /agrar/config/feldblockfinder` | URLs pro Bundesland (DE-BY, DE-NW, DE-NI, DE-BW) für iframe-Integration |
| **AGR-COM-04** | QS/GQS-Export | `POST /agrar/compliance/qs-export?jahr=&format=` | Strukturierte Feldbuch-Daten für QS-Audits |
| **AGR-COM-05** | LEA-Export | `POST /agrar/compliance/lea-export?jahr=` | Aggregierte Flächen- und Kulturdaten für Förderanträge |
| **AGR-INV-04** | Mindestbestand-Warnung | `GET /agrar/inventory/low-stock?threshold=` | Artikel mit Bestand ≤ Schwellwert (Saatgut, Dünger, PSM) |

---

## 2. Bereits vorhanden (vor Phase 6)

| ID | Capability | Quelle |
|----|------------|--------|
| AGR-COM-01 | Düngebilanz | `GET /agrar/feldbuch/duengebilanz` |
| AGR-COM-03 | Cross-Compliance | `GET /agrar/feldbuch/cross-compliance` |
| AGR-COM-02 | PSM-Compliance | Validierung in Massnahme-Erfassung |
| AGR-FLD-01/02 | Schlagverwaltung | CRUD in `agrar_feldbuch.py` |

---

## 3. Geänderte Dateien

| Datei | Änderung |
|-------|----------|
| `app/api/v1/endpoints/agrar_feldbuch.py` | +5 Endpoints (Feldkalender, Feldblockfinder, QS/LEA-Export, Low-Stock); Imports Duenger, PSM, Saatgut |

---

## 4. Dokumentation

- [`docs/GAP-CLOSURE-SUMMARY.md`](GAP-CLOSURE-SUMMARY.md) — Phase 6 ergänzt
- [`docs/GAP-UND-TODO-INDEX.md`](GAP-UND-TODO-INDEX.md) — Phase-6-Report verlinkt

---

## 5. Offen (Phase 6+)

- AGR-OPS-03: Mitarbeiter-Zuordnung (`assigned_employee_id`) in Maßnahmen — erfordert Migration
- AGR-FLD-04/05: GIS-Visualisierung, Polygon-Erfassung (P1/P2)
- AGR-OPS-05: GPS-Tracking (P3)
- AGR-INV-01/02/03: Bestandsführung Dünger/PSM/Saatgut — Stammdaten vorhanden, Bestandslogik im Inventory-Modul ausbauen
