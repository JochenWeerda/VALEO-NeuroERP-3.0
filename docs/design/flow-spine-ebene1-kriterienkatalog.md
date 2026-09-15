# Ebene-1-Kriterienkatalog (FSX-030)

Stand: 2026-09-15 · Gehoert zu `docs/design/flow-spine-entlastung-masterplan.md`.

Dieser Katalog beantwortet die Frage, die im Masterplan bewusst offen blieb: **wann
gilt eine Belegmaske als alltagstauglich?** Ohne ihn sind Aussagen wie „ueberwiegend
vorhanden" nicht zu treffen — sie erzeugen falsche Planungssicherheit.

## Die Regel, gegen die geprueft wird

> Alle fuer die aktuelle Fachaufgabe notwendigen Informationen sind in der Belegmaske
> erreichbar. Uebergreifende Analysen und Koordination ueber mehrere Vorgaenge hinweg
> duerfen ausschliesslich im Leitstand bleiben.

Der Pruefsatz lautet also **nicht** „nichts nur im Leitstand", sondern: kein Feld, das
zur Bearbeitung *dieses* Belegs gebraucht wird, zwingt in den Leitstand.

## K1 bis K6 — die Kriterien

Eine Maske erfuellt Ebene 1, wenn **alle sechs** zutreffen. Teilerfuellung wird als
Teilerfuellung berichtet, nicht als Prozentsatz einer Gesamtzahl.

### K1 — Prozessstand ist ohne Wechsel sichtbar

Die Maske zeigt, in welcher Phase der Vorgang steht, ohne dass jemand den Leitstand
oeffnet. Umgesetzt ueber `workflow.phases` in der ScreenDefinition plus dem
`WorkflowState` zur Laufzeit (`ProcessBand`).

**Nicht erfuellt**, wenn der Stand nur als interner Schluessel erscheint
(`Workflow: procure-to-pay`) — das ist Technik, keine Information.

### K2 — Genau eine naechste Aktion

Die Maske benennt **eine** naechste Aktion, nicht eine Liste. Eine Liste ist wieder ein
Entscheidungsproblem und verschiebt die Arbeit zurueck zum Nutzer.

Sind mehrere Aktionen erlaubt, gehoert die Auswahl in die Aktionsleiste der Maske —
nicht in das Prozessband.

### K3 — Blocker sind benannt, nicht nur angezeigt

> **Stand 2026-09-15: erfuellt.** Quelle ist `detail_rows` des Knotens
> (`reason_category`/`reason_code`/`reason_note` des juengsten Ereignisses,
> erschlossen durch FSX-001). Ein kritischer Knotenstatus allein erzeugt keinen
> Blocker; ein fehlender Grund wird als fehlend benannt.


Ein blockierter Vorgang sagt **warum**. „Gesperrt" ohne Grund erfuellt K3 nicht.
Mehrere Blocker werden nacheinander abgearbeitet; das Band nennt den ersten.

### K4 — Belegbindung ist deklariert

`workflow.documentType` ist gesetzt, damit die Maske ueber FSX-010 fragen kann, ob zu
diesem Beleg bereits ein Vorgang existiert — ohne dass jede Maske den Prozess selbst
verdrahtet.

**Nicht erfuellt**, wenn die Maske den Fall nur ueber URL-Parameter aus einem
Handover kennt: dann funktioniert der Einstieg aus dem Leitstand, aber nicht der
belegzentrierte Weg.

### K5 — Teilmengen und Zuordnungen sind in der Maske aufloesbar

> **Nachtrag 2026-09-15 spaet: die Sperre ist aufgehoben.** Das
> positionsbezogene Mengenmodell steht (`FSX-MENGENMODELL`):
> `domain_docs.doc_allocation_sources` fuehrt je Quellposition Gesamt- und
> zugeordnete Menge, `doc_allocations` die n:m-Zeilen mit Menge und Einheit.
> Split, Merge, Restmenge und Status sind damit abbildbar; die Grenze gegen
> Ueberbuchung haelt eine CHECK-Bedingung in der Datenbank, nicht die
> Anwendung.
>
> **K5 ist damit wieder ein Kriterium je Maske — aber noch von keiner Maske
> erfuellt.** Das Modell ist die Voraussetzung, nicht die Erfuellung: „100 dt
> geliefert · 60 dt berechnet · 40 dt offen" liefert
> `DocumentAllocationService.source_state`, gezeigt wird es bisher nirgends.
> Wer K5 fuer eine Maske abhakt, muss auf deren Anzeige zeigen koennen.
>
> Der urspruengliche Sperrvermerk bleibt stehen, weil er die Begruendung traegt:

> **Stand 2026-09-15: heute nicht erfuellbar, und zwar aus einem Modellgrund.**
> Codex hat belegt, dass die positionsbezogene n:m-Zuordnung zwischen Belegen
> fehlt: Docflow gibt bei einer zweiten Umwandlung derselben Beziehungsart die
> vorhandene Rechnung zurueck (wiederholter Split blockiert), die Sammelrechnung
> uebernimmt ganze Lieferscheinsummen mit **einer** `invoice_id` (Merge ohne
> Teilmengen), und der Einkaufsabgleich aggregiert auf Kopfebene.
>
> **Folge fuer diesen Katalog:** K5 darf bis auf Weiteres fuer **keine** Maske
> als erfuellt berichtet werden — auch nicht fuer solche, die Teilmengen
> *anzeigen*. Anzeigen ist nicht aufloesen. Wer K5 abhakt, bevor Quellposition,
> Zielposition, zugeordnete Menge und Status modelliert sind, berichtet einen
> Stand, den das Datenmodell nicht traegt.


Teillieferungen, Teilrechnungen, Chargenzuordnungen und Belegbeziehungen sind in der
Maske erreichbar — aufklappbar genuegt, sichtbar muss es nicht dauerhaft sein
(Ebene 2). Wer dafuer in den Leitstand wechseln muss, erfuellt K5 nicht.

### K6 — Kein operativer Wert ohne Quelle

Was die Maske als Stand, Menge oder Zeitpunkt zeigt, stammt aus einer benannten
Quelle. Fehlende Werte bleiben als fehlend erkennbar. Das ist dieselbe Regel wie
FSX-003 im Leitstand — sie gilt auf Ebene 1 unveraendert weiter.

## Was ausdruecklich **nicht** Ebene 1 ist

Diese Dinge duerfen im Leitstand bleiben, und es ist kein Mangel:

- Vergleiche ueber mehrere Vorgaenge (Durchlaufzeiten, Engpaesse, Auslastung)
- Ausnahmebehandlung ueber Faelle hinweg (was haengt seit wann)
- Koordination zwischen Rollen und Schichten
- Prozessweite Kennzahlen

Wer diese in jede Belegmaske zieht, hat nicht entdichtet, sondern verteilt.

## Messung

Der Katalog wird **je Maske** gefuehrt, nicht als Gesamtquote. Ein Bericht lautet
„14 von 18 Masken erfuellen K1-K4, K5 fehlt bei 9" — nicht „78 % fertig".

Die Erhebung gehoert zu FSX-013 (Rollout des Prozessbands) und wird dort je Welle
fortgeschrieben. Vor dem Rollout gibt es keinen Stand zu berichten; das ist der
Grund, warum der Masterplan die Zahl „70 %" wieder entfernt hat.

## Vertrag in der ScreenDefinition

```python
"workflow": {
    "processKey": "procure-to-pay",      # welcher Prozess
    "documentType": "purchase_order",     # K4: Belegbindung
    "phases": [                           # K1: Prozessdefinition, statisch
        {"key": "draft",    "label": "Erfassung"},
        {"key": "approval", "label": "Freigabe"},
        {"key": "ordered",  "label": "Bestellt"},
        {"key": "invoiced", "label": "Berechnet"},
    ],
    "auditRequired": True,
}
```

**Streng getrennt:** `phases` sind Prozessdefinition und duerfen statisch sein
(FSX-003 Fall 1). Der *aktuelle* Stand, die Aktionen und die Blocker kommen
ausschliesslich aus dem `WorkflowState` zur Laufzeit. Ein Band, das seinen Stand aus
der Definition zieht, zeigt in jedem Beleg dasselbe — genau der Fehler, den
FSX-002/003 im Leitstand beseitigt haben. Ein Test haelt das fest.
