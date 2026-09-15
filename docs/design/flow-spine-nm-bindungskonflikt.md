# Belegbindung gegen n:m — ein latenter Widerspruch

Stand: 2026-09-15 · Claude Code. Gehoert zu
`docs/design/flow-spine-entlastung-masterplan.md` und zu Codex' n:m-Befund.

## Worum es geht

Codex hat festgehalten, was das n:m-Belegmodell vom Flow Spine verlangt:

> `linked_document_id` darf hoechstens der fuehrende Einstiegsbeleg sein.
> Zusaetzlich braucht der Vorgang mehrere Belegverknuepfungen. Beim Hinzufuegen
> einer Rechnung wird die bestehende Lieferscheinbindung also weder
> ueberschrieben noch als unerlaubtes Umbinden behandelt.

**Heute ist genau das verboten.** `_reject_rebind_to_other_document`
(`app/api/v1/endpoints/flow_spines.py:69`) wirft 409, sobald ein Vorgang mit
gesetzter Belegzuordnung auf einen **anderen** Beleg gebunden werden soll.

## Warum es heute trotzdem nicht auffaellt

Nur **zwei** Belegarten nutzen `capture-then-resolve` und schreiben damit
ueberhaupt eine Bindung: `purchase_order` und `delivery_note`. Alle uebrigen
laufen ueber `attach-or-start`, also die Entscheidung **vor** der Erfassung —
und die patcht keine Bindung.

Pro Prozess gibt es damit heute genau einen bindenden Beleg. Der Guard kann in
einer normalen Belegkette nicht ausloesen.

**Das ist der Grund, warum der Widerspruch gefaehrlich ist: er ist latent.** Er
wird nicht beim Bauen sichtbar, sondern erst, wenn jemand die zweite Belegart
eines Prozesses auf `capture-then-resolve` stellt — was das n:m-Modell verlangt.

## Der Ausloesefall, konkret

1. O2C-Vorgang startet am Sofort-Lieferschein: `linked_document_id = LS-1`,
   `linked_document_type = delivery_note`.
2. Spaeter wird Rechnung `RE-1` erfasst und soll demselben Vorgang zugeordnet
   werden — fachlich der Normalfall einer Belegkette.
3. Der Aufrufer patcht `linked_document_id = RE-1`.
4. **409 „Dieser Vorgang ist bereits an einen anderen Beleg gebunden."**

Der Nutzer sieht einen Konflikt, wo er eine voellig gewoehnliche Fortsetzung
gemacht hat.

## Was **nicht** die Loesung ist

**Den Guard aufweichen.** Er ist heute richtig und faengt einen echten Fehler:
eine `workflowInstanceId` aus der URL darf eine bestehende Zuordnung nicht
umbiegen. Wer ihn fuer den n:m-Fall lockert, oeffnet genau die Luecke wieder,
die FSX-012 geschlossen hat — und zwar an einer Stelle, an der niemand mehr
hinsieht.

Ebenso wenig ist die Loesung, `linked_document_id` mehrfach zu belegen oder eine
Liste daraus zu machen: der partielle Unique-Index aus FSX-011 haengt daran, und
er ist es, der die Doppelanlage bei parallelem Speichern verhindert.

## Was die Loesung ist

**Trennen, was heute ein Feld ist:**

| Sache | Ort | Kardinalitaet |
|-------|-----|---------------|
| Fuehrender Einstiegsbeleg | `linked_document_id`/`-type` auf der Instanz | 1, unveraenderlich nach dem Setzen |
| Beteiligte Belege | neue Verknuepfungstabelle je Vorgang | n |
| Positionsbezogene Zuordnung mit Menge | Codex' n:m-Modell (Quellposition, Zielposition, Menge, Einheit, Status) | n:m |

Dann gilt beides ohne Widerspruch:

- Der **Unique-Index** bleibt auf dem fuehrenden Beleg — die Doppelanlage bleibt
  verhindert.
- Der **Guard** bleibt scharf — der fuehrende Beleg wird weiterhin nicht
  umgebogen.
- **Weitere Belege haengen sich an**, ohne den fuehrenden anzufassen. Das ist
  kein Umbinden und wird auch nicht so behandelt.
- Eine **Sammelrechnung** kann in mehreren Vorgaengen als beteiligter Beleg
  auftauchen — was Codex ausdruecklich verlangt und mit einem einzelnen Feld
  nicht geht.

## Empfehlung zur Reihenfolge

Die Verknuepfungstabelle sollte **vor** der zweiten `capture-then-resolve`-Policy
stehen. Andernfalls entsteht genau der Fall oben, und die naheliegende
Schnellkorrektur waere das Aufweichen des Guards.

Ich habe den Widerspruch nicht behoben — das Belegmodell liegt nicht in meiner
Spur, und Codex arbeitet gerade daran. Er ist hier festgehalten, damit er nicht
als Bug missverstanden wird, wenn er zum ersten Mal ausloest.
