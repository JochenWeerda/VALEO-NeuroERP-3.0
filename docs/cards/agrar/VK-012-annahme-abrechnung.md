---
card_id: VK-012
chain: harvest-to-settlement
chain_step: 7
card_type: process-step
flow_spine: flow-spine-harvest-to-settlement
workflow_doc: docs/workflows/vk-012-annahme-abrechnung.md
---
# VK-012 — Annahme-Abrechnung (Card)

**Slice:** VK-012 | **Owner:** Claude Sonnet 4.6 | **Datum:** 2026-03-27
**Status:** abgeschlossen

---

## 1. Zweck

Settlement-Anlage nach Ernte-Annahme: Abzugsberechnung (Trocknung/Reinigung/Fracht), Freigabe-Workflow und FIBU-Verbuchung als Abschluss der Annahmekette.

## 2. Betroffene Dateien

- `packages/frontend-web/src/pages/annahme/rohware.tsx` — Rohware-Schnellerfassung
- `packages/frontend-web/src/pages/annahme/abrechnung.tsx` — Settlement-Flow
- `docs/workflows/vk-012-annahme-abrechnung.md` — Workflow-Analyse

## 3. Fachlicher Kontext

Die Abrechnung schließt den Annahme-Kreislauf. Der Landwirt liefert Rohware; nach Wägung und optionaler Qualitätserfassung wird ein Settlement-Beleg angelegt. Abzüge werden regelbasiert berechnet (DryingRuleEngine), dann durch Sachbearbeiter und Abteilungsleiter freigegeben und schließlich automatisch als Journal Entry in die FIBU gebucht.

## 4. API-Endpoints

| Endpoint | Methode | Zweck |
|---|---|---|
| `/api/v1/agrar/harvest-acceptance` | POST | Rohware-Annahme anlegen |
| `/api/v1/agrar/settlements` | GET | Settlement-Liste |
| `/api/v1/agrar/settlements` | POST | Settlement anlegen |
| `/api/v1/agrar/settlements/billing-weight/preview` | POST | Abrechnungsgewicht Vorschau |
| `/api/v1/agrar/settlements/drying/compute` | POST | Trocknungsabzug berechnen |
| `/api/v1/agrar/settlements/preview` | POST | Settlement Gesamtvorschau |
| `/api/v1/agrar/settlements/{id}/freigabe` | POST | Freigabe-Schritt |
| `/api/v1/agrar/settlements/{id}/post-fibu` | POST | FIBU-Verbuchung |
| `/api/v1/agrar/settlements/{id}/cancel` | POST | Storno |

## 5. Datenfluss-Übergaben

```
rohware.tsx → navigate('/annahme/abrechnung', {
  state: { fromQualitaetsCheck: true, artikel, feuchtigkeit, verunreinigung }
})

abrechnung.tsx → useEffect([location.state]) → setForm(prefilled values)
```

## 6. Abzugslogik

| Bedingung | Abzugstyp | Berechnung |
|---|---|---|
| feuchtigkeit > 14% | drying | rate_per_ton × billing_weight |
| verunreinigung > 2% | cleaning | rate_per_ton × billing_weight |
| freightFixed > 0 | freight | fixed_amount |

**Primärpfad:** DryingRuleEngine → `invoice_weight_kg` (aus crop_code + moisture_pct)
**Fallback:** billing-weight/preview → `billing_weight_kg`

## 7. Freigabe-Zustands-Automat

```
ENTWURF → ZUR_FREIGABE → TEILWEISE_FREIGEGEBEN → FREIGEGEBEN → VERBUCHT
                                                 ↓
                                              ABGELEHNT
```

## 8. Optimistic Locking

Alle schreibenden Operationen (post-fibu, freigabe, cancel) senden `expected_row_version`. Bei 409 + `code: row_version_conflict` → queryClient.invalidateQueries + User-Toast.

## 9. Behobene Bugs

### Bug VK-012-B1: Falsche POST-URL in rohware.tsx

- **Symptom:** Rohware-Annahme liefert 404
- **Ursache:** `POST /api/v1/harvest-acceptance` — fehlender `/agrar/`-Prefix
- **Backend:** Route registriert als `prefix="/agrar/harvest-acceptance"` in `api.py:679`
- **Fix:** URL korrigiert auf `/api/v1/agrar/harvest-acceptance`
- **Datei:** `rohware.tsx:119`

## 10. Offene Punkte

| ID | Beschreibung | Priorität |
|---|---|---|
| VK-012-P1 | `getStepValidationError` im Rohware-Wizard | ~~Mittel~~ erledigt in **VK-020** |
| VK-012-P2 | Supplier-ID CRM-Dropdown statt Freitext | Mittel |
| VK-012-P3 | Artikel/Lager-Listen aus API (statt hardcoded) | Niedrig |

## 11. Tests

Manuelle Testschritte:
1. Rohware-Annahme Wizard durchlaufen → Annahmenummer erhalten (kein 404)
2. "Zur Abrechnung" → feuchtigkeit/artikel werden prefilled
3. Supplier-ID eingeben → Preview berechnen → Settlement anlegen
4. Freigabe ENTWURF → ZUR_FREIGABE → FREIGEGEBEN
5. FIBU verbuchen → Journal Entry geprüft
6. Optimistic Locking: gleichzeitiger Zugriff → 409 → Toast

## 12. Doku-Updates

- `docs/workflows/vk-012-annahme-abrechnung.md` — Vollanalyse (Sektionen A-G)
- `docs/cards/agrar/VK-012-annahme-abrechnung.md` — diese Karte

## 13. Handoff

**Nächster Slice:** VK-013 Ernte-Kampagne-Abschluss (Gesamtabrechnung über alle Settlements)
**Oder:** VK-012-P1 Rohware-Wizard Schritt-Validierung als eigenständiger Sub-Slice

---

*Erstellt von Claude Sonnet 4.6 — Slice VK-012 — 2026-03-27*
