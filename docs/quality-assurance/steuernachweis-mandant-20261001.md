---
title: Steuerliche Nachweise — Gelangensbestätigung und Intrastat gehören einem Haus
owner: Claude Code
type: reference
audience: [entwickler, agent, qa, betrieb, compliance]
status: aktiv
last_reviewed: 2026-10-01
version: 1.0.0
description: Warum der Intrastat-Export die Zeilen aller Häuser enthielt, warum eine leere Fälligkeitsliste Steuerwirkung hat, und warum drei von fünf Wegen der Gelangensbestätigung nie eine Antwort liefern konnten.
---

# Steuerliche Nachweise

## Der Befund in einem Satz

**`domain_compliance.gelangensbestaetigung` und `.intrastat_meldungen` legte
keine Migration an, und beide Module nahmen `get_tenant_id` entgegen und
benutzten ihn nicht** — kein einziger Filter in keinem Weg.

| Weg | was ein fremdes Haus damit konnte |
|---|---|
| `GET /gelangensbestaetigung` | alle Häuser lesen: Kundennummer, Empfängername, **USt-IdNr.**, Warenwert, Bestimmungsland |
| `GET /gelangensbestaetigung/faellig` | dito — und bei einem Lesefehler `[]`, also „nichts nachzufassen" |
| `POST …/{id}/bestaetigen` | einen fremden Nachweis als erhalten setzen |
| `POST …/{id}/mahnung` | das **Token** eines fremden Nachweises abrufen — den Link, mit dem der Empfänger bestätigt |
| `DELETE /intrastat/meldungen/{id}` | die **Intrastat-Meldung eines fremden Hauses löschen** |
| `PUT /intrastat/meldungen/{id}` | sie ändern |
| `POST …/{zeitraum}/export-csv` | einen Export ziehen, der die Zeilen **aller** Häuser enthält |
| Meldenummernkreis | `COUNT(*)` über alle Häuser: Das zweite Haus begann, wo das erste stand |

## Warum das keine Formfrage ist

Die **Gelangensbestätigung** ist der Nachweis, mit dem eine
innergemeinschaftliche Lieferung steuerfrei bleibt (§ 6a UStG, § 17a UStDV).
Fehlt sie, schuldet das Haus die Umsatzsteuer. Eine Fälligkeitsliste, die bei
einem Lesefehler `[]` zurückgibt, sagt „nichts nachzufassen" — mit genau dieser
Folge.

Die **Intrastat-Meldung** geht an das Statistische Bundesamt. Ein Export, der
die Zeilen eines fremden Hauses enthält, ist eine falsche Meldung. Und ein
Nummernkreis, der über Häuser hinweg zählt, erzeugt in jedem Haus Lücken, die
kein Prüfer erklären kann.

## Drei Wege konnten nie eine Antwort liefern

Das kam erst heraus, als die Tabelle existierte: Vorher antwortete jeder Weg
503, und das verdeckte, dass die Antwortmodelle nicht zu den Antworten passen.

| Weg | Modell verlangte | Weg lieferte | Folge |
|---|---|---|---|
| `POST /gelangensbestaetigung` | 13 Felder | 4 (`id`, `token`, `erinnerung_am`, `status`) | 500 |
| `GET …/faellig` | 13 Felder | 10 (ohne `status`, ohne USt-IdNr.) | 500, sobald eine Zeile existiert |
| `POST …/{id}/mahnung` | 13 Felder | 2 | 500 |
| `POST /intrastat/meldungen` | `IDResponse` (`id`, `message`) | `id`, **`meldenummer`**, `status` | die Meldenummer fiel aus der Antwort |

Der letzte ist der tückischste: Kein Fehler, nur ein stilles Weglassen — und
weggelassen wurde die Kennung, unter der die Meldung abgegeben wird.

Jeder Weg hat jetzt ein Antwortmodell, das zu seiner Antwort passt. Außerdem
sind `rechnung_nr` und `empfaenger_ust_id_nr` im Listenmodell **optional**: Beide
dürfen in der Datenbank fehlen, und ein Pflichtfeld hätte jede Liste mit einer
solchen Zeile in einen 500er verwandelt.

## Was die Datenbank jetzt hält

Die Form stammt aus den `INSERT`-Spalten und den Pydantic-Modellen. Ergänzt sind
`tenant_id NOT NULL` und vier Bedingungen, jede für einen benannten Grund:

| Bedingung | Grund |
|---|---|
| `UNIQUE (token)` | Der Empfänger bestätigt über einen Link; zwei gleiche Token wären zwei Nachweise, die sich überschreiben |
| `UNIQUE (tenant_id, lieferschein_nr)` | Zwei Nachweise zum selben Lieferschein sind kein Nachweis, sondern eine Frage |
| `UNIQUE (tenant_id, meldezeitraum, meldenummer)` | Der Nummernkreis läuft je Haus — die Datenbank hält, was der Zähler zieht |
| `status <> 'ERHALTEN' OR erhalten_am IS NOT NULL` | Ein erhaltener Nachweis braucht den Zeitpunkt; das ist das Beweisstück, nicht der Status |
| `meldezeitraum ~ '^[0-9]{4}-[0-9]{2}$'` | Ein Meldezeitraum, den niemand als Monat lesen kann, lässt sich nicht melden |

Dazu Prüfbedingungen auf die Wertemengen, die die Module selbst prüfen
(`AUSSTEHEND|ERHALTEN|ABGELAUFEN`, `ENTWURF|GEMELDET|STORNIERT`,
`EINGANG|VERSAND`, `NIEDRIG|MITTEL|HOCH`).

Auch der Nummernkreis hat seinen `except: seq = 1` verloren: Eine Meldenummer zu
raten, die es schon gibt, ist schlechter als keine Meldung anzulegen.

## Offen, und bewusst

`domain_compliance.eudr_due_diligence` bleibt ohne Migration. Der Code kennt
davon **nur** ein `COUNT(*) WHERE tenant_id` in einem `try/except`. Das genügt
nicht, um eine EUDR-Sorgfaltserklärung zu definieren — und sie zu erfinden wäre
hier besonders falsch: Die Verordnung schreibt den Inhalt vor. Benannte Lücke für
den Compliance-Owner.

## Abnahme

18 Verträge in `tests/test_steuernachweis_mandant_vertrag.py`:

| Gruppe | prüft |
|---|---|
| Eigentümer | ein angelegter Nachweis gehört dem anlegenden Haus |
| Lesen | die Liste eines fremden Hauses ist leer und enthält **keine USt-IdNr. und keinen Empfängernamen** im Text; die Fälligkeitsliste ebenso |
| Bestätigen | fremder Nachweis 404 und bleibt `AUSSTEHEND` ohne `erhalten_am`; der eigene wird bestätigt |
| Token | die Mahnung eines fremden Nachweises gibt kein Token heraus |
| Bedingungen | `ERHALTEN` ohne Zeitpunkt wird abgewiesen; zwei Nachweise zum selben Lieferschein im selben Haus ebenso, in einem anderen Haus nicht |
| Nummernkreis | beide Häuser beginnen bei `-00001`, das zweite Haus verschiebt den Zähler des ersten nicht |
| Intrastat | Liste nur eigene; fremde Meldung nicht löschbar und nicht änderbar (**geprüft in der Tabelle**); Zusammenfassung zählt nur das eigene Haus |
| Export | enthält die eigene Warennummer, **nicht** die fremde, und genau eine Datenzeile |
| Meldezeitraum | „August" wird von der Prüfbedingung abgewiesen |
| Störung | drei Wege: Spalte kurzzeitig umbenannt → 503, nicht `[]` |

```bash
DATABASE_URL=postgresql://valeo_dev:…@127.0.0.1:5432/valeo_probe \
  python -m pytest tests/test_steuernachweis_mandant_vertrag.py -q
```

**Ergebnis 2026-10-01:** 18 Verträge grün, dazu 80 vorhandene Tests
(`test_sanctions_genossenschaft_intrastat.py`,
`test_process_kernel_wave23_nebenkosten_intrastat.py`,
`test_welle4_response_models.py`). Alle Ratschen grün; Tabellen-Ratsche 17 → 14.
