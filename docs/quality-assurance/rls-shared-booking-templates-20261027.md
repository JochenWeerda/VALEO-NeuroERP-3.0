---
title: QA RLS-SHARED-BOOKING-TEMPLATES-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: Gemeinsame System-Buchungsvorlagen für alle Mandanten lesbar und anwendbar, nicht änderbar; erste begründete system_lesbar-Tabelle.
---

# QA RLS-SHARED-BOOKING-TEMPLATES-20261027

**Nutzerentscheidung 2026-10-27:** System-Vorlagen stehen allen Mandanten zur Verfügung.
**Basis:** `claude/rls-systemwide-split-20261027` (#69), Zweig `claude/rls-shared-booking-templates-20261027`.

## Lieferung

| Datei | Änderung |
|---|---|
| `alembic/versions/rls_booking_templates_shared_20261027.py` | `tenant_isolation_select` auf `domain_erp.booking_templates`: eigene + `system`-Zeilen. INSERT/UPDATE/DELETE bleiben eigen. Rückweg: nur eigene |
| `docs/admin/rls-exceptions.json` | erste Begründung in `system_lesbar` |
| `app/api/v1/endpoints/booking_templates.py` | Liste und Abruf zeigen eigene und gemeinsame Vorlagen (`shared`). Anwenden einer gemeinsamen Vorlage bucht im eigenen Mandanten, Konten: eigenes Konto vor gemeinsamem Kontenrahmen (wie `sales_credit_notes.py`/`steuerschluessel.py`). Ändern und Löschen einer gemeinsamen Vorlage: 403 statt 404 |
| `tests/test_rls_shared_booking_templates.py` | 3 Tests als `valeo_app` |
| `tests/test_booking_templates_api.py` | Fake-Zeile um die Spalte `shared` ergänzt (SELECT-Reihenfolge) |
| `tests/test_rls_system_read_justified.py` | `KEEP_SYSTEM_READ ⊆ system_lesbar`; spätere Freigaben laufen über eigene Migrationen |
| OpenAPI | nur `BookingTemplateResponse.shared` |

## Nachweise (valeo_probe, zurückgerollt)

```
pytest tests/test_rls_shared_booking_templates.py                  -> 3 passed
pytest tests/test_booking_templates_api.py tests/test_hauptbuch_rollen_vertrag.py (conftest) -> 847 passed
pytest tests/test_rls_*.py tests/test_provision_db_roles.py        -> 191 passed
```

| Abnahmekriterium | Test |
|---|---|
| Freigabe begründet, Form `getrennt_system` | `test_freigabe_ist_begruendet_und_form_stimmt` |
| gemeinsame Vorlage für A und B lesbar; weder änderbar noch löschbar noch übernehmbar; keine neue `system`-Vorlage durch Mandanten; eigene Vorlage nicht auf `system` umhängbar; ohne Mandant nichts sichtbar | `test_gemeinsame_vorlagen_lesbar_aber_nicht_aenderbar` |
| Fachkette: Liste mit Kennzeichen, Anwenden einer gemeinsamen Vorlage → Buchungsentwurf im eigenen Mandanten, eigenes Konto 9810 vor dem gemeinsamen, gemeinsames Konto 9820; Ändern/Löschen 403; fremde eigene Vorlage für B 404; gemeinsame für B sichtbar | `test_fachkette_gemeinsame_vorlage_anwenden` |

`test_studio_listen_kommandos.py` hat 14 rote Tests zu Lade-Grenzen (`limit ≤ 200`). Sie
sind auf der Basis #69 genauso rot, also vorbestehend und Studio-Besitz.

## Offen

- **Maske `finance/buchungsvorlagen`** (`screen_definitions_listen.py`, Codex-Leadbesitz,
  generierte Studio-Artefakte): Spalte „Gemeinsam“ (`shared`) und `visibleWhen` für
  „Löschen“ nur bei eigenen Vorlagen. Bis dahin beantwortet der Server „Löschen“ einer
  gemeinsamen Vorlage mit einer verständlichen 403-Meldung.
- **Live:** Die 70 `system`-Vorlagen stehen allen Mandanten zur Verfügung, sobald die
  Migration läuft. Ob ihre Kontonummern zum jeweiligen Kontenrahmen passen, zeigt die
  Anwendung: Fehlt das Konto, antwortet sie mit „Account not found“.
