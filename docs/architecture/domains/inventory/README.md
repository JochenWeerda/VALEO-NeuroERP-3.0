---
title: Inventory Domain Pack
type: explanation
audience: [entwickler, architect]
owner: domain/inventory
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Inventory / Lager — Domain Pack

Lager, Bestand, Warenbewegungen, Silo/Materialfluss (Agrar-Überschneidung).

## Navigation

| Thema | Datei |
|---|---|
| API | [api.md](api.md) |
| Workflows | [workflows.md](workflows.md) |
| Tests | [tests.md](tests.md) |
| Entscheidungen | [decisions.md](decisions.md) |

## Sichten

- [C4 Einkauf/Lager](../../views/components/c4-procurement-inventory.md)
- Container: `inventory-service`, `backend`

## UIX / Universal Mask Generator

Inventory/Lager ist fuer die zweite Generator-Welle relevant, weil Listen und
Tabellen hier besonders gross werden. Neue generatorfaehige Listen muessen
serverseitige Pagination, Sortierung, Filterung und `VirtualDataTable`-Eignung
dokumentieren. Bestehende Lager- und Artikelmasken bleiben bis zur Paritaet auf
ihrem aktuellen Renderer.
