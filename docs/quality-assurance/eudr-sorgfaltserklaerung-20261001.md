---
title: EUDR-Sorgfaltserklärung — die Lücke nach dem Verordnungstext geschlossen
type: reference
audience: [entwickler, agent, qa, betrieb, compliance]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-01
version: 1.0.0
description: Welche Felder die Verordnung (EU) 2023/1115 vorschreibt, welche drei Regeln jetzt die Datenbank hält, und warum die EUDR-Maske vorher „KONFORM" meldete, ohne etwas geprüft zu haben.
---

# EUDR-Sorgfaltserklärung

## Warum die Lücke offen war — und warum sie es nicht bleiben durfte

Im Vorgänger-Slice blieb `domain_compliance.eudr_due_diligence` bewusst ohne
Migration: Der Code kannte davon **nur** ein `COUNT(*) WHERE tenant_id`, und
daraus eine Tabelle zu erfinden wäre bei einer Verordnung, die den Inhalt
vorschreibt, besonders falsch gewesen.

Dann kam der Befund, der die Lücke dringlich machte.
`GET /api/v1/compliance/eudr` las `domain_inventory.lots` — eine Tabelle, die
**kein Migrationsstand anlegt** und deren Spalten `eudr_compliant` und
`origin_country` es nirgends gibt (`inventory_lots` hat sie nicht,
`ops_chargen` auch nicht). Jeder Lesefehler lief in:

```python
except Exception:
    total = compliant = flagged = 0
```

und daraus wurde:

```python
status_label = "KONFORM" if flagged == 0 else …
"deforestation_risk": "NIEDRIG" if flagged == 0 else "MITTEL"
```

**Null markierte Chargen, weil es keine Chargen gab — und daraus „KONFORM" mit
„NIEDRIG".** Die Maske `/nachhaltigkeit/eudr-compliance` zeigte eine
Compliance-Rate von 0,0 % **und** den Status „KONFORM". Nach Art. 3/4 der
Verordnung (EU) 2023/1115 ist das Inverkehrbringen ohne Sorgfaltserklärung
verboten; eine grüne Anzeige ist hier die gefährlichste aller Antworten. Der
Mandant kam dort außerdem aus `?tenant_id=` mit Rückfall `"default"`.

Also: Lücke schließen — nach dem Verordnungstext, nicht nach dem, was der Code
zufällig anfasste.

## Der Feldsatz folgt der Verordnung

| Quelle | was sie verlangt | wo es jetzt steht |
|---|---|---|
| **Anhang II Nr. 1** | Marktteilnehmer mit Anschrift und EORI-Nummer | `betreiber_name`, `betreiber_adresse`, `eori_nummer` |
| **Anhang II Nr. 2** | HS-Code, Warenbeschreibung, Menge | `hs_code`, `warenbeschreibung`, `menge_netto_kg`, `menge_volumen_m3`, `ergaenzende_einheit`, `rohstoff` |
| **Anhang II Nr. 3 / Art. 9** | Produktionsland, Geolokation **aller** Flurstücke, Produktionszeitraum | `produktionsland`, `produktion_von/bis`, Tabelle `eudr_geolokationen` |
| **Anhang II Nr. 4** | Referenznummern vorgelagerter Erklärungen | Tabelle `eudr_vorgelagerte_erklaerungen` |
| **Anhang II Nr. 5/6** | die Erklärung und ihre Unterzeichnung mit Name und Funktion | `erklaerung_abgegeben_am`, `erklaerung_durch_name`, `erklaerung_durch_funktion` |
| **Art. 9** | Lieferantenangaben; belastbare Nachweise für Abholzungsfreiheit und Rechtskonformität | `lieferant_*`, `nachweis_abholzungsfrei(_quelle)`, `nachweis_rechtskonform(_quelle)` |
| **Art. 10/11** | Risikobewertung, bei mehr als vernachlässigbarem Risiko Minderung | `risikostufe`, `risikobewertung_am/durch`, `minderungsmassnahmen` |
| **Art. 33** | Referenz- und Verifizierungsnummer des EU-Informationssystems | `referenznummer`, `verifizierungsnummer`, `eingereicht_am` |

Die sieben relevanten Rohstoffe aus Anhang I (`RIND`, `KAKAO`, `KAFFEE`,
`OELPALME`, `KAUTSCHUK`, `SOJA`, `HOLZ`) sind eine Wertemenge, die die Datenbank
hält. Für einen Landhandel sind `SOJA`, `OELPALME` und `HOLZ` die praktisch
relevanten.

**Was ausdrücklich *keine* Bedingung wurde:** Art. 2 definiert
„abholzungsfrei" mit dem Stichtag **31.12.2020**. Daraus folgt keine
Datumsprüfung auf den Produktionszeitraum — nicht die Herstellung muss vor dem
Stichtag liegen, sondern die Fläche darf nach ihm nicht abgeholzt worden sein.
Das trägt ein Nachweisfeld, keine Prüfbedingung. Eine falsche Bedingung wäre
schlimmer als keine.

## Drei Regeln hält jetzt die Datenbank

**1. Eingereicht nur, was eingereicht werden darf** (Art. 3/4). `status =
'EINGEREICHT'` verlangt: `risikostufe = 'VERNACHLAESSIGBAR'`, eine
Risikobewertung mit Zeitpunkt, **beide** Nachweise, Name und Funktion der
unterzeichnenden Person, Referenznummer und Einreichungszeitpunkt. Eine
eingereichte Erklärung ohne Risikobewertung ist keine Sorgfalt, sondern eine
Behauptung.

**2. Flurstücke über vier Hektar nur als Polygon** (Art. 9). Ein Punkt genügt
dann nicht. Der Dienst weist es mit 422 ab, die Datenbank mit einer
Prüfbedingung — ein Weg, der die Prüfung umgeht, kommt nicht durch.

**3. Nicht vernachlässigbares Risiko nur mit Minderungsmaßnahmen** (Art. 11).

Dazu: die Referenznummer ist global eindeutig (sie stammt aus dem
EU-Informationssystem), der Produktionszeitraum endet nicht vor seinem Beginn,
und die Geolokation liegt in gültigen Koordinatenbereichen.

## Der Lebenszyklus

```
Entwurf  ──(Art. 10/11)──▶  bewertet  ──(Art. 3/4 + Art. 33)──▶  eingereicht
```

Eine **eingereichte** Erklärung wird nicht nachträglich verändert: Weder
Flurstücke noch Risikobewertung lassen sich danach ändern (409). Das ist die
Nachvollziehbarkeit, die ein Nachweis braucht, um einer zu sein.

## Der Status behauptet nichts mehr

| Stand | wann |
|---|---|
| `OHNE_ERKLAERUNG` | das Register ist leer — **nicht** `KONFORM` |
| `UNVOLLSTAENDIG` | es gibt Erklärungen, aber nicht alle sind eingereicht |
| `KRITISCH` | mindestens eine Erklärung trägt nicht vernachlässigbares Risiko |
| `KONFORM` | jede Erklärung ist eingereicht und trägt vernachlässigbares Risiko |

Und `deforestation_risk` ist `UNBEKANNT`, solange eine Erklärung unbewertet ist
**oder** das Register leer ist. „Nichts geprüft" ist keine Entlastung. Ein
Lesefehler ist ein 503, keine grüne Kachel.

Die Maske zeigt jetzt das Register statt Chargenzahlen, die es nie gab:
Erklärungen gesamt, eingereicht, im Entwurf, ohne Risikobewertung — und
`Chargenbezogene Kennzeichnung: nicht umgesetzt` im Klartext, statt sie durch
Nullen anzudeuten.

## Grenzen — ausdrücklich

**Dies ist eine Modellierung nach dem Verordnungstext, kein Rechtsrat.** Der
Feldsatz folgt Anhang II und Art. 9; die **fachjuristische Abnahme gehört dem
Compliance-Owner**. Zwei Dinge gehören dabei besonders geprüft:

1. **Die chargenbezogene EUDR-Kennzeichnung** ist nicht umgesetzt. Welche Charge
   welchen Nachweis trägt, ist eine Fachentscheidung (und `inventory_lots` hat
   die Spalten nicht). Bis dahin sagt die Maske das, statt es zu verschweigen.
2. **Aufbewahrung.** Die Verordnung verlangt, die Unterlagen fünf Jahre
   vorzuhalten. Technisch steht dem nichts entgegen — ein Löschlauf, der
   Erklärungen vorzeitig entfernt, gibt es nicht —, aber eine ausdrückliche
   Aufbewahrungsregel ist nicht implementiert. `downgrade` löscht die
   Erklärungstabelle **nicht**.

## Abnahme

35 Verträge in `tests/test_eudr_sorgfaltserklaerung_vertrag.py`:

| Gruppe | prüft |
|---|---|
| Anhang II | die Erklärung trägt Betreiber, EORI, HS-Code, Menge, Land, Zeitraum und ihre Flurstücke; vorgelagerte Erklärungen werden mitgeführt |
| Anhang I | alle sieben Rohstoffe; ein achter („WEIZEN") wird abgewiesen |
| Art. 9 | über vier Hektar ohne Polygon → 422; mit Polygon geht es; **die Datenbank hält dieselbe Regel**, auch wenn man den Dienst umgeht |
| Art. 10/11 | nicht vernachlässigbares Risiko ohne Minderungsmaßnahmen → 422; die Bewertung wird mit Zeitpunkt und Bewerter festgehalten |
| Art. 3/4 | ohne Bewertung, bei zu hohem Risiko und ohne Nachweise jeweils kein Einreichen; die Datenbank weist ein direktes `EINGEREICHT` ab |
| Art. 33 | Referenz- und Verifizierungsnummer werden festgehalten; eine Referenznummer gibt es nur einmal, auch über Häuser hinweg |
| Unveränderbarkeit | zweimal einreichen → 409; eine eingereichte Erklärung nimmt kein Flurstück und keine neue Bewertung mehr an |
| Mandant | fremde Erklärung nicht lesbar (und kein Lieferantenname im Text), nicht in der Liste, nicht bewertbar — geprüft **in der Tabelle** |
| Registerstand | leer → `OHNE_ERKLAERUNG`; Entwurf → `UNVOLLSTAENDIG`; riskant → `KRITISCH`; eingereicht → `KONFORM` |
| Alter Statusweg | kein `KONFORM` ohne Erklärung; unbewertet ist kein niedriges Risiko; `?tenant_id=` wird nicht befolgt; Störung → 503 auf allen drei Wegen, und **kein `KONFORM` im Text** |

```bash
DATABASE_URL=postgresql://valeo_dev:…@127.0.0.1:5432/valeo_probe \
  python -m pytest tests/test_eudr_sorgfaltserklaerung_vertrag.py -q
```

**Ergebnis 2026-10-01:** 35 Verträge grün, dazu `test_gap_fixes_batch1.py` (25
Tests) grün — dessen eigene Prüfung „Status muss berechnet sein, nicht ein
statisches KONFORM" war genau der Punkt und ist jetzt auf das neue Vokabular
nachgezogen. `tsc` und `eslint` ohne Befund zur Maske. Alle Ratschen grün;
Tabellen-Ratsche 14 → 12.
