# Kundenstufe der Preisfindung und führendes Preismodell (Slice PREISMODELL-KUNDENSTUFE-20261005)

Stand: 2026-10-05 · Welle 2, Slice 16 · schließt die beiden offenen Punkte aus
[Preisfindung-Kaskade](preisfindung-kaskade-20261005.md)

## 1. Der Kundenrabatt las die falsche Tabelle

```python
text("SELECT discount, discount_percent FROM domain_crm.customers WHERE id = :id AND tenant_id = :tid")
```

Diese beiden Spalten gibt es nicht. Die Methode fing den Fehler und lieferte
`None` — und sie sagte das im Docstring, also hat sie nicht gelogen. Die Stufe
wirkte nur nie. Ein dokumentierter Blindgänger ist besser als ein stiller, aber
ein Kundenrabatt, der nie greift, ist für ein Landhandelssystem keine
Nebensache.

Die Rabattinformation liegt vollständig an anderer Stelle:

| Quelle | Aussage |
| --- | --- |
| `domain_crm.business_partner_price_agreements` | Kunde + Artikel → **Preis** (`price_net`, `discount_allowed`, `price_incl_freight`, `payment_condition`) |
| `domain_crm.business_partner_discount_items` | Kunde + Artikel → **Rabatt** |
| `domain_crm.business_partners.discount_percent` | Kunde → pauschaler Rabatt |

`domain_crm.customers.business_partner_id` ist die Brücke. Beide Wege werden
akzeptiert: Aufrufer geben je nach Maske eine CRM-Kundenkennung oder direkt eine
Partnerkennung; `partner_id_fuer_kunden()` prüft beide gegen den Mandanten.

### Die Mandantengrenze kommt aus dem Verbund

Die beiden Satellitentabellen führen **kein** `tenant_id`. Das bleibt so, und das
ist eine Entscheidung: Eine zweite Mandantenspalte neben der des Vaters wäre eine
zweite Wahrheit, die abweichen kann — und abweichen würde, sobald ein Satellit
ohne den Vater geschrieben wird. Gelesen wird deshalb immer

```sql
JOIN domain_crm.business_partners p
     ON p.partner_id = s.partner_id AND p.tenant_id = :tid
```

Ein Vertrag prüft das strukturell: Beide Leser müssen diesen Verbund enthalten.

## 2. Zwei Sperren, die der Bestand kennt und die Kaskade nie gelesen hat

**`domain_inventory.articles.rabattfaehig`.** Der Artikelstamm sagt je Artikel,
ob er rabattfähig ist (und kennt daneben `rabatt_auftrag_rechnung`,
`rabatt_selbstabholer`, `rabatt_lose`). Die Kaskade las nichts davon. Ein nicht
rabattfähiger Artikel bekam Rabatt — eine Preiszusage, die das Haus nicht geben
wollte.

**`business_partner_price_agreements.discount_allowed`.** Ist ein Preis zugesagt
und weiterer Rabatt ausgeschlossen, darf keine spätere Stufe ihn senken.

Beide Sperren stehen **über** den Stufen, nicht in ihnen. Und sie werden in der
Antwort benannt: `rabatt_gesperrt` und `rabatt_sperrgrund`. Ein stillschweigender
Rabatt von null wäre nicht unterscheidbar von „kein Rabatt gefunden" — und genau
diese Verwechslung ist das Muster, das diese Welle abbaut.

## 3. Die Kaskade jetzt

| # | Stufe | Quelle |
| --- | --- | --- |
| 0 | `base` | `articles.sales_price` |
| 1 | `price_list` | `price_lists` + `price_list_items` |
| 2 | `contract` | `kon_contract_line` |
| 3 | `customer_price` | `business_partner_price_agreements` |
| 4 | `staffelrabatt` | `staffelrabatte` |
| 5 | `customer_article_discount` | `business_partner_discount_items` |
| 6 | `customer_discount` | `business_partners.discount_percent` |
| 7 | `employee_discount` | `discount_rules` |

**`customer_price` vor `staffelrabatt`:** Eine mit dem Kunden vereinbarte
Preisstellung ist eine Zusage, eine Mengenstaffel eine allgemeine Hausregel.
Sonst könnte eine neu gepflegte Staffel eine zugesagte Preisstellung aushebeln.

**`customer_article_discount` vor `customer_discount`:** Kunde **und** Artikel ist
spezifischer als Kunde allein.

Die Reihenfolge steht einmal im Code (`preisfindung_service.STUFEN`); `QUELLEN`
leitet sich daraus ab.

## 4. Das ADR

`docs/architecture/domains/preise/fuehrendes-modell.md` ordnet **alle zwanzig**
Preis- und Rabatttabellen in drei Klassen:

* **Führend (8 Tabellen):** die Kaskade oben.
* **Eigener Zweck (7):** Tagespreise Agrar, qualitätsbezogene Zu-/Abschläge der
  Rohware, MATIF-Hedges, das Abweichungsprotokoll, Vertreterprovisionen, die
  Preisfindungsparameter am Partner. Die Zu-/Abschlagsstaffel der Rohware wird
  ausdrücklich **nicht** mit der Mengenstaffel zusammengelegt: Die eine bewertet
  die gelieferte Qualität, die andere die Menge.
* **Abzulösen (2):** `domain_shared.individualpreise` (sagt dasselbe wie die
  Preisvereinbarungen) und `domain_inventory.article_price_thresholds` (dasselbe
  wie die Mengenstaffel, ohne Weg dorthin).

### Nicht anschließbar — und das ist jetzt benannt

`preis_rabattgruppen` / `preis_rabattklassen` / `preis_rabattsaetze` sind die
klassische Rabattmatrix (Kundengruppe × Artikelklasse × Richtung → Satz). Das ist
**keine** Doppelung — es ist die Gruppenebene, die die artikelbezogenen Satelliten
nicht haben. Sie kann heute aber nicht ausgewertet werden:

* Kundenseite vorhanden: `business_partners.price_group`.
* **Artikelseite fehlt:** `articles` führt keine `rabattklasse_nr`.

Das ADR nennt die fehlende Voraussetzung genau — eine Spalte plus die Stufe
`group_discount` zwischen `customer_discount` und `employee_discount` — und legt
deren Platz in der Kaskade vorab fest, damit er später nicht erfunden wird.

### Zur Ablösung von `individualpreise`

Entschieden, nicht ausgeführt: Daran hängen eine Maske, ein API-Modul, generierte
Routen, ein Navigationseintrag, ein 220-Zeilen-Endpunkt und ein Maskentest. Beide
Tabellen sind leer (0 Zeilen), eine Datenübernahme ist also nicht nötig. Solange
sagt die Maske, was sie ist:

> **Dieser Weg bestimmt den Preis nicht.** Die Preisfindung liest
> kundenspezifische Preise aus den Preisvereinbarungen am Geschäftspartner.

Eine Maske, in der man einen Preis erfasst, der nie gilt, ist dieselbe Täuschung
wie ein verschluckter Fehler.

## Nachweis

```
DATABASE_URL=…/valeo_probe python -m pytest \
  tests/test_preismodell_kundenstufe_vertrag.py   → 20 passed
  tests/test_preisfindung_kaskade_vertrag.py      → 29 passed
  tests/test_api_gap_lager_pricing_scan.py        → zusammen 67 passed
```

Die 20 neuen Verträge prüfen unter anderem: der pauschale Rabatt kommt aus dem
Partnerstamm; eine Partnerkennung wirkt wie eine Kundenkennung; ein fremder Kunde
bringt keinen Rabatt (Haus B gewährt 25 %, in Haus A wirkt es nicht); ein Rabatt
von null ist kein Rabatt; der artikelbezogene Rabatt schlägt den pauschalen; ein
Rabattposten zu einem anderen Artikel, ein abgelaufener und einer des fremden
Partners wirken nicht; die Preisvereinbarung ersetzt den Listenpreis; der
Artikelrabatt gilt auf den vereinbarten Preis; `discount_allowed = false`
schließt Rabatt aus und nennt den Grund; `rabattfaehig = false` sperrt jeden
Rabatt; die Sperre ist von „kein Rabatt gefunden" unterscheidbar; die alte
Abfrage auf `customers.discount` kommt im Code nicht mehr vor; beide Satelliten
werden über den Verbund eingegrenzt.

**Keine Migration.** Alle benötigten Spalten waren vorhanden — das war der
eigentliche Befund: Die Information lag da, sie wurde nur nicht gelesen.

Gates: alle vier grün, Tabellenverweise unverändert bei 7 an lebenden Wegen.

## Offene Punkte (Handshake)

1. **Fachliche Abnahme der Stufenreihenfolge** beim Vertriebs-Owner.
2. **`rabattfaehig` greift jetzt.** Das kann Preise ändern, die bisher
   stillschweigend rabattiert wurden. Gehört vor der Inbetriebnahme
   kommuniziert.
3. **Die Rabattmatrix** braucht `articles.rabattklasse_nr` — eigener Slice, Platz
   in der Kaskade im ADR festgelegt.
4. **Ablösung `individualpreise`** — entschieden, eigener Slice.
5. **`business_partner_pricing_rules`** (Selbstabholerrabatt,
   `price_determination_mode`) ist ein naheliegender Kandidat für eine weitere
   Stufe. Benannte Lücke.
6. **Fremder Rotstand:** `tests/test_crm_customer_business_partner_link.py`
   schlägt mit zwei Fehlern fehl — `_FakeResult` kennt kein `mappings()` und
   `_CapturingDb` kein `rollback()`, seit `customer_service._attach_partner_mask_fields`
   (Commit `c4a206f04`) so liest. Die Kette liegt vollständig in
   `customer_service.py`; nicht aus diesem Slice, nicht angefasst — CRM-Agent.
