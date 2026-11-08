---
title: Handshake RLS-DOMAIN-EINKAUF-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Übergabe Claude → Codex für die RLS-Domain einkauf mit Fachkorrekturen an Beschaffungswegen, Bestellstatus, Waren- und Rechnungseingängen; Live-Blocker DEMO-PO-001/002.
---

# Handshake RLS-DOMAIN-EINKAUF-20261027 (Claude Code → Codex)

## Basis und Reihenfolge

- Basis: `claude/rls-domain-inventory-20261027` (#77). Der PR zielt auf den inventory-Zweig und wird nach #77 integriert.
- Alembic: `rls_domain_inventory_20261027 → rls_domain_einkauf_20261027`. `alembic heads` zeigt einen einzigen Head.

## Prüfstand

Das Fenster wurde nach deiner Freigabe genutzt: 50 Verhaltenstests ohne Übersprung, Gegenprobe ohne
Verbund-FKs 19 rot, mit dem alten Code 7 rot. Die gewachsene Datenbank habe ich nur lesend geprüft.
Danach steht `valeo_probe` unverändert auf `loading_stop_fk_20261023`, 0 offene Sitzungen.

## Für dich

1. **Live-Blocker:** `DEMO-PO-001/002` (Mandant `00000000-0000-0000-0000-000000000001`) verweisen auf den
   Lieferanten `019ca040-5090-79fd-95ea-f4d3e9b4ff26` des Mandanten `valeo`. Die Migration bricht live
   absichtlich ab. Herkunft klären, dann umhängen oder als Demodaten entfernen. Ich habe nichts geändert.
2. **Live-relevant:** Die fünf `/api/v1/procurement/...`-Wege ignorieren `X-Tenant-ID` und nehmen den
   Token-Mandanten. Ohne Token-Mandant kein Rückfall auf `"default"` mehr.
3. **Fachkorrekturen:** Bestellstatus, Rechnungseingänge (Prüfen, Freigeben, Verbuchen) und die
   Wareneingangsliste arbeiten nur noch im eigenen Mandanten. Die Wareneingangsliste war vorher immer leer
   (Join auf das nicht vorhandene `docs_store`).
4. **P5-Tabellen:** Fünf `einkauf_*`-Tabellen bekommen statt `DEFAULT 'default'` den Kontextmandanten als
   Vorgabe; drei Verweise (`kontrakte.lieferant_id`, `artikel_lager_parameter.std_lieferant_id`,
   `rfq_quotes.rfq_id`) werden Verbund-FKs. Policies unverändert.
5. OpenAPI nur für die fünf Beschaffungspfade. Die vorbestehende Drift (`/finance/closing-checklists*`,
   `/agrar/biostimulanzien*`, `/weighing-tickets*`) bleibt bei dir.
6. `tests/rls_domain_support.py`: `probe` gewährt `USAGE` auf die Sequenzen der Schemata.
7. **Prüfprotokoll Rechnungseingang:** Akteur ist jetzt der angemeldete Nutzer (vorher ein beliebiger aktiver Nutzer
   des Mandanten). Ohne eindeutige lokale Nutzerzuordnung antworten Prüfen/Freigeben/Verbuchen mit 403.
8. Folgebefunde (QA-Dokument): drei D-Tabellen fehlen in der gewachsenen DB; keine Tabelle für Lieferantenretouren.
9. Nicht berührt: Codex-Claims (Agrar, Allokationen, MATERIAL-FLOW-SQL), Studio/Masken, Systemrollen, Live.
