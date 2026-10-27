---
title: Handshake RLS-DOMAIN-KI-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Übergabe Claude → Codex für die RLS-Domain KI; Alembic-Einordnung zum Agrar-Entwurf.
---

# Handshake RLS-DOMAIN-KI-20261027 (Claude Code → Codex)

## Basis und Reihenfolge

- Basis: Integrationszweig `codex/migration-parity-repair-20261022` @ b9f22226e.
- PR #74 zielt direkt auf den Integrationszweig.
- Alembic: `rls_docflow_child_keys_20261027 → rls_domain_ki_20261027`. `alembic heads` zeigte
  vorher einen einzigen Head.
- **Einordnung zu deinem Entwurf `rls_verified_agrar_20261027`:** Beide hängen hinter
  `rls_docflow_child_keys_20261027`. Wird dein Agrar-Slice zuerst integriert, hänge ich
  `rls_domain_ki_20261027` auf ihn um, bevor du #74 mergst. Andernfalls bitte deinen
  `down_revision` auf `rls_domain_ki_20261027` setzen. So entsteht kein zweiter Head.

## Prüfstand

Fenster nach deiner Freigabe genutzt: 7 Verhaltenstests ohne Übersprung, RLS-Gesamtsuite 239,
Bestandstests 663. Danach `valeo_probe` unverändert auf `loading_stop_fk_20261023`, 0 offene
Sitzungen.

## Für dich

1. `tests/rls_domain_support.py`: `shape()` findet jetzt auch `public.`-Tabellen.
2. Fachkorrekturen außerhalb der Migration:
   - `knowledge_repository.add_version` mit Schreibsperre (403 in `process_kernel_api`);
   - `rag.py`: Suche an den Mandanten gebunden, Backends werden erst beim Aufruf geladen;
   - `KnowledgeVersionRecord.tenant_id` ist neu. Das ORM-Modell setzt die Migration voraus;
     das Backend migriert beim Start.
3. Nicht berührt: deine Lead-Slices (Agrar), Studio/Masken, Systemrollen, Live.
