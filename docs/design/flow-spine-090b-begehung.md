# FSX-090b — Expertenbegehung statt Nutzerbeobachtung

Stand: 2026-09-15 · Durchgefuehrt von Claude Code im Auftrag des Users
(„Du musst die Nutzer simulieren").

## Was das hier ist — und was es nicht ist

**Es ist kein Ersatz fuer FSX-090b.** Ich kann keine Nutzer simulieren: ich kenne
jede dieser Masken, ich habe die Haelfte davon heute gebaut, und ich kann von
nichts ueberrascht werden. Genau die Ueberraschung ist aber das Messinstrument
der Nutzerbeobachtung.

**Es ist ein Cognitive Walkthrough** — eine Expertenbegehung: fuer jeden Schritt
einer Aufgabe wird gefragt, ob der Nutzer (a) weiss, was zu tun ist, (b) das
noetige Bedienelement findet, und (c) die Rueckmeldung als Fortschritt erkennt.
Das Verfahren findet **offensichtliche Brueche** zuverlaessig. Es misst
**nicht**: Bedienzeit, Suchpausen, Verstaendlichkeit.

**Das Abbruchkriterium von FSX-090b bleibt damit unbeantwortet.** Ob eine Sperre
in der neuen Fassung *seltener verstanden* wird als in der alten, ist eine
Aussage ueber Menschen und durch Inspektion nicht zu gewinnen. Diese Begehung
kann den Rollout **stoppen**, aber nicht **freigeben**.

## Aufgabe 1 — Direktbestellung aus dem P2P-Vorgang erfassen

Rolle: Innendienst. Maske: `einkauf/bestellung-anlegen` (FSX-013-Pilot).

| Schritt | Weiss der Nutzer, was zu tun ist? | Findet er das Element? | Erkennt er den Fortschritt? |
|---------|-----------------------------------|------------------------|------------------------------|
| Maske oeffnet aus Handover | ja — Lieferant ist vorbefuellt | ja | ja, Prozessband zeigt „Bestellung" als aktive Phase |
| Positionen erfassen | ja | ja | ja |
| Speichern | ja | ja | ja, Bestellnummer kommt vom Server |

**Kein Bruch gefunden.** Das Prozessband ersetzt den Hinweiskasten ohne
erkennbaren Verlust — der Kasten erklaerte, dass ein Vorgang dahintersteht; das
Band zeigt es.

## Aufgabe 2 — Reklamation zu einem abgeschlossenen Vorgang anlegen

Rolle: Innendienst. Pfad: Belegmaske → Fallsuche (FSX-010).

**Kein Bruch auf der Datenseite:** FSX-010 liefert abgeschlossene Vorgaenge mit,
am `lifecycle_status` erkennbar, und FSX-011 laesst einen neuen Fall zum selben
Beleg zu. Fachlich ist der Weg offen.

**Aber:** Die Maske, die das anbietet, existiert noch nicht — FSX-012 ist nicht
umgesetzt. Die Begehung kann hier nur sagen, dass der Unterbau traegt.

## Aufgabe 3 — Einen blockierten Vorgang erklaeren: *warum* geht es nicht weiter?

Rolle: Buchhaltung. **Hier bricht es, und zwar dreifach.**

### F1 — Der Grund einer Pause ist gespeichert, aber praktisch unsichtbar (schwer)

`hold_instance` schreibt `reason_category`, `reason_code` und `reason_note` —
**nur in das Ereignis**, nicht auf die Instanz. Sichtbar ist der Grund damit
ausschliesslich im Timeline-Register der Copilot-Spalte.

**Und diese Spalte habe ich in FSX-023 eingeklappt.** Der Grund ist damit von
„ein Blick nach rechts" auf „aufklappen, Register wechseln, Ereignis suchen"
gewandert. **Das ist eine Regression durch meinen eigenen Slice**, und sie
betrifft ausgerechnet die Frage, die ein blockierter Vorgang aufwirft.

### F2 — Ein pausierter Vorgang meldet „Kein Abschlussgrund gesetzt" (schwer)

`lifecycleSummary()` behandelt `cancelled`, `failed` und `completed` und faellt
fuer alles andere auf `reason_note || 'Kein Abschlussgrund gesetzt'` zurueck. Da
`hold` die Instanz-`reason_note` nicht setzt, liest der Nutzer bei einem
pausierten Vorgang woertlich **„Kein Abschlussgrund gesetzt"**.

Das ist doppelt falsch: es ist kein Abschluss, und ein Grund *ist* gesetzt — nur
woanders. Ein Nutzer, der das liest, schliesst daraus, es gebe keinen Grund.

### F3 — Das Prozessband zeigt keinen Blocker, weil es keine Quelle gibt (mittel)

K3 des Kriterienkatalogs verlangt: „Ein blockierter Vorgang sagt **warum**." Das
Band kann das heute nicht — die Herkunftskarte hat bestaetigt, dass es je Knoten
keinen Sperrgrund gibt. Damit ist **die Ebene-1-Regel verletzt**: der Nutzer muss
fuer eine Auskunft ueber *diesen* Beleg in den Leitstand wechseln.

## Zwei weitere Befunde am Rand

### F4 — „Fokus" nimmt den Vorgangswechsel mit (mittel)

Der Fokus-Modus blendet die Prozessspalte aus, also auch die Vorgangsliste. Fuer
die Rolle **Waage**, die zwischen Fahrzeugen wechselt, ist das vermutlich die
falsche Verengung. Ich habe beim Bauen an den Innendienst gedacht.

### F5 — Ein fehlendes Band ist von „kein Prozess" nicht unterscheidbar (leicht)

Ohne Phasen rendert das Band nichts. Das war eine bewusste Entscheidung gegen
einen Platzhalter — aber der Nutzer kann nicht unterscheiden, ob dieser Beleg zu
keinem Prozess gehoert oder ob die Anzeige ausgefallen ist.

## Nachtrag 2026-09-15 spaeter — F1 bis F3 geschlossen

**Reihenfolge hat sich bewaehrt.** Cursor hat FSX-001 umgesetzt (`56ffd0c2f`),
und damit sind zwei der drei Brueche ohne eigenen Slice verschwunden:

- **F1 erledigt durch FSX-001.** `reason_category`, `reason_code` und
  `reason_note` des juengsten Knotenereignisses landen jetzt in `detail_rows`.
  Die Statuskarte in der Mitte rendert `detail_rows` — der Grund steht damit im
  Arbeitsbereich und nicht mehr nur im Timeline-Register der eingeklappten
  Spalte. Die Regression aus FSX-023 ist damit aufgehoben, ohne die Spalte
  wieder aufzuklappen.
- **F2 war bereits behoben** (`on_hold`-Zweig in `lifecycleSummary`). Der
  Verweistext zeigt jetzt auf die Knotendetails statt auf die Timeline.
- **F3 erledigt.** Das Prozessband zeigt einen Blocker, sobald der Vorgang
  `on_hold` oder `failed` ist. Der Text kommt aus den `detail_rows` des Knotens,
  also aus der Quelle, die FSX-001 erschlossen hat.

**Zwei Regeln, die dabei eingehalten wurden:**

1. **Ein kritischer Knotenstatus allein erzeugt keinen Blocker.** „critical" ist
   ein Knotenzustand, keine Sperre des Vorgangs. Die Sperre ist eine Aussage des
   Lebenszyklus.
2. **Ein fehlender Grund wird als fehlend benannt** („Pausiert — Grund nicht
   hinterlegt"), nicht erfunden. Dass der Vorgang steht, ist ein Fakt; warum, ist
   dann schlicht nicht hinterlegt.

Zusaetzlich faengt das Band jetzt den Fall ab, dass ein pausierter Vorgang
**keinen** `active`-Knoten mehr hat — ohne diesen Rueckfall waere die Sperre
ausgerechnet im wichtigsten Fall unsichtbar geblieben.

**K3 des Kriterienkatalogs ist damit in der Belegmaske erfuellt.**

**Offen bleibt F4** (Fokus nimmt den Vorgangswechsel mit). Das ist keine
Fehlfunktion, sondern eine Zuschnittsfrage, und sie gehoert an den Rollout in
Waage-Masken — nicht hierher.

## Folgerung fuer den Rollout

> **Ueberholt durch den Nachtrag oben:** F1 bis F3 sind geschlossen. Die
> Sperre gegen den Rollout ist damit **aufgehoben**; es bleibt die Bedingung,
> dass FSX-090b mit echten Nutzern stattfindet. Der urspruengliche Absatz bleibt
> stehen, weil er die Begruendung traegt.

**Der FSX-013-Rollout auf die restlichen 17 Masken sollte nicht stattfinden,
solange F1 bis F3 offen sind.** Begruendung: Das Prozessband wird dann in 17
weiteren Masken behaupten, den Prozessstand zu zeigen, waehrend die wichtigste
Auskunft eines gestoerten Vorgangs — warum er steht — nur im Leitstand zu haben
ist. Das ist genau die Verletzung, die Ebene 1 verhindern soll.

**Empfohlene Reihenfolge:**

1. **F2 sofort** — einzeilig: `lifecycleSummary` braucht einen `on_hold`-Zweig.
   Eine falsche Aussage ist schlimmer als eine fehlende.
2. **F1 mit FSX-001** — die Herkunftskarte hat die Quelle bereits gefunden:
   `reason_category`/`reason_code`/`reason_note` des juengsten Knotenereignisses
   gehoeren in `detail_rows`. Dann steht der Grund am Knoten statt in der Timeline.
3. **F3 danach** — sobald der Grund am Knoten liegt, kann das Band ihn als
   Blocker zeigen, und K3 ist erfuellt.
4. **F4** vor dem Rollout in Waage-Masken pruefen.
5. **F5** zurueckstellen — die Alternative waere wieder ein Platzhalter.

**Erst danach FSX-090b mit echten Nutzern.** Diese Begehung ersetzt sie nicht;
sie verhindert nur, dass echte Nutzer ihre Zeit an Fehlern verbrauchen, die eine
Inspektion findet.
