# Rettung: LKW-Dispositionszuweisung (Stand 09.11.2026)

Gesichert beim Glattziehen der Codex-Staende (Nutzerauftrag 09.11.2026: "LKW Dispositionsaenderungen auf
Rettungsbranch vollstaendig sichern"). **Nicht fuer main** ohne fachliche Pruefung; nichts davon ist eingebunden.

## Inhalt

| Datei | Herkunft | Stand |
|---|---|---|
| `app/api/v1/endpoints/disposition_assignment.py` | Hauptbaum, unversioniert | 22.10.2026 |
| `app/services/disposition_assignment_service.py` | Hauptbaum, unversioniert | 22.10.2026 |
| `app/services/disposition_assignment_repository.py` | Hauptbaum, unversioniert | 22.10.2026 |
| `app/services/disposition_assignment_validation.py` | Hauptbaum, unversioniert | 22.10.2026 |
| `tests/test_disposition_assignment_persist.py` | Hauptbaum, unversioniert | 22.10.2026 |
| `tests/test_disposition_assignment_validation.py` | Hauptbaum, unversioniert | 22.10.2026 |
| `docs/agent-ops/handoffs/adaptive-workspace-20261022.md` | Hauptbaum, unversioniert (Abnahme LKW-Dispositionstafel) | 22.10.2026 |

## Vollstaendigkeit geprueft

* Inhaltlich identisch (ohne Zeilenenden) mit der aelteren Codex-Rettung `codex/wip-rescue-20261023` (Commit
  `963b04b96`); seitdem nicht weiterbearbeitet.
* Codex-Klon `Documents/ChatGPT/Runtime Punkte schließen/repo`: keine Fassung dieser Dateien.
* Codex-Sitzungen 12.10., 30.10., 04./05.11.2026: keine spaetere Aenderung an den Dateien; die November-Sitzungen
  betreffen nur die Dispositionstafel, die bereits in main liegt
  (`packages/frontend-web/src/components/mask-builder/specialized/disposition-board*.{tsx,json}`).
* Keine Router-Registrierung in `app/api/v1/api.py`, keine eigene Migration: Das Repository schreibt in die
  vorhandenen Tabellen `domain_logistics.tours` / `tour_stops` (Spalten der Kern-Migration).

## Vor einer Uebernahme

* Router `/logistik/disposition` einbinden und gegen `tests/test_compliance_register_batch9.py` pruefen (dort ist nur
  `/api/v1/disposition` verboten, nicht `/logistik/disposition`).
* Schreibweg als Fachaktion fuer Maske, CLI und MCP (`run_delegated_mask_action`), Mandantenbindung, Rollen.
* f-String-SQL (`TOURS_TABLE`/`STOPS_TABLE`) gegen die SQL-Ratsche pruefen; Tests auf frischem Pruefstand.
