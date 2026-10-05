---
title: Hinweisgebermeldungen — fünf Befunde in einer Tabelle
type: reference
audience: [entwickler, agent, compliance, betrieb]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-30
version: 1.0.0
description: Warum die Whistleblower-Tabelle keine Migration hatte, zwei unvereinbare Formen trug, mandantenübergreifend lesbar war und an einem generischen Pfad hing — und was davon behoben ist.
---

# Hinweisgebermeldungen

## Gefunden beim Abarbeiten der Schema-Drift-Liste

`domain_compliance.whistleblower_reports` stand auf der Liste der 76 Tabellen,
die der Code benutzt und die keine Migration anlegt. Beim Nachsehen kamen
**fünf** Befunde heraus, und die Daten sind das Sensibelste, was dieses System
führt: Meldungen von Hinweisgebern.

## Die fünf Befunde

### 1. Keine Migration — die Tabelle legte sich selbst an

`compliance_whistleblower.py` enthielt ein `CREATE TABLE IF NOT EXISTS`, das
bei jedem Aufruf lief. Das Schema hing damit davon ab, **welcher Endpunkt
zuerst aufgerufen worden war**. Genau so entstand der Unterschied zwischen der
Entwicklungsdatenbank und dem Migrationsstand.

### 2. Zwei Endpunkte, zwei unvereinbare Formen

| `compliance_whistleblower.py` | `compliance_whistleblower_lksg.py` |
|---|---|
| `report_token` | — |
| `description_encrypted` | `description` |
| `severity` | — |
| `submitted_at` | `created_at` |
| `notes` | — |
| — | `contact_email` |
| — | `anonymous` |
| **kein `tenant_id`** | `tenant_id` |

Wer zuerst lief, bestimmte die Tabelle; der andere bekam dauerhaft
`503 whistleblower_reports table not available`. Auf einer frischen
Installation war einer der beiden Wege **immer** kaputt.

### 3. Kein Mandantenbezug — `GET` listete alle Häuser

In der zur Laufzeit erzeugten Form fehlt `tenant_id`. Die Liste konnte deshalb
gar nicht filtern und gab alle Meldungen aller Mandanten zurück. Die
EU-Hinweisgeberrichtlinie verlangt Vertraulichkeit (Art. 16); schon Existenz,
Kategorie und Schwere einer fremden Meldung gehören nicht in eine Liste.

### 4. JSON-Injektion in der Notiz

```python
{"note": f'[{{"note": "{payload.note}", "ts": "…"}}]'}
```

Die Notiz wurde per f-String in einen JSON-Text gesetzt. Ein
Anführungszeichen zerlegt die Struktur; ein Hinweisgeberformular ist die
letzte Stelle, an der man auf wohlgeformte Eingaben hoffen sollte.

### 5. Montiert an einem generischen Pfad

Der Router hatte **kein Präfix**. Die Routen landeten damit unter:

```
POST /api/v1/reports                  ← Hinweis einreichen
GET  /api/v1/reports                  ← alle Meldungen listen
GET  /api/v1/reports/status/{token}
```

— im selben Namensraum wie `/api/v1/reports/sales-performance` und
`/api/v1/reports/dashboard/summary`. Ein `GET /api/v1/reports` lieferte
Hinweisgebermeldungen, wo jemand eine Auswertung erwartete.

### Dazu: ein Name, der etwas verspricht

Die Spalte hieß `description_encrypted` und bekam den **Klartext**. Ein Name,
der Verschlüsselung verspricht, ist schlechter als einer, der es nicht tut: Er
lädt dazu ein, sich auf etwas zu verlassen, das nicht da ist.

## Was behoben ist

**Migration `whistleblower_eine_tabelle_20260930`** legt **eine** Tabelle mit
der Vereinigung beider Formen an, mit `tenant_id` und zwei Indizes.

Zum Mandanten bei Bestandszeilen: Aus einer Zeile ohne `tenant_id` lässt er
sich **nicht** ableiten. Ihn zu erraten hieße, eine Hinweisgebermeldung dem
falschen Haus zuzuordnen — schlimmer als eine Zeile, die niemand sieht.
Deshalb: `NOT NULL` nur, wenn keine Zeile ohne Mandanten steht; sonst bleibt
die Spalte nullbar, und weil der Code immer filtert, wird eine solche Altzeile
unsichtbar. Für eine Vertraulichkeitsfrage ist das die sichere Richtung.

`report_token` wird nullbar: Er gehört zum kurzen Weg, nicht zum LkSG-Weg. Die
Laufzeitfassung hatte ihn als `NOT NULL` angelegt — auf einer solchen
Installation wäre der LkSG-Weg weiter kaputt gewesen, nur mit einer anderen
Fehlermeldung. **Das fiel erst beim Probelauf gegen die gewachsene Datenbank
auf**, nicht gegen die frische.

`description_encrypted` und `submitted_at` bleiben als leere Altspalten stehen
und werden nachgefüllt (`WHERE … IS NULL`), statt still gelöscht zu werden.

**Endpunkt** `compliance_whistleblower.py`:

- Präfix `/compliance/hinweisgeber` — kein Namensraum mit den Auswertungen
  mehr. Kein Aufrufer im Repo benutzte die alten Pfade.
- `tenant_id` in jeder Abfrage, schreibend wie lesend.
- Ein fremder Token bekommt dieselbe Antwort wie ein unbekannter (404 mit
  gleichem Wortlaut) — der Unterschied wäre selbst eine Auskunft.
- Die Notiz entsteht über `json.dumps`.
- Kein `CREATE TABLE` mehr im Endpunkt.

`compliance_whistleblower_lksg.py` blieb **unverändert**: Es schrieb schon
`tenant_id` und `description` und filterte korrekt. Es war die richtige Seite.

## Nachweis

`tests/test_whistleblower_vertraulichkeit.py`, sechs Verträge, grün gegen
**beide** Datenbankstände (frisch und gewachsen):

- Ein Haus sieht die Meldung des anderen nicht.
- Ein fremder Token gibt keine Auskunft, auch nicht, dass es ihn gibt.
- Ein fremder Hinweis lässt sich nicht bearbeiten — Status und Notizen bleiben.
- Eine Notiz mit `"` und eingebetteter JSON-Struktur kommt unverändert an und
  schaltet nichts um.
- Beide Endpunkte schreiben dieselbe Tabelle, beide Listen sehen beide
  Meldungen.
- Der Endpunkt legt keine Tabelle mehr an.

## Offen — eine Produktentscheidung

**Sind die beiden Wege Dubletten?** Der kurze Weg bietet einen Token für die
anonyme Statusabfrage, `severity` und Notizen; der LkSG-Weg bietet
`contact_email`, ein `anonymous`-Kennzeichen und Statusübergänge. Beide
schreiben jetzt dieselbe Tabelle. Ob sie zusammengelegt gehören — und wenn ja,
welcher Weg bleibt —, weiß der Fachbereich, nicht der Code.

**Und: soll die Meldung verschlüsselt werden?** Heute steht sie im Klartext.
Das ist jetzt wenigstens ehrlich benannt. Eine echte Verschlüsselung braucht
eine Schlüsselverwaltung und ist eine Entscheidung des Hauses.
