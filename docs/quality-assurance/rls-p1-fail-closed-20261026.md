---
title: RLS P1 Mandantenkontext fail-closed (2026-10-26)
type: qa
audience: [entwickler, qa, agent]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# RLS P1: Mandantenkontext fail-closed (2026-10-26)

Slice `RLS-P1..P7-20261026`, Phase P1, Zweig `claude/rls-p1-fail-closed-20261026` (gestapelt auf
P0, PR #56). Plan: `docs/architecture/rls-mandantenkernel-plan.md`.

## Aenderung

- `app/core/tenant_context.py`: kein Standardwert mehr. `get_current_tenant_id()` wirft
  `TenantContextMissing`, `current_tenant_or_none()` fragt ohne Ausnahme; leerer Mandant wird
  nicht gesetzt. Neu `tenant_scope(tenant, grund)` und `cross_tenant_scope(grund)` (loescht den
  Mandanten, markiert die Arbeit fuer die Systemverbindung aus P6).
- `app/core/tenant_registry.py`: Mandanten fuer Hintergrundarbeit nur aus
  `domain_shared.tenants` (Klasse D, auch unter RLS lesbar); `for_each_tenant` isoliert Fehler je
  Mandant.
- Worker je Mandant: Herden-Sync, Rationen-Lebenszyklus, RAG-Indexer, Mail-Abruf,
  Preisueberwachung (bisher nur `DEFAULT_TENANT_ID`), Lagerbestand-Agent (Ereignis ohne Mandant
  wird verworfen statt `default`), Scheduler-Jobs Mahnwesen und Trigger-Nachlauf.
- Bewusst mandantenuebergreifend markiert: Outbox-Versand, Compliance-Monitor (eine Summenmeldung
  ueber alle Mandanten) sowie die `BaseWorker`-Jobs Cleanup, Compliance-Check, Tages-, Wochen-,
  Monatsberichte, GAP-Sync (`@cross_tenant_job`). `BaseWorker.initialize()` verweigert den Start
  ohne Kontext.
- Middleware unveraendert: der Dev-Rueckfall haengt an `API_DEV_TOKEN`, im laufenden System seit
  2026-10-12 nicht gesetzt.

## Nebenbefund

`rag_indexer` fragte `SELECT DISTINCT tenant_id FROM domain_shared.tenants WHERE active` ab; das
Register hat `id`/`is_active`. Die Abfrage konnte nie gelingen, der Indexer lief nie fuer einen
Mandanten. Jetzt ueber `active_tenant_ids`.

## Pruefung

- `tests/test_rls_p1_tenant_context.py` (26): fail-closed, Scope-Verschachtelung,
  Grundpflicht, Cross-Tenant loescht den Mandanten, Fehlerisolation je Mandant, `BaseWorker`
  ohne Kontext wirft; Vertrag: jede Worker-Datei, die die Datenbank oeffnet, nennt ihren Kontext
  und faellt auf keinen Standardmandanten zurueck (Muster-Selbsttest).
- Betroffene Suiten gegen valeo_probe: 206 gruen (zwei Preis-Tests und ein BaseWorker-Test
  liefen bisher ohne Mandant; sie setzen ihn jetzt ausdruecklich). Alle Testdateien mit
  Mandanten-/Middleware-Bezug: 571 gruen, 46 uebersprungen.
- P0-Ratsche schlug wie vorgesehen an (drei neue Registerzugriffe), Inventar nachgezogen:
  `DEFAULT_TENANT_ID` 55 → 54 Dateien.

## Offen fuer spaetere Phasen

- Codewege ausserhalb von Workern ohne Request (Kommandozeilen-Pipelines `geo_pipeline`,
  `lkv_pipeline`) sehen unter RLS nichts, bis sie einen Scope setzen (fail-closed, gewollt).
- 54 Dateien mit `DEFAULT_TENANT_ID`, vor allem in Diensten unter `services/*` (P6).
- Compliance-Monitor je Mandant aufteilen (aendert den Meldevertrag).
