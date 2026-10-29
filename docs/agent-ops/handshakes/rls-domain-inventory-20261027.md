---
title: Handshake RLS-DOMAIN-INVENTORY-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Übergabe Claude → Codex für die RLS-Domain inventory (ohne Silo/Materialfluss, Agrar und Dienst-Tabellen) mit Fachkorrekturen an Rüstlisten, NVE, Artikelerweiterungen, POS-Retoure und BVL-Meldung.
---

# Handshake RLS-DOMAIN-INVENTORY-20261027 (Claude Code → Codex)

## Basis und Reihenfolge

- Basis: `claude/rls-domain-crm-20261027` (#76). Der PR zielt auf den CRM-Zweig und wird nach #76 integriert.
- Alembic: `rls_domain_crm_20261027 → rls_domain_inventory_20261027`. `alembic heads` zeigt einen einzigen Head.

## Prüfstand

Das Fenster wurde nach deiner Freigabe genutzt: 100 Verhaltenstests ohne Übersprung, Gegenprobe ohne
Verbund-FKs 55 rot, mit den alten Endpunkten 10 rot. Die gewachsene Datenbank habe ich nur lesend geprüft:
keine Zeile ohne Mandant, kein Verweis über Mandantengrenzen.
Danach steht `valeo_probe` unverändert auf `loading_stop_fk_20261023`, 0 offene Sitzungen.

## Abgrenzung zu deinen Claims

1. **MATERIAL-FLOW-SQL:** Ich habe keine Silo- oder Materialflusstabelle angefasst (`silos`, `silo_cells`,
   `silo_lots`, `silo_lot_movements`, `silo_systems`, `material_flow_*`) und keine Datei der Materialflussdienste.
   Ihre Verweise auf Lager, Zonen, Plätze und Gänge bleiben einfache Schlüssel. Die Eltern haben jetzt
   `UNIQUE (id, tenant_id)`, ein späterer Silo-Slice kann direkt darauf aufsetzen.
   **Berührungspunkt:** `inventory_stock_movements` (Buchungen der Spülcharge, Lot-Link) steht jetzt unter RLS
   und verweist über `(article_id, tenant_id)`, `(bin_id, tenant_id)` und `(warehouse_id, tenant_id)`.
   Buchungen ohne Mandantenkontext schlagen fehl, Buchungen auf Artikel oder Plätze eines anderen Mandanten auch.
2. **Agrar:** `agrar_contracts`, `weighing_tickets` und `agrar_contract_allocations` sind unverändert.
   `weighing_ticket_lines.article_id` (P5) bekam den Verbund-FK zum Artikel.
3. **P5-Tabellen** bekamen nur Schlüssel, keine Policy-Änderung (Liste im QA-Dokument).

## Für dich

1. **Live-relevant (Wege mit Mandant aus Query oder Rumpf):** `/preparation-lists*`, `/nve`, `/articles/batches`,
   `/articles/selections*`, `/pos/retoure`, `/compliance/bvl-umsaetze`, `/compliance/ustva` nehmen jetzt
   den Token-Mandanten. Ein mitgegebenes `?tenant_id=` oder `tenant_id` im Rumpf wird ignoriert.
2. **POS-Retoure:** Unbekannter Artikel → 422, gescheiterte Buchung → 500. Bisher kam in beiden Fällen
   „erfolgreich gebucht“. Die Maske `pos/retoure` (Studio) sollte die Fehlermeldung zeigen.
3. **PSM-Nachweis** (`compliance/pflanzenschutz-nachweis`, `/compliance/bvl-umsaetze`): Die Abfrage war
   immer leer, weil sie eine fehlende Spalte nannte. Sie zählt jetzt Artikel mit `pflanzenschutzmittel = true`.
   Live sind das 0 Artikel; 8 Artikel der Kategorie „Pflanzenschutz“ müssen gepflegt werden. Fehler ergeben 500.
4. **Lieferantenregister** `/articles/{id}/suppliers` endete immer mit 500 (Filter auf `ArticleSupplier.tenant_id`,
   das Modell kennt die Spalte nicht). Jetzt filtert es über den mandantengeprüften Artikel. Das Modell bleibt
   ohne Spalte, damit Code und Migration nicht gekoppelt ausgerollt werden müssen.
5. OpenAPI nur für die sieben Pfade oben und `RetourRequest`. Die vorbestehende Drift
   (`/finance/closing-checklists*`, `/agrar/biostimulanzien*`, `/weighing-tickets*`) bleibt bei dir.
6. `tests/rls_domain_support.py`: `assert_tenant_isolation(values=...)` für feste Spaltenwerte (Belegart-Trigger),
   zufällige eindeutige Ganzzahlen passen in `numeric(p,s)`. Alle bisherigen Domain-Tests bestehen damit.
7. Folgebefunde (QA-Dokument): `/compliance/ustva` meldet „EINGEREICHT“ ohne Übermittlung; `POST /pos/checkout`
   meldet „completed“ ohne Buchung; Lose und EPCIS-Ereignisse verweisen ohne FK.
8. Nicht berührt: Dienst-Tabellen und `services/*`, deine Lead-Slices (Agrar, Materialfluss), Studio/Masken,
   Systemrollen, Live.
