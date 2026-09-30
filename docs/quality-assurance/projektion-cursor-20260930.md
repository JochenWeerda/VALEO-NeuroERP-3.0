---
title: Projektionsbuchhaltung — drei Tabellen aus Laufzeit-DDL in eine Migration
type: reference
audience: [entwickler, agent, qa, betrieb]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-30
version: 1.0.0
description: Warum domain_shared.process_projection_registry, .snapshots und .cursors keine Migration hatten, was stattdessen zur Laufzeit geschah, und woran der Nachtrag geprüft wurde.
---

# Projektionsbuchhaltung

## Der Befund in einem Satz

**Die drei Tabellen, in denen die Finanz-Read-Models ihren eigenen Fortschritt
buchen, entstanden erst beim ersten Abruf** — und zwar an zwei Stellen im
Quellcode, für die Cursor-Tabelle wortgleich doppelt.

| Tabelle | wofür | angelegt von |
|---|---|---|
| `domain_shared.process_projection_registry` | welche Projektion wie viele Posten hat | `finance_read_model_service.py` |
| `domain_shared.process_projection_snapshots` | der abgelegte Stand einer Projektion | `finance_read_model_service.py` |
| `domain_shared.process_projection_cursors` | wie weit ein Verbraucher gelesen hat | `finance_read_model_service.py` **und** `app/core/projection_cursor_service.py` |

Das ist der dritte Eintrag der Welle, die die 76 Tabellen ohne Migration
abarbeitet (`schema-drift-2026-09-30.md`); die ersten zwei waren
`whistleblower_eine_tabelle_20260930` und `pos_zahlarten_aktionen_20260930`.

## Was daran zählt

Eine Tabelle, die zur Laufzeit entsteht, hat **keine Form, sondern eine
Geschichte.** Welche Spalten sie trägt, hängt davon ab, welche Fassung des
Programms sie zuerst angelegt hat. Bei der Cursor-Tabelle stand die DDL zweimal
im Code — hätte eine der beiden Stellen eine Spalte bekommen, wäre die Form von
der Reihenfolge der Aufrufe abhängig geworden, nicht vom Migrationsstand.

Zwei Dinge, die hier **nicht** das Problem waren, und das ist erwähnenswert,
weil sie es bei den ersten beiden Einträgen der Welle waren:

- **Mandantentrennung.** Alle drei Tabellen tragen `tenant_id`, und jede
  Abfrage filtert danach. `tenant_id` steht außerdem vorn im
  Primärschlüssel — deshalb braucht keine der drei einen zusätzlichen Index.
- **Eine Störung, die wie eine Konfiguration aussieht.** Der Projektionsstand
  ist Betriebsauskunft. Fällt eine Quelle aus, zeigt die Antwort einen
  *stehenden* Stand, und das ist auffällig, nicht beruhigend.

## Der Nebenbefund: vier tote Transaktionen im Lesepfad

Die vier Lesehilfen fingen jeden Fehler ab und gaben einen Leerstand zurück —
**ohne Rollback.** Postgres bricht nach einem Fehler die ganze Transaktion ab;
jede weitere Abfrage derselben Anfrage scheitert danach mit
`InFailedSqlTransaction`. Da `get_projection_status` alle vier Quellen
hintereinander liest, hätte der Ausfall **einer** Tabelle die drei anderen
mitgenommen — und nichts davon stand im Protokoll.

Genau dieses Muster ließ am 29.09. eine Löschung nach Art. 17 DSGVO
stillschweigend nichts tun (`pruefstand-datenbank.md`). Behoben: `_rollback_quietly`
gibt die Transaktion frei, und jeder Ausfall wird mit `logger.exception`
protokolliert. Der Leerstand als Rückgabe bleibt — der Statusabruf soll an einer
ausgefallenen Quelle nicht scheitern —, ist aber jetzt sichtbar.

## Die Zeitstempel bleiben `TEXT`

Bewusst. Der Code schreibt ISO-Zeichenketten und vergleicht sie als
Zeichenketten (`str(a) > str(b)`), um den jüngsten Stand zu finden. Ein Wechsel
auf `TIMESTAMPTZ` würde die Tabellen richtiger machen **und den Lesepfad
ändern**. Das ist ein eigener Vorgang, keine Nebenwirkung eines Nachtrags. Die
Migration übernimmt die Form wörtlich aus der entfernten Laufzeit-DDL — sie ist
nicht erfunden.

## Abnahme

Fünf Verträge in `tests/test_projektion_cursor_vertrag.py`, 10 Fälle:

| Vertrag | prüft |
|---|---|
| Form | Spalten, Typen und Nullbarkeit gegen die entfernte Laufzeit-DDL, je Tabelle |
| Primärschlüssel | Reihenfolge, und dass `tenant_id` vorn steht |
| Schreiben ohne Bootstrap | `persist_projection_cursor`, `…registry_entry`, `…snapshot` gegen den migrierten Stand |
| keine Laufzeit-DDL | statisch: `CREATE TABLE … process_projection_*` kommt in `app/` und `modules/` nicht mehr vor |
| Lesefehler | die gelesene Spalte wird kurzzeitig umbenannt; dieselbe Sitzung ist danach weiter benutzbar |

```bash
export TEST_DATABASE_URL=postgresql://valeo_dev:…@127.0.0.1:5432/valeo_probe
python scripts/pruefstand_db.py
DATABASE_URL="$TEST_DATABASE_URL" python -m pytest tests/test_projektion_cursor_vertrag.py -q
```

**Ergebnis 2026-09-30:** 10 Verträge grün gegen den frischen Stand. Dazu 162
vorhandene Tests aus `test_finance_read_models_api.py`,
`test_process_kernel_wave43_checkpoints_projections.py` und
`test_process_kernel_wave19_read_model_contracts.py` grün.

**Gegen den gewachsenen Stand** wurde die Migration zusätzlich angewandt. Die
Gegenprobe: Die 24 Spalten der drei Tabellen sind in `valeo_neuro_erp` und
`valeo_probe` Zeile für Zeile identisch. Der Nachtrag erhebt also keinen
gewachsenen Zufall zur Migration, sondern schreibt fest, was ohnehin überall
steht.

## Nachgezogen: Tabellen-Ratsche 28 → 25 lebend

`scripts/check_table_references.py` stand seit dem 29.09. drei Plätze zu hoch:
Die Tabellen, die `whistleblower_eine_tabelle_20260930` und
`pos_zahlarten_aktionen_20260930` nachgetragen haben, sind auf einer frischen
Installation da, die Schwelle blieb aber bei 28. Drei neue Verweise ins Leere
wären durchgegangen. Gemessen gegen `valeo_probe`: 25 lebend, 25 ruhend — die
lebende Schwelle steht jetzt bündig, die ruhende war schon bündig.

Die drei Projektionstabellen selbst zählt diese Ratsche nicht: Sie liest nur
`app/api/v1/endpoints`, und der Zugriff liegt in `app/services` und `app/core`.
