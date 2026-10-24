# Primaere Listen-Navigation auf Native-Routen

Stand: 2026-10-22 · Slice `MASK-PRIMARY-NAV-NATIVE-20261022`

## Auftrag

Frontend-Masken-Migrationsstand messen und offene, funktionssichere
Verdrahtungen fortsetzen: wo UIX-057 bereits eine native Detailroute und
`*-native`-Wrapper vorsieht, sollen Listen bestehende Datensaetze dort oeffnen.
Neuanlage bleibt auf Legacy, bis Create-Paritaet nachgewiesen ist.

## Messung (route-inventory.gen.json)

Skript: `python scripts/mask_route_migration_inventory.py`

Artefakt: `docs/architecture/uix/mask-route-migration-inventory.md`

| Metrik | Frueher (Referenz) | 2026-10-22 |
|--------|--------------------|------------|
| handgebaute Routen | 442 | 757 |
| Routen mit alten Maskenmustern (ObjectPage/ListReport ohne Runtime) | 80 | 122 |
| Runtime-verdrahtet (UMR / UniversalMaskRenderer / UniversalNativeDetailPage) | — | 61 |
| Studio-Entwuerfe | 154 | nicht gemessen (keine `DATABASE_URL` / `TEST_DATABASE_URL` in dieser Session) |
| Registrierte ScreenDefinition-Builder | — | 102 |

Hinweis: Die Absolute `hand_built` ist nicht 1:1 mit 442 vergleichbar — die
aktuelle Inventur umfasst **941** generierte Routen. Studio-Entwuerfe sind
**kein** Nachweis produktiver Ablösung.

## Umgesetzte Verdrahtung (low risk laut UIX-057)

| Liste | Vorher (Detail) | Nachher (Detail) | Neuanlage |
|-------|-----------------|------------------|-----------|
| `agrar/saatgut-liste` | `/agrar/saatgut-stamm/:id` | `/agrar/saatgut/:id` → `saatgut-native` | `/agrar/saatgut-stamm` |
| `agrar/duenger-liste` | `/agrar/duenger-stamm/:id` | `/agrar/duenger/:id` → `duenger-native` | `/agrar/duenger-stamm` |
| `einkauf/lieferanten-liste` | `/einkauf/lieferant/:id` | `/einkauf/lieferanten/:id` → `supplier-native` | `/einkauf/lieferant/neu` |

Legacy-Module bleiben unter ihren Pfaden erreichbar (Rollback UIX-057).

## Bewusst nicht umgestellt (Stand damaliger Slice)

- ~~`einkauf/bestellungen/:id` → weiterhin `bestellung-stamm`~~ → nachgezogen in
  `MASK-BESTELLUNG-NAV-NATIVE-20261022` (Listen/Folgebelege → native; Create Legacy;
  Paritaetsluecken CaseBand/Allokation/Freigabe-Detail/Komm-Senden bleiben).
- Beleg-Alt-Einstiege (14er Matrix) — Create/Edit ueber Belegfamilie vorhanden,
  Sonderfeld-/Kettenparitaet offen; STUDIO-BELEG-THEME bei Codex.
- CRM Opportunity Create (`/crm/opportunity/new`) — Legacy ObjectPage mit
  Operational-Panels; Detail `:id` ist bereits native.

## Tests

```bash
cd packages/frontend-web && npx vitest run src/__tests__/pages/mask-primary-nav-native.test.ts
python scripts/mask_route_migration_inventory.py
```

## Risiken

Studio-Import oder YAML allein ersetzt keine Runtime-Verdrahtung. Native
Lieferanten-SD deckt nicht Sperre/Archiv/Banken/Duplikatcheck des 1741-Zeilen-
Legacy-Stamms — diese Funktionen bleiben ueber Legacy-URL erreichbar.
