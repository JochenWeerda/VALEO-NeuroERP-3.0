---
title: QA RLS-DOMAIN-OPS-TEIL2-20261028
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-28
version: 1.0.0
description: Zehn domain_ops-Tabellen ohne Mandantenspalte (live leer) mit Mandant, getrennten Policies und Verbund-FKs; Dokument-, Waage-, Fuhrpark-, Frachttarif- und Rahmenvertragswege im Token-Mandanten mit Urheber aus dem Token.
---

# QA RLS-DOMAIN-OPS-TEIL2-20261028

**Basis:** `claude/rls-domain-erp-20261028` (#87). Migration `rls_domain_ops_teil2_20261028` folgt auf
`rls_domain_erp_20261028`; `alembic heads` zeigt einen Head. Live sind alle zehn Tabellen leer: kein Datensatz
muss zugeordnet werden. Findet die Migration Zeilen ohne Mandantenspalte, bricht sie ab.

## Befunde

| Weg | Befund | Korrektur |
|---|---|---|
| `/dokumente` (8 Wege) | Tabelle ohne Mandant: Liste, Abruf, Aenderung, Loeschung und Versionen ueber alle Mandanten; Urheber- und Loeschfelder frei im Rumpf (`hochgeladen_von`, `created_by`, `geloescht_von`) | Token-Mandant, fremd 404; Urheber, Aenderer, Loescher und Versionsersteller aus dem Token |
| `/einkauf/suppliers/{id}/documents` (compat) | ohne Mandant; Urheber aus `hochgeladenVon`, sonst `"system"` | Token-Mandant, Urheber aus dem Token |
| `/waage/waagen`, `/waage/wiegungen` | ohne Mandant; Wiegung konnte auf jede Waage zeigen | Token-Mandant; fremde Waage 404; Urheber aus dem Token |
| `POST /waage/wiegungen` | Partiepflicht-Angaben (`wiegetyp`, `partie_id`, `charge_id`, `lot_id`) gingen als Spalten in `Wiegung(**daten)`: **jede partiepflichtige Wiegung scheiterte** (TypeError, 400) | Partie wird `chargennummer`, Pruefangaben werden nicht gespeichert; unbekannte Felder 422 |
| Fuhrpark Schaeden, Bussgelder, Statushistorie | Kindtabellen ohne Mandant (Lesen ueber das mandantengepruefte Fahrzeug), `erstellt_von`/`benutzer` aus dem Rumpf | Mandant beim Schreiben und in jedem Filter; Bearbeiter aus dem Token |
| `/strecke-speditionen/frachttarife`, `/vertraege/rahmenvertraege`, Kontraktliste | ohne Mandant; Rahmenvertragsnummer systemweit eindeutig | Token-Mandant; Nummer je Mandant eindeutig |
| `app/core/database.py` (SQL-Ausweichpfad) | legte `ops_dokumente`, `ops_dokument_versionen`, `ops_rahmenvertraege` ohne Mandant an | mit `tenant_id NOT NULL`, Nummer je Mandant |

**Repositories:** `Waage`, `Wiegung`, `FahrzeugTour`, `SpeditionFrachttarif`, `Dokument`, `DokumentVersion` und
`Rahmenvertrag` nehmen den Mandanten im Konstruktor (ohne Mandant `ValueError`); jede Abfrage filtert, Anlage setzt
ihn, Schluessel und Mandant aus der Nutzlast werden verworfen. Ein alter Aufruf ohne Mandant scheitert laut, statt
mandantenuebergreifend zu lesen.

**Schema:** getrennte Policies, `tenant_id` NOT NULL mit Vorgabe aus dem Kontext; Verbund-FKs Version->Dokument,
Bussgeld/Schaden/Statushistorie/Tour->Fahrzeug, Wiegung->Waage (SET NULL nur auf `waage_id`). Live fehlte
`UNIQUE (id, tenant_id)` auf `ops_fahrzeuge` (Drift); die Migration legt es bei Bedarf an. Ausnahmen 69 → 65.

## Nachweise

```
pytest tests/test_rls_domain_ops_teil2.py                             -> 25 passed, 0 skipped (valeo_probe)
Gegenprobe alter Code ohne Migration                                  -> 25 rot
Gegenprobe alter Code mit Migration                                   -> 6 rot (alle Fachwege), 19 Schema gruen
70 betroffene Bestandsmodule (4 Pakete zu 20, Speicherpruefung)       -> 0 neu rot
   (12 rot wie auf der Basis: Meridian 4, MCP-Lokalaktionen 5, Tourenplanung 1, Architektur-Index 1, Welle-4 1)
RLS-Suite + Fallback-, Identitaets-, Urheber- und Kontenplan-Vertrag  -> 685 passed, 0 skipped
alembic heads 1; RLS-Inventar/Matrix/Systemlesen/Rollout und Code-Inventare neu erzeugt
```

## Testgrenze nachgezogen

- `tests/test_fuhrpark_isolation_effects.py::db` oeffnete den Pruefstand **ohne** die ausstehenden Migrationen;
  jede neue Spalte machte die Fuhrpark-Tests dort rot. Neu: modulweite Fixture `pruefstand` spielt sie zurueckgerollt
  ein (wie `rls_domain_support.probe`), `db` ist ein Savepoint je Test. Bewusst je Modul, nicht je Prozess: ein erster
  Versuch je Prozess hielt die Tabellensperren der Migrationen bis zum Prozessende und liess spaetere Tests haengen.
- `tests/test_waage_api.py`: HTTP-Tests gegen `app.main` laufen auf derselben migrierten Verbindung; Repository-Attrappen
  mit Mandant; zwei Tests, die 201/400/500 gleichermassen akzeptierten, pruefen jetzt 422 (unbekanntes Feld), 201 mit
  Mandant und 404 (fremde Waage).

## Offen

- **13 domain_ops-Tabellen mit Live-Zeilen ohne Mandantenspalte** (`ops_disposition` 74, `ops_labor_auftraege` 74,
  `ops_zertifikate` 61, `ops_labor_proben` 7, `ops_compliance_items` 3 und weitere mit 1–2 Zeilen). Der Mandant ist
  nicht ableitbar: `ops_labor_auftraege` haengt an Chargen mit `legacy-unassigned`, die uebrigen tragen keinen Verweis.
  Eine pauschale Zuordnung waere eine Live-Datenkorrektur. Zuordnung durch die Fachseite, danach derselbe Weg wie hier.
- `ops_fahrer` (1 Live-Zeile) ohne Mandant; `ops_fahrzeug_touren.fahrer_id` und `ops_fahrzeug_bussgeld.fahrer_id`
  behalten deshalb den einfachen Schluessel.
- `ops_fahrzeuge` selbst ist nicht unter RLS (1 Live-Zeile mit `legacy-unassigned`).
- Die Payload-Felder `erstellt_von` und `benutzer` stehen noch in den Fuhrpark-Schemas, werden aber ignoriert.
