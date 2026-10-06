# Ein Platzhalter darf den Mount-Fetch nicht verhindern (Slice FRONTEND-INITIALDATA-MOUNTFETCH-20261006)

Stand: 2026-10-06 · Welle 2, Slice 24

## Anlass

Dieser Fehler ist nicht gefunden, sondern **gemeldet** worden. Am 17.07.2026 schrieb
der Nutzer:

> „Ackerschlagkartei zeigte initial weder Schläge noch Maßnahmen — erst nach einer
> Mutation erschienen die Seed-Daten."

Die Ursache steht seit damals im Regressionstest
`src/__tests__/lib/portal-feldbuch-hooks.test.tsx`:

> `initialData: []` + `staleTime` ließ React Query die leere Liste als frische Daten
> werten, der Mount-Fetch entfiel.

`initialData` schreibt den Platzhalter in den Cache, **als wäre er vom Server
gekommen**. Mit `staleTime: 2 * 60 * 1000` gilt er zwei Minuten als frisch — die
Abfrage fragt in dieser Zeit **gar nicht**. Die Maske zeigt „keine Einträge", und
niemand sieht, dass nie gefragt wurde. Das ist derselbe Fehlertyp wie `except:
return []` im Backend: Ein Fehlen sieht aus wie ein geordneter leerer Stand.

Behoben wurde es damals für **zwei** Hooks. **199 weitere Stellen** in 40 Dateien
trugen denselben Fehler weiter; sieben Stellen hatten die Gegenmaßnahme schon — der
Weg war also im Haus bekannt und nur nicht gegangen.

## Was dieser Slice tut

Jede `initialData`-Option in einem `useQuery`-artigen Aufruf hat jetzt
`initialDataUpdatedAt: 0` daneben. Der Platzhalter ist damit **sofort veraltet**, der
Mount-Fetch findet statt, und die Form der Daten bleibt unverändert: kein Aufrufer
bricht, keine Typänderung (`tsc --noEmit` ohne einen einzigen neuen Fehler).

Betroffen war unter anderem die Fabrik `makeHook` in `lib/api/betrieb.ts`, hinter der
allein über zwanzig Hooks stehen — sie setzte `initialData: fallback` **und**
`staleTime: 2 Minuten`.

### Ein Fehler im ersten Entwurf des Werkzeugs

Mein Umschreibe-Skript suchte `queryKey`/`queryFn` in den **40 Zeilen oberhalb** der
Option, um Abfrage-Optionen von gleichnamigen Komponenten-Eigenschaften zu
unterscheiden. `useSalesDashboard` hat einen langen `queryFn`-Rumpf (drei Aufrufe in
`Promise.allSettled`); `queryKey` stand **43** Zeilen darüber. Die Option wurde
übergangen, der Hook blieb kaputt — und zwar still: Die Zahl der geänderten Stellen
sah richtig aus.

Aufgefallen ist es nur, weil ein Vertrag genau diesen Hook prüft. Das Skript bestimmt
jetzt den **umgebenden Aufruf** (rückwärts bis `useQuery(`, abgebrochen bei
`useMutation(`) statt mit einem Zeilenfenster zu raten. Lehre: Ein Fenster ist keine
Struktur.

## Die Ratsche

`scripts/check_initial_data.py`:

1. **Jede** `initialData`-Option in einer Abfrage muss `initialDataUpdatedAt: 0` im
   selben Aufruf tragen. Ein Verstoß ist ein **Fehler**, keine Zahl — dieser Fehler
   hat einmal einen Nutzer gekostet.
2. Die **Gesamtzahl** der `initialData`-Stellen ist down-only (205, einschließlich
   der Testdateien). Das Ziel ist `placeholderData`; die Zahl hält den Weg offen,
   damit er nicht versandet.

```
python scripts/check_initial_data.py
→ initialData: 205 Stellen (Schwelle 205), 0 ohne initialDataUpdatedAt: 0
→ OK: kein Platzhalter verdeckt einen fehlenden Mount-Fetch.
```

## Was dieser Slice **nicht** tut

**Die Umstellung auf `placeholderData`.** Das ist das richtige Ziel: Es schreibt den
Cache nicht an und markiert sich über `isPlaceholderData` selbst als Platzhalter.
Aber es macht `data` im Fehlerfall `undefined` und ist damit **je Aufrufer** eine
eigene, zu prüfende Änderung. 205 Stellen in einem Zug umzustellen wäre ein Umbau
ohne Einzelnachweis. Die Ratsche hält die Zahl fest.

**Die zweite Hälfte des Fehlers bleibt:** Im **Fehlerfall** steht der Platzhalter
weiter sichtbar da, weil er im Cache liegt. `isError` ist wahr, aber eine Maske, die
`isError` nicht liest, zeigt weiterhin eine Attrappe. Ein Vertrag hält das
ausdrücklich fest (`ein Fehlschlag bleibt ein Fehlschlag`), damit es nicht als
behoben gilt.

## Nachweis

```
npx vitest run src/__tests__/lib/initialdata-mountfetch.test.tsx \
               src/__tests__/lib/portal-feldbuch-hooks.test.tsx
  → 8 passed (2 Dateien)
npx tsc --noEmit                → 0 Fehler
npx eslint <die 40 Dateien>     → 0 Fehler
python scripts/check_initial_data.py → grün
```

Die sechs neuen Verträge zeigen an Hooks aus fünf Fächern (`schaeden`, `betrieb` über
`makeHook`, `portal`, `crm`, `dashboard`), dass beim Mount **trotz** `staleTime`
geladen wird und die Serverdaten den Platzhalter ersetzen — plus den Vertrag über die
noch offene zweite Hälfte. Kein Backend nötig: `apiClient` ist gemockt.

Die vier Backend-Ratschen ohne Datenbankbedarf (Pagination, Baseline-Integrität, tote
Transaktionen, Godfiles) sind grün.

## Was beim Lesen noch auffiel (nicht Teil dieses Slices)

* **`Promise.allSettled` als Fehlerschlucker.** `useSalesDashboard` fragt drei
  Berichte parallel und setzt bei Fehlschlag `0` bzw. `[]`. Ein Umsatz von 0 €, der
  in Wahrheit ein Verbindungsfehler ist, ist dieselbe Lüge wie der Platzhalter —
  nur eine Ebene tiefer. Gilt auch für mehrere Dashboard-Hooks.
* **`catch { return [] }` mit Begründung** in `lib/api/sales.ts` („Bewusst still: Die
  Liste ist eine Uebersicht, kein Vorgang"). Begründet und damit regelkonform, aber
  die Begründung trägt nur, solange die Maske nicht Zahlen daraus bildet.

Beides gehört in einen eigenen Slice zur Fehlersichtbarkeit in den Masken.

## Offene Punkte (Handshake)

1. **Die Ratsche ist nicht in CI verdrahtet.**
   `.github/workflows/quality-gate.yml` ist derzeit von Codex geclaimt
   (Tabellenkatalog-Drift-Evidenz); ich habe die Datei nicht angefasst. Der Eintrag
   gehört in denselben Backend-Schritt wie die anderen Ratschen und ist ein
   Einzeiler.
2. **`placeholderData`** als Zielbild — je Fach ein Slice, die Ratsche zählt mit.
3. **`isError` in den Masken** — die zweite Hälfte des Fehlers, siehe oben.
