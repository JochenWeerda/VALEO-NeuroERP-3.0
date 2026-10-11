# Einzelmaske Mahnwesen abgelöst

Stand: 2026-10-11 · Slice `MAHNWESEN-EINZELMASKE-ABLOESEN-20261011` · offener Punkt 1 aus
[Versandwege](versandwege-echt-20261008.md)

## Entscheidung

Vorgabe des Auftraggebers: „Was nicht einfach läuft, läuft einfach nicht."

Die Einzelmaske `/finance/mahnwesen` wird **abgelöst, nicht angeschlossen**. `/finance/mahnwesen` und
`/finance/dunning` zeigen jetzt den Mahnlauf (`pages/finance/mahnlauf.tsx`).

## Warum nicht anschließen

Die Maske sah aus wie ein Arbeitsplatz und war keiner:

| Was sie zeigte | Was dahinter war |
|---|---|
| Debitor zur Auswahl | drei fest eingetragene Namen (K001 Müller GmbH, K002 Schmidt KG, K003 Bauer e.K.) |
| Mahnung bearbeiten | geladen wurde immer `id: 'new'` – nie eine bestehende Mahnung |
| Speichern | sendete `opId`, `debitorId`, `mahnstufe`, `text` … an `POST /dunning`; der Weg kennt diese Felder nicht |
| Senden, Zahlung buchen | verlangten eine gespeicherte Mahnung, die es so nie gab |
| Mahnung generieren | schickte das Formular an `POST /dunning/run` |

Anschließen hieße: Debitorenwahl aus den Stammdaten, Feldzuordnung, Laden einer Bestandsmahnung –
ein zweiter Weg zu dem, was der Mahnlauf schon kann. Eine Mahnung entsteht aus einem überfälligen
offenen Posten, nicht aus einem leeren Formular. Der Mahnlauf zeigt die Kandidaten, erzeugt die
Mahnungen mit Gebühr, Zinsen und Frist und versendet sie je Zeile per E-Mail oder vermerkt den
Postversand.

## Was sich für Anwender ändert

- *Finanzen → Mahnwesen*, die Suche („Mahnwesen"), der Knopf „Mahnlauf starten" in den Offenen Posten
  und der Verweis aus dem Kontrakt führen auf den Mahnlauf. Kein Link wurde ungültig.
- Es gibt die Maske mit den erfundenen Debitoren nicht mehr.

## Was entfällt, ohne Ersatz

- Die Aktion **„PDF-Export"** (`POST /finance/followup/mahnwesen/export`) und die **„Vorschau"** als
  Meldung. Beide hingen an der Einzelmaske. Das Mahnschreiben als PDF ist ohnehin ein offener Punkt.
- **„Zahlung buchen"** an der Mahnung. Der Weg `PUT /dunning/{id}/paid` besteht weiter; in der Maske
  war er nie erreichbar, weil keine Mahnung geladen wurde. Zahlungen laufen über den Zahlungseingang.

## Geändert

- `pages/finance/mahnwesen.tsx` entfernt (560 Zeilen).
- `route-aliases.json` und die zwei Gruppeneinträge: `finance/mahnwesen` und `finance/dunning` →
  `@/pages/finance/mahnlauf`; Routendateien neu erzeugt (939 Routen, Routing-Prüfung grün).
- `dispo-copilot-uix.test.ts`: Der Test, der den Quelltext der alten Seite las, hält jetzt fest, dass
  beide Wege zum Mahnlauf führen und die alte Seite nicht zurückkommt.

Nicht angefasst: `offene-posten.tsx` und `FrmKontraktDetail.tsx` (fremde Änderungen im Arbeitsbaum).
Ihre Links bleiben über die Route gültig.

## Offen

1. **Dritter Mahnlauf:** `pages/mahnwesen/mahnlauf.tsx` (Weg `/mahnwesen/mahnlauf`) ist ein eigener,
   an `/finance/mahnlauf/*` angeschlossener Ablauf ohne Eintrag in der Navigation. Zwei Mahnläufe
   nebeneinander sind einer zu viel; welcher bleibt, ist nicht entschieden.
2. **Benutzerhandbuch:** `docs/benutzerhandbuch/finanzbuchhaltung.md` nennt für beide Wege noch das alte
   Modul und zeigt das Bild der alten Maske. Es wird mit Bildschirmfotos erzeugt und ist hier nicht neu
   erzeugt worden.
3. **Mahnschreiben als PDF** bleibt offen.
