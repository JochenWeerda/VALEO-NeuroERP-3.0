# BELEG-020: Eine Belegmaske, neun Varianten

Stand: 2026-10-13 · Slice `BELEG-020` (Teil 1: Definition und Lesewege) · aus dem
[Masterplan Belegmaske mit Varianten](../design/belegmaske-varianten-masterplan.md) ·
Folge aus [Belegvertrag](belegvertrag-20261013.md), [Lesender Belegweg](belege-lesen-20261013.md),
[Rechte an Belegen](beleg-rechte-20261013.md)

## Auftrag

Entscheidung des Auftraggebers vom 13.10.2026: Für jeden Schritt einer Belegfolge keine eigene Maske,
sondern die Variante einer Belegmaske — mal mit Preisen, mal nur mit Mengen.

## Geliefert

- **Eine Quelle:** `app/core/screen_definitions_beleg.py`, `build_beleg_screen_definition(belegart)`.
  Aus einem Grundgerüst und der Variante des Belegvertrags entsteht die ScreenDefinition
  `beleg/<belegart>` — für alle neun Belegarten. Es gibt keine ausgeschriebene Definition je Belegart.
- **Was die Variante bestimmt:** Titel und Beschriftungen (Rechnung Nr. / Kunde / Umsatzsteuer gegen
  Eingangsrechnung Nr. / Lieferant / Vorsteuer), Preisspalten und Summenfelder nur mit Preisen,
  Aufwandskonto nur im Einkauf, offene Menge nur mit Folgebeleg, Buchungsstand nur, wo Finance bucht.
- **Was gleich bleibt:** fünf Reiter (Kopf, Positionen, Belegkette, Dokumente, Verlauf) und die Spalten
  von Kette, Dokumenten und Verlauf.
- **Aktionen aus dem Verzeichnis der Belegkommandos:** Adresse, Methode, Recht und Gefahrenstufe; ab
  R3 mit Bestätigung. Genau eine Hauptaktion je Variante: der nächste Schritt der Belegfolge.
- **Die Variante als Begriff der Definition** (`variant`: Belegart, Partnerrolle, mit Preisen, bucht,
  Folgebelege).
- **Lesewege für die Maske**, aus dem Belegvertrag, mit denselben Rechten:
  `GET /api/v1/belege/{belegart}/{id}/kopf` (flache Kopffelder, dazu die Aktionen des Belegs) und
  `GET …/tabs/{positionen|kette|dokumente|historie}` (Seiten in der Form der Mask-Engine).

## Nachweis

`tests/test_beleg_screen_definition.py`, 24 bestanden gegen `valeo_probe`:

- Jede der neun Varianten besteht die Regeln der Masken (`governance_errors`, `ux_lint` ohne Befund).
- Preise nur in Varianten mit Preisen; der Lieferschein hat genau die sieben Mengenspalten.
- Aktionen stimmen mit Verzeichnis und Variante überein.
- **Die Definition verspricht nichts, was der Weg nicht liefert:** Für alle 17 Referenzbelege antwortet
  jede Datenquelle, und jedes Kopffeld und jede Spalte der Definition ist in der Antwort.
- Kopf und Reiter gelten dieselben Rechte wie der Beleg: 403 ohne Rolle, das Lager ohne jeden Betrag.
- Kette lesbar beschriftet, Blättern stimmt.

## Was noch nicht gilt

- **Die Maske ist nicht sichtbar.** Die neun Definitionen sind nicht in der Registry der Masken
  eingetragen; es gibt keine Route, keinen Navigationspunkt und keinen Aufruf im Frontend. Der Eintrag
  zieht Aktionskatalog, MCP-Aktionskarte, Agenten-Handbuch, Synonyme und Routen nach und gehört mit der
  Sichtprüfung im Browser zusammen (Entscheidung E4: keine Maskenmigration ohne sie).
- **Die Maske führt noch keine Aktion aus.** Die Definition nennt die Kommandos; dass die Mask-Engine
  sie mit Idempotenzschlüssel, Version und Mengenangabe aufruft und den Zustand aus `aktionen`
  übernimmt, ist nicht gebaut.
- **Erfassen und Bearbeiten** eines Belegs in der Maske fehlt; die Variante ist lesend.
- **Bausteine** (Lieferung, Zahlung, Lager …) hängt noch keine Variante ein.
- Das Recht `belege.<recht>` der Aktionen ist ein Name der Definition; das Frontend kennt ihn nicht.
