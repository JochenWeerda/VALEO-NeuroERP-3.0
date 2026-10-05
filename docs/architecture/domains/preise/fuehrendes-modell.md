# Führendes Preismodell (ADR)

Stand: 2026-10-05 · Status: **entschieden** · Entscheider: Claude Code, fachliche
Abnahme offen beim Vertriebs-Owner

## Anlass

Zwanzig Tabellen in sechs Schemata führen Preise, Rabatte, Staffeln oder
Zu-/Abschläge. Beim Slice `PREISFINDUNG-KASKADE-20261005` zeigte sich, warum das
nicht nur unübersichtlich ist: Die Preisfindung las drei Quellen, die es nicht
gibt, und ignorierte eine, die gepflegt wird. Ohne eine Festlegung, **welche
Tabelle für welche Aussage führt**, wiederholt sich das bei jedem neuen Weg.

Dieses ADR ordnet alle zwanzig. Jede wird einer von drei Klassen zugewiesen:

* **führend** — die Preisfindung liest sie, und sie ist die Wahrheit für ihre
  Aussage;
* **eigener Zweck** — sie trägt eine andere Aussage und steht zu Recht daneben;
* **abzulösen** — sie sagt dasselbe wie eine führende Tabelle.

## A. Führend — die Preiskaskade

Die Kaskade ist in `app/services/preisfindung_service.py` festgelegt
(`STUFEN`), ausgewertet in `GET /api/v1/pricing/calculate`. Es gilt **eine**
Stufe — die erste, die greift; nicht additiv. Die Reihenfolge geht vom Besonderen
zum Allgemeinen, weil eine Zusage für diesen Kunden und diesen Artikel mehr wiegt
als eine allgemeine Regel.

| # | Stufe | Führende Tabelle | Aussage |
| --- | --- | --- | --- |
| 0 | `base` | `domain_inventory.articles.sales_price` | Verkaufspreis des Artikels |
| 1 | `price_list` | `domain_pricing.price_lists` + `price_list_items` | Allgemeine Preisliste, ersetzt den Basispreis |
| 2 | `contract` | `domain_ops.kon_contract_line` | Zusage für **diesen Vorgang**: `unit_price`, `discount_pct` je Artikel |
| 3 | `customer_price` | `domain_crm.business_partner_price_agreements` | Dauerhafte Zusage für Kunde + Artikel (`price_net`, `discount_allowed`) |
| 4 | `staffelrabatt` | `domain_pricing.staffelrabatte` + `staffelrabatt_artikel` | Mengenstaffel, hängt an der bestellten Menge |
| 5 | `customer_article_discount` | `domain_crm.business_partner_discount_items` | Rabatt für Kunde + Artikel |
| 6 | `customer_discount` | `domain_crm.business_partners.discount_percent` | Pauschaler Rabatt des Kunden |
| 7 | `employee_discount` | `domain_pricing.discount_rules` | Rabatt einer Rolle |

Dazu zwei **Sperren**, die keine Stufe sind, sondern über allen stehen:

| Sperre | Quelle | Wirkung |
| --- | --- | --- |
| Rabattfähigkeit | `domain_inventory.articles.rabattfaehig` | Ein nicht rabattfähiger Artikel bekommt **keinen** Rabatt, aus keiner Stufe. |
| Rabattverbot der Zusage | `business_partner_price_agreements.discount_allowed` | Ist ein Preis zugesagt und weiterer Rabatt ausgeschlossen, senkt ihn keine spätere Stufe. |

Beide werden in der Antwort benannt (`rabatt_gesperrt`, `rabatt_sperrgrund`): Ein
stillschweigender Rabatt von null wäre nicht unterscheidbar von „kein Rabatt
gefunden".

### Zwei Entscheidungen zur Reihenfolge

**`customer_price` vor `staffelrabatt`.** Eine mit dem Kunden vereinbarte
Preisstellung ist eine Zusage; eine Mengenstaffel ist eine allgemeine Regel des
Hauses. Die Zusage gewinnt — sonst könnte eine neu gepflegte Staffel eine
vertraglich zugesagte Preisstellung aushebeln.

**`staffelrabatt` vor `customer_discount`.** Die Staffel hängt an der
tatsächlich bestellten Menge und ist damit die spezifischere Aussage als ein
pauschaler Kundenrabatt. Der artikelbezogene Kundenrabatt
(`customer_article_discount`) steht wiederum darüber, weil er Kunde **und**
Artikel nennt.

### Mandantengrenze der Satelliten

`business_partner_price_agreements` und `business_partner_discount_items` führen
**kein** `tenant_id`. Das bleibt so: Die Grenze kommt aus dem Verbund mit
`business_partners` (`JOIN … ON p.partner_id = s.partner_id AND p.tenant_id = :tid`).
Eine zweite Mandantenspalte neben der des Vaters wäre eine zweite Wahrheit, die
abweichen kann — und abweichen würde, sobald ein Partner den Mandanten wechselt
oder ein Satellit ohne den Vater geschrieben wird.

## B. Eigener Zweck — bleiben, sind keine Preisfindung

| Tabelle | Aussage | Weg |
| --- | --- | --- |
| `domain_inventory.daily_prices` | Tagespreis Agrar (Erfassung, Überwachung) | `daily_prices.py`, `price_monitoring_worker.py`, `harvest_acceptance.py` |
| `domain_inventory.price_adjustment_rules` | Regeln zur Tagespreisfortschreibung | `daily_prices.py` |
| `domain_shared.rohware_za_staffeln` + `_zeilen` | **Qualitätsbezogene** Zu- und Abschläge bei Rohware (Feuchte, Besatz) — nicht mengenbezogen | `rohwarengruppen.py` |
| `domain_ops.price_hedges` | MATIF-Absicherung einer Position | Kontrakt-Hedging |
| `domain_sales.sales_preisabweichungen` | Protokoll der Abweichung vom gefundenen Preis (Kontrolle) | `sales_preisabweichung_service.py` |
| `domain_shared.vertreter_provisionsstaffeln` + `_zeilen` | Provision des Vertreters — kein Preis gegenüber dem Kunden | `vertreterprovisionen.py` |
| `domain_crm.business_partner_pricing_rules` | Parameter der Preisfindung je Partner (`price_determination_mode`, `self_pickup_discount_percent`) | CRM-360 |

Die Zu-/Abschlagsstaffel der Rohware wird ausdrücklich **nicht** mit der
Mengenstaffel zusammengelegt: Die eine bewertet die gelieferte Qualität, die
andere die Menge. Sie treffen verschiedene Aussagen über verschiedene Dinge.

`business_partner_pricing_rules` ist ein naheliegender Kandidat für eine spätere
Stufe (Selbstabholerrabatt). Heute liest die Kaskade sie nicht; das ist eine
benannte Lücke, keine stille.

## C. Abzulösen

### `domain_shared.individualpreise`

Sagt dasselbe wie `business_partner_price_agreements`: Partner + Artikel →
Preis, mit Gültigkeitszeitraum. Sie führt zusätzlich `preis_typ` und
`staffel_menge`, also eine dritte Mengenstaffel.

**Entschieden:** `business_partner_price_agreements` führt. Begründung: Sie liegt
im Partnerdomänenmodell, in dem der Partner selbst liegt (eine Beziehung statt
einer Nummernkopie `partner_nr`), und sie trägt die Felder, die ein Landhandel
braucht — `price_incl_freight`, `special_freight`, `payment_condition`,
`discount_allowed` — sowie Änderungsnachweise.

**Stand und nächste Schritte:** Beide Tabellen sind in allen Datenbanken **leer**
(0 Zeilen), es ist also keine Datenübernahme nötig. Die Ablösung ist in diesem
ADR entschieden, aber **nicht ausgeführt**: Es hängen eine Maske
(`pages/preise/individualpreise.tsx`), ein API-Modul
(`lib/api/individualpreise.ts`), generierte Routen, ein Navigationseintrag, ein
Endpunkt (220 Zeilen) und ein Maskentest daran. Das ist ein eigener Slice.
Solange: Die Preisfindung liest `individualpreise` **nicht**, und die Maske sagt
das — eine Maske, in der man einen Preis erfasst, der nie gilt, ist dieselbe
Täuschung wie ein verschluckter Fehler.

### `domain_inventory.article_price_thresholds`

Mengenschwellen je Artikel — dasselbe wie `staffelrabatte` ohne Kunden- und
Gruppenbezug. 0 Zeilen, **kein Weg dorthin** (nur ein Modell in
`l3c_models.py`). Abzulösen durch `staffelrabatte`; kein Handlungsbedarf außer
dem Nichtbenutzen, weil nichts darauf zeigt.

## D. Nicht anschließbar — benannte Lücke

`domain_shared.preis_rabattgruppen`, `preis_rabattklassen` und
`preis_rabattsaetze` bilden die klassische Rabattmatrix: Kundengruppe ×
Artikelklasse × Richtung (EK/VK) → Rabattsatz, mit `ab_menge`.

Das ist **keine** Doppelung — es ist die Gruppenebene, die die artikelbezogenen
Satelliten nicht haben. Sie kann heute aber nicht ausgewertet werden:

* Kundenseite vorhanden: `business_partners.price_group`.
* **Artikelseite fehlt:** `domain_inventory.articles` führt keine Rabattklasse.
  Es gibt `warengruppe`, `mvo_gruppe`, `gefahrgutklasse` — keine
  `rabattklasse_nr`.

Solange diese Spalte fehlt, bleibt die Matrix ein Erfassungsweg ohne Wirkung. Die
fehlende Voraussetzung ist damit genau benannt: **eine Spalte `rabattklasse_nr`
auf `domain_inventory.articles`** plus die Stufe `group_discount` zwischen
`customer_discount` und `employee_discount`. Das ist ein eigener Slice; dieses
ADR legt die Stelle in der Kaskade vorab fest, damit sie nicht später erfunden
wird.

## Was dieses ADR nicht entscheidet

* Die fachliche Reihenfolge der Stufen — sie ist hier begründet, aber die Abnahme
  gehört dem Vertriebs-Owner.
* Die einkaufsseitige Preisfindung (`richtung = 'EK'` in der Matrix,
  `articles.purchase_price`). Die Kaskade ist verkaufsseitig.
* Die Ablösung der Erfassungswege unter C — entschieden, aber als eigene Slices
  zu terminieren.

## Nachweis

`tests/test_preisfindung_kaskade_vertrag.py` (29) und
`tests/test_preismodell_kundenstufe_vertrag.py` (20) prüfen die Kaskade gegen
eine echte Datenbank, einschließlich der Reihenfolge, der Mandantengrenze über
den Verbund und beider Sperren. Die Stufenfolge steht genau einmal im Code
(`preisfindung_service.STUFEN`); `QUELLEN` leitet sich daraus ab.

Belege und Fundstellen:
`docs/quality-assurance/preisfindung-kaskade-20261005.md`,
`docs/quality-assurance/preismodell-kundenstufe-20261005.md`.
