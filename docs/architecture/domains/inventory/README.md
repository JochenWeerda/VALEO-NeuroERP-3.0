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

## MDE-Eingang

## Inventur-Nebenlaeufe

`lager/inventur-nebenlaeufe` fuehrt Zaehlliste, kontrollierten Import,
Kontrolllauf, vorlaeufige Bewertung und Bestandsvortrag als hashgebundene,
auditierte Batches ueber der kanonischen Inventur.

## Fremdware und Fremdbestand

`lager/fremdware` projiziert die kanonische Fremdwaren-Einlagerung als
serverseitig paginierte Meridian-Worklist. Mandant und Eigentuemer bleiben
sichtbar; Umbuchung und Teil-/Vollauslagerung sind statusvalidiert und mit
Benutzer, Pflichtgrund sowie Vorher-/Nachherwerten append-only auditiert.

`L3-MDE-INBOX-003` nutzt den plattformseitigen Mobile-Sync-Kern als kanonische
Eingangsqueue. Inventurzaehlungen werden erst nach Vorvalidierung und
idempotenter Queue-Verarbeitung in die Inventory-Domaene delegiert. Die
Operator-Maske `schnittstelle/mde-inbox` ist eine native, serverseitig
paginierte Meridian-Worklist; die Queue selbst bleibt in `domain_ops`.
