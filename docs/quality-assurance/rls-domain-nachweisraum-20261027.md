---
title: QA RLS-DOMAIN-NACHWEISRAUM-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: Nachweis für die RLS-Domain nachweisraum (Nachweisdokumente, GoBD-Exporte) mit getrennten Policies, Verbund-FK des Prüfprotokolls und tokengebundenem Mandanten.
---

# QA RLS-DOMAIN-NACHWEISRAUM-20261027

**Basis:** `claude/rls-domain-audit-compliance-20261027` (#67), Zweig `claude/rls-domain-nachweisraum-20261027`.
Migration `rls_domain_nachweisraum_20261027` folgt auf `rls_domain_audit_compliance_20261027`.

## Lieferung

| Datei | Änderung |
|---|---|
| `alembic/versions/rls_domain_nachweisraum_20261027.py` | getrennte Policies `tenant_isolation_*` (kein `system`-Lesen) auf `nachweisraum_dokumente` und `gobd_exporte`; Verbund-FK `nachweisraum_audit_log (dokument_id, tenant_id) → nachweisraum_dokumente` ohne CASCADE; Abbruch bei Platzhalter-Mandanten und bei verwaisten oder fremden Protokollzeilen |
| `app/api/v1/endpoints/doc_nachweisraum_actions.py` | Mandant aus `get_tenant_id` (Token) statt `Header(x_tenant_id)` in allen vier Wegen |
| `app/services/doc_nachweisraum_lifecycle_service.py` | Wiederlesen nach Anlage und Statuswechsel nur im eigenen Mandanten |
| `tests/test_rls_domain_nachweisraum.py` | 1 Quelltextvertrag + 9 Tests als `valeo_app` |
| `tests/rls_domain_support.py` | Eigentümer-Vergleich über `::text` (UUID-Schlüssel) |
| Inventare, `rls-exceptions.json`, OpenAPI (nur `/nachweisraum/*`) | 514 Tabellen mit RLS, 201 zurückgestellt (−2) |

## Nachweise (valeo_probe, zurückgerollt; Rolle valeo_app)

```
pytest tests/test_rls_domain_nachweisraum.py tests/test_dom_doc_004.py tests/test_welle7_response_models.py \
       tests/test_rls_domain_hr.py tests/test_rls_domain_audit_compliance.py   -> 58 passed
pytest tests/test_mcp_execution.py -k "nachweis or gobd" (mit conftest)        -> 1 passed
pytest tests/test_rls_*.py tests/test_provision_db_roles.py
  -> 153 passed, 1 failed (bekannter P5-Formtest, Codex-Besitz)
python scripts/pruefstand_db.py --status -> loading_stop_fk_20261023 (unverändert)
```

| Abnahmekriterium | Test |
|---|---|
| Mandant nur aus dem Token, kein `Header(...)` | `test_endpunkte_nehmen_den_mandanten_nur_aus_dem_token` |
| eigener Mandant anlegen/ändern/löschen; fremder Mandant SELECT/INSERT/UPDATE/DELETE gesperrt; `system` weder lesbar noch änderbar, löschbar oder übernehmbar; kein `tenant_id`-Wechsel; ohne Kontext fail-closed | `test_mandantengrenze_je_tabelle` |
| kein Protokoll unter fremdem Dokument, kein Umhängen; Dokument mit Protokoll nicht still löschbar | `test_pruefprotokoll_nicht_unter_fremdem_dokument` |
| Kontextwechsel, Savepoint, Pool, Hintergrund | `test_kontextwechsel_und_savepoint`, `test_pool_wiederverwendung`, `test_hintergrund_nur_mit_ausdruecklichem_kontext` |
| Fachkette Dokument (Eingang → Prüfung → Freigabe) und GoBD-Export (Offen → In Erstellung); fremder Mandant „nicht gefunden“, sieht kein Protokoll | `test_fachkette_dokument_und_gobd_export` |

**Gegenprobe:** Ohne den Verbund-FK wird der Elternbeleg-Test rot.

## Risiken / vor Live-Aktivierung

- Die MCP-Lesewege (`mcp_execution_service.py`, Nachweis- und GoBD-Status) filtern bereits
  tokengebunden. Der Matrix-Treffer „referenzdaten“ war ein Fehltreffer.
- **Masken:** Nachweisraum (Dokumente, Freigabe, Wiedervorlage) und GoBD-Export mit zwei
  Mandanten. **Worker:** keine.
- Der P5-Formtest (Codex) bleibt für Tabellen ohne `system`-Lesen rot (Handshake hr).
