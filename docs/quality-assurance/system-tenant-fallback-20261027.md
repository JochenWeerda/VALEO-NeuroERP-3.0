---
title: QA SYSTEM-TENANT-FALLBACK-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: Befund "tenant_id = system als Vorgabe" geschlossen; Mandant nur aus Token oder Kontext, gemeinsamer Mandant benannt, Ratsche gegen neue Rückfälle.
---

# QA SYSTEM-TENANT-FALLBACK-20261027

**Nutzerauftrag 2026-10-27:** den Befund aus RLS-SYSTEMWIDE-SPLIT schließen. Viele Stellen
setzten `tenant_id = "system"` als Vorgabe oder Rückfall.
**Basis:** `claude/rls-shared-booking-templates-20261027` (#70), Zweig `claude/system-tenant-fallback-20261027`.

## Befund

Gezählt wurde im Syntaxbaum, nicht im Text: 216 Stellen in 65 Quelldateien.

| Form | Stellen | Wirkung vorher |
|---|---|---|
| Routenparameter `tenant_id: str = "system"` oder `Query("system")` | 13 + 59 | Der Aufrufer wählte den Mandanten, ohne Angabe galt `system`. Im Backend überschreibt `install_tenant_bindings` Query und Body zwar mit dem Token-Mandanten, die Agenten-Ops-Routen waren aber ganz ohne Token erreichbar |
| Request-Modelle mit `tenant_id = "system"` | 13 | wie oben, über den Body |
| interne Funktionen und Modelle mit Vorgabe `"system"` (Agenten, Registries, Wissensspeicher, Kanäle, Fälle, Ereignisse, ISO-Module) | ~110 | Ohne Mandanten landeten Daten im Mandanten `system`. Unter RLS scheitert das Schreiben, das Lesen findet nichts |
| `.get("tenant_id", "system")`, `tenant_id or "system"` (Copilot-Websocket, Prozesskern, Debitoren, Nutzerverwaltung) | 5 | Rückfall bei fehlendem Claim oder Feld |
| SQL `tenant_id IS NULL AND :tenant_id = 'system'` (Kreditoren, Datenqualität) | 14 | NULL-Zeilen gehörten dem Mandanten `system` |
| feste `tenant_id="system"` in zwei Vorschau-Berechnungen | 2 | reine Berechnung ohne Speicherung |

## Umsetzung

| Regel | Umsetzung |
|---|---|
| HTTP-Eingang | `tenant_id: str = Depends(get_tenant_id)`, also der geprüfte Token-Mandant. Request-Modelle tragen keinen Mandanten mehr (Agenten-Ops, RAG-Index, Auto-Matching, Trocknungsvorschau). `?tenant_id=` an Debitoren-, FiBu-, Kampagnen-, Bericht-, OP-, Policy-, Nachhaltigkeits-, PSM- und Export-Routen entfällt |
| intern | `tenant_id: str \| None = None` → `tenant_id or get_current_tenant_id()`. Das ist fail-closed (`TenantContextMissing`) statt `system`. Modellfelder: `default_factory=get_current_tenant_id` |
| gemeinsamer Mandant | `SHARED_TENANT_ID = "system"` in `app/core/tenant_context.py`. Das mitgelieferte Produktwissen (`_default_knowledge_objects`) nennt ihn ausdrücklich; `KnowledgeObject.tenant_id` und `KnowledgeRepository.create_object(tenant_id=…)` sind Pflicht |
| Wissens-API | Lesen: eigene + gemeinsame Objekte. Ändern, Archivieren und Versionieren: nur eigene; gemeinsame ergeben 403. Anlegen im Token-Mandanten statt Standardmandant |
| NULL-Zeilen | Kreditoren und Datenqualität lesen nur noch den eigenen Mandanten |
| reine Vorschau | `current_tenant_or_none() or "ohne-mandant"`, ausdrücklich gekennzeichnet, nie gespeichert |
| Ratsche | `tests/test_system_tenant_fallback_contract.py`: 0 Rückfälle auf `"system"`; `"default"`-Rückfälle je Datei eingefroren, nur abnehmend; Selbsttest der Muster; gemeinsamer Mandant benannt |

## Nachweise

```
pytest tests/test_system_tenant_fallback_contract.py tests/test_rls_p1_tenant_context.py  -> 30 passed
Betroffene Testmodule, Vergleich mit der Basis #70 (conftest, DATABASE_URL = Prüfstand):
  54 Module (direkte Importe)                     -> 550 passed, wie Basis
  26 Module (geänderte Endpunkte)                 -> 1227 passed, wie Basis
  32 Module (umgestellte Query-Routen)            -> 2222 passed; 18 rot wie auf der Basis (vorbestehend), 0 neu rot
python scripts/check_mcp_rest_bindings.py         -> OK
python scripts/generate_code_inventories.py --check -> OK
OpenAPI: 65 Pfade + 13 Request-Schemas nachgezogen; Drift /finance/closing-checklists* (vorbestehend, Codex) unverändert
```

Angepasste Tests:
- 15 Dienst-Testmodule bekommen per autouse-Fixture einen ausdrücklichen Testmandanten.
- Agenten-Ops-Tests: `test-mandant` statt `system`, Mandant über `ersetze_mandant`.
- `test_security_creditors`: neue SQL-Klausel.
- `test_psm_proplanta_endpoints`: Mandant aus der Identität, nicht aus `?tenant_id=`.

## Nachtrag: Wissensobjekte unter RLS

Mit dem Rückbau des Standardmandanten in `knowledge_api.py` entfiel der Rückstellungsgrund
von `domain_shared.knowledge_objects`. `rls_rollout.py` meldete die Tabelle als `ready`, die
P5-Ratsche wäre rot gewesen. Sie ist deshalb in diesem PR abgesichert
(`rls_knowledge_objects_shared_20261027`):
- SELECT liest eigene und gemeinsame Objekte; das gemeinsame Produktwissen ist begründet in
  `system_lesbar`.
- Schreiben ist nur im eigenen Mandanten möglich.

Live gibt es 6 `system`-Objekte, die bleiben. Tests: `tests/test_rls_knowledge_objects_shared.py`,
3 passed als `valeo_app` (Lesen, Schreibsperren, Fachkette Wissens-API). RLS-Gesamtlauf: 198
passed. Zurückgestellt sind jetzt 200 Tabellen.

## Verbleibend

- **`"default"`-Rückfälle** (Standardmandant): 52 Stellen in 19 Dateien, eingefroren. Am
  stärksten betroffen sind `finance_actions`, `controlling_actions`, `procurement_match`,
  `external_agent_integrations`, `service_anfragen`, `numbering_*`. Das ist der
  Matrix-Befund `standardmandant`; er wird mit den Domains abgebaut, die Ratsche verhindert
  Zuwachs.
- **Wissensbasis:** `KnowledgeRepository.list_objects/get_object` lesen ohne Mandantenfilter.
  Unter RLS sehen sie jetzt eigene plus gemeinsame Objekte. `knowledge_versions` (Klasse C)
  ist noch zurückgestellt.
- **Akteur aus dem Body:** `changed_by`/`requested_by` in den Agenten-Ops-Modellen ist ein
  eigener Identitätsbefund, nicht Teil dieses Slices.
- **Nicht genutzte Module:** Die ISO-artigen Module (backup, certification, continuity,
  security/*, quality/* u. a.) importiert niemand. Sie sind nur konsistent umgestellt; ob man
  sie entfernt, ist eine eigene Entscheidung.
