# FSX-001 Herkunftskarte — Ausfuellvorlage

Stand: 2026-09-15 · Geruest von Claude Code, **Inhalt offen**.
Gehoert zu `docs/design/flow-spine-entlastung-masterplan.md`, Slice FSX-001.

## Warum es diese Karte gibt

> Unterschiedliche Zahlen in zwei Instanzen allein beweisen keine korrekte
> Datenquelle.

Ein Test "zwei Vorgaenge liefern verschiedene Werte" haette auch ein
Zufallsgenerator bestanden. Deshalb braucht FSX-001 **vor** der Implementierung
je operativem Feld eine **benannte** Quelle — oder ein ausdrueckliches
"nicht ermittelbar". Der Vertragstest prueft den Wert dann gegen diese Quelle,
nicht gegen einen anderen Vorgang.

## So wird ausgefuellt

Je Zeile **eine** der beiden Spalten fuellen:

- **Quelle:** konkretes Instanzattribut (`FlowSpineInstance.<feld>`) oder benanntes
  Readmodel mit Tabelle bzw. Endpunkt. Keine Absichtserklaerung.
- **Nicht ermittelbar:** `ja` — das ist ein **gueltiges** Ergebnis und keine Luecke.
  Ein ehrliches "nicht ermittelbar" ist besser als eine Quelle, die beim
  Implementieren nicht traegt.

Dazu je Zeile:

- **Mandant:** wie die Quelle je Mandant getrennt wird.
- **Kosten:** braucht die Quelle eine eigene Abfrage je Knoten? Der
  Workspace-Endpunkt ist heute gecacht und rein lesend — das soll er bleiben.

**Nicht neu zu klaeren** (steht bereits im Masterplan): `insight` und
`footer_cards` sind Fall 1, solange sie keine Mengen, Daten oder Agentenaussagen
tragen. Nur `timestamp` ist als Fall 3 vorentschieden (V13).

## Die 63 Zeilen

### complaint-to-resolution

Knoten (5): `capture`, `triage`, `investigation`, `resolution`, `closure`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` |  |  |  |  |  |
| `submetric` |  |  |  |  |  |
| `timestamp` |  |  |  |  | Fall 3 vorentschieden (V13): `_now()` beim Cache-Fuellen. Nur ersetzen, wenn es eine echte Vorgangszeit gibt. |
| `detail_rows` |  |  |  |  |  |
| `kpis` |  |  |  |  |  |
| `documents` |  |  |  |  | Muss die am Vorgang haengenden Belege zeigen oder leer bleiben. |
| `agent` |  |  |  |  | Vorsicht: generischer Beispieltext im echten Vorgang ist ein Fehler, kein Platzhalter. |

### compliance-to-report

Knoten (5): `collection`, `aggregation`, `validation`, `approval`, `reporting`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` |  |  |  |  |  |
| `submetric` |  |  |  |  |  |
| `timestamp` |  |  |  |  | Fall 3 vorentschieden (V13): `_now()` beim Cache-Fuellen. Nur ersetzen, wenn es eine echte Vorgangszeit gibt. |
| `detail_rows` |  |  |  |  |  |
| `kpis` |  |  |  |  |  |
| `documents` |  |  |  |  | Muss die am Vorgang haengenden Belege zeigen oder leer bleiben. |
| `agent` |  |  |  |  | Vorsicht: generischer Beispieltext im echten Vorgang ist ein Fehler, kein Platzhalter. |

### contract-to-settlement

Knoten (4): `contract`, `acceptance`, `quality`, `settlement`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` |  |  |  |  |  |
| `submetric` |  |  |  |  |  |
| `timestamp` |  |  |  |  | Fall 3 vorentschieden (V13): `_now()` beim Cache-Fuellen. Nur ersetzen, wenn es eine echte Vorgangszeit gibt. |
| `detail_rows` |  |  |  |  |  |
| `kpis` |  |  |  |  |  |
| `documents` |  |  |  |  | Muss die am Vorgang haengenden Belege zeigen oder leer bleiben. |
| `agent` |  |  |  |  | Vorsicht: generischer Beispieltext im echten Vorgang ist ein Fehler, kein Platzhalter. |

### finance-to-close

Knoten (6): `buchung`, `abstimmung`, `meldewesen`, `abschluss-check`, `genehmigung`, `abschluss`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` |  |  |  |  |  |
| `submetric` |  |  |  |  |  |
| `timestamp` |  |  |  |  | Fall 3 vorentschieden (V13): `_now()` beim Cache-Fuellen. Nur ersetzen, wenn es eine echte Vorgangszeit gibt. |
| `detail_rows` |  |  |  |  |  |
| `kpis` |  |  |  |  |  |
| `documents` |  |  |  |  | Muss die am Vorgang haengenden Belege zeigen oder leer bleiben. |
| `agent` |  |  |  |  | Vorsicht: generischer Beispieltext im echten Vorgang ist ein Fehler, kein Platzhalter. |

### harvest-to-settlement

Knoten (6): `annahme`, `trocknung`, `einlagerung`, `kontrakt`, `abrechnung`, `zahlung`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` |  |  |  |  |  |
| `submetric` |  |  |  |  |  |
| `timestamp` |  |  |  |  | Fall 3 vorentschieden (V13): `_now()` beim Cache-Fuellen. Nur ersetzen, wenn es eine echte Vorgangszeit gibt. |
| `detail_rows` |  |  |  |  |  |
| `kpis` |  |  |  |  |  |
| `documents` |  |  |  |  | Muss die am Vorgang haengenden Belege zeigen oder leer bleiben. |
| `agent` |  |  |  |  | Vorsicht: generischer Beispieltext im echten Vorgang ist ein Fehler, kein Platzhalter. |

### inventory-to-settlement

Knoten (6): `inventory-check`, `transfer`, `picking`, `dispatch`, `billing`, `settlement`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` |  |  |  |  |  |
| `submetric` |  |  |  |  |  |
| `timestamp` |  |  |  |  | Fall 3 vorentschieden (V13): `_now()` beim Cache-Fuellen. Nur ersetzen, wenn es eine echte Vorgangszeit gibt. |
| `detail_rows` |  |  |  |  |  |
| `kpis` |  |  |  |  |  |
| `documents` |  |  |  |  | Muss die am Vorgang haengenden Belege zeigen oder leer bleiben. |
| `agent` |  |  |  |  | Vorsicht: generischer Beispieltext im echten Vorgang ist ein Fehler, kein Platzhalter. |

### order-to-cash

Knoten (6): `order`, `check`, `delivery`, `invoice`, `payment`, `close`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` |  |  |  |  |  |
| `submetric` |  |  |  |  |  |
| `timestamp` |  |  |  |  | Fall 3 vorentschieden (V13): `_now()` beim Cache-Fuellen. Nur ersetzen, wenn es eine echte Vorgangszeit gibt. |
| `detail_rows` |  |  |  |  |  |
| `kpis` |  |  |  |  |  |
| `documents` |  |  |  |  | Muss die am Vorgang haengenden Belege zeigen oder leer bleiben. |
| `agent` |  |  |  |  | Vorsicht: generischer Beispieltext im echten Vorgang ist ein Fehler, kein Platzhalter. |

### procure-to-pay

Knoten (6): `requisition`, `approval`, `purchase-order`, `goods-receipt`, `invoice`, `payment`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` |  |  |  |  |  |
| `submetric` |  |  |  |  |  |
| `timestamp` |  |  |  |  | Fall 3 vorentschieden (V13): `_now()` beim Cache-Fuellen. Nur ersetzen, wenn es eine echte Vorgangszeit gibt. |
| `detail_rows` |  |  |  |  |  |
| `kpis` |  |  |  |  |  |
| `documents` |  |  |  |  | Muss die am Vorgang haengenden Belege zeigen oder leer bleiben. |
| `agent` |  |  |  |  | Vorsicht: generischer Beispieltext im echten Vorgang ist ein Fehler, kein Platzhalter. |

### service-to-customer

Knoten (5): `request`, `planning`, `dispatch`, `report`, `closure`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` |  |  |  |  |  |
| `submetric` |  |  |  |  |  |
| `timestamp` |  |  |  |  | Fall 3 vorentschieden (V13): `_now()` beim Cache-Fuellen. Nur ersetzen, wenn es eine echte Vorgangszeit gibt. |
| `detail_rows` |  |  |  |  |  |
| `kpis` |  |  |  |  |  |
| `documents` |  |  |  |  | Muss die am Vorgang haengenden Belege zeigen oder leer bleiben. |
| `agent` |  |  |  |  | Vorsicht: generischer Beispieltext im echten Vorgang ist ein Fehler, kein Platzhalter. |

## Danach

Gegen diese Karte wird FSX-001 implementiert: `merge_instance_statuses` speist
die Felder mit benannter Quelle, alle uebrigen bleiben leer und damit sichtbar
fehlend (FSX-003 Fall 3). Der Vertragstest prueft jeden Wert **gegen seine
deklarierte Quelle**.

49 Knoten in 9 Prozessen sind betroffen; die Karte ist bewusst **je Prozess und
Feld** gefuehrt, nicht je Knoten — 343 Einzelzellen waeren nicht zu pflegen und
die Quelle ist erfahrungsgemaess je Feldart dieselbe. Weicht ein einzelner Knoten
ab, gehoert das in die Hinweisspalte.
