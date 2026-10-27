---
title: QA RLS-DOMAIN-KI-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: in-arbeit
last_reviewed: 2026-10-27
version: 0.1.0
description: RLS-Domain KI (Agentenvorschläge, Werkzeugausführungen, Wissensversionen) samt Prüfung von RAG, Caches und Agentenpfaden; Datenbankabnahme steht aus.
---

# QA RLS-DOMAIN-KI-20261027

**Basis:** Integrationszweig `codex/migration-parity-repair-20261022` @ b9f22226e (Kette bis #73).
Zweig `claude/rls-domain-ki-20261027`. Die Migration `rls_domain_ki_20261027` folgt auf
`rls_docflow_child_keys_20261027`, den einzigen Head laut `alembic heads`. Codex'
Agrar-Entwurf nennt denselben Vorgänger; die Einordnung steht im Handshake.

**Status:** Codevorbereitung fertig, Datenbankabnahme offen. Codex hat `valeo_probe` noch
nicht freigegeben, deshalb sind die 7 Verhaltenstests noch nicht gelaufen. Inventar,
Ausnahmeliste und Obergrenze folgen nach der Abnahme, weil `rls_inventory.py` den Prüfstand
braucht.

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

## Nachweise bisher (ohne Datenbank)

```
tests/test_rag_search_tenant.py                                   -> 4 passed
tests/test_system_tenant_fallback_contract.py, test_rls_domain_matrix.py,
  test_rls_policy_shape.py, test_rls_p5_rollout.py (ohne TEST_DATABASE_URL) -> passed, DB-Teile übersprungen
tests/test_rls_domain_ki.py (7 Verhaltenstests)                   -> gesammelt, noch nicht gegen valeo_probe gelaufen
rls_rollout.py --check, rls_domain_matrix.py, generate_code_inventories.py --check -> OK
```

## Offen

- 7 Verhaltenstests als `valeo_app` auf `valeo_probe` nach der Freigabe durch den Lead.
- Danach Inventar regenerieren, `rls-exceptions.json` verkleinern (3 Tabellen austragen,
  `knowledge_versions` in `system_lesbar`), Obergrenze senken, Bestandstests (Wissens-API,
  Prozesskern, MCP, Gutschriften) gegen die Basis vergleichen.
- Maskenabnahme: Agentenvorschläge/Gutschrift-Freigabe, Wissensbasis (Versionen), Operator-Agent.
