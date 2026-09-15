# FSX-012 Vorklaerung — `capture-then-resolve` erweitern, nicht danebenbauen

Stand: 2026-09-15 · **Erarbeitet von Claude Code in Vertretung fuer Codex**
(Auftrag des Users). Gehoert zu `docs/design/flow-spine-entlastung-masterplan.md`,
Befund V15.

**Umgesetzt 2026-09-15 (Cursor Auto):** Policy `outgoing-purchase-order`,
Verknuepfung in `bestellung-anlegen.tsx` nach dem Speichern, PATCH-409 gegen
Umbiegen, Slice `docs/agent-ops/slices/FSX-012.yaml`. Die Vorklaerung bleibt
die Begruendung; der Code folgt dem Zuschnitt unten. Offener Nachlauf: die
Detailmaske einer bestehenden Bestellung bietet die Verknuepfung noch nicht
erneut an — nur der Wizard nach dem Speichern und der Retry auf derselben Seite.

Geprueft: `packages/frontend-web/src/lib/workflow/document-entry-policy.ts`.

## Die Antwort auf die gestellte Frage

**FSX-012 erweitert das bestehende Muster. Ein zweiter Pfad waere ein Fehler.**

Der Befund V15 stimmt, aber er unterschaetzt, was schon da ist:
`resolveCapturedDocumentWorkflow` ist bereits die Funktion, die **nach** dem
Speichern entscheidet — sie bekommt eine `documentId`, also einen existierenden
Beleg, und liefert `attach`, `start`, `manual-review` oder `standalone`.

## Wo das Muster heute ansetzt

| Belegart | Policy | Flow Spine |
|----------|--------|------------|
| `delivery_note` (Sofort-Lieferschein) | **`capture-then-resolve`** | order-to-cash, Knoten `delivery` |
| `purchase_order` (Bestellung) | **`capture-then-resolve`** | procure-to-pay, Knoten `purchase-order` |
| `sales_offer`, `sales_order`, `sales_invoice`, `credit_note` | `attach-or-start` | order-to-cash |
| `delivery_advice`, `goods_receipt`, `supplier_delivery_note`, `supplier_invoice` | `attach-or-start` | procure-to-pay |

**Genau zwei** Belegarten nutzen `capture-then-resolve` (Lieferschein und,
seit FSX-012, Bestellung). Der Rest laeuft ueber
`resolveDocumentWorkflowIntent` — das ist die Entscheidung **vor** der Erfassung,
also der alte Weg, den FSX-012 fuer P2P-001 umgekehrt hat.

## Drei Befunde, die die Umsetzung praegen

### 1. Die Bestellung fehlt in der Policy-Liste

`purchase_order` **steht** seit FSX-012 in `DOCUMENT_ENTRY_POLICIES` als
`outgoing-purchase-order` mit `capture-then-resolve`. Der Eintrag unten war der
Zuschnitt und ist der Ist-Stand.

```ts
{
  id: 'outgoing-purchase-order',
  label: 'Bestellung erfassen',
  direction: 'outgoing',
  documentType: 'purchase_order',
  partyRole: 'supplier',
  targetRoute: '/einkauf/bestellungen/neu',
  workflowPolicy: 'capture-then-resolve',   // nicht attach-or-start
  matchKeys: ['supplierId', 'supplierNumber', 'requisitionId', 'contractId', 'rfqId'],
  flowSpine: { ...PROCURE_TO_PAY_FLOW, resumeNodeId: 'purchase-order',
               resumeRoute: '/einkauf/bestellungen/neu' },
}
```

Die `matchKeys` sind nicht geraten: `requisitionId`, `contractId` und `rfqId`
liest `bestellung-anlegen.tsx` bereits aus der URL.

### 2. Die Kandidaten hatten bis heute keine Quelle — jetzt haben sie eine

`resolveCapturedDocumentWorkflow` erwartet `candidates` vom Aufrufer und
entscheidet daraus. **Woher die kommen sollten, war offen** — bis FSX-010.
`GET /flow-spines/{process_key}/instances?linked_document_id=&linked_document_type=`
ist genau diese Quelle. Die beiden Slices passen ohne Anpassung zusammen.

Die Zuordnung `confidence` muss der Aufrufer setzen. Vorschlag:
`exact` bei Treffer auf die Belegreferenz, `strong` bei Partner **und** offenem
Vorgang, `weak` bei Partner allein.

### 3. Die Ambiguitaet ist bereits besser geloest als in meinem Auftrag skizziert

Bei mehreren oder unsicheren Treffern liefert die Funktion `manual-review` und
**haengt nichts automatisch an**. Das ist strenger als das, was FSX-012
urspruenglich verlangte, und sollte so bleiben.

## Was das Muster **nicht** abdeckt: der Teilfehler

Das ist die eigentliche Luecke, und sie liegt **nicht** in der Policy.

`resolveCapturedDocumentWorkflow` ist eine **reine Funktion**: sie entscheidet
und liefert `createPayload`/`savePayload` zurueck. Den Schreibvorgang fuehrt der
Aufrufer aus. Faellt er nach dem Speichern des Belegs aus, weiss die Policy davon
nichts — und **soll es auch nicht**. Eine Entscheidungsfunktion, die
Wiederholungen verwaltet, ist keine mehr.

**Der Teilfehler gehoert in die Maske**, und FSX-011 hat ihn billig gemacht:

1. Beleg speichern. Er ist die fuehrende Groesse; schlaegt danach etwas fehl,
   bleibt er gueltig und der Nutzer verliert keine Eingaben.
2. `resolveCapturedDocumentWorkflow` aufrufen, Kandidaten aus FSX-010.
3. Je nach `mode` anhaengen oder anlegen.
4. **Schlaegt Schritt 3 fehl:** sichtbarer Teilfehlerzustand
   („Bestellung gespeichert, Vorgang noch nicht verknuepft") mit einer Aktion
   zum erneuten Verknuepfen — und diese Aktion ruft **nur** Schritt 3 erneut auf,
   nie Schritt 1.

**Warum die Wiederholung gefahrlos ist:** `POST .../instances` ist seit FSX-011
auf der Belegreferenz idempotent. Derselbe Aufruf liefert stets denselben Fall
(200 statt 201). Ein Wiederholungsmechanismus muss also **nichts entdoppeln** —
er muss nur erneut aufrufen. Das war vor FSX-011 der teure Teil und ist es
nicht mehr.

## Antwort auf die dritte Frage: braucht die Bestellmaske eine Abweichung?

**Nein, mit einer Ausnahme.** Der Sofort-Lieferschein wird in einem Zug erfasst;
die Bestellung laeuft ueber einen **Wizard mit mehreren Schritten**. Der
`capture-then-resolve`-Aufruf gehoert deshalb an das Speichern am Ende, nicht an
den Schritt-Wechsel. Der bestehende
`persistWorkflowResume`-Aufruf in `bestellung-anlegen.tsx` zeigt, wo die Stelle
ist — er laeuft schon heute beim Speichern.

## Empfohlener Zuschnitt fuer FSX-012

1. Policy-Eintrag `outgoing-purchase-order` ergaenzen (oben).
2. In der Bestellmaske: nach erfolgreichem Speichern Kandidaten ueber FSX-010
   holen, `resolveCapturedDocumentWorkflow` aufrufen, Ergebnis ausfuehren.
3. Teilfehlerzustand mit Wiederholung, die nur die Verknuepfung wiederholt.
4. Serverseitige Pruefung einer `workflowInstanceId` aus der URL auf Mandant,
   `process_key` und bestehende Belegzuordnung — 404 statt 403, um keine
   Existenz fremder Faelle preiszugeben.
5. `docs/workflows/p2p-001-*.md` und die Cards nachziehen.

**Nicht** empfohlen: ein eigener Pfad fuer die Bestellung, ein zweiter
Entscheidungsmechanismus, oder eine Erweiterung der reinen Funktion um
Wiederholungslogik.
