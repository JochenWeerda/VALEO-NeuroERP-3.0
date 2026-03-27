# INV-001 — Inventory-to-Settlement (Card)

**Slice:** INV-001 | **Lane:** Inventory-to-Settlement | **Status:** abgeschlossen
**Owner:** Claude Opus 4.6 | **Datum:** 2026-03-27

---

## 1. Zweck

End-to-End Analyse der Lager-Lane: Einlagerung → Bestandsführung → Kommissionierung →
Verladung → Abrechnung. Prüfung aller 11 beteiligten Masken auf API-Korrektheit,
CRUD-Vollständigkeit und Flow-Spine-Integration.

## 2. Betroffene Dateien

- `packages/frontend-web/src/pages/lager/einlagerung.tsx` — hardcoded Artikel/Lagerorte
- `packages/frontend-web/src/pages/lager/auslagerung.tsx` — gemischte apiClients
- `packages/frontend-web/src/pages/lager/lagerbewegungen.tsx` — Full CRUD (ok)
- `packages/frontend-web/src/pages/lager/terminal.tsx` — Barcode-Scan (ok)
- `packages/frontend-web/src/pages/lager/inventur.tsx` — kein Create
- `packages/frontend-web/src/pages/lager/lagerplaetze.tsx` — Mock-Kapazität
- `packages/frontend-web/src/pages/lager/bestandsuebersicht.tsx` — Dashboard (ok)
- `packages/frontend-web/src/pages/verladung/liste.tsx` — Touren (ok)
- `packages/frontend-web/src/pages/verladung/lkw-beladung.tsx` — Touch-Beladung (ok)

## 3. API-Endpoints

| Endpoint | Methode | Zweck |
|---|---|---|
| `/api/v1/lager/einlagerung` | POST | Wareneingang buchen |
| `/api/v1/lager/auslagerung` | POST | Warenausgang buchen |
| `/api/v1/inventory/stock-movements` | GET/POST/PUT/DELETE | Lagerbewegungen CRUD |
| `/api/v1/articles` | GET | Artikelsuche (Barcode, Liste) |
| `/api/v1/inventory/warehouses` | GET | Lagerort-Stammdaten |
| `/api/v1/inventory/inventur` | GET | Inventurliste |
| `/api/v1/inventory/inventur/complete` | POST | Inventur abschließen |
| `/api/v1/inventory/inventur/{id}` | DELETE | Inventur stornieren |
| `/api/v1/inventory/mhd-warnings` | GET | MHD-Artikel |
| `/api/v1/inventory/top-sellers` | GET | Renner |
| `/api/v1/inventory/slow-movers` | GET | Penner |

## 4. Client-Warnung

- `einlagerung.tsx` nutzt `@/lib/api-client` (AxiosResponse) — korrekt mit `.data`
- `auslagerung.tsx` mischt `@/lib/axios` (POST) + `@/lib/api-client` (GET) — inkonsistent
- `terminal.tsx` nutzt `@/lib/api-client` — korrekt mit `.data`
- `lagerbewegungen.tsx` nutzt Service-Abstraktion über `@/lib/api-client` — korrekt

## 5. Offene Punkte

| ID | Beschreibung | Priorität |
|---|---|---|
| INV-001-P1 | Einlagerung: Artikel aus API statt hardcoded Array | Hoch |
| INV-001-P2 | Einlagerung: Lagerorte aus API statt hardcoded Array | Hoch |
| INV-001-P3 | Auslagerung: POST auf einheitlichen apiClient umstellen | Mittel |
| INV-001-P4 | Lagerplätze: echte Kapazitätsberechnung statt Mock | Mittel |
| INV-001-P5 | Flow-Spine Instance-ID durch alle Lager-Masken durchreichen | Mittel |

## 6. Tests (manuell)

1. Terminal → Barcode scannen → Artikel erkannt → Navigation zu Einlagerung
2. Einlagerung → Charge + Artikel + Menge + Lagerort → POST erfolgreich
3. Auslagerung → Artikel auswählen → FIFO → POST erfolgreich
4. Lagerbewegungen → Neue Bewegung → Edit → Delete
5. Inventur → Position abschließen → Differenz wird berechnet
6. Bestandsübersicht → MHD-Warnungen und Renner/Penner korrekt

---

*Erstellt von Claude Opus 4.6 — Slice INV-001 — 2026-03-27*
