---
title: Kontrakt und Vertrag — führendes Modell je Fachbegriff
type: reference
audience: [entwickler, agent, architekt, qa, betrieb]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-01
version: 1.0.0
description: Welche der sechs Kontrakttabellen führt, warum zwei Implementierungen von Fixierung und Abrechnung existierten, und warum die zweite nach GoBD nicht bleiben konnte.
---

# Kontrakt und Vertrag

## Die Entscheidung in drei Zeilen

| Fachbegriff | führendes Modell | Pfad |
|---|---|---|
| **Warenkontrakt** (Handelsgeschäft: Menge, Ware, Preisbildung, Fixierung, Andienung, Abrechnung) | `domain_ops.kon_contract` + `_line` + `_fixing` + `_movement` + `_reminder` | `/api/v1/contracts/…` |
| **Agrar-Erzeugerkontrakt** (Erntejahr, Pool, Erzeuger) | `domain_inventory.agrar_contracts` + `agrar_contract_allocations` | `/api/v1/agrar/contracts/…` |
| **Vertrag** (juristisches Dokument: Miete, Pacht, Dienstleistung, mit Versionen und Pflichten) | `domain_contracts.contracts` + `contract_versions` + `contract_obligations` | `/api/v1/vertraege/…` |

Drei Fachbegriffe, drei Modelle, drei Pfade. Alles andere ist entweder Satellit
eines dieser drei oder Altlast.

## Die Beweislage

Gemessen am 01.10.2026 gegen die gewachsene Entwicklungsdatenbank **und** gegen
einen frisch migrierten Stand.

| Tabelle | Spalten | Zeilen (dev) | Code | Masken |
|---|---|---|---|---|
| `domain_ops.kon_contract` | **31** | 8 (+8 Positionen, 2 Fixierungen, 6 Bewegungen) | 4 Dienste, 4 Endpunktmodule, ORM | **4** Frontend-Module |
| `domain_inventory.agrar_contracts` | 18 | **94** | CRM-360, Lieferantenportal, Masken-Brücken, ORM | Portal, CRM |
| `domain_einkauf.kontrakte` (+ Positionen) | 19 | 0 | Preisermittlung, ORM | — |
| `domain_contracts.contracts` | 14 | 0 | Vertragsregister | — |
| `domain_kontrakte.*` (4 Tabellen) | — | **0** | 3 Dienste, 1 Endpunktmodul, 7 Routen | **keine** |
| `domain_portal.customer_contracts` | — | 0 | Kundenportal (ORM) | Portal |
| `domain_agrar.kontrakte`, `.kontrakt_dispositionen` | — | **existiert nicht** | 2 Verweise ins Leere | — |

**Warum `kon_contract` führt:** Es ist das einzige Modell, das den Warenkontrakt
vollständig beschreibt. `pricing_model`, `min_price`, `premium_type`,
`premium_value`, `basis_reference`, `pricing_window_from/to` sind die
Prämien-/Basis-Preisbildung mit Fixierungsfenster — das Herz eines
Getreidekontrakts. Dazu `quantity_type`, `allow_overdelivery`, `payment_terms`,
Debitoren- und Kreditorenkonto. Es hat Positionen, Fixierungen, Bewegungen und
Erinnerungen als echte Satelliten, ORM-Modelle, vier Dienste, vier
Endpunktmodule, vier Frontend-Module — und Bestand. Keine andere Tabelle hat
mehr als die Hälfte davon.

## Was stillgelegt wurde, und warum nach GoBD

`domain_kontrakte` war eine **zweite, vollständige Fassung von Fixierung und
Abrechnung** (DOM-CON-004, Juni 2026): `kontrakt_lifecycle`, `kontrakt_fixings`,
`kontrakt_settlements`, `kontrakt_status_log`, dazu drei Dienste, ein
Endpunktmodul und sieben Routen.

Der Grund für die Stilllegung ist nicht die Doppelung, sondern **der fehlende
Vertragsbezug**:

- Es gibt in diesem Schema **keine Kopftabelle.** `kontrakt_lifecycle` diente
  sich selbst als Kopf und wurde bei Bedarf angelegt.
- `kontrakt_id` war eine **freie Zeichenkette**, geprüft gegen nichts. Eine
  Fixierung konnte auf einen Kontrakt zeigen, den es nicht gibt; eine Abrechnung
  ebenso.

Nach GoBD müssen Aufzeichnungen **nachvollziehbar und nachprüfbar** sein
(Rz. 30 ff.): Ein Geschäftsvorfall muss sich von der Buchung zum Beleg und
zurück verfolgen lassen. Eine Preisfixierung und eine Abrechnung ohne
nachweisbaren Vertragsbezug erfüllen das nicht. Das ist kein
Schönheitsproblem — es ist der Unterschied zwischen einer Aufzeichnung und einer
Notiz.

**Warum die Stilllegung keinen Bestand verliert:** Alle vier Tabellen hatten in
**beiden** Datenbanken **null Zeilen**, und die sieben Routen (`/api/v1/lifecycle`,
`/fixing`, `/settlement` — bemerkenswert: ohne Fachpräfix direkt an der
API-Wurzel) hatten keinen Aufrufer, weder im Frontend noch im Backend. Es gab
nie einen aufbewahrungspflichtigen Datensatz, also auch keine
Aufbewahrungspflicht.

Die Migration `kontrakt_ordnung_20261001` ist dabei **nicht blind**: Sie zählt
vor dem Löschen und **bricht ab**, wenn irgendwo doch Zeilen liegen, mit der
Anweisung, den Bestand vorher in das führende Modell zu übernehmen. Lieber eine
rote Migration als eine stille Löschung. `downgrade` legt die Tabellen in der
Form wieder an, in der sie stillgelegt wurden.

## Was aufgeräumt wurde

| Altlast | Maßnahme |
|---|---|
| `domain_kontrakte.*` (4 Tabellen, 1 Schema) | stillgelegt, mit Bestandsprüfung und Rücknahme |
| `kontrakt_actions.py` (7 Routen an der API-Wurzel) | entfernt |
| `kontrakt_actions_schemas.py` | entfernt |
| `kontrakt_fixing_service.py`, `kontrakt_lifecycle_service.py`, `kontrakt_settlement_service.py` | entfernt |
| `tests/test_dom_con_004.py` (12 Tests auf die entfernte Fassung) | entfernt |
| `KontraktFristenProjector` las `domain_agrar.kontrakte` | liest das führende Modell |

Der Kalender-Projektor ist der Fund, der am meisten über den Zustand sagt: Er
war sauber gebaut, lief aber seit immer gegen eine Tabelle, die **kein
Migrationsstand anlegt**. `_safe_mappings` fing den Fehler und gab eine leere
Liste zurück — der Kalender zeigte **keine** Kontraktfrist und sah dabei aus, als
gäbe es keine. Sein Test stubte die Abfrage und bewies damit die Form, nicht die
Quelle.

Jetzt projiziert er zwei Fristen, die es im führenden Modell wirklich gibt: das
**Ende des Lieferzeitraums** (`valid_to`) und das **Ende des Fixierungsfensters**
(`pricing_window_to`) — bis dahin muss der Preis fixiert sein, sonst greift das
Mindestpreis- oder Basismodell.

## Benannte Lücken — nicht erfunden, nicht verschwiegen

1. **Andienungsfrist und Frühbezugsrabatt** haben im führenden Modell kein
   eigenes Feld. Der alte Projektor erwartete sie; sie sind fachlich sinnvoll
   (die Andienungsfrist ist nicht immer das Laufzeitende). Das gehört entschieden
   und dann als Spalte ergänzt — nicht aus `valid_to` hergeleitet.
2. **`domain_einkauf.kontrakte`** ist der Rahmenkontrakt mit Preisen an der
   Position; die Preisermittlung liest ihn. Ob er langfristig im Warenkontrakt
   aufgeht, lässt sich nicht entscheiden, solange er leer ist — es gibt keinen
   Bestand, an dem man sieht, wie er benutzt wird.
3. **`domain_agrar.kontrakt_dispositionen`** und ihre fehlende Elterntabelle
   bleiben beim Agrar-Owner (eigener Handshake im Workboard, 30.09.): Dort ist
   zusätzlich der Mandantenbezug offen.
4. **`domain_portal.customer_contracts`** ist leer, hat aber ein ORM-Modell und
   wird vom Kundenportal abgefragt. Das ist eine unfertige Funktion, keine
   Altlast — angefasst wird sie hier nicht.

## Die Regel, die bleibt

Ein zweites Modell für denselben Fachbegriff entsteht nicht aus Absicht, sondern
weil zwei Leute dasselbe Wort verschieden lesen. Dagegen hilft nur, dass die
Zuordnung aufgeschrieben ist und ein Vertrag sie prüft:
`tests/test_kontrakt_ordnung_vertrag.py` lässt kein neues Schema `domain_kontrakte`
und keine zweite Fixierungs- oder Abrechnungsfassung zurückkommen.
