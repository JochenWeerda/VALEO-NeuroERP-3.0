# BELEG-010: Belegvertrag

Stand: 2026-10-13 · Slice `BELEG-010` · aus dem
[Masterplan Belegmaske mit Varianten](../design/belegmaske-varianten-masterplan.md)

## Auftrag

Eine Belegmaske mit Varianten statt einer Maske je Belegschritt. Dafür braucht es eine Form, in der die
Maske jeden Beleg liest — unabhängig davon, welche Domäne ihn führt.

## Geliefert

- **Die Form** (`app/core/belegvertrag.py`, Modell `Beleg`): Kopf, Partner, Positionen, Summen,
  Buchungsstand, Belegkette, Dokumente, Historie, erlaubte Aktionen. Unbekannte Felder werden abgelehnt.
- **Neun Varianten** (`BELEGARTEN`): Bezeichnung, Partnerrolle, Steuerrichtung, mit oder ohne Preise,
  ob Finance bucht, Folgebelege. Lieferschein und Wareneingang sind ohne Preise.
- **Prüfung** `pruefe(beleg)`: nennt jeden Verstoß eines Belegs gegen seine Variante.
- **Preise:** `ohne_preise(beleg)` entfernt Preisfelder und Summen. Ein Beleg ohne Preisrecht, der die
  Felder trotzdem trägt, ist ein Vertragsverstoß — Ausblenden genügt nicht.
- **Abbildung** (`ABBILDUNG`): 64 Kopffelder und 45 Positionsspalten der fünf vorhandenen
  Beleg-ScreenDefinitions, jedes mit seinem Platz im Vertrag oder in einem der zwölf Bausteine
  (Lieferung, Zahlung, Lager, Kontrakt …).
- **Erzeugt:** `docs/schnittstellen/contracts/belegvertrag.schema.json` und
  `docs/schnittstellen/belegvertrag.md` über `scripts/generate_belegvertrag.py [--check]`.

## Was die Tests festhalten

`tests/test_belegvertrag.py`, 27 bestanden (ohne Datenbank):

- Jede DocFlow-Belegart außer der Kasse hat eine Variante; Folgebelege und Steuerrichtung der Variante
  sind die von DocFlow. Ändert DocFlow einen Übergang, wird der Test rot.
- Die Abbildung deckt Kopf und Positionen der fünf ScreenDefinitions **genau**: Ein neues Feld ohne
  Platz im Vertrag macht den Test rot, ein Eintrag für ein entferntes Feld ebenso.
- Jedes Ziel der Abbildung gibt es im Vertrag.
- Summen müssen auf den Cent zu den Positionen passen; gebucht braucht einen Journalbezug, ein
  Prüfvermerk einen Grund; ein Auftrag kann nicht „gebucht" sein.
- Kette und Aktionen dürfen nur Belegarten nennen, die die Variante zulässt; eine gesperrte Aktion
  nennt ihren Grund.
- Schema und Übersicht sind aktuell.

## Auslegungen (meine, nicht entschieden)

- **Lieferschein und Wareneingang tragen im Vertrag keine Preise**, auch wenn DocFlow sie in der
  Position mitführt (für die spätere Rechnung). Die einfachste Regel, die zum Beispiel des
  Auftraggebers passt („mal mit Preisen, mal nur Mengenangabe"). Ein bewerteter Wareneingang wäre eine
  eigene Variante.
- **Kassenbelege** (`pos_receipt`, `pos_storno`, `pos_retoure`) haben keine Variante: Die Kasse hat
  eine eigene Oberfläche.
- **`line_total` des Auftrags und `betrag` der Bestellung** sind als Netto der Position abgebildet. An
  den Daten nicht nachgemessen.
- **Fälligkeit und Zahlungsbedingung** stehen im Baustein `zahlung`, nicht im Grundgerüst: Der
  DocFlow-Kopf kennt beides noch nicht.

## Nicht Teil dieses Slices

- Kein Lieferweg: Noch liefert keine Domäne Belege in dieser Form (BELEG-011).
- Kein Preisrecht an der API (BELEG-012); der Vertrag sagt nur, was dann fehlen muss.
- Die Abbildung erfasst Kopf und Positionen. Die übrigen Reiter der fünf Definitionen (Lieferung,
  Zahlung, Bestellfall, Kommunikation, Steuertabelle) sind den Bausteinen noch nicht feldweise
  zugeordnet.
- Wiegeschein, Frachtbrief und Kontrakt haben noch keine Variante.
