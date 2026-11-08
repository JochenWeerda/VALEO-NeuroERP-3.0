# Bestellung Dual-Pfad — Detail-Einstiege auf Native

Stand: 2026-10-22 · Slice `MASK-BESTELLUNG-NAV-NATIVE-20261022`

## Auftrag

Einstiege, die eine **bestehende** Einkaufsbestellung oeffnen und noch auf
Legacy-Plural `/einkauf/bestellungen/:id` (`bestellung-stamm`) zeigten, auf die
kanonische UniversalMaskRuntime-Route `/einkauf/bestellung/:id`
(`bestellung-native`, SD `einkauf/purchase-order`) umhaengen. Neuanlage bleibt
`/einkauf/bestellungen/neu`. Legacy-Plural bleibt UIX-057-Rollback.

## Analyse

| Einstieg | Stand vor diesem Slice | Rolle |
|----------|------------------------|-------|
| `bestellungen-liste` als `NativeListPage` + SD `einkauf/bestellungen` | `row_route=/einkauf/bestellung/{id}` (MASK-STUDIO-ROLLOUT) | Primaernav bereits native |
| MCP / Voice `einkauf.bestellung.status` | `/einkauf/bestellung/{id}` | bereits kanonisch |
| `bestellung-anlegen` (Pfad aus Auftrag) | `/einkauf/bestellung/:id` | bereits native |
| `bestellung-anlegen` Resume nach Speichern / Flow-Spine | `/einkauf/bestellungen/:id` | Legacy-Plural → migriert |
| `angebot-stamm` inBestellung | `/einkauf/bestellungen/:id` | Legacy-Plural → migriert |
| Neuanlage / Policy | `/einkauf/bestellungen/neu` | Create bleibt Legacy |

### Native SD-Tragfaehigkeit (`einkauf/purchase-order`)

- `adapter.temporary=false`, Meridian-Layout (`objectPage`, `contextRail=workflow`)
- Tabs inkl. Positionen und Kommunikation (Lesetabelle)
- `workflow.phases` (ProcessBand)
- Actions: Bearbeiten, Speichern (CE), Versenden (CE)
- Datenquelle `/api/v1/einkauf/bestellungen/{id}`

## Umgesetzt

| Quelle | Nachher |
|--------|---------|
| `einkauf/bestellung-anlegen` Resume + `resumeRoute` | `/einkauf/bestellung/:id` |
| `einkauf/angebot-stamm` (inBestellung) | `/einkauf/bestellung/:id` |
| Primaerliste | unveraendert NativeListPage; Detail weiter ueber Listen-SD `row_route` |

## Paritaetsluecken (Legacy unter `/einkauf/bestellungen/:id`)

| Luecke | Legacy | Native |
|--------|--------|--------|
| DocumentCaseBand / Fallbindung in der Maske | ja | ProcessBand-Phasen ja; CaseBand nein |
| Positionsallokation | ja | nein |
| Freigeben / Stornieren am Detail | ja | Listen-Aktionen (Studio) / CE; nicht 1:1 Legacy-UI |
| Kommunikation senden | ja | nur Lesetabelle |
| Create / Wizard | `bestellung-anlegen` | kein Create in Objekt-SD |

## Tests

```bash
cd packages/frontend-web && npx vitest run src/__tests__/pages/mask-bestellung-nav-native.test.ts
python scripts/mask_route_migration_inventory.py
```

## Inventar

941 / 61 runtime_wired / 122 legacy / 757 hand_built — Delta 0 Klassen
(`bestellung-native` war bereits runtime_wired).
