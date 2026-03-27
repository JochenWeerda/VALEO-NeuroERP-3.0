# Card: CTS-001 — Contract-to-Settlement

| Feld | Wert |
|------|------|
| **Card-ID** | CTS-001 |
| **Name** | Contract-to-Settlement (Kontrakt bis Abrechnung) |
| **Flow-Spine** | `flow-spine-contract-to-settlement` |
| **Prozessbereich** | Kontrakthandel / Agrar / Verkauf / Einkauf |
| **Status** | Erstanalyse abgeschlossen |
| **Erstellt** | 2026-03-27 |
| **Bearbeiter** | Cursor Agent |

## Zweck

Vollstaendige Workflow-Analyse des Kontraktlebenszyklus im Landhandel — von Anlage ueber Abruf, Lieferung, Fakturierung bis Kontraktschliessung. Fokus auf Praxistauglichkeit fuer Agrargenossenschaften und Landhandelsunternehmen.

## Betroffene Bereiche

### Frontend
- `pages/kontrakte/FrmKontraktDetail.tsx` — Kontraktstammdaten und Positionen
- `pages/kontrakte/LstKontraktUebersicht.tsx` — Kontraktliste
- `pages/kontrakte/DlgKontraktUmSaetze.tsx` — Umsaetze-Dialog
- `pages/kontrakte/DlgAuswahlVerkaufKontrakte.tsx` — Lookup-Dialog
- `pages/kontrakte/FrmKontraktProtokoll.tsx` — Audit-Protokoll
- `pages/sales/order-editor.tsx` — Auftrag (Kontraktnr. auf Position)
- `pages/verkauf/lieferschein-erfassung.tsx` — Lieferschein (Kontraktnr. auf Position)
- `lib/api/kontrakte.ts` — API-Client

### Backend
- `app/api/v1/endpoints/kontrakte.py` — CRUD + Movements + Audit + Lookup
- `app/api/v1/endpoints/contract_pricing_api.py` — Preismatrix + Lots
- `app/services/kontrakte_service.py` — Validation, Security, Audit, Restmengen, Nummernkreis
- `app/services/position_guard_service.py` — Short-Violation-Check
- `app/domains/operations/models.py` — KonContract, KonContractLine, KonContractMovement

## Workflow-Dokumentation

Siehe: [docs/workflows/cts-001-contract-to-settlement.md](../../workflows/cts-001-contract-to-settlement.md)

## Card-Zerlegung (15 Cards)

| Card-ID | Name | Ist-Stand | Kritikalitaet |
|---------|------|-----------|---------------|
| C01 | VK-Kontrakt anlegen | Grundfunktion ✓ | Sperr-/Kreditpruefung fehlt |
| C02 | EK-/ZK-Kontrakt anlegen | Grundfunktion ✓ | Agrarspezifik lueckenhaft |
| C03 | MATIF-Preisfixierung | Datenmodell ✓, Prozess ✗ | **KRITISCH** |
| C04 | Kontrakt aendern | Funktional ✓ | Konsistenz-Check fehlt |
| C05 | Lieferschein/Auftrag mit Kontraktbezug | **Nur Freitext** | **KRITISCH** |
| C06 | Movement buchen | API ✓, Automation ✗ | **KRITISCH** |
| C07 | Restmengen-Ueberwachung | Berechnung ✓, Alarm ✗ | mittel |
| C08 | Storno | Mechanisch ✓ | Folgebeleg-Check fehlt |
| C09 | Loeschen | Physisch ✗ | GoBD-Risiko |
| C10 | Kontraktliste | Funktional ✓ | Spalten unvollstaendig |
| C11 | Audit-Protokoll | Gut ✓ | Export fehlt |
| C12 | Teillieferungen | Datenmodell ✓, Prozess ✗ | **KRITISCH** |
| C13 | Fakturierung gegen Kontrakt | ✗ | hoch |
| C14 | Kontrakt schliessen | Manuell ✓ | Automatik fehlt |
| C15 | Externe Uebernahme | ✗ | mittel (Ausbau) |

## Top-4-Risiken (kritisch)

1. Kontraktnummer auf Belegen ist nur Freitext — keine Preisuebernahme, keine Mengensteuerung
2. Movements werden nicht automatisch aus Belegfluss erzeugt
3. MATIF-Preisfixierung hat kein UI
4. Teillieferungen nicht verdrahtet

## Empfohlene naechste Slices

| Slice-ID | Thema | Prio | Status |
|----------|-------|------|--------|
| CTS-002 | Kontraktbindung auf Belegen (echte Referenz) | P1 | **umgesetzt** |
| CTS-003 | Automatische Movement-Buchung | P1 | **umgesetzt** |
| CTS-004 | MATIF-Preisfixierungs-Dialog | P2 | **umgesetzt** |
| CTS-005 | Soft-Delete und Bestaetigung | P2 | **umgesetzt** |
| CTS-006 | Kontraktliste aufwerten | P3 | **umgesetzt** |
| CTS-007 | Tabs differenzieren | P3 | **umgesetzt** |
| CTS-008 | Alarm-Dashboard | P3 | **umgesetzt** |
| CTS-009 | Rohwaren-Positionsmonitor (Long/Short) | P1 | **umgesetzt** |

## Lane-Hinweis

Dieser Slice gehoert zur **Kontrakt-Lane** und hat Ueberlappung mit:
- **Order-to-Cash** (Auftrag, Lieferschein, Rechnung)
- **Harvest-to-Settlement** (Ankaufskontrakte, Ernte-Annahme)
- **Procure-to-Pay** (Einkaufskontrakte, Bestellvorschlag)

Bei paralleler Arbeit: Dateien in `pages/kontrakte/` und `lib/api/kontrakte.ts` gehoeren zu CTS. Aenderungen an `order-editor.tsx` und `lieferschein-erfassung.tsx` muessen mit der OTC-Lane und der VK-Lane abgestimmt werden.
