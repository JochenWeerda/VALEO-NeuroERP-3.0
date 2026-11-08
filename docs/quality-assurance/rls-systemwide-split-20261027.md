---
title: QA RLS-SYSTEMWIDE-SPLIT-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: Systemweite Umstellung auf getrennte RLS-Policies, system-Lesen nur mit Begründung, Übernahme des P5-Formtests von Codex.
---

# QA RLS-SYSTEMWIDE-SPLIT-20261027

**Nutzerauftrag 2026-10-27:** den P5-Formtest von Codex übernehmen und die Umstellung
systemweit ausrollen. Codex pausiert (Nutzungslimit), Übergabe im Handshake.
**Basis:** `claude/rls-domain-nachweisraum-20261027` (#68), Zweig `claude/rls-systemwide-split-20261027`.

## Lieferung

| Schritt | Inhalt |
|---|---|
| Cherry-pick 943ba2bb0 (Autor Codex) | P3/P5/P6 mit vier getrennten Policies statt ALL-Policy; `test_rls_shared_row_write_boundaries.py`; Codex-QA `rls-ordered-integration-20261027.md`. Bisher nur auf Codex' lokalem `main`, jetzt in der Kette |
| `alembic/versions/rls_system_read_justified_20261027.py` | `tenant_isolation_select` auf den 501 Bestandstabellen liest nur noch den eigenen Mandanten, außer bei begründeten Tabellen (`KEEP_SYSTEM_READ` = `system_lesbar`, derzeit leer). Tabellenlisten aus den drei Migrationen, Rückweg stellt exakt deren Form wieder her. Keine Datenänderung |
| `scripts/rls_system_read.py` → `docs/admin/rls-system-read.json` | Befund je RLS-Tabelle: `system`-Zeilen frisch/live und Code, der `system` als Mandanten liest |
| `tests/test_rls_p5_rollout.py` (übernommen) | Formprüfung über `scripts/rls_policy_shape.py`: nur die getrennte Form; `system`-Lesen nur für `system_lesbar` |
| `tests/test_rls_p3_pilot.py` | Erwartung angepasst: `system`-Kostenstellen sind nicht mehr lesbar, weiterhin weder änderbar noch löschbar noch übernehmbar |
| `tests/test_rls_system_read_justified.py` | Konsistenz Migration ↔ Ausnahmeliste; deckt genau 501 Tabellen; `system`-Seeds für Mandanten unsichtbar und unberührbar, für `valeo_system` sichtbar; Hin- und Rückweg der Migration |
| `docs/admin/rls-exceptions.json` | `altbestand_hoechstens` 501 → 0 |
| `docs/admin/rls-inventory.json` | regeneriert: 4 Policies je Tabelle (Codex' Korrektur war noch nicht im Inventar) |

## Befund `system`-Lesen (frisch zurückgerollt, live nur lesend)

| Tabelle | `system`-Zeilen | Code liest `system`? | Entscheidung |
|---|---|---|---|
| `domain_erp.booking_templates` | live 70 | nein, `booking_templates.py` filtert `tenant_id = :tenant_id` | kein `system`-Lesen; ob Vorlagen gemeinsam sein sollen, ist eine fachliche Entscheidung (dann `system_lesbar` + Code) |
| `domain_finance.aufbewahrungsfristen` | frisch 5 (Seeds) | nein, `gobd.py` legt je Mandant an und liest je Mandant | kein `system`-Lesen |
| `domain_erp.journal_entries` | live 1 („Integrationstest Buchung“, IMP-AUDIT-001) | nein | kein `system`-Lesen; Testrest zur Klärung gemeldet, nicht gelöscht |
| `journal_entry_lines`, `sales_returns`, `tax_keys`, `system_properties` | 0 | Fehltreffer: die Zeilen betreffen `chart_of_accounts` (noch ohne RLS) | – |

Der einzige echte `system`-Leser ist `chart_of_accounts` (`chart_of_accounts.py`,
`steuerschluessel.py`, `sales_credit_notes.py`). Die Tabelle hat noch keine RLS
(zurückgestellt, Klasse B). Mit ihrem Domain-Slice bekommt sie den ersten begründeten
`system_lesbar`-Eintrag (Kontenrahmen-Vorlage).

## Nachweise (valeo_probe, zurückgerollt)

```
pytest tests/test_rls_*.py tests/test_provision_db_roles.py   -> 188 passed (vorher 1 rot: P5-Formtest)
  darin: test_rls_shared_row_write_boundaries (Codex) 30, test_rls_system_read_justified 4,
         test_rls_p5_rollout (übernommen), test_rls_policy_shape (Altbestand 0)
python scripts/rls_rollout.py --check / rls_domain_matrix.py --check / generate_code_inventories.py --check -> OK
python scripts/pruefstand_db.py --status -> loading_stop_fk_20261023 (unverändert)
```

## Verbleibende Risiken / Folgearbeit

- **`system` als Standardmandant im Code:** 49 Dateien verwenden `tenant_id: str = "system"`
  oder `default="system"` als Vorgabe, vor allem Agenten (`agents.py`, `agent_ops.py`,
  `neuroassist_*`), Sicherheits- und Qualitätsmodule und `closing_checklists_service.py`.
  Das ist ein Rückfall wie `DEFAULT_TENANT_ID`. Schreiben unter einem echten Mandanten
  scheitert an WITH CHECK, Lesen findet unter RLS nichts. `rls_rollout.py` erkennt das
  Muster bisher nicht (nur `default`). Es gehört zu den jeweiligen Domain-Slices.
- **Live:** Die 70 `system`-Buchungsvorlagen und die eine `system`-Testbuchung sind nach der
  Aktivierung für Mandanten unsichtbar, so wie sie im Code schon heute nicht vorkommen.
  Sichtbar bleiben sie für den Eigentümer und `valeo_system`.
- **Codex' lokales `main`** enthält 943ba2bb0 mit anderem Hash. Inhaltlich ist der Stand
  gleich; bei der Integration genügt meine Kette (Handshake).
