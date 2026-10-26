---
title: Restliche CRM-Dienst-Ketten (2026-10-26)
type: qa
audience: [entwickler, qa, betrieb]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# Restliche CRM-Dienst-Ketten (2026-10-26)

Slice `CRM-CHAINS-REST-20261026`, Zweig `claude/crm-chains-rest-20261026`, gestapelt auf
`SERVICES-VERSION-TABLE-20261026` (PR #52). Auftrag: Codex-Empfehlung nach #52/#53.

## Ausgangslage

crm-ai, crm-consent, crm-gdpr und crm-marketing hatten keine eigene Versionstabelle (Ratsche
im Vertragstest). Keiner der Dienste laeuft; ihre Tabellen gibt es weder in `valeo_neuro_erp`
noch auf valeo_probe, das Backend verwendet keinen ihrer Tabellennamen.

| Dienst | Befund der Altkette gegen `app.db.models` |
| --- | --- |
| crm-ai | laeuft, weicht ab: IDs varchar statt uuid, jsonb statt json, Nullbarkeit |
| crm-consent | laeuft, weicht ab: IDs/Tokens varchar statt uuid, Enum-Spalten als varchar(20) |
| crm-gdpr | laeuft, weicht ab wie crm-consent; Zeitstempel der Loeschtabellen nullbar |
| crm-marketing | nicht aufloesbar: `002_add_campaign_schema` verweist auf das nicht vorhandene `001_initial_segment_schema` und legt Enums doppelt an; Doublette von `002_campaign`. Auch ohne sie: 38 Spalten und eine Tabelle (`campaign_ab_tests` statt `campaign_variants`) abweichend |

Was nur die Altketten trugen:

- **Indizes** auf echten Abfragewegen (consent: status, channel, history.changed_at; gdpr:
  requests.status/request_type, history.changed_at, vier Indizes der Loeschtabellen inkl.
  `ix_privacy_erasure_exec_gate`; marketing: recipients.email) – **in die Modelle
  uebernommen**, damit die Modelle die eine Quelle bleiben.
- **Token-Eindeutigkeit** (`double_opt_in_token`, `verification_token`) – war in den Modellen
  bereits als eindeutiger Index vorhanden, nichts verloren.
- **Server-Defaults** – bewusst nicht uebernommen: das ORM setzt alle Werte selbst, und die
  Enum-Defaults der Altketten (`'pending'`) passen nicht zu den Modell-Enums, die Namen
  speichern (`'PENDING'`).

## Aenderung

- vier `env.py`: `version_table=VERSION_TABLE` online und offline.
- Altrevisionen entfernt (keine war je angewendet), je eine Basis `<dienst>_0001` per
  Autogenerate aus den Modellen gegen einen leeren Suchpfad auf valeo_probe (nur lesend);
  `astext_type=Text()` der Autogenerate-Ausgabe zu `sa.Text()` korrigiert.
- `tests/test_service_alembic_version_tables.py`: Ratsche leer, Revisionspruefung fuer alle
  Dienste.

## Pruefung (valeo_probe, je Dienst eine Transaktion, ROLLBACK)

- Offline-SQL: kein Enum doppelt (auch das von zwei Tabellen genutzte `consentstatus` einmal).
- Online `upgrade()` im Schema `vt_chain` gegen `create_all` der Modelle in `vt_model`:
  Tabellen 5/2/5/10, 0 Abweichungen bei Spalten (Typ, Laenge, Nullbarkeit, Default),
  Indizes, Constraints, Enum-Werten; `downgrade()` hinterlaesst 0 Tabellen und 0 Typen.
- Negativprobe: verfaelschte Spaltenlaenge wird gemeldet.
- Danach keine `vt_*`-Schemata. Vertragstest 18 gruen, crm-gdpr-Diensttests 5 gruen,
  `test_ai_service_no_huggingface_contract.py` gruen; Inventare unveraendert aktuell.

## Live

Keine Aenderung. Die Dienste laufen nicht; beim ersten Start legt ihr Entrypoint die Tabellen
ueber die Migrator-Anmeldung an.

Keine Aussage ueber vollstaendige Sicherheit oder Gesamtfreigabe.
