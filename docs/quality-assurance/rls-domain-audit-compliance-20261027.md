---
title: QA RLS-DOMAIN-AUDIT-COMPLIANCE-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: Nachweis für die RLS-Domain audit/compliance (Attestierungen, Löschanträge, Intrastat, PCN-Verlauf) mit getrennten Policies, Verbund-FK und zwei Fachkorrekturen.
---

# QA RLS-DOMAIN-AUDIT-COMPLIANCE-20261027

**Basis:** `claude/rls-domain-hr-20261027` (#66), Zweig `claude/rls-domain-audit-compliance-20261027`.
Migration `rls_domain_audit_compliance_20261027` folgt auf `rls_domain_hr_20261027`.

## Lieferung

| Datei | Änderung |
|---|---|
| `alembic/versions/rls_domain_audit_compliance_20261027.py` | getrennte Policies `tenant_isolation_*` (kein `system`-Lesen) auf `domain_audit.attestations`, `domain_compliance.compliance_pcn_status_log`, `data_erasure_requests`, `intrastat_meldungen`; PCN-Verlauf tenant_id NOT NULL; Verbund-FK `(meldung_id, tenant_id) → compliance_pcn_meldungen(id, tenant_id)` ohne CASCADE; Abbruch bei Platzhalter-Mandanten und bei verwaisten oder fremden Verlaufszeilen |
| `app/services/compliance_pcn_lifecycle_service.py` | Lesen, Statuswechsel und Rückzug nur im eigenen Mandanten; eine fremde Kennung ergibt „nicht gefunden“ statt „gehört nicht zu Tenant“ (vorher Existenzhinweis) |
| `app/api/v1/endpoints/intrastat.py` | `PUT /intrastat/meldungen/{id}` auf eine fremde oder fehlende Meldung ergibt 404; vorher meldete der Weg „aktualisiert“ ohne Wirkung |
| `tests/test_rls_domain_audit_compliance.py` | 12 Tests als `valeo_app` |
| Inventare, `rls-exceptions.json` | 512 Tabellen mit RLS, 203 zurückgestellt (−4) |

Die Matrix-Fundstellen sind Fehltreffer der dateiweiten Heuristik:
- `compliance.py:846` ist ein Kommentar.
- `compliance_dsgvo.py:205` betrifft `domain_crm.activities`.
- `sales_delivery_notes.py:54` ist eine ungenutzte Konstante `DEFAULT_TENANT`. Gemeldet, nicht geändert: die Datei gehört zur Domain sales.

Die Anlage einer Attestierung nimmt den Mandanten aus `get_tenant_id`.

## Nachweise (valeo_probe, zurückgerollt; Rolle valeo_app)

```
pytest tests/test_rls_domain_audit_compliance.py  -> 12 passed
pytest tests/test_steuernachweis_mandant_vertrag.py tests/test_dom_compliance_004.py \
       tests/test_intrastat_pruefung.py tests/test_sanctions_genossenschaft_intrastat.py
  -> 63 passed (mit conftest, DATABASE_URL = Prüfstand; der Vertragstest räumt seine
     Zeilen selbst ab, danach 0 Testzeilen in den vier Tabellen)
```

| Abnahmekriterium | Test |
|---|---|
| eigener Mandant anlegen/ändern/löschen; fremder Mandant SELECT/INSERT/UPDATE/DELETE gesperrt; `system` weder lesbar noch änderbar, löschbar oder übernehmbar; kein `tenant_id`-Wechsel; ohne Kontext fail-closed | `test_mandantengrenze_je_tabelle` (4 Tabellen) |
| kein Verlauf unter fremder Meldung, kein Umhängen; Meldung mit Verlauf nicht still löschbar | `test_pcn_verlauf_nicht_unter_fremder_meldung` |
| Kontextwechsel, Savepoint, Pool | `test_kontextwechsel_und_savepoint`, `test_pool_wiederverwendung` |
| Hintergrund nur mit ausdrücklichem Kontext | `test_hintergrund_nur_mit_ausdruecklichem_kontext` |
| Fachkette PCN: Anlage → Prüfung → Rückzug mit Verlauf; fremder Mandant „nicht gefunden“, sieht keinen Verlauf | `test_fachkette_pcn_lebenszyklus` |
| Fachkette Intrastat: Anlage → Liste → Änderung → Löschung; fremder Mandant 404 bei Ändern, Löschen und Prüfen | `test_fachkette_intrastat` |
| Fachkette Löschantrag (Art. 17): Anlage → Abruf → Ablehnung; fremder Mandant 404 | `test_fachkette_loeschantrag` |

**Gegenprobe:** Ohne die Intrastat-Korrektur wird `test_fachkette_intrastat` rot. Die
PCN-Korrektur wirkt auch ohne RLS; unter RLS sieht der Dienst die fremde Meldung ohnehin
nicht.

## Befunde und Risiken

- **Musterbefund für spätere Domains:** „gehört nicht zu Tenant“ nach einem Lesen ohne
  Mandantenfilter steht auch in `agrar_partie_aggregate_service`,
  `agrar_selbstabrechnung_lifecycle_service`, `agrar_trocknung_abrechnung_service`,
  `compliance_vvvo_sachkunde_service` und `controlling_budget_lifecycle_service`. Diese
  Dateien sind nicht in diesem Slice; sie kommen mit ihren Domains.
- **Nebenbefund, nicht geändert:** `IntrastatMeldungCreate` beschreibt `meldungsart` als
  „EINGANG | VERSENDUNG“, die Prüfbedingung der Tabelle erlaubt aber `VERSAND`.
- **Schemadrift:** `domain_audit.attestations` hat live 8 Spalten und keine FKs, im frischen
  Schema 11 Spalten mit FKs. Die Migration berührt nur Policies und ist für beide Stände
  geprüft (frisch: Tests; live: nur Lesen, 0 Zeilen).
- **Vor der Live-Aktivierung** sind abzunehmen: Masken Intrastat, Löschanträge (DSGVO),
  PCN-Meldungen und der Lieferschein-Druck mit Attestierung, jeweils mit zwei Mandanten.
  Worker: keine.
- Der P5-Formtest (Codex) bleibt für neue Tabellen ohne `system`-Lesen rot (Handshake hr).
