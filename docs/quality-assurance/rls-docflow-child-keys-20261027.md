---
title: QA RLS-DOCFLOW-CHILD-KEYS-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: Verbund-FKs fuer die Kinder der docflow-Tabellen (P5, uebernommen von Codex).
---

# QA RLS-DOCFLOW-CHILD-KEYS-20261027

Basis #72. Migration `rls_docflow_child_keys_20261027`: 12 Verweise in 6 P5-Tabellen (Kopf-Links, Belegpositions-Links, Buchungen, Rueckgabefaelle, POS-Belegpruefung, TSE-Meldungen) als Verbund-FK `(eltern, tenant_id)`; ON DELETE bleibt, SET NULL leert nur den Verweis (PG15). `UNIQUE (id, tenant_id)` an Positionen, Artefakten, TSE. Policies unveraendert. Gewachsene Daten: 0 fremde Verweise.

Nachweise: `tests/test_rls_docflow_child_keys.py` 15 passed als valeo_app (je Verweis Anlage und Umhaengen gesperrt, SET NULL behaelt tenant_id, Rueckgabefall haelt Kopf). Gegenprobe mit alten Einzel-FKs: 13 rot. Nicht gelaufen: RLS-Gesamtsuite und Bestandstests auf diesem Zweig (Nutzungslimit) - vor Integration nachholen.
