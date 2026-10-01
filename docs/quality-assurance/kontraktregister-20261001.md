---
title: Vertragsregister — drei Tabellen ohne Migration, und ein Pfad für zwei Dinge
type: reference
audience: [entwickler, agent, qa, betrieb]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-01
version: 1.0.0
description: Warum die zentrale Vertrags-Engine auf einer frischen Installation vollständig 503 meldete, warum zwei ihrer Wege auch danach unerreichbar geblieben wären, und warum Kontrakt und Vertrag zwei Pfade bekommen.
---

# Vertragsregister

## Der Befund in einem Satz

**`domain_contracts.contracts`, `.contract_versions` und
`.contract_obligations` legt keine Migration an** — auf einer frischen
Installation meldet deshalb jeder Weg der zentralen Vertrags-Engine 503: anlegen,
auflisten, ändern, verlängern, Pflichten führen, Auswertung.

Das Modul selbst (`central_contracts.py`) ist ungewöhnlich sauber: Mandantenfilter
auf **jedem** Weg, 503 statt leerer Liste, Abfragegrenzen mit Obergrenze,
`nosec`-Begründungen an den dynamischen `WHERE`-Teilen. Hier fehlte wirklich nur
die Migration — das ist in dieser Welle die Ausnahme.

## Die Form ist übernommen, nicht erfunden

Aus den `INSERT`-Spalten, den Pydantic-Modellen (`ContractOut`, `ObligationOut`)
und den Wertemengen, die das Modul selbst prüft. Drei Dinge sind ergänzt, und
jedes für einen benannten Grund:

| ergänzt | Grund |
|---|---|
| Fremdschlüssel Version/Pflicht → Vertrag, `ON DELETE CASCADE` | Eine Vertragsversion ohne Vertrag ist kein Dokument |
| `CHECK` auf die fünf Wertemengen | Was die Anwendung prüft, soll die Datenbank halten — sonst steht beim nächsten Schreibweg ein Wort drin, das keine Maske kennt |
| `UNIQUE (tenant_id, contract_number)` und `UNIQUE (contract_id, version_number)` | Die Vertragsnummer ist die Kennung, unter der ein Haus den Vertrag führt. Und `_next_version_number` zieht aus `MAX(version_number) + 1` — zwei gleichzeitige Änderungen dürfen nicht beide die 2 bekommen |

Dazu eine Laufzeitbedingung: `end_date >= start_date`. Ein Vertrag, der endet,
bevor er beginnt, ist ein Tippfehler, und die Datenbank darf ihn ablehnen.

## Nebenbefund: ein Pfad für zwei verschiedene Dinge

Die Abnahme deckte auf, dass die Migration allein nicht genügt hätte. Zwei Wege
des Registers waren **unerreichbar**:

| Weg | wer ihn verschluckte |
|---|---|
| `GET /api/v1/contracts/{contract_id}` | `compat.py` → `contracts_router` ist zuerst eingebunden |
| `GET /api/v1/contracts/expiring` | dieselbe Route — „expiring" wurde als Vertragskennung gelesen |

Das zweite ist das schlimmere: Es ist die Liste, die einen auslaufenden Vertrag
anzeigt, **bevor** er sich stillschweigend verlängert. Ein Vertrag mit
`auto_renewal_days` und niemandem, der die Frist sieht, verlängert sich von
selbst.

Die Ursache ist keine Nachlässigkeit, sondern eine Doppelbelegung des Wortes:

- **Kontrakt** ist im Landhandel der Warenkontrakt — Menge, Ware, Fixierung,
  Andienung, Abrechnung. Er hängt an `/api/v1/contracts` und wird von der
  Bestellmaske, der Fixierung, der Erfüllung und der Abrechnung benutzt.
- **Vertrag** ist das juristische Dokument — Miete, Pacht, Dienstleistung,
  Einkauf, Verkauf, mit Versionen, Fristen und Pflichten. Das ist dieses
  Register.

**Entschieden: zwei Dinge, zwei Pfade.** Das Register hängt jetzt unter
`/api/v1/vertraege`:

| vorher | jetzt |
|---|---|
| `GET /contracts` | `GET /vertraege` |
| `POST /contracts` | `POST /vertraege` |
| `GET /contracts/expiring` *(unerreichbar)* | `GET /vertraege/expiring` |
| `GET /contracts/{id}` *(unerreichbar)* | `GET /vertraege/{id}` |
| `PATCH /contracts/{id}` | `PATCH /vertraege/{id}` |
| `…/{id}/obligations`, `…/{id}/renew` | unter `/vertraege` |
| `GET /analytics` | `GET /vertraege/analytics` |

Der Warenkontrakt behält `/api/v1/contracts` samt Compat-Route — dort hängen
Masken, und ein Entzug hätte niemandem geholfen. **Es bricht kein Aufrufer:** Das
Register hatte keinen. Die Frontend-Zugriffe auf `/api/v1/contracts/…` gehen alle
an den Warenkontrakt (Bestellanlage, Fixierung, Erfüllung, Abrechnung), und
`/api/v1/analytics/kpis` und `…/cubes/…` sind andere Module.

`GET /analytics` war außerdem ein merkwürdig globaler Name für die Auswertung
**eines** Fachbereichs. Innerhalb des neuen Prefixes steht sie bewusst **vor** der
Detailroute: `/analytics` ist ein Segment und wäre von `/{contract_id}`
verschluckt worden — dieselbe Falle, nur eine Ebene tiefer. FastAPI entscheidet
nach Deklarationsreihenfolge, und darauf darf man sich nicht versehentlich
verlassen.

## Was dieser Slice nicht entscheidet

Welche Kontrakttabelle die führende ist. Im Migrationsstand liegen
nebeneinander:

`domain_einkauf.kontrakte`, `domain_inventory.agrar_contracts`,
`domain_ops.kon_contract` (+ `_line`, `_fixing`, `_movement`, `_reminder`),
`domain_portal.customer_contracts`, die Satelliten in `domain_kontrakte`
(`kontrakt_fixings`, `kontrakt_lifecycle`, `kontrakt_settlements`,
`kontrakt_status_log`) — **ohne Kopftabelle in ihrem eigenen Schema** — und
dieses Register.

Das ist die größte Fachfrage des Systems und gehört dem Domänen-Owner, nicht
einem Migrations-Slice. Was hier entschieden ist, ist kleiner und sicher: Das
**Vertragsregister** ist nicht dasselbe wie der **Warenkontrakt** und bekommt
seinen eigenen Pfad. Die Satelliten ohne Kopftabelle sind ein eigener Befund und
gehören in denselben Vorgang.

## Abnahme

20 Verträge in `tests/test_kontraktregister_vertrag.py`:

| Gruppe | prüft |
|---|---|
| Anlegen | Vertrag entsteht mit Nummer, Haus, Wert; die erste Version („Erstanlage") steht; eine Änderung schreibt Version 2 |
| Bedingungen | unbekannte Vertragsart, unbekannter Stand, unbekannte Partnerart werden von der **Datenbank** abgewiesen; Ende vor Beginn ebenso |
| Eindeutigkeit | Vertragsnummer je Haus (zweimal dieselbe im eigenen Haus scheitert, ein anderes Haus darf sie tragen); Versionszähler je Vertrag; eine Version ohne Vertrag ist nicht speicherbar |
| Pflichten | anlegen und abschließen; eine Pflicht mit Frist in der Vergangenheit entsteht als `UEBERFAELLIG`; Pflichten verschwinden mit dem Vertrag |
| Verlängern | setzt das neue Ende und aktiviert |
| Auslaufend | der Vertrag mit 10 Tagen Restlaufzeit erscheint, der mit 300 nicht |
| Auswertung | zählt nur das eigene Haus |
| Mandant | fremder Vertrag nicht lesbar, nicht in der Liste, und nicht änderbar — geprüft **in der Tabelle**, nicht am Statuscode (Titel und Ende unverändert, keine Pflicht angelegt) |

```bash
# Gegen die vorhandene gemeinsame Prüfstand-Datenbank, ohne Zurücksetzen
# (test-database-resource-policy-20261001.md).
DATABASE_URL=postgresql://valeo_dev:…@127.0.0.1:5432/valeo_probe \
  python -m pytest tests/test_kontraktregister_vertrag.py -q
```

**Ergebnis 2026-10-01:** 20 Verträge grün, dazu 14 vorhandene Tests
(`test_compat_einkauf_anfragen.py` — die Compat-Route des Warenkontrakts bleibt
unberührt — und `test_verkauf_kontrakte_central.py`) grün.

**Tabellen-Ratsche:** 21 → 18 lebend, Schwelle bündig.

## Offen und nicht meins

Die beiden CRM-Gates aus diesem Lauf sind geschlossen. Die Listenabfrage der
Kundenakte ist auf 25 Zeilen begrenzt und hebt `pagination_baseline.json` nicht
an. `crm_360.py` liegt unter 1.000 Zeilen; die Meldung mit 1.808 Zeilen galt vor
der Zerlegung.
