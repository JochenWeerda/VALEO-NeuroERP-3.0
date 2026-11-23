# Abnahmeblatt Verkauf (Angebot bis Rechnung)

Erzeugt mit `python scripts/domaenen_abnahme.py` aus [`verkauf.yaml`](verkauf.yaml); nicht von Hand bearbeiten.

- Reifematrix: D01; L3-Referenz: `l3-vertrieb-referenz`
- Prozesse: 10 — abgenommen 0, teilweise 9, fehlt 1; hoechste offene Luecke: P1
- Erhoben: 2026-11-23 von Cursor

## Prozessliste (L3-Referenz)

| ID | Prozess | L3 | VALEO-Maske | Rolle | Nachweis | Status |
|---|---|---|---|---|---|---|
| VK-01 | Angebot erfassen und in Auftrag umwandeln | ERFASSUNG > Verkauf > Angebot (gelber Kopf, Positionen mit Detailzeile, Summen) | `sales/angebote` (studio_versioniert)<br>`sales/angebot/neu` (studio_versioniert)<br>`sales/angebot/:id` (studio_versioniert) | VERKAUF (beleg_write); Preise nur mit Preisrecht | `tests/test_docflow_partial_conversion_postgres.py`<br>`tests/test_docflow_conversion_options_http.py`<br>`tests/test_beleg_rechte.py` | teilweise |
| VK-02 | Auftrag erfassen und bestaetigen | ERFASSUNG > Verkauf > Auftrag (F5), Kreditlimit im Kopf, LS/Rechnung direkt aus dem Auftrag | `sales/auftraege` (studio_versioniert)<br>`sales/orders/new` (studio_versioniert)<br>`sales/sales-order/:id` (studio_versioniert) | VERKAUF (beleg_write) | `tests/test_docflow_auftragsbestaetigung.py`<br>`tests/test_docflow_auftraege_uebernahme.py`<br>`tests/test_rls_domain_sales.py` | teilweise |
| VK-03 | Lieferschein erfassen, kommissionieren und ausbuchen | ERFASSUNG > Verkauf > Lieferschein (F6), Charge, Selbstabholung, "wie vorheriger LS" (F11) | `sales/lieferungen` (studio_versioniert)<br>`sales/lieferungen/neu` (studio_versioniert)<br>`sales/delivery-note/:id` (studio_versioniert)<br>`verkauf/lieferschein-erfassung` (studio_versioniert) | VERKAUF und LAGER (Lager ohne Preise) | `tests/test_lieferschein_pickliste_docflow.py`<br>`tests/test_docflow_teilmengen_statushistorie.py`<br>`tests/test_beleg_rechte.py` | teilweise |
| VK-04 | Sofort-Rechnung aus dem Lieferschein | Lieferschein > Sofort-Rechnung | `sales/rechnungen` (studio_versioniert)<br>`sales/invoices/new` (studio_versioniert)<br>`verkauf/rechnung/:id` (studio_versioniert) | VERKAUF; Buchen Sachbearbeitung, Storno Buchhaltung/Bereichsleitung | `tests/test_mcp_rechnung_aus_docflow_lieferschein.py`<br>`tests/test_docflow_teilmengen_statushistorie.py::test_teilrechnungen_aus_dem_lieferschein_bis_zur_gelieferten_menge`<br>`tests/test_beleg_aktionen.py` | teilweise |
| VK-05 | Fakturierung (Sammelrechnungslauf ueber gelieferte Lieferscheine) | ABRECHNUNG > Faktur > Verkauf (F8) — Auswahl nach Niederlassung, Zeitraum, Kunde; Aufbereiten, Kontrolle, Druck | — | VERKAUF / Fakturierung | — | fehlt |
| VK-06 | Rechnungsausgangsbuch | DATEI > Hauptmodule > Rechnungsausgangsbuch (F9) — Filter, Storno anzeigen, Uebergabe Fibu, EUR/sFr | `sales/rechnungen` (studio_versioniert)<br>`verkauf/rechnungen` (studio_versioniert) | VERKAUF lesen; Buchhaltung | `tests/test_beleg_erechnung.py`<br>`tests/test_docflow_gobd.py` | teilweise |
| VK-07 | Verkaufsgutschrift | Lieferschein "Gutschrift kennzeichnen"; Rechnungsausgangsbuch Korrektur | `sales/credit-notes` (studio_versioniert)<br>`sales/credit-note-editor` (studio_versioniert) | VERKAUF; Buchen Sachbearbeitung | `tests/test_gutschrift_umsatzsteuer.py`<br>`tests/test_beleg_aktionen.py::test_die_gutschrift_mit_bezugsrechnung_bucht_die_sachbearbeitung` | teilweise |
| VK-08 | Storno von Rechnung und Lieferung | Rechnungsausgangsbuch > Stornieren; LS loeschen | `sales/lieferung-storno` (studio_versioniert, **Platzhalter**)<br>`sales/rechnungen` (studio_versioniert) | Storno gebuchter Belege nur Buchhaltung/Bereichsleitung, mit Grund | `tests/test_beleg_aktionen.py::test_storno_aus_der_maske_braucht_einen_grund_und_das_recht`<br>`tests/test_docflow_teilmengen_statushistorie.py::test_stornierte_rechnung_gibt_ihre_menge_wieder_frei`<br>`tests/test_beleg_rechte.py::test_gebuchtes_storniert_nur_buchhaltung_und_bereichsleitung` | teilweise |
| VK-09 | Kreditlimit pruefen | Auftrag/Lieferschein-Kopf Kredit-Limit | `sales/kreditlimit-pruefung` (studio_versioniert) | VERKAUF lesen | `tests/test_sales_credit.py` | teilweise |
| VK-10 | Unerledigte Auftragspositionen (Rueckstand) | Auftrag offen/teilgeliefert | `verkauf/unerledigte-auftrags-positionen` (studio_versioniert, **Platzhalter**) | VERKAUF lesen | `tests/test_docflow_teilmengen_statushistorie.py::test_ein_auftrag_drei_teillieferscheine_dann_ist_schluss` | teilweise |

## Befunde je Prozess

- **VK-01 Angebot erfassen und in Auftrag umwandeln:** Angebot ist DocFlow-Beleg der Familie beleg (Variante sales_offer); Umwandlung mit Teilmengen, Wiederholung und Mandantengrenze gegen PostgreSQL/RLS geprueft, Rechte je Bereich geprueft. Im Browser nur Ladetest (playwright-tests/specs/sales/angebote-smoke.spec.ts), keine Umwandlung durch die Maske.
- **VK-02 Auftrag erfassen und bestaetigen:** Auftrag und Auftragsbestaetigung (Stand confirmed) laufen ueber DocFlow, Bestaetigen auch ueber die Maske (test_belegaktion_bestaetigen_ueber_die_maske). Kreditlimit wird geprueft (VK-09). Browser: nur Ladetest des Editors (order-flow.spec.ts).
- **VK-03 Lieferschein erfassen, kommissionieren und ausbuchen:** Teillieferscheine bis zur Auftragsmenge, Ueberlieferung abgewiesen, Lagerabgang genau einmal ueber die Pickliste, Lager sieht keine Preise. Nicht belegt: L3-Spalten zur Rueckverfolgung (Charge, Serie, Gefahrgutpunkte, Bio) in den Lieferscheinpositionen und "wie vorheriger LS".
- **VK-04 Sofort-Rechnung aus dem Lieferschein:** Rechnung entsteht als DocFlow-Folgebeleg aus dem Lieferschein (Maske und MCP denselben Weg), Teilrechnungen bis zur gelieferten Menge, Folgebeleg genau einmal. Browserkette fehlt.
- **VK-05 Fakturierung (Sammelrechnungslauf ueber gelieferte Lieferscheine):** Kein Sammellauf: keine Route, kein Endpunkt fuer die Auswahl offener Lieferscheine je Zeitraum/Kunde und Erzeugung aller Rechnungen. Rechnungen entstehen nur einzeln aus dem Lieferschein (VK-04). Im L3-Betrieb ist das der regulaere Weg zur Ausgangsrechnung.
- **VK-06 Rechnungsausgangsbuch:** Rechnungsliste ist die Belegliste der Familie (beleg-liste/sales-invoice). XRechnung aus dem gebuchten Beleg ins GoBD-Archiv geprueft. Nicht belegt: Spalten Fibu-Uebergabe, Storno-Filter und Summen je Waehrung wie im L3-Ausgangsbuch.
- **VK-07 Verkaufsgutschrift:** Umsatzsteuer je Position ueber Steuerschluessel, Erloes netto, Forderung brutto, Reverse Charge nicht automatisch, doppelte Nummer abgewiesen; MCP-Trockenlauf schreibt nichts. Browserkette fehlt.
- **VK-08 Storno von Rechnung und Lieferung:** Storno aus der Belegmaske verlangt Grund und Recht, stornierte Rechnung gibt die Menge frei, Statushistorie unveraenderlich. Die Route sales/lieferung-storno ist gesondert zu pruefen (siehe Maskenabnahme).
- **VK-09 Kreditlimit pruefen:** Pruefregel rein getestet (kein Limit, Warnung ab 80 %, Sperre ab 100 %, verfuegbarer Rahmen). Nicht belegt: Wirkung der Sperre beim Freigeben eines Auftrags gegen die Datenbank.
- **VK-10 Unerledigte Auftragspositionen (Rueckstand):** Restmengen je Position fuehrt DocFlow (Teillieferscheine bis zur Auftragsmenge). Die Rueckstandsliste ist eine generische Platzhaltermaske und zeigt weder Auftrag, Artikel noch Restmenge.

## Luecken

| Prio | Prozess | Luecke | Eintrag |
|---|---|---|---|
| P1 | VK-05 | Sammelfakturierung offener Lieferscheine (Auswahl, Kontrolle, Probedruck, Lauf) fehlt | — |
| P2 | VK-01 | Browserkette Angebot > Auftrag durch die Belegmaske mit echtem Backend fehlt | — |
| P2 | VK-02 | Browserkette Auftrag erfassen > bestaetigen > Lieferschein durch die Belegmaske fehlt | — |
| P2 | VK-03 | Agrarspalten der Lieferscheinposition (Charge, Gefahrgut, Bio/Nachhaltigkeit) gegen L3 nicht abgeglichen | — |
| P2 | VK-04 | Browserkette Lieferschein > Rechnung buchen durch die Belegmaske fehlt | — |
| P2 | VK-06 | Ausgangsbuch-Sicht mit Fibu-Uebergabestatus, Storno-Filter und Summen je Waehrung nicht belegt | — |
| P2 | VK-07 | Browserkette Gutschrift mit Bezugsrechnung durch die Belegmaske fehlt | — |
| P2 | VK-08 | Maske sales/lieferung-storno gegen den Storno-Weg der Belegmaske abgleichen oder entfernen | — |
| P2 | VK-09 | Kreditlimitsperre beim Freigeben eines Auftrags als Integrationstest gegen PostgreSQL fehlt | — |
| P2 | VK-10 | Rueckstandsliste als echte Liste offener Auftragspositionen mit Restmenge aus DocFlow, mit Integrationstest | — |
| P3 | VK-03 | Funktion "wie vorheriger Lieferschein" (L3 F11) nicht vorhanden oder nicht belegt | — |

## Maskenabnahme (maschinell)

Bereiche im Inventar: sales, verkauf, vertrieb. Routen: 48 — studio_versioniert 48.

Generische Platzhaltermasken (nur Kennung/Name/Status/Datum, nur Export): 8:

- `sales/auftrag-lieferschein-abgleich` — Auftrag lieferschein abgleich
- `sales/auftragskette` — Auftragskette
- `sales/kalkulationen/neu` — Kalkulation
- `sales/lieferung-storno` — Lieferung storno
- `verkauf/betriebs-auftraege` — Betriebs auftraege
- `verkauf/kommissions-auftraege` — Kommissions auftraege
- `verkauf/unerledigte-auftrags-positionen` — Unerledigte auftrags positionen
- `vertrieb/kundenumsatz` — Kundenumsatz

Aktionen der Domaenenmasken: 119, davon serverwirksam 61; ohne CLI 0; nicht verfuegbar 0; nicht deklariert 7.

## Demo- und Festwerte (Stichwortsuche in den Seitenquellen)

Keine Treffer.

## Rollen

Schreibwege ohne erkennbare Rollenpruefung systemweit: 0 (`python scripts/check_write_routes_roles.py --check`). Die Rolle je Prozess steht in der Prozessliste; sie ist am Endpunkt gelesen, nicht nur an der Navigation.
