---
title: Prüfstand-Datenbank — frisch für das Schema, gewachsen für die Daten
type: runbook
audience: [entwickler, agent, qa]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-30
version: 1.0.0
description: Warum Schema- und Vertragstests gegen eine frisch migrierte Datenbank laufen, wie man sie aufsetzt, und wofür die gewachsene Entwicklungsdatenbank weiterhin die richtige ist.
---

# Prüfstand-Datenbank

## Die Regel in einem Satz

**Für das Schema ist eine frische Datenbank der Prüfstand, für die Daten die
gewachsene.** Beide braucht es, und sie sind nicht austauschbar.

| Prüfstand | wofür | woher |
|---|---|---|
| **frisch** | Schema, Migrationen, Vertragstests, alles mit rohem SQL | `scripts/pruefstand_db.py` |
| **gewachsen** | Maskenabnahme, Statuswörterbücher, echte Datenlagen | `DATABASE_URL` |

## Warum es diese Regel gibt

Am 29.09.2026 waren neunundfünfzig Tests rot. Keiner davon wegen eines
Programmierfehlers. Geprüft worden war gegen die gewachsene
Entwicklungsdatenbank, und die weicht in **beide** Richtungen von einer frischen
Installation ab.

**Sie hat Bedingungen verloren.** Fremdschlüssel
(`delivery_notes.customer_id` → `customers`,
`delivery_note_positions.artikel_id` → `articles`), Prüfbedingungen
(`ck_delivery_notes_status`) und NOT-NULL-Regeln auf `sales_orders`
(`description`, `currency`, `status`, `total_amount`, `version`) sind dort nicht
mehr da. Tests, die Kunden und Artikel nie anlegten, liefen deshalb grün — und
in CI gegen einen 500er.

**Sie hat Spalten und Tabellen gewonnen, die keine Migration anlegt.**
`sales_offers.customer_name`, `sales_offers.is_pauschale`,
`sales_orders.is_pauschale`, `sales_order_items.ek_price` und `.unit`, dazu
`domain_crm.crm_customers` und `domain_crm.contacts`. Auf einer frischen
Installation scheiterte damit schon das Anlegen eines Angebots.

Dahinter standen **drei echte Fehler**, die niemand sah:

1. Ein Lieferschein kam auf einer Neuinstallation nie über den Entwurf hinaus —
   Buchen, Versenden, Sammelrechnung und Storno liefen jeweils in einen 500er,
   weil die Statusbedingung nur fünf der neun geschriebenen Zustände kannte.
2. Ein Angebot ließ sich nicht anlegen — `sales_offers.customer_name` fehlte.
3. Eine Löschung nach Art. 17 DSGVO tat **nichts** und meldete 503. Eine
   fehlende Nebentabelle brach die Transaktion ab; das `except` fing zwar, aber
   jede weitere Anweisung scheiterte danach mit `InFailedSqlTransaction`.

Das dritte ist das Muster, auf das es ankommt: **Ein `except` fängt den Fehler,
die Transaktion ist trotzdem tot, und was danach kommt, sieht aus wie ein
Ergebnis.**

## Aufsetzen

```bash
# Einmal pro Umgebung: die Verbindung setzen. Ohne diese Variable wird sie aus
# DATABASE_URL abgeleitet, indem der Datenbankname durch valeo_probe ersetzt
# wird — Host, Port und Zugangsdaten bleiben.
export TEST_DATABASE_URL=postgresql://valeo_dev:…@127.0.0.1:5432/valeo_probe

python scripts/pruefstand_db.py            # löschen, anlegen, migrieren
python scripts/pruefstand_db.py --status    # nur nachsehen
python scripts/pruefstand_db.py --keep      # nicht löschen, nur migrieren
```

Der Lauf ist idempotent: Er endet immer bei derselben frisch migrierten
Datenbank, gleich wie oft er läuft und in welchem Zustand sie vorher war.

**Sicherung.** Das Skript löscht nur Datenbanken, deren Name `probe`, `test`
oder `pruefstand` enthält. Ein Zeigefehler auf `valeo_neuro_erp` bricht ab:

```
'valeo_neuro_erp' sieht nicht wie ein Prüfstand aus.
```

Im Code steht kein Passwort und keine Zugangsdatei.

## Benutzen

Die Tests lesen `DATABASE_URL`. Der Prüfstand wird also so vorgeschaltet:

```bash
DATABASE_URL="$TEST_DATABASE_URL" python -m pytest tests/… --no-cov -q -p no:logging
```

Nachweis vom 30.09.2026: Die elf Testdateien, die in CI rot waren, laufen gegen
einen von null aufgebauten Prüfstand mit **87 bestandenen Tests** durch.

## Wann welche Datenbank

**Frisch prüfen** bei allem, was das Schema berührt:

- eine neue Alembic-Migration (auch und besonders eine, die lokal „schon läuft")
- ein Testfixture mit rohem `INSERT`/`UPDATE`
- ein Endpunkt, der Spalten schreibt
- Vertragstests, Ratschen, Inventare

**Gewachsen prüfen** bei allem, was von echten Daten lebt:

- Maskenabnahme im Browser
- Statuswörterbücher und Altbestände (siehe
  `lieferschein-statuswerte-2026-09-29.md`: `geliefert` steht nur dort)
- Auswertungen, Salden, Periodenvergleiche

**Eine Migration braucht beide.** Für das Schema die frische, für die Daten die
gewachsene. Am 29.09. hätte die Statusbedingung auf der gewachsenen Datenbank
nicht angelegt werden können, weil dort der Altbestandswert `geliefert` liegt —
das fiel erst beim zweiten Probelauf auf:

```bash
python scripts/pruefstand_db.py                                    # Schema
DATABASE_URL="$DATABASE_URL" python -m alembic upgrade head        # Daten
```

## Was der Prüfstand nicht leistet

Er sagt nichts darüber, ob die gewachsene Datenbank **noch** zum Schema passt.
Diese Frage beantwortet `scripts/check_schema_drift.py` (Slice
`SCHEMA-DRIFT-GATE`), das beide vergleicht und jede Abweichung ausweist statt
sie zu erraten.
