# Ein Mahnlauf

Stand: 2026-10-11 · Slice `EIN-MAHNLAUF-20261011` · offener Punkt aus
[Einzelmaske Mahnwesen abgelöst](mahnwesen-einzelmaske-abloesen-20261011.md)

## Befund

Zwei Mahnlauf-Seiten am selben Backend (`/finance/mahnlauf/*`), jede mit einer Hälfte:

| Seite | Weg | kann | kann nicht |
|---|---|---|---|
| `pages/finance/mahnlauf.tsx` | Navigation *Finanzen → Mahnlauf* | Mahnungen versenden | einen Posten auslassen |
| `pages/mahnwesen/mahnlauf.tsx` | `/mahnwesen/mahnlauf`, kein Navigationseintrag | Posten auswählen | versenden |

Dazu zwei Fehler im Ablauf:

- **Bediener aus dem Rumpf.** Die zweite Seite sendete `bediener: 'Portal'`; ohne Angabe schrieb das
  Backend „KIM" in den Vermerk der Mahnung. Wer den Lauf ausgeführt hat, stand nirgends.
- **Leere Auswahl = Gesamtlauf.** `rechnungsnrn: []` fiel im Backend auf „alle überfälligen Posten"
  zurück. Wer alles abwählte und trotzdem auslöste, hätte alle gemahnt.

## Entscheidung

Vorgabe des Auftraggebers: „Was nicht einfach läuft, läuft einfach nicht."

**Es gibt einen Mahnlauf.** Die Seite in der Navigation bekommt die Auswahl, die zweite entfällt;
`/mahnwesen/mahnlauf` zeigt die eine Seite.

- Jeder Kandidat ist **vorgewählt**. Der Normalfall – alles mahnen – bleibt ein Klick.
- Wer einen Posten auslässt (Zahlung zugesagt, Reklamation offen), nimmt den Haken heraus. Der Knopf
  zeigt „3 von 4".
- Ohne Abwahl läuft der Gesamtlauf wie bisher; mit Abwahl gehen genau die gewählten Rechnungen.
- Nach dem Lauf ist wieder alles vorgewählt.
- **Wer mahnt, sagt die Anmeldung** (`anmeldename()`), wie in den übrigen Modulen. Das Feld `bediener`
  bleibt im Eingabemodell erlaubt und wird nicht gelesen.
- Eine leere Auswahl mahnt niemanden.

Ein Posten ohne Rechnungsnummer lässt sich nicht einzeln ansprechen (der Weg kennt nur
Rechnungsnummern). Sein Haken ist fest gesetzt; in einer Teilmenge läuft er nicht mit, und die
Abschlussmeldung sagt das. Bleibt nach der Abwahl nur ein solcher Posten übrig, startet nichts.

## Geändert

- `app/api/v1/endpoints/finance_dunning.py` (`run`): Bediener aus der Anmeldung; leere Auswahl ist leer.
- `pages/finance/mahnlauf.tsx`: Spalte „Mahnen" mit Haken je Kandidat, Zähler im Knopf.
- `lib/api/finance-dunning.ts`: `useRunDunning` nimmt `rechnungsnrn`.
- `pages/mahnwesen/mahnlauf.tsx` entfernt (202 Zeilen); Route und Gruppeneintrag zeigen auf
  `@/pages/finance/mahnlauf`, Routendateien neu erzeugt.

## Nachweis

- Backend `tests/test_finance_dunning_run_subset.py`: Anmeldung statt Rumpf (Teilmenge und Einzelposten),
  leere Auswahl mahnt niemanden, ohne Auswahl Gesamtlauf, ohne Anmeldung kein Lauf.
- Frontend `mahnlauf-auswahl.test.tsx`: Vorwahl und Gesamtlauf, Teilmenge, kein `bediener` im Rumpf,
  alles abgewählt startet nichts, Posten ohne Rechnungsnummer, Vorwahl nach dem Lauf, alle vier Wege
  führen auf dieselbe Seite.

## Offen

1. **Rollen:** Die Wege unter `/finance/mahnlauf/*` verlangen eine Anmeldung, aber keine Rolle. Wer
   angemeldet ist, kann einen Mahnlauf auslösen. Erledigt am 11.10.2026:
   [mahnwesen-rollen-20261011.md](mahnwesen-rollen-20261011.md).
2. **Teilmenge in mehreren Schritten:** Bei einer Teilmenge läuft der Dienst je Rechnung einzeln.
   Scheitert einer mittendrin, sind die vorherigen Mahnungen erzeugt.
3. **Benutzerhandbuch** nennt `/mahnwesen/mahnlauf` noch mit dem alten Modul und Bild.
