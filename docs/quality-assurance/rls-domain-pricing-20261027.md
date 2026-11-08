---
title: QA RLS-DOMAIN-PRICING-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: Nachweis für die erste RLS-Domain domain_pricing (Preislisten und Positionen) mit getrennten Policies, Verbund-FK und tokengebundenem Mandanten.
---

# QA RLS-DOMAIN-PRICING-20261027

**Basis:** `claude/rls-domains-matrix-20261027` (#64), Zweig `claude/rls-domain-pricing-20261027`.
Migration `rls_domain_pricing_20261027` folgt auf `rls_system_role_20261026`.

## Lieferung

| Datei | Änderung |
|---|---|
| `alembic/versions/rls_domain_pricing_20261027.py` | `price_list_items.tenant_id` aus dem Kopf (NOT NULL, Default `rls_current_tenant()`), `UNIQUE (id, tenant_id)` am Kopf, Verbund-FK `fk_pli_price_list_tenant`, getrennte Policies auf beiden Tabellen, kein `system`-Lesen; Abbruch bei Platzhalter-Mandanten |
| `app/api/v1/endpoints/price_lists.py` | Mandant aus `get_tenant_id` (Token) statt `Query(DEFAULT_TENANT_ID)`/Body; Lesen, Ändern und Löschen filtern nach Mandant (vorher gar nicht); Positionen mit `tenant_id`; Cache wird auch bei Änderung/Löschung invalidiert; `SCHREIBEN["VERKAUF"]` unverändert |
| `tests/test_rls_domain_pricing.py` | 2 Quelltextverträge + 11 Verhaltenstests als `valeo_app` |
| `docs/admin/rls-inventory.json`, `rls-rollout.json`, `rls-domain-matrix.*`, `migration-inventory.md` | regeneriert: 503 Tabellen mit RLS, 212 zurückgestellt |
| `docs/admin/rls-exceptions.json`, `tests/test_rls_domain_matrix.py` | zwei Einträge ausgetragen, Obergrenze 214 → 212 |

## Fachbefund vor der Korrektur

`GET/PUT/DELETE /api/v1/price-lists/{id}` lasen, änderten und löschten Preislisten **jedes**
Mandanten nur über die ID. Die Anlage nahm den Mandanten aus `?tenant_id=` mit dem Standard
`DEFAULT_TENANT_ID` oder aus dem Body. Die Middleware prüft Body-Selektoren gegen das Token.
Der Query-Parameter und der fehlende Filter blieben trotzdem eine Lücke. Das Frontend
(`lib/api/konditionen.ts`) sendet `?tenant_id=` noch mit; der Parameter wird jetzt
ignoriert.

## Nachweise (valeo_probe, zurückgerollt; Rolle valeo_app)

```
python scripts/pruefstand_db.py --status  -> Revision loading_stop_fk_20261023 (vorher und nachher)
pytest tests/test_rls_domain_pricing.py   -> 13 passed
pytest tests/test_rls_*.py tests/test_provision_db_roles.py
  -> 118 passed, 1 failed (test_rls_p5_rollout::…genau_die_mandantenpolicy, siehe Risiken)
python scripts/generate_code_inventories.py --check -> OK
```

| Abnahmekriterium | Test |
|---|---|
| eigener Mandant erfolgreich (SELECT/INSERT/UPDATE/DELETE, Position erbt Mandanten) | `test_eigener_mandant_lesen_anlegen_aendern_loeschen` |
| fremder Mandant: SELECT, INSERT, UPDATE, DELETE gesperrt | `test_fremder_mandant_select_insert_update_delete_gesperrt` |
| fehlender Kontext fail-closed (auch `cross_tenant_scope` ohne Systemverbindung) | `test_ohne_mandantenkontext_fail_closed` |
| `tenant_id`-Wechsel zum fremden Mandanten oder zu `system` gesperrt | `test_wechsel_von_tenant_id_zum_fremden_mandanten_gesperrt` |
| `system`-Zeilen: hier nicht lesbar (keine Freigabe), weder änderbar noch löschbar noch übernehmbar | `test_system_zeilen_…` |
| keine Position unter fremdem Kopf, auch nicht durch Umhängen | `test_keine_position_unter_fremdem_elternbeleg` |
| Kontextwechsel und Savepoint-Rollback ohne Übertrag | `test_kontextwechsel_und_savepoint_rollback_ohne_mandantenuebertrag` |
| Pool-Wiederverwendung (gleiche Backend-PID, echte Commits, temporäre Tabelle) | `test_pool_wiederverwendung_uebertraegt_keinen_mandanten` |
| Hintergrundarbeit nur mit ausdrücklichem Kontext; `valeo_system` sieht alles | `test_hintergrundverarbeitung_nur_mit_ausdruecklichem_kontext` |
| Fachkette Anlage → Liste → Detail → Änderung → Preisfindung → Löschung; fremder Mandant 404 | `test_fachkette_preislisten_und_preisfindung` |
| Policy-Form `getrennt` | `test_migration_und_policy_form` |

**Gegenprobe:** Zwei Mutationen der Migration wurden ausgeführt und danach zurückgenommen.
- Einfacher FK statt Verbund-FK: Der Elternbeleg-Test wird rot.
- Zusätzliche ALL-Policy der Altform: Sechs Tests werden rot, darunter Fremdzugriff, `system` und Hintergrund.

## Verbleibende Risiken / vor Live-Aktivierung

- **Überschneidung mit Codex:** `test_rls_p5_rollout.py::test_alle_rls_tabellen_tragen_genau_die_mandantenpolicy`
  verlangt für jede RLS-Tabelle genau `tenant_isolation`. Er ist rot für die beiden
  Pricing-Tabellen. CI setzt `TEST_DATABASE_URL` nicht, deshalb zeigt sich das nur auf dem
  Prüfstand. Die Lösung liegt bei Codex' P3/P5-Korrektur (Handshake).
- **Maskenabnahme mit gewachsenen Daten** (live 0 Preislisten): Konditionen/Preislisten-Maske
  mit Anlage, Änderung und Löschung, außerdem `POST /api/v1/pricing/...` in der
  Auftragserfassung, beides mit zwei Mandanten.
- **Worker:** keine. Die Preisfindung liest nur im Request.
- Die Migration ist live nicht angewendet. Sie läuft durch Codex im Wartungsfenster, nach P1/P2.
