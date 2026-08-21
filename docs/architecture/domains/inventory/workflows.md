---
title: Inventory — Workflows
type: explanation
audience: [entwickler]
owner: domain/inventory
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Inventory — Workflows

Inventur-Nebenlauf: Inventur waehlen -> unveraenderlichen Zaehllisten-,
Import-, Kontroll-, Bewertungs- oder Vortragsbatch erzeugen -> Hash pruefen ->
durch abweichenden Benutzer reviewen/freigeben -> Import oder Bestandsvortrag
idempotent uebernehmen. Kontrolle und Bewertung bleiben nebenwirkungsfrei.

MDE-Inventurzaehlung (`L3-MDE-INBOX-003`): Geraet ->
Mobile-Sync-Vorvalidierung -> `domain_ops.mobile_event_queue` ->
Inventory-Handler -> kanonische Bestandsbewegung. Fehler wechseln nach
begruendetem Retry und dem dritten Fehlversuch in `quarantined`.

- Wareneingang / -ausgang — Process Map Lager
- Agrar-Materialfluss: Überschneidung mit [agrar](../agrar/workflows.md) (`agri_silo_*`)
- Einkauf → WE: [c4-procurement-inventory.md](../../views/components/c4-procurement-inventory.md)
