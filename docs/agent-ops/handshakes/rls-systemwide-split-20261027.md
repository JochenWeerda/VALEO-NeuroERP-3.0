---
title: Handshake RLS-SYSTEMWIDE-SPLIT-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Claude hat während Codex' Pause dessen P5-Formtest übernommen und die getrennten Policies systemweit ausgerollt; Übergabe an Codex.
---

# Handshake RLS-SYSTEMWIDE-SPLIT-20261027 (Claude Code → Codex)

**Anlass:** Der Nutzer hat am 27.10.2026 angeordnet, dass ich deinen P5-Formtest übernehme
und die Umstellung systemweit ausrolle. Du warst wegen deines Nutzungslimits pausiert.

## Was ich von dir übernommen habe

1. **943ba2bb0** (nur auf deinem lokalen `main`) per `cherry-pick -x` in meine Kette,
   Autor du, ohne Konflikt. Das betrifft P3/P5/P6, deinen Schreibgrenzentest und deine QA.
   Inhalt unverändert.
2. **`tests/test_rls_p5_rollout.py`:** Die Formprüfung läuft jetzt über
   `scripts/rls_policy_shape.py`, eine Definition für alle Tabellen. `system` im SELECT ist
   nur für Tabellen in `docs/admin/rls-exceptions.json` → `system_lesbar` erlaubt. Die
   Auswertung als `valeo_app` am Ende des Tests ist unverändert.
3. **`tests/test_rls_p3_pilot.py`:** Die Erwartung „`system`-Kostenstellen lesbar“ ist
   umgedreht. Sie sind jetzt unsichtbar und bleiben unveränderbar.

## Was neu ist

`rls_system_read_justified_20261027` ist die letzte Migration der Kette. Sie stellt
`tenant_isolation_select` der 501 Bestandstabellen auf den eigenen Mandanten um. Der Befund
in `docs/admin/rls-system-read.json` zeigt: Kein Lesepfad dieser Tabellen liest
`system`-Zeilen. Begründete Ausnahmen kommen über `KEEP_SYSTEM_READ` und `system_lesbar`
hinzu, derzeit keine. `altbestand_hoechstens` steht jetzt auf 0.

## Kette zur Integration

`#63 → #64 → #65 → #66 → #67 → #68 → dieser PR`. Alembic:
`… → rls_domain_nachweisraum_20261027 → rls_system_read_justified_20261027`.

**Dein lokales `main`** hat 943ba2bb0 mit anderem Hash. Vorschlag: meine Kette auf deinen
Stand setzen oder deinen Commit gegen meinen tauschen. Der Inhalt ist identisch, Git löst
das beim Mergen ohne Konflikt. Dein `rls-ordered-integration-20261027.md` ist mit drin.
Der Hinweis dort, die Inventare seien noch zu regenerieren, ist erledigt.

## Für dich offen

- Live-Rollout, Systemrollen-URL, Masken- und Fachkettenabnahme. Die Listen stehen in den
  QA-Berichten der Domain-Slices.
- Das Muster `tenant_id: str = "system"` als Vorgabe steht in 49 Dateien (QA). Es fällt
  in die jeweiligen Domains.

## Nicht berührt

Dein Arbeitsbaum und dein lokales `main` (nur gelesen und per Cherry-pick übernommen), keine
Live-DB; `valeo_probe` unverändert.
