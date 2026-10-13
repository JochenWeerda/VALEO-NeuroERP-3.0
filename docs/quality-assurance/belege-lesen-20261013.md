# BELEG-011: Lesender Belegweg

Stand: 2026-10-13 · Slice `BELEG-011` · aus dem
[Masterplan Belegmaske mit Varianten](../design/belegmaske-varianten-masterplan.md) ·
Folge aus [Belegvertrag](belegvertrag-20261013.md)

## Geliefert

`GET /api/v1/belege/{belegart}/{beleg_id}` liefert einen DocFlow-Beleg in der Form des Belegvertrags:
Kopf, Partner, Positionen mit übernommener und offener Menge, Summen je Steuerschlüssel, Buchungsstand,
Belegkette in beide Richtungen mit Mengen, Statushistorie und die Aktionen, die im Zustand des Belegs
möglich sind.

- **Mandant aus der geprüften Anmeldung**, Anmeldung Pflicht. Ein Beleg eines anderen Mandanten oder
  einer anderen Belegart unter der Adresse ist 404.
- **Der Weg schreibt nichts.** Anders als `GET /docflow/{id}` zieht er keine Kopie aus den Tabellen
  des Verkaufs nach.
- **Lieferschein und Wareneingang kommen ohne Preise:** Preisfelder und Summen werden nicht
  ausgeliefert.
- **Buchungsstand** `nicht_gebucht`, `gebucht` (mit Journalbezug), `storniert` (neu im Vertrag) oder
  `pruefen` mit Grund. Der Grund kommt aus derselben Prüfung von Finance, die auch das Buchen benutzt
  — der Adapter (`app/services/docflow_belegadapter.py`) entscheidet nichts selbst. Ein Beleg, der auf
  „gebucht" steht, aber keinen Buchungsnachweis hat, steht auf `pruefen`.
- **Aktionen** tragen das Kommando dahinter (`docflow.update`, `.release`, `.post`, `.convert`,
  `.reverse`) und, wenn gesperrt, den Grund: Rechnung ohne Steuerschlüssel nicht buchbar; Auftrag mit
  Lieferungen nicht direkt berechenbar; gebuchte Gutschrift nicht stornierbar; alle Mengen übernommen.

## Nachweis

- `tests/test_belege_lesen.py`: 10 bestanden gegen `valeo_probe`, an den 17 Referenzbelegen — jeder
  kommt vertragsgerecht (`pruefe` ohne Befund), mit Historie und Akteur; gebuchte Rechnung mit Journal,
  Kette und zwei Steuergruppen; Lieferschein und Wareneingang ohne Preisfelder; Belege ohne
  Steuerschlüssel auf `pruefen`, Buchen gesperrt mit demselben Grund; offene Rechnungen buchbar;
  stornierte Belege bieten nichts mehr an; Auftrag und Bestellung mit zwei Teillieferungen nicht
  direkt berechenbar, Mengen gehen auf; 404 bei falscher Belegart, fremdem Mandanten, Unbekanntem;
  Lesen ändert keine Zeile.
- `tests/test_belegvertrag.py`: 27 bestanden.
- Architektur-Index, Pagination, tote Transaktionen, Baseline-Integrität: in Ordnung. OpenAPI und
  Inventare nachgezogen.

## Auslegungen (meine, nicht entschieden)

- **„Buchen" wird nur für Belegarten angeboten, die Finance bucht.** DocFlow lässt `post` auch für
  Auftrag oder Lieferschein zu und setzt dann nur den Status; der Belegweg bietet das nicht an.
- **Übernommene Menge** eines Auftrags ist der größere der beiden Wege (Lieferung oder direkte
  Rechnung), weil nur einer von beiden benutzt werden darf.
- **Buchen und Stornieren tragen `freigabe_noetig`.** Das ist eine Angabe für Maske und Agent, noch
  keine durchgesetzte Freigabe.

## Grenzen

- **Kein Recht des Lesers eingerechnet:** Jeder angemeldete Benutzer des Mandanten liest jeden Beleg
  mit Preisen, und die Aktionen sagen, was im Zustand geht, nicht, was der Leser darf (BELEG-012).
- **Partnername fehlt** — DocFlow führt nur die Nummer. Die Referenzbelege benutzen Platzhalter.
- **Dokumente** (Anhänge) sind leer; die Anbindung an die Ablage fehlt.
- **Kassenbelege** haben keine Variante und sind hier nicht lesbar; ein Kassenbeleg als Vorgänger
  einer Rechnung erschiene in der Kette mit einer Belegart außerhalb des Vertrags.
- **Nur DocFlow.** Aufträge und Lieferscheine, die nur in den Tabellen des Verkaufs stehen, liefert
  der Weg nicht (Entscheidung E2 im Masterplan).
- **Keine Liste, keine Suche** — folgt mit den lesenden MCP-Werkzeugen.
- Noch liest keine Maske über diesen Weg.
