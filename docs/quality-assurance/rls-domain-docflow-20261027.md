---
title: QA RLS-DOMAIN-DOCFLOW-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: Nachweis für die RLS-Domain docflow (Belegköpfe, Positionen, Archivartefakte, E-Rechnungs-XML, TSE-Geräte) mit Verbund-FKs und tokengebundenem GoBD-Archiv.
---

# QA RLS-DOMAIN-DOCFLOW-20261027

**Basis:** `claude/system-tenant-fallback-20261027` (#71), Zweig `claude/rls-domain-docflow-20261027`.
Migration `rls_domain_docflow_20261027` folgt auf `rls_knowledge_objects_shared_20261027`.

## Lieferung

| Datei | Änderung |
|---|---|
| `alembic/versions/rls_domain_docflow_20261027.py` | getrennte Policies `tenant_isolation_*` (kein `system`-Lesen) auf `document_headers`, `document_items`, `document_artifacts`, `invoice_xml_store`, `pos_tse_devices`; `UNIQUE (id, tenant_id)` an `document_headers` und `pos_terminals`; Verbund-FKs Positionen/Artefakte/XML → Kopf und TSE → Terminal, ON DELETE wie vorher; Abbruch bei Platzhalter-Mandanten oder fremden Elternsätzen |
| `app/api/v1/endpoints/gobd_archiv.py` | alle 8 Wege nehmen den Mandanten aus dem Token (`get_tenant_id`) statt aus `?tenant_id=` mit Standardmandant |
| `tests/test_rls_domain_docflow.py` | 15 Tests als `valeo_app` |
| Inventare, `rls-exceptions.json`, OpenAPI `/gobd/*` | 195 zurückgestellt (−5) |

Gewachsene Daten: 25 Köpfe, 35 Positionen, 2 Artefakte und 1 XML in zwei Mandanten. Keine
Kindzeile hängt unter einem Kopf eines anderen Mandanten.

## Nachweise (valeo_probe, zurückgerollt)

```
pytest tests/test_rls_domain_docflow.py                     -> 15 passed
31 docflow-/GoBD-Bestandsmodule (conftest, Prüfstand)       -> 402 passed, 0 rot
pytest tests/test_rls_*.py tests/test_provision_db_roles.py tests/test_system_tenant_fallback_contract.py -> 213 passed
Gegenprobe ohne Verbund-FKs                                 -> 6 Tests rot
```

| Abnahmekriterium | Test |
|---|---|
| Mandantengrenze je Tabelle (eigen ok; fremd und `system` SELECT/INSERT/UPDATE/DELETE gesperrt; kein `tenant_id`-Wechsel; fail-closed) | `test_mandantengrenze_je_tabelle` (5) |
| keine Position, kein Artefakt, kein XML unter fremdem Kopf; keine TSE an fremdem Terminal; auch nicht durch Umhängen | `test_kein_verweis_auf_fremde_elternsaetze` (4) |
| Kopf mit Positionen kann den Mandanten nicht wechseln | `test_kopf_mit_positionen_behaelt_seinen_mandanten` |
| Kontextwechsel/Savepoint, Pool, Hintergrund | je ein Test |
| Fachkette GoBD-Archiv: E-Rechnung speichern → abrufen → validieren, Artefakte listen; fremder Mandant sieht nichts und kann keine E-Rechnung an einen fremden Kopf hängen | `test_fachkette_e_rechnung_und_archiv` |

## Folgebefund / vor Live-Aktivierung

- **Weitere Kinder von `document_headers`** sind P5-Tabellen und haben einfache FKs:
  `document_links`, `document_header_links`, `document_postings`, `pos_receipt_compliance`
  und `document_return_cases`. Dort fehlt die strukturelle Sperre gegen fremde Köpfe noch.
  Mit `UNIQUE (id, tenant_id)` am Kopf ist der Verbund-FK jetzt möglich (eigener Slice).
- **Masken:** Belegkette Verkauf/Einkauf (Kopf, Positionen), GoBD-Archiv, E-Rechnung,
  POS/TSE, jeweils mit zwei Mandanten. Die Statushistorie schreibt ein Trigger in eine
  P5-Tabelle; live hat `valeo_app` dafür die Rechte.
