---
title: Kontrakt-Ordnung — Abnahme der Stilllegung
type: reference
audience: [entwickler, agent, qa, betrieb]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-01
version: 1.0.0
description: Wie die Stilllegung des zweiten Kontrakt-Modells geprüft wurde, was dabei an Altlasten wegfiel, und welche zwei Gate-Befunde dabei auffielen.
---

# Kontrakt-Ordnung

Die Entscheidung und ihre Beweislage stehen in
`docs/architecture/domains/kontrakte/fuehrendes-modell.md`. Dieses Dokument ist
die Abnahme.

## Was entfernt wurde

| Gegenstand | Umfang |
|---|---|
| `domain_kontrakte.*` | 4 Tabellen + Schema, stillgelegt mit Bestandsprüfung |
| `kontrakt_actions.py` | 7 Routen an der API-Wurzel (`/api/v1/lifecycle`, `/fixing`, `/settlement`) |
| `kontrakt_actions_schemas.py` | die zugehörigen Antwortmodelle |
| `kontrakt_fixing_service.py`, `kontrakt_lifecycle_service.py`, `kontrakt_settlement_service.py` | die zweite Fassung von Fixierung und Abrechnung |
| `tests/test_dom_con_004.py` | 12 Tests auf die entfernte Fassung |
| ein Testblock in `test_welle4_response_models.py` | Typprüfung der entfernten Modelle |

Zusammen 66 Zeilen Testblock und fünf Module. Was **bleibt**, ist die eine
Fassung: `contract_fixing_service`, `contract_settlement_service`,
`contract_engagement_service`, `contract_fulfillment_service` auf
`domain_ops.kon_contract`.

## Die Stilllegung ist nicht blind

Die Migration `kontrakt_ordnung_20261001` zählt die Zeilen aller vier Tabellen
und **bricht mit einer Fehlermeldung ab**, wenn irgendwo Bestand liegt — mit der
Anweisung, ihn vorher in das führende Modell zu übernehmen. Auf einer
Installation, auf der jemand den Overlay doch benutzt hat, löscht sie nichts.
`downgrade` legt die vier Tabellen in genau der Form wieder an, in der sie
stillgelegt wurden (aus `information_schema` abgelesen, nicht aus der alten
Migration geraten: `id` ist `UUID`, `fixing_datum` und `lieferung_datum` sind
`TEXT`).

## Der Nebenbefund, der am meisten über den Zustand sagt

`KontraktFristenProjector` im Kalender war sauber gebaut und lief seit immer
gegen `domain_agrar.kontrakte` — eine Tabelle, die **kein Migrationsstand
anlegt**. `_safe_mappings` fing den Fehler und gab eine leere Liste zurück: Der
Kalender zeigte **keine** Kontraktfrist und sah dabei aus, als gäbe es keine. Sein
Test stubte die Abfrage und bewies damit die Form, nicht die Quelle.

Jetzt liest er das führende Modell und projiziert zwei Fristen, die es dort
wirklich gibt: **Ende Lieferzeitraum** (`valid_to`) und **Ende
Fixierungsfenster** (`pricing_window_to`). „Andienungsfrist" und
„Frühbezugsrabatt" als eigene Felder hat das führende Modell nicht — das ist als
Lücke benannt und nicht aus `valid_to` hergeleitet.

## Abnahme

10 Verträge in `tests/test_kontrakt_ordnung_vertrag.py`:

| Gruppe | prüft |
|---|---|
| Rückkehr | kein Code verweist mehr auf `domain_kontrakte.`; die fünf Module sind weg; keine Fachroute mehr an der API-Wurzel |
| Eine Fassung | höchstens **ein** Modul schreibt eine Fixierung, höchstens eines eine Abrechnung |
| Kalender | keine Abfrage auf `domain_agrar.kontrakte`; das führende Modell steht in der Quelle |
| Datenbank | die vier Overlay-Tabellen sind weg; die drei führenden Modelle stehen |
| Begründung | `kon_contract` trägt die zehn Spalten, auf die sich die Entscheidung stützt — fällt eine weg, ist die Entscheidung nicht mehr begründet |

Der letzte Vertrag ist der wichtigste: Er prüft nicht nur den Zustand, sondern
die **Begründung**. `pricing_model`, `min_price`, `premium_type`,
`premium_value`, `basis_reference`, `pricing_window_from/to`, `quantity_type`,
`allow_overdelivery`, `tenant_id` sind der Grund, aus dem dieses Modell führt.

```bash
DATABASE_URL=postgresql://valeo_dev:…@127.0.0.1:5432/valeo_probe \
  python -m pytest tests/test_kontrakt_ordnung_vertrag.py -q
```

**Ergebnis 2026-10-01:** 63 Tests grün — 10 neue Verträge plus
`test_uix063_planning_calendar.py`, `test_welle4_response_models.py`,
`test_kontraktregister_vertrag.py`, `test_verkauf_kontrakte_central.py` und
`test_compat_einkauf_anfragen.py`. Alle Ratschen grün: Tabellenverweise 18 gegen
18, Pagination 285 ohne neuen Fund, Baseline-Integrität in Ordnung, keine neue
tote Transaktion, Godfile-Baseline exakt.

## Zwei Gate-Befunde, die dabei auffielen

**1. Ein Modul löschen trippt die Coverage-Ratsche.**
`config/coverage_ratchet_baseline.json` trug Schwellen für die fünf entfernten
Module. Nimmt man sie heraus, meldet `check_baseline_integrity.py`
„Absenkung verboten" — die Richtung für diese Baseline ist `up`, und ein
**entfernter** Eintrag ist für den Vergleich dasselbe wie ein gesenkter. Die vier
Einträge bleiben deshalb stehen und zeigen auf Dateien, die es nicht mehr gibt.

*Handshake an den Eigentümer der Gates:* Das Entfernen eines Moduls muss von der
Absenkung einer Schwelle unterscheidbar sein — etwa indem ein Eintrag nur
entfernt werden darf, wenn die Datei im Zielcommit fehlt. Sonst wächst die
Baseline mit jeder Aufräumarbeit um Leichen.

**2. `check_critical_backend_coverage.py` ist unabhängig davon rot** —
`portal_innendienst.py` 31,5 % gegen 60 %, `external_gates.py` 48,3 % gegen 70 %,
`quality_evidence.py` 49,1 % gegen 70 %. Das ist Altbestand, nicht Folge dieses
Slices.
