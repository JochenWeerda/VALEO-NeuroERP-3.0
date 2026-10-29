---
title: RLS-Domains — Entscheidungsmatrix und Reihenfolge
type: architecture
audience: [agent, entwickler]
owner: Claude Code
status: entwurf
last_reviewed: 2026-10-27
version: 1.0.0
description: Inventar der noch nicht abgesicherten Mandantentabellen nach Ursache, Entscheidungsmatrix je Domain, Policy-Muster und Reihenfolge der Domain-Slices.
---

# RLS-Domains — Entscheidungsmatrix und Reihenfolge

Folgt auf den Mandantenkernel P0–P7 (`rls-mandantenkernel-plan.md`, PRs #55–#63). Codex
integriert den Kern, korrigiert die P3/P5-Policies und aktiviert live
(RLS-ORDERED-INTEGRATION-20261027). Dieses Dokument bereitet die **noch offenen Tabellen**
vor. Es aktiviert nichts.

Generierte Detailmatrix je Tabelle: [`docs/admin/rls-domain-matrix.md`](../admin/rls-domain-matrix.md)
(`scripts/rls_domain_matrix.py`). Eingefrorene Ausnahmeliste:
`docs/admin/rls-exceptions.json`. Policy-Formen: `scripts/rls_policy_shape.py`.

## 1. Stand am 27.10.2026

Basis ist P7 (#63) auf dem Integrationszweig @ c3142eb1d. Zwischen der Kette und dem
Integrationszweig liegt keine neue Migration. Inventar und Rollout sind gegen `valeo_probe`
geprüft (`--check` OK).

| | Zahl |
|---|---|
| Tabellen im frischen Schema | 775 |
| mit RLS (P3/P5/P6; bei Codex auf getrennte Form korrigiert) | 501 |
| **Mandantentabellen ohne RLS** | **214** |
| davon Klasse A (tenant_id NOT NULL), zurückgestellt | 110 |
| davon Klasse B (tenant_id nullbar) | 51 |
| davon Klasse C (keine tenant_id, Elternbeleg mit Mandant) | 53 |
| Klasse D (ohne Mandant, global oder verwaist) — nicht Teil dieser Matrix | 60 |

Die bisherigen 110 zurückgestellten Tabellen waren nur Klasse A. Klasse B und C kamen im
Rollout gar nicht vor. Die tatsächliche Lücke sind daher **214** Tabellen.

### Datenbefund der gewachsenen Datenbank

Gelesen in einer Nur-Lese-Transaktion (`--data`): 199 der 214 Tabellen existieren dort, 15
nur im frischen Schema. Die meisten sind leer oder klein, die Daten sind sauberer als
erwartet. Echte Blocker:

| Tabelle | Befund | Folge |
|---|---|---|
| `domain_agrar.feeding_nutrient_definitions` / `_unit_definitions` / `_reference_revisions` | 19 / 8 / 22 Zeilen ohne Mandant | fachlich Normtabellen (GfE/DLG), Kandidat für `system`-Lesen; Herkunft im Domain-Slice belegen |
| `domain_erp.chart_of_accounts` | 28 `system`-Zeilen (Kontenrahmen-Vorlage) | `system`-Lesen begründen oder je Mandant kopieren |
| `domain_shared.knowledge_objects` | 6 `system`-Zeilen | Wissensbasis: `system`-Lesen begründen |
| `domain_shared.users` | 2 `default`-, 2 `system`-Zeilen | Identitätstabelle, eigener Slice mit Anmeldung |
| `domain_shared.policy_rules` | 3 Zeilen ohne Mandant | Herkunft klären |
| `domain_agrar.feldbuch_schlaege` | 1 `default`-Zeile | Herkunft klären |
| `public.outbox_events` | 8 `default`-Zeilen | Outbox läuft über `valeo_system`; alte Ereignisse zuordnen oder verwerfen |
| `domain_shared.audit_logs` | 1 `system`-Zeile | Protokoll: keine gemeinsame Lesbarkeit; Zeile zuordnen |

Nichts davon wird pauschal dem Standardmandanten oder `system` zugeschlagen. Jede Zeile ohne
geklärte Herkunft blockiert die Migration ihres Slices.

## 2. Lücken nach Ursache

Führende Ursache je Tabelle. Mehrere Ursachen pro Tabelle sind möglich, die Detailmatrix
zeigt alle.

| Ursache | Tabellen | Bedeutung | Behandlung |
|---|---|---|---|
| `standardmandant` | 62 | Code mit Zugriff fällt auf `DEFAULT_TENANT_ID`/`'default'` zurück | Rückfall entfernen, Mandant aus `get_tenant_id` (tokengebunden); Fundstellen Datei:Zeile in der Matrix |
| `position` | 51 | Klasse C: Mandant hängt am Elternbeleg | `tenant_id` aus dem Elternbeleg, `NOT NULL`, Verbund-FK `(eltern_id, tenant_id)` |
| `referenzdaten` | 41 | Code liest NULL- oder `system`-Zeilen als gemeinsame Daten | je Tabellenfamilie entscheiden: `system`-Lesen begründen oder je Mandant führen |
| `mandant_nullbar` | 38 | Klasse B oder Code fragt `tenant_id IS NULL` | Herkunft der NULL-Zeilen klären, dann `NOT NULL` |
| `dienst` | 20 | Modell/Zugriff unter `services/*` | erst tokengebundene Identität ([Vorschlag](rls-dienste-identitaet-vorschlag.md)) |
| `identitaet` | 2 | Schlüssel/Token vor der Mandantenbindung | keine Mandanten-Policy; Nachschlagen über `valeo_system` |

Die Code-Befunde sind dateiweit und heuristisch. Beispiele: `mcp_execution_service.py:3155`
trifft viele Tabellen; `customers`/`articles` werden in Diensten teils nur als Wort gefunden.
Sie sagen, wo nachzusehen ist, nicht, dass dort ein Fehler liegt. Die Entscheidung fällt im
Domain-Slice am Code.

## 3. Policy-Muster für neue Tabellen

Die Altform `tenant_isolation` (eine ALL-Policy, USING eigen ODER `system`, WITH CHECK
eigen) lässt Mandanten `system`-Zeilen **löschen** und per UPDATE **übernehmen**.
WITH CHECK greift bei DELETE nicht, und UPDATE prüft nur das Ergebnis. Codex hat P3/P5/P6
korrigiert (943ba2bb0, RLS-ORDERED-INTEGRATION-20261027): vier Policies
`tenant_isolation_select/_insert/_update/_delete`. Seit RLS-SYSTEMWIDE-SPLIT-20261027
(`rls_system_read_justified_20261027`) gilt systemweit: SELECT liest `system` nur mit
Begründung. Kein Lesepfad der 501 Bestandstabellen las `system`-Zeilen
(`docs/admin/rls-system-read.json`). Alle Tabellen haben diese Form:

```sql
ALTER TABLE t ENABLE ROW LEVEL SECURITY;                     -- kein FORCE (Plan 2.4)
CREATE POLICY tenant_isolation_select ON t FOR SELECT USING (tenant_id = public.rls_current_tenant());
CREATE POLICY tenant_isolation_insert ON t FOR INSERT WITH CHECK (tenant_id = public.rls_current_tenant());
CREATE POLICY tenant_isolation_update ON t FOR UPDATE USING (tenant_id = public.rls_current_tenant())
                                            WITH CHECK (tenant_id = public.rls_current_tenant());
CREATE POLICY tenant_isolation_delete ON t FOR DELETE USING (tenant_id = public.rls_current_tenant());
```

- **`system`-Lesen** nur, wenn `docs/admin/rls-exceptions.json` → `system_lesbar` die Tabelle
  begründet. Dann lautet `tenant_isolation_select` USING
  `tenant_id = rls_current_tenant() OR (tenant_id = 'system' AND rls_current_tenant() IS NOT NULL)`.
  Die drei schreibenden Policies bleiben unverändert. Deshalb ist eine `system`-Zeile lesbar,
  aber nicht änderbar, nicht löschbar und nicht übernehmbar. Neue `system`-Zeilen entstehen
  nur über zentrale Fachcommands mit `valeo_system`.
- **Keine weitere permissive Policy** auf derselben Tabelle: PostgreSQL verknüpft permissive
  Policies mit OR, eine breite ALL-Policy höbe alles auf.
- **Positionen:** `tenant_id` mit `DEFAULT public.rls_current_tenant()`. Dazu kommen
  `NOT NULL`, `UNIQUE (id, tenant_id)` am Kopf und der Verbund-FK
  `(kopf_id, tenant_id) → kopf(id, tenant_id)`. FK-Prüfungen umgehen RLS. Der Verbund-FK
  ist daher die strukturelle Sperre gegen fremde Elternbelege, auch beim Umhängen.
- RLS ersetzt keine Rollenprüfung. `SCHREIBEN[...]`/`require_roles` und die Fachcommands
  bleiben.

Die Ratschen `tests/test_rls_policy_shape.py` und `tests/test_rls_p5_rollout.py` erlauben nur
die getrennte Form. Altbestand (ALL-Policy oder `system`-Lesen ohne Begründung) ist auf 0
gesetzt (`altbestand_hoechstens`). Alles andere ist rot: eine zusätzliche ALL-Policy, eine restriktive
oder rollengebundene Policy, `system` in INSERT/UPDATE/DELETE, fehlendes WITH CHECK, FORCE.
Die Namen folgen Codex' Korrektur (943ba2bb0).

## 4. Entscheidungsmatrix je Domain

Spalten: Tabellen (Klassen) · führende Ursachen · führendes Modell · Schreiber-Dateien ·
Identitätsquelle der Verbraucher · Worker · Bereinigung · Policy-Entscheidung · Risiko.
„Token“ heißt: `get_tenant_id` aus `app.core.tenant` bzw. über die Middleware, die
Kopfzeilen mit dem Token-Mandanten überschreibt (`tenant_binding.bind_headers`). „Nutzlast“
heißt: `tenant_id` aus Body/Payload. Die Middleware prüft Body-Selektoren gegen das Token,
ein Rückfall im Code bleibt trotzdem ein Befund.

| Domain | Tabellen | Ursachen | Modell | Schreiber | Identität | Worker | Bereinigung | Policy | Risiko |
|---|---|---|---|---|---|---|---|---|---|
| **pricing** | 2 (A1, C1) | standardmandant, position | Roh-SQL (Migration) | 1 | Query-Parameter mit Standard, Nutzlast | – | 0 Zeilen | getrennt, kein `system`; Positionen aus `price_lists` | **umgesetzt** (RLS-DOMAIN-PRICING-20261027) |
| hr | 5 (A3, B2) | referenzdaten, nullbar, standard (Fehltreffer) | Roh-SQL | 2 | Token | – | 0 Zeilen; `person`/`employment` nur frisch | getrennt, kein `system`; Verbund-FK der Kinder | **umgesetzt** (RLS-DOMAIN-HR-20261027) |
| nachweisraum | 2 (A2) | referenzdaten (Fehltreffer MCP-Generik) | Roh-SQL | 1 | Kopfzeile → Token | – | 0 Zeilen | getrennt; Prüfprotokoll mit Verbund-FK | **umgesetzt** (RLS-DOMAIN-NACHWEISRAUM-20261027) |
| audit / compliance | 4 (A3, B1) | standard, nullbar (Fehltreffer) | Roh-SQL | 4 | Token | – | 0 Zeilen | getrennt; PCN-Verlauf mit Verbund-FK | **umgesetzt** (RLS-DOMAIN-AUDIT-COMPLIANCE-20261027) |
| docflow | 5 (A5) | standardmandant (`gobd_archiv.py`) | Roh-SQL | 9 | Token (GoBD-Archiv vorher Query + Standardmandant) | – | 63 Zeilen, sauber | getrennt; Positionen/Artefakte/XML am Kopf, TSE am Terminal | **umgesetzt** (RLS-DOMAIN-DOCFLOW-20261027) |
| ki | 2 (A2) | referenzdaten | ORM `agent_proposal_model` | 3 | Token, Nutzlast | – | 0 Zeilen | getrennt | mittel: Agentenpfade |
| sales | 5 (A2, B1, C2) | position, referenzdaten | Roh-SQL | 10 | Token, Nutzlast, Rückfall | – | 7 Zeilen | getrennt; Positionen aus Kopf | mittel: Buchungskette |
| einkauf | 14 (A3, B4, C7) | position, nullbar | ORM `einkauf_models` + Roh-SQL | 13 | Token | – | 197 Zeilen | getrennt; Positionen aus Kopf | mittel |
| logistics / log / ops | 21 | position, nullbar, dienst | ORM `verladung`, `operations` | 44 | Kopfzeile, Nutzlast, Rückfall | – | 104 Zeilen | getrennt | mittel; `log_touren` hängt an Dienst |
| erp | 10 (A4, B5, C1) | referenzdaten, nullbar | ORM | 44 | Token, Kopfzeile | `scheduler_service.py` | 28 `system`-Zeilen Kontenrahmen | `system`-Lesen für `chart_of_accounts` begründen | hoch: Buchungsautorität |
| agrar | 23 (A14, B8, C1) | standard, referenzdaten, nullbar | ORM `agrar_models` + Roh-SQL | 39 | Token, Rückfall (11 Dateien) | – | 49 NULL-Normzeilen, 1 `default` | Normtabellen `system`-Lesen begründen | hoch: Ernte/Abrechnung |
| inventory | 41 (A26, B7, C8) | standard, referenzdaten, dienst | ORM `wms_models`, `l3c_models` | 69 | Token, Nutzlast, Dienst | `compliance_monitor.py` | 392 Zeilen | getrennt; `public.inventory_*` erst mit Dienst-Identität | hoch: Lagerbuchung |
| crm | 37 (A11, B9, C17) | position, dienst | ORM `crm/models`, `domains/crm` | 62 | Token, Nutzlast, Dienst | `compliance_*` | 140 Zeilen | getrennt; Partner-Positionen aus `business_partners` | hoch: 17 Partnerunterobjekte, Dienste |
| shared | 35 (A25, B4, C6) | standardmandant (21) | ORM gemischt | 86 | Token, Rückfall (21 Dateien) | `cleanup_worker.py`, `job_runner.py` | `users`, `policy_rules`, `knowledge_objects`, `outbox_events` | familienweise; `users`/Schlüssel nicht als Mandantentabelle | hoch: Identität, Outbox |
| finance / procurement / mfg / portal / infrastructure / dev_mock | 8 | dienst, nullbar, identität | gemischt | 6 | – | – | `mfg`/`portal` nur frisch | Dienst zuerst; `dev_mock` entfernen statt absichern | einzeln |

## 5. Reihenfolge der Domain-Slices

Jeder Slice bringt Migration, Fachkorrekturen, Verhaltenstests als `valeo_app`, das
aktualisierte Inventar und die verkürzte Ausnahmeliste mit, dazu QA-Bericht und Handshake.
Er stapelt auf dem vorigen.

1. **RLS-DOMAIN-PRICING** (umgesetzt, `docs/quality-assurance/rls-domain-pricing-20261027.md`) — `price_lists` + `price_list_items`. Gewählt, weil: 0 Zeilen live
   (keine Datenbereinigung), kein Worker, zwei Verbraucher (`price_lists.py`,
   `preisfindung_service.py`), ein Rückfall. Der Slice führt das schwierigste Muster
   vollständig ein: Positionen mit vom Kopf abgeleitetem Mandanten und Sperre gegen fremde
   Elternbelege. Fachkorrektur: Lese-, Änderungs- und Löschwege in `price_lists.py` filtern
   heute gar nicht nach Mandant, und die Anlage nimmt den Mandanten aus einem Query-Parameter
   mit Standardwert.
2. hr + audit/compliance + nachweisraum (je kleiner Slice, keine Daten).
3. docflow, ki, sales (Belegketten, Positionsmuster wiederverwenden).
4. einkauf, logistics/log/ops.
5. erp, agrar (Referenzdatenfamilien mit Begründung), inventory, crm.
6. shared (Identität, Outbox) und alles mit Ursache `dienst` erst nach dem
   Dienst-Identitätsvorschlag.

## 6. Abnahme vor der Live-Aktivierung (je Domain)

Die Verhaltenstests laufen als `valeo_app` in einer zurückgerollten Transaktion auf
`valeo_probe`. Vor dem Live-Schalten durch Codex braucht jede Domain außerdem:

- **Maskenabnahme** mit gewachsenen Daten. Für pricing sind das Preislisten-Liste und
  -Detail, Anlage/Änderung/Löschung und die Preisfindung in der Auftragserfassung
  (`/api/v1/pricing/...`).
- **Worker**: die Matrix nennt sie je Domain, für pricing keinen.
- **Kein Superuser im Pfad**: Bestandstests verbinden als Superuser und sehen RLS nicht.
