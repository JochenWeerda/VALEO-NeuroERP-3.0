# FSX-001 Herkunftskarte

Stand: 2026-09-15 · **Ausgefuellt von Claude Code in Vertretung fuer Codex**
(Auftrag des Users, weil FSX-001 und FSX-012 sonst stillstehen).
Gehoert zu `docs/design/flow-spine-entlastung-masterplan.md`, Slice FSX-001.

> **An Codex:** Du hattest FSX-001-QUELLENKARTE per `fsx-claim.patch` reserviert,
> und der Dateibesitz lag bei dir. Der User hat mich gebeten, deine Aufgaben
> voruebergehend zu uebernehmen. Das hier ist **recherchiert, nicht geraten** —
> jede Zeile nennt Tabelle und Spalte. Widersprich, wo du es besser weisst;
> bei `metric`/`kpis` kennst du die Domaenen-Readmodels laenger als ich.

## Das Ergebnis in einem Satz

**Zwei der sieben operativen Felder haben eine echte Quelle, fuenf nicht** —
und die Quellen sind in allen neun Prozessen **dieselben**, weil sie am Vorgang
haengen und nicht am Prozess.

| Feld | Ergebnis |
|------|----------|
| `timestamp` | **Quelle vorhanden** — juengstes Knotenereignis |
| `detail_rows` | **teilweise** — Bearbeiter, Aktion, Grund aus demselben Ereignis |
| `metric`, `submetric`, `kpis`, `documents`, `agent` | **nicht ermittelbar** |

Das ist ein ernuechterndes, aber brauchbares Ergebnis. Der Leitstand kann
kuenftig zeigen, **wann** an einem Knoten zuletzt etwas geschah, **wer** es tat
und **warum** — aber keine Mengen, Quoten oder Bewertungen. Wer diese will,
muss sie erst erzeugen; sie liegen nirgends.

## Abweichung zu V13 — `timestamp` ist doch ermittelbar

Der Masterplan hat `timestamp` als Fall 3 vorentschieden, mit der Begruendung:
`_now()` beim Cache-Fuellen sieht aus wie eine Vorgangszeit, ist aber der
Zeitpunkt des ersten Cache-Fuellens. **Die Begruendung stimmt, die Folgerung
nicht.** Dass die *heutige* Herkunft wertlos ist, heisst nicht, dass es keine
gibt: `ops_flow_spine_instance_events` fuehrt `node_id`, `actor_id` und
`created_at` je Ereignis. Das juengste Ereignis eines Knotens ist genau die
Zeit, die der Leitstand meint.

V13 bleibt als **Befund** richtig (der bisherige Wert ist Fall 3) und ist als
**Zuordnung** ueberholt.

## Was fehlt, und was es kosten wuerde

- **`agent`:** `agent_proposals` traegt `rationale` und `risk_level`, aber kein
  `instance_id`/`node_id`. Es genuegte, `execute_agent_action` die Bewertung mit
  Vorgangs- und Knotenbezug im `context_snapshot` persistieren zu lassen. Das ist
  ein eigener Slice, **keine** Feldzuordnung — bis dahin ist die ehrliche
  Antwort "nicht ermittelbar".
- **`documents`:** Der Instanzbeleg ist da, die Knotenzuordnung fehlt. Sie waere
  deklarativ loesbar (welcher Knoten traegt welche Belegart), gehoert aber in den
  Prozessvertrag, nicht in diese Karte.
- **`metric`/`submetric`/`kpis`:** Hier liegt nichts. Jeder Prozess braeuchte ein
  eigenes Readmodel — neun Slices. Das sollte erst beginnen, wenn jemand sagen
  kann, **welche** Zahl am Knoten gebraucht wird. Die heutigen Registerwerte sind
  dafuer kein Beleg; sie waren Beispiele.

## Mandantentrennung

Alle beteiligten Tabellen fuehren `tenant_id`: `ops_flow_spine_instances`,
`ops_flow_spine_instance_events`, `agent_proposals`. Die Ereignisabfrage **muss**
zusaetzlich zu `instance_id` auf `tenant_id` filtern — die Instanz-ID allein ist
zwar ein UUID, aber der Filter gehoert gesetzt, damit ein Mandantenfehler
auffaellt statt Daten preiszugeben.

## Abfragekosten

**Eine** zusaetzliche Abfrage je Workspace-Aufruf mit Instanz, nicht eine je Knoten:

```sql
SELECT DISTINCT ON (node_id)
       node_id, created_at, event_type, actor_id,
       reason_category, reason_code, reason_note
  FROM domain_ops.ops_flow_spine_instance_events
 WHERE instance_id = :instance_id AND tenant_id = :tenant_id
   AND node_id IS NOT NULL
 ORDER BY node_id, created_at DESC;
```

Der Index auf `instance_id` besteht, `created_at` ist ebenfalls indiziert. Der
**Katalogpfad ohne Instanz bleibt unberuehrt und damit gecacht** — die Abfrage
laeuft nur im Instanzzweig, der ohnehin nicht gecacht ist.

## Die Tabellen je Prozess

Sie sind bewusst neunmal gleich: die Quellen haengen am Vorgang, nicht am
Prozess. Knotenabweichungen waeren hier einzutragen — **es wurden keine gefunden.**

### complaint-to-resolution

Knoten (5): `capture`, `triage`, `investigation`, `resolution`, `closure`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` | — | ja | — | — | Kein Traeger im Datenmodell. Waere je Prozess ein eigenes Readmodel — ein Slice je Prozess, keine Feldzuordnung. |
| `submetric` | — | ja | — | — | Wie `metric`. |
| `timestamp` | `FlowSpineInstanceEvent.created_at` des juengsten Ereignisses mit `node_id = <Knoten>` | nein | `ops_flow_spine_instance_events.tenant_id` | 1 Abfrage je **Instanz** (DISTINCT ON node_id), nicht je Knoten | **Korrigiert V13** — siehe Abschnitt "Abweichung zu V13". |
| `detail_rows` | Je Knoten aus demselben juengsten Ereignis: `event_type`, `actor_id`, `reason_category`, `reason_code`, `reason_note`. Instanzweit zusaetzlich `case_number`, `entry_mode`, `assigned_owner`, `business_status` | teilweise | wie `timestamp` | keine zusaetzliche Abfrage (dieselbe wie `timestamp`) | Die heutigen Registerzeilen ("Belegart", "Pflichtdaten") sind Prozessbeschreibung, nicht Vorgangsdaten — sie kehren nicht zurueck. |
| `kpis` | — | ja | — | — | Prozessweite Kennzahlen existieren (z. B. Freigabedichte), aber weder je Knoten noch je Vorgang. Sie gehoeren auf Ebene 3. |
| `documents` | Instanzweit **genau ein** Beleg: `linked_document_id` + `linked_document_type` | ja (je Knoten) | `ops_flow_spine_instances.tenant_id` | keine zusaetzliche Abfrage | Es fehlt die Knotenzuordnung. Den einen Instanzbeleg an einem geratenen Knoten auszugeben waere eine Behauptung — er gehoert in den Vorgangskopf. |
| `agent` | — | ja | — | — | `agent_proposals` existiert mit `rationale`/`risk_level`/`approval_status`, hat aber keine Verknuepfung zu `instance_id`/`node_id`; `execute_agent_action` persistiert nichts. Siehe "Was fehlt". |

### compliance-to-report

Knoten (5): `collection`, `aggregation`, `validation`, `approval`, `reporting`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` | — | ja | — | — | Kein Traeger im Datenmodell. Waere je Prozess ein eigenes Readmodel — ein Slice je Prozess, keine Feldzuordnung. |
| `submetric` | — | ja | — | — | Wie `metric`. |
| `timestamp` | `FlowSpineInstanceEvent.created_at` des juengsten Ereignisses mit `node_id = <Knoten>` | nein | `ops_flow_spine_instance_events.tenant_id` | 1 Abfrage je **Instanz** (DISTINCT ON node_id), nicht je Knoten | **Korrigiert V13** — siehe Abschnitt "Abweichung zu V13". |
| `detail_rows` | Je Knoten aus demselben juengsten Ereignis: `event_type`, `actor_id`, `reason_category`, `reason_code`, `reason_note`. Instanzweit zusaetzlich `case_number`, `entry_mode`, `assigned_owner`, `business_status` | teilweise | wie `timestamp` | keine zusaetzliche Abfrage (dieselbe wie `timestamp`) | Die heutigen Registerzeilen ("Belegart", "Pflichtdaten") sind Prozessbeschreibung, nicht Vorgangsdaten — sie kehren nicht zurueck. |
| `kpis` | — | ja | — | — | Prozessweite Kennzahlen existieren (z. B. Freigabedichte), aber weder je Knoten noch je Vorgang. Sie gehoeren auf Ebene 3. |
| `documents` | Instanzweit **genau ein** Beleg: `linked_document_id` + `linked_document_type` | ja (je Knoten) | `ops_flow_spine_instances.tenant_id` | keine zusaetzliche Abfrage | Es fehlt die Knotenzuordnung. Den einen Instanzbeleg an einem geratenen Knoten auszugeben waere eine Behauptung — er gehoert in den Vorgangskopf. |
| `agent` | — | ja | — | — | `agent_proposals` existiert mit `rationale`/`risk_level`/`approval_status`, hat aber keine Verknuepfung zu `instance_id`/`node_id`; `execute_agent_action` persistiert nichts. Siehe "Was fehlt". |

### contract-to-settlement

Knoten (4): `contract`, `acceptance`, `quality`, `settlement`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` | — | ja | — | — | Kein Traeger im Datenmodell. Waere je Prozess ein eigenes Readmodel — ein Slice je Prozess, keine Feldzuordnung. |
| `submetric` | — | ja | — | — | Wie `metric`. |
| `timestamp` | `FlowSpineInstanceEvent.created_at` des juengsten Ereignisses mit `node_id = <Knoten>` | nein | `ops_flow_spine_instance_events.tenant_id` | 1 Abfrage je **Instanz** (DISTINCT ON node_id), nicht je Knoten | **Korrigiert V13** — siehe Abschnitt "Abweichung zu V13". |
| `detail_rows` | Je Knoten aus demselben juengsten Ereignis: `event_type`, `actor_id`, `reason_category`, `reason_code`, `reason_note`. Instanzweit zusaetzlich `case_number`, `entry_mode`, `assigned_owner`, `business_status` | teilweise | wie `timestamp` | keine zusaetzliche Abfrage (dieselbe wie `timestamp`) | Die heutigen Registerzeilen ("Belegart", "Pflichtdaten") sind Prozessbeschreibung, nicht Vorgangsdaten — sie kehren nicht zurueck. |
| `kpis` | — | ja | — | — | Prozessweite Kennzahlen existieren (z. B. Freigabedichte), aber weder je Knoten noch je Vorgang. Sie gehoeren auf Ebene 3. |
| `documents` | Instanzweit **genau ein** Beleg: `linked_document_id` + `linked_document_type` | ja (je Knoten) | `ops_flow_spine_instances.tenant_id` | keine zusaetzliche Abfrage | Es fehlt die Knotenzuordnung. Den einen Instanzbeleg an einem geratenen Knoten auszugeben waere eine Behauptung — er gehoert in den Vorgangskopf. |
| `agent` | — | ja | — | — | `agent_proposals` existiert mit `rationale`/`risk_level`/`approval_status`, hat aber keine Verknuepfung zu `instance_id`/`node_id`; `execute_agent_action` persistiert nichts. Siehe "Was fehlt". |

### finance-to-close

Knoten (6): `buchung`, `abstimmung`, `meldewesen`, `abschluss-check`, `genehmigung`, `abschluss`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` | — | ja | — | — | Kein Traeger im Datenmodell. Waere je Prozess ein eigenes Readmodel — ein Slice je Prozess, keine Feldzuordnung. |
| `submetric` | — | ja | — | — | Wie `metric`. |
| `timestamp` | `FlowSpineInstanceEvent.created_at` des juengsten Ereignisses mit `node_id = <Knoten>` | nein | `ops_flow_spine_instance_events.tenant_id` | 1 Abfrage je **Instanz** (DISTINCT ON node_id), nicht je Knoten | **Korrigiert V13** — siehe Abschnitt "Abweichung zu V13". |
| `detail_rows` | Je Knoten aus demselben juengsten Ereignis: `event_type`, `actor_id`, `reason_category`, `reason_code`, `reason_note`. Instanzweit zusaetzlich `case_number`, `entry_mode`, `assigned_owner`, `business_status` | teilweise | wie `timestamp` | keine zusaetzliche Abfrage (dieselbe wie `timestamp`) | Die heutigen Registerzeilen ("Belegart", "Pflichtdaten") sind Prozessbeschreibung, nicht Vorgangsdaten — sie kehren nicht zurueck. |
| `kpis` | — | ja | — | — | Prozessweite Kennzahlen existieren (z. B. Freigabedichte), aber weder je Knoten noch je Vorgang. Sie gehoeren auf Ebene 3. |
| `documents` | Instanzweit **genau ein** Beleg: `linked_document_id` + `linked_document_type` | ja (je Knoten) | `ops_flow_spine_instances.tenant_id` | keine zusaetzliche Abfrage | Es fehlt die Knotenzuordnung. Den einen Instanzbeleg an einem geratenen Knoten auszugeben waere eine Behauptung — er gehoert in den Vorgangskopf. |
| `agent` | — | ja | — | — | `agent_proposals` existiert mit `rationale`/`risk_level`/`approval_status`, hat aber keine Verknuepfung zu `instance_id`/`node_id`; `execute_agent_action` persistiert nichts. Siehe "Was fehlt". |

### harvest-to-settlement

Knoten (6): `annahme`, `trocknung`, `einlagerung`, `kontrakt`, `abrechnung`, `zahlung`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` | — | ja | — | — | Kein Traeger im Datenmodell. Waere je Prozess ein eigenes Readmodel — ein Slice je Prozess, keine Feldzuordnung. |
| `submetric` | — | ja | — | — | Wie `metric`. |
| `timestamp` | `FlowSpineInstanceEvent.created_at` des juengsten Ereignisses mit `node_id = <Knoten>` | nein | `ops_flow_spine_instance_events.tenant_id` | 1 Abfrage je **Instanz** (DISTINCT ON node_id), nicht je Knoten | **Korrigiert V13** — siehe Abschnitt "Abweichung zu V13". |
| `detail_rows` | Je Knoten aus demselben juengsten Ereignis: `event_type`, `actor_id`, `reason_category`, `reason_code`, `reason_note`. Instanzweit zusaetzlich `case_number`, `entry_mode`, `assigned_owner`, `business_status` | teilweise | wie `timestamp` | keine zusaetzliche Abfrage (dieselbe wie `timestamp`) | Die heutigen Registerzeilen ("Belegart", "Pflichtdaten") sind Prozessbeschreibung, nicht Vorgangsdaten — sie kehren nicht zurueck. |
| `kpis` | — | ja | — | — | Prozessweite Kennzahlen existieren (z. B. Freigabedichte), aber weder je Knoten noch je Vorgang. Sie gehoeren auf Ebene 3. |
| `documents` | Instanzweit **genau ein** Beleg: `linked_document_id` + `linked_document_type` | ja (je Knoten) | `ops_flow_spine_instances.tenant_id` | keine zusaetzliche Abfrage | Es fehlt die Knotenzuordnung. Den einen Instanzbeleg an einem geratenen Knoten auszugeben waere eine Behauptung — er gehoert in den Vorgangskopf. |
| `agent` | — | ja | — | — | `agent_proposals` existiert mit `rationale`/`risk_level`/`approval_status`, hat aber keine Verknuepfung zu `instance_id`/`node_id`; `execute_agent_action` persistiert nichts. Siehe "Was fehlt". |

### inventory-to-settlement

Knoten (6): `inventory-check`, `transfer`, `picking`, `dispatch`, `billing`, `settlement`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` | — | ja | — | — | Kein Traeger im Datenmodell. Waere je Prozess ein eigenes Readmodel — ein Slice je Prozess, keine Feldzuordnung. |
| `submetric` | — | ja | — | — | Wie `metric`. |
| `timestamp` | `FlowSpineInstanceEvent.created_at` des juengsten Ereignisses mit `node_id = <Knoten>` | nein | `ops_flow_spine_instance_events.tenant_id` | 1 Abfrage je **Instanz** (DISTINCT ON node_id), nicht je Knoten | **Korrigiert V13** — siehe Abschnitt "Abweichung zu V13". |
| `detail_rows` | Je Knoten aus demselben juengsten Ereignis: `event_type`, `actor_id`, `reason_category`, `reason_code`, `reason_note`. Instanzweit zusaetzlich `case_number`, `entry_mode`, `assigned_owner`, `business_status` | teilweise | wie `timestamp` | keine zusaetzliche Abfrage (dieselbe wie `timestamp`) | Die heutigen Registerzeilen ("Belegart", "Pflichtdaten") sind Prozessbeschreibung, nicht Vorgangsdaten — sie kehren nicht zurueck. |
| `kpis` | — | ja | — | — | Prozessweite Kennzahlen existieren (z. B. Freigabedichte), aber weder je Knoten noch je Vorgang. Sie gehoeren auf Ebene 3. |
| `documents` | Instanzweit **genau ein** Beleg: `linked_document_id` + `linked_document_type` | ja (je Knoten) | `ops_flow_spine_instances.tenant_id` | keine zusaetzliche Abfrage | Es fehlt die Knotenzuordnung. Den einen Instanzbeleg an einem geratenen Knoten auszugeben waere eine Behauptung — er gehoert in den Vorgangskopf. |
| `agent` | — | ja | — | — | `agent_proposals` existiert mit `rationale`/`risk_level`/`approval_status`, hat aber keine Verknuepfung zu `instance_id`/`node_id`; `execute_agent_action` persistiert nichts. Siehe "Was fehlt". |

### order-to-cash

Knoten (6): `order`, `check`, `delivery`, `invoice`, `payment`, `close`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` | — | ja | — | — | Kein Traeger im Datenmodell. Waere je Prozess ein eigenes Readmodel — ein Slice je Prozess, keine Feldzuordnung. |
| `submetric` | — | ja | — | — | Wie `metric`. |
| `timestamp` | `FlowSpineInstanceEvent.created_at` des juengsten Ereignisses mit `node_id = <Knoten>` | nein | `ops_flow_spine_instance_events.tenant_id` | 1 Abfrage je **Instanz** (DISTINCT ON node_id), nicht je Knoten | **Korrigiert V13** — siehe Abschnitt "Abweichung zu V13". |
| `detail_rows` | Je Knoten aus demselben juengsten Ereignis: `event_type`, `actor_id`, `reason_category`, `reason_code`, `reason_note`. Instanzweit zusaetzlich `case_number`, `entry_mode`, `assigned_owner`, `business_status` | teilweise | wie `timestamp` | keine zusaetzliche Abfrage (dieselbe wie `timestamp`) | Die heutigen Registerzeilen ("Belegart", "Pflichtdaten") sind Prozessbeschreibung, nicht Vorgangsdaten — sie kehren nicht zurueck. |
| `kpis` | — | ja | — | — | Prozessweite Kennzahlen existieren (z. B. Freigabedichte), aber weder je Knoten noch je Vorgang. Sie gehoeren auf Ebene 3. |
| `documents` | Instanzweit **genau ein** Beleg: `linked_document_id` + `linked_document_type` | ja (je Knoten) | `ops_flow_spine_instances.tenant_id` | keine zusaetzliche Abfrage | Es fehlt die Knotenzuordnung. Den einen Instanzbeleg an einem geratenen Knoten auszugeben waere eine Behauptung — er gehoert in den Vorgangskopf. |
| `agent` | — | ja | — | — | `agent_proposals` existiert mit `rationale`/`risk_level`/`approval_status`, hat aber keine Verknuepfung zu `instance_id`/`node_id`; `execute_agent_action` persistiert nichts. Siehe "Was fehlt". |

### procure-to-pay

Knoten (6): `requisition`, `approval`, `purchase-order`, `goods-receipt`, `invoice`, `payment`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` | — | ja | — | — | Kein Traeger im Datenmodell. Waere je Prozess ein eigenes Readmodel — ein Slice je Prozess, keine Feldzuordnung. |
| `submetric` | — | ja | — | — | Wie `metric`. |
| `timestamp` | `FlowSpineInstanceEvent.created_at` des juengsten Ereignisses mit `node_id = <Knoten>` | nein | `ops_flow_spine_instance_events.tenant_id` | 1 Abfrage je **Instanz** (DISTINCT ON node_id), nicht je Knoten | **Korrigiert V13** — siehe Abschnitt "Abweichung zu V13". |
| `detail_rows` | Je Knoten aus demselben juengsten Ereignis: `event_type`, `actor_id`, `reason_category`, `reason_code`, `reason_note`. Instanzweit zusaetzlich `case_number`, `entry_mode`, `assigned_owner`, `business_status` | teilweise | wie `timestamp` | keine zusaetzliche Abfrage (dieselbe wie `timestamp`) | Die heutigen Registerzeilen ("Belegart", "Pflichtdaten") sind Prozessbeschreibung, nicht Vorgangsdaten — sie kehren nicht zurueck. |
| `kpis` | — | ja | — | — | Prozessweite Kennzahlen existieren (z. B. Freigabedichte), aber weder je Knoten noch je Vorgang. Sie gehoeren auf Ebene 3. |
| `documents` | Instanzweit **genau ein** Beleg: `linked_document_id` + `linked_document_type` | ja (je Knoten) | `ops_flow_spine_instances.tenant_id` | keine zusaetzliche Abfrage | Es fehlt die Knotenzuordnung. Den einen Instanzbeleg an einem geratenen Knoten auszugeben waere eine Behauptung — er gehoert in den Vorgangskopf. |
| `agent` | — | ja | — | — | `agent_proposals` existiert mit `rationale`/`risk_level`/`approval_status`, hat aber keine Verknuepfung zu `instance_id`/`node_id`; `execute_agent_action` persistiert nichts. Siehe "Was fehlt". |

### service-to-customer

Knoten (5): `request`, `planning`, `dispatch`, `report`, `closure`

| Feld | Quelle | Nicht ermittelbar | Mandant | Kosten | Hinweis |
|------|--------|-------------------|---------|--------|---------|
| `metric` | — | ja | — | — | Kein Traeger im Datenmodell. Waere je Prozess ein eigenes Readmodel — ein Slice je Prozess, keine Feldzuordnung. |
| `submetric` | — | ja | — | — | Wie `metric`. |
| `timestamp` | `FlowSpineInstanceEvent.created_at` des juengsten Ereignisses mit `node_id = <Knoten>` | nein | `ops_flow_spine_instance_events.tenant_id` | 1 Abfrage je **Instanz** (DISTINCT ON node_id), nicht je Knoten | **Korrigiert V13** — siehe Abschnitt "Abweichung zu V13". |
| `detail_rows` | Je Knoten aus demselben juengsten Ereignis: `event_type`, `actor_id`, `reason_category`, `reason_code`, `reason_note`. Instanzweit zusaetzlich `case_number`, `entry_mode`, `assigned_owner`, `business_status` | teilweise | wie `timestamp` | keine zusaetzliche Abfrage (dieselbe wie `timestamp`) | Die heutigen Registerzeilen ("Belegart", "Pflichtdaten") sind Prozessbeschreibung, nicht Vorgangsdaten — sie kehren nicht zurueck. |
| `kpis` | — | ja | — | — | Prozessweite Kennzahlen existieren (z. B. Freigabedichte), aber weder je Knoten noch je Vorgang. Sie gehoeren auf Ebene 3. |
| `documents` | Instanzweit **genau ein** Beleg: `linked_document_id` + `linked_document_type` | ja (je Knoten) | `ops_flow_spine_instances.tenant_id` | keine zusaetzliche Abfrage | Es fehlt die Knotenzuordnung. Den einen Instanzbeleg an einem geratenen Knoten auszugeben waere eine Behauptung — er gehoert in den Vorgangskopf. |
| `agent` | — | ja | — | — | `agent_proposals` existiert mit `rationale`/`risk_level`/`approval_status`, hat aber keine Verknuepfung zu `instance_id`/`node_id`; `execute_agent_action` persistiert nichts. Siehe "Was fehlt". |

## Danach

Gegen diese Karte wird FSX-001 implementiert: `merge_instance_statuses` speist
`timestamp` und `detail_rows` aus dem juengsten Knotenereignis; `metric`,
`submetric`, `kpis`, `documents` und `agent` bleiben leer und damit sichtbar
fehlend (FSX-003 Fall 3). Der Vertragstest prueft die beiden gefuellten Felder
**gegen ihre Quelle** — Ereignis anlegen, Workspace lesen, Wert vergleichen —
und fuer die uebrigen fuenf, dass sie leer **bleiben**.
