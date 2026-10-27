---
title: QA RLS-DOMAIN-KI-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: RLS-Domain KI (Agentenvorschläge, Werkzeugausführungen, Wissensversionen) samt Prüfung von RAG, Caches und Agentenpfaden; Datenbankabnahme auf valeo_probe bestanden.
---

# QA RLS-DOMAIN-KI-20261027

**Basis:** Integrationszweig `codex/migration-parity-repair-20261022` @ ed77dded3. Das ist die
Kette bis #73 plus Codex' `rls_verified_agrar_20261027`. Zweig `claude/rls-domain-ki-20261027`. Die
Migration `rls_domain_ki_20261027` hängt nach der vereinbarten Regel hinter
`rls_verified_agrar_20261027`; `alembic heads` zeigt einen einzigen Head.

**Nachzug auf ed77dded3:**
- `SharedKnowledgeReadOnly` erbt jetzt von `PermissionDeniedError` (zentraler 403-Handler).
- `process_kernel_api.py` ist wieder identisch mit dem Integrationsstand, damit die
  Größenratsche (6100) hält.
- Prüfstandsfenster laut Codex frei (RLS-GESAMTABNAHME-20261027). Neu gelaufen: KI 11 passed;
  RLS-Gesamtsuite mit Größenratsche 286 passed; Bestand 663 passed.
- Inventar regeneriert: 190 zurückgestellt.

**Status:** abgeschlossen. Prüfstandsfenster nach Freigabe durch Codex (27.10.2026): `valeo_probe`
war auf `loading_stop_fk_20261023`, ohne fremde Sitzungen, `TEST_DATABASE_URL` gesetzt.
Danach unverändert und ohne offene Sitzung.

## Analyse KI

| Bereich | Befund | Entscheidung |
|---|---|---|
| `public.agent_proposals` | alle Wege (MCP-Dienst, Gutschriften, Repository) filtern mit dem verifizierten Mandanten; live 0 Zeilen | getrennte Policies, kein `system`-Lesen |
| `public.mcp_tool_executions` | Idempotenzjournal, Primärschlüssel enthält `tenant_id`; Mandant nur aus Token-Claims (`execute_mcp_tool` lehnt Kopf und Parameter ab) | getrennte Policies, kein `system`-Lesen |
| `domain_shared.knowledge_versions` (C) | Mandant hing nur am Objekt; live 8 Zeilen | `tenant_id` aus dem Objekt, NOT NULL, Default aus dem Kontext, Verbund-FK; SELECT eigen + gemeinsam (dieselbe Familie wie `knowledge_objects`) |
| Wissensbasis-Schreibwege | `POST /process-kernel/knowledge/store/objekte/{id}/versionen` und die Übernahme von Verbesserungsvorschlägen hängten Versionen an beliebige Objekte, auch an gemeinsames Produktwissen | `KnowledgeRepository.add_version` ändert mit Mandantenkontext nur eigene Objekte (`SharedKnowledgeReadOnly`, 403); zentrale Pflege ohne Kontext bleibt möglich |
| `knowledge_improvement_proposals.target_knowledge_id` | verweist bewusst auch auf gemeinsames Produktwissen (Vorschlag an die zentrale Pflege) | kein Verbund-FK; Übernahme durch Mandanten wird durch die Schreibsperre abgewiesen |
| RAG-Suche (`/rag/search`) | Collections enthalten alle Mandanten, die Suche filterte nur mit Aufruferfiltern. Router nicht eingehängt (`main.py` auskommentiert), Lücke latent | Suche immer `$and` mit Token-Mandant (`tenant_where`); Vektorspeicher und Indexer werden erst beim Aufruf geladen |
| RAG-Indexer-Worker | je Mandant in `tenant_scope` | unverändert |
| RAG-Abfragecache | ungenutzt; Schlüssel ohne Mandant | Befund, kein Eingriff; bei Nutzung den Mandanten in den Schlüssel aufnehmen |
| Systemverbindung | `system_session`/`cross_tenant_scope` kommen in Agenten-, MCP-, Neuro- und RAG-Pfaden nicht vor | – |
| Read-Model-Cache | Schlüssel enthält `tenant_id` (`cached_read_model`) | – |

## Nachweise

```
pytest tests/test_rls_domain_ki.py -rs                 -> 7 passed, 0 skipped (valeo_app, zurückgerollt)
Gegenprobe ohne Verbund-FK/Policies auf den Versionen -> 3 rot
pytest tests/test_rls_*.py tests/test_provision_db_roles.py tests/test_system_tenant_fallback_contract.py
       tests/test_rag_search_tenant.py -rs             -> 239 passed, 0 skipped
22 berührte Bestandsmodule (Wissensbasis, Prozesskern, MCP, Gutschriften, Operator-Agent; conftest, Prüfstand)
                                                       -> 663 passed, wie auf der Basis b9f22226e; 0 neu rot
rls_inventory/rls_rollout/rls_domain_matrix regeneriert, generate_code_inventories.py --check -> OK
```

| Abnahmekriterium | Test |
|---|---|
| eigener Mandant; fremder Mandant für SELECT/INSERT/UPDATE/DELETE gesperrt; `system` nicht lesbar und nicht übernehmbar; kein `tenant_id`-Wechsel; fail-closed | `test_mandantengrenze_mandanteneigene_tabellen` (Vorschläge, Ausführungen) |
| Versionen: eigene + gemeinsame lesbar, nur eigene änderbar; keine Version unter fremdem oder gemeinsamem Objekt, auch nicht umgehängt; Mandant aus dem Kontext | `test_versionen_gemeinsam_lesbar_nur_eigene_schreibbar` |
| Objekt mit Versionen behält seinen Mandanten | `test_objekt_mit_versionen_behaelt_seinen_mandanten` |
| Kontextwechsel/Savepoint, Hintergrund, Pool | `test_kontextwechsel_savepoint_hintergrund_pool` |
| Fachkette Wissensbasis: Version am eigenen Objekt, Sperre am gemeinsamen, Anlage mit Version | `test_fachkette_wissensversionen` |
| Policy-Formen | `test_policy_formen` |

Inventar: 190 zurückgestellt (−3 gegenüber dem Integrationsstand), `knowledge_versions` begründet in `system_lesbar`.

## Verbleibend / vor Live-Aktivierung

- Maskenabnahme: Gutschrift-Buchungsvorschläge (Freigabe/Ausführung), Wissensbasis
  (Versionen, Verbesserungsvorschläge), Operator-Agent, jeweils mit zwei Mandanten.
- RAG bleibt ausgehängt. Vor dem Einhängen: Router-Rechte festlegen, Abfragecache mit
  Mandant im Schlüssel.
- Die Übernahme von Verbesserungsvorschlägen an gemeinsamem Produktwissen ist nur noch
  zentral möglich (`valeo_system`). Ein zentraler Fachcommand dafür fehlt.
